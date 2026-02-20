from fastapi import APIRouter, UploadFile, File, HTTPException
from app import schemas
import csv
from app.config import settings
from app.database import get_connect
from io import StringIO

router = APIRouter(prefix="/upload-grades", tags=["upload"])

@router.post("/", response_model=schemas.UploadResponse)
async def upload_csv_batch(file: UploadFile = File(...)):
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")
    
    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Cannot decode file. Please upload a UTF-8 encoded CSV.")

    f = StringIO(text)
    reader = csv.DictReader(f, delimiter=';')

    count_students = 0
    count_records = 0
    async with get_connect() as connect:
        async with connect.transaction():
            batch_grades_know_stud = []
            batch_grades_unknow_stud = []

            records = await connect.fetch("SELECT id, full_name, study_group FROM Students")
            students_cache = { (r["full_name"], r["study_group"]): r["id"] for r in records }

            for row in reader:
                try:
                    data_grade = schemas.CsvDataGrade(**row)
                    count_records += 1
                except Exception as e:
                    print(f"Ошибка валидации строки {row}: {e}")
                    continue
                
                key = (data_grade.full_name, data_grade.study_group)
                if key in students_cache:
                    batch_grades_know_stud.append((data_grade.grade, data_grade.time_of_mark, students_cache[key]))
                else:
                    batch_grades_unknow_stud.append((data_grade.full_name, data_grade.study_group, data_grade.grade, data_grade.time_of_mark))

                if len(batch_grades_know_stud) >= settings.SIZE_BATCH:
                    await flush_batch_grades_know_stud(connect, batch_grades_know_stud)
                
                if len(batch_grades_unknow_stud) >= settings.SIZE_BATCH_NEW_STUD:
                    await flush_batch_grades_unknow_stud(connect, batch_grades_unknow_stud, students_cache)

            if batch_grades_know_stud:
                await flush_batch_grades_know_stud(connect, batch_grades_know_stud)
            if batch_grades_unknow_stud:
                await flush_batch_grades_unknow_stud(connect, batch_grades_unknow_stud, students_cache)
            count_students = len(students_cache)

    return schemas.UploadResponse(
        status = "ok",
        records_loaded = count_records,
        students = count_students
    )


async def flush_batch_grades_know_stud(connect, batch_grades_know_stud: list):
    await connect.executemany(
        """
        INSERT INTO Grades (grade, date_of_mark, id_student) VALUES ($1, $2, $3)
        """,
        batch_grades_know_stud
    )
    batch_grades_know_stud.clear()


async def flush_batch_grades_unknow_stud(connect, batch_grades_unknow_stud: list, students_cache: dict):
    new_students = list(set([(batch[0], batch[1]) for batch in batch_grades_unknow_stud]))

    
    await connect.executemany(
        """
        INSERT INTO Students (full_name, study_group) VALUES ($1, $2)
        ON CONFLICT (full_name, study_group) DO NOTHING
        """,
        new_students
    )
                        
    records = await connect.fetch(
        """
        SELECT id, full_name, study_group FROM Students
        WHERE (full_name, study_group) = ANY($1::(varchar, char(4))[])
        """,
        new_students)
    for r in records:
        students_cache[(r.full_name, r.study_group)] = r.id
                        
    await connect.executemany(
        """
        INSERT INTO Grades (grade, date_of_mark, id_student) VALUES ($1, $2, $3)
        """,
        [(batch[2], batch[3], students_cache[(batch[0], batch[1])]) for batch in batch_grades_unknow_stud]
    )
    
    batch_grades_unknow_stud.clear()