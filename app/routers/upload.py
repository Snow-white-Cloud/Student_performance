from fastapi import APIRouter
from app import schemas
import csv
from app.config import settings
from app.database import get_connect

router = APIRouter(prefix="/upload-grades", tags=["Upload"])

@router.post("/")
async def upload_csv_batch(csv_path: str):
    async with get_connect() as connect:
        async with connect.transaction():
            with open(csv_path, encoding='utf-8') as f:
                batch = []
                count_students = 0
                count_records = 0
                students_cache = dict()

                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    try:
                        data_grade = schemas.CsvDataGrade(**row)
                        count_records += 1
                    except Exception as e:
                        print(f"Ошибка валидации строки {row}: {e}")
                        continue
                        
                    key = (data_grade.full_name, data_grade.group)
                    if key in students_cache:
                        id_student = students_cache[key]
                    else:
                        record = await connect.fetchrow(
                            "SELECT id FROM Students WHERE full_name = $1 AND group = $2",
                            {data_grade.full_name, data_grade.group}
                        )
                        if not(record):
                            record = await connect.fetchrow(
                                "INSERT INTO Students (full_name, group) VALUES ($1, $2) RETURNING id",
                                {data_grade.full_name, data_grade.group}
                            )
                            count_students += 1
                        id_student = record["id"]
                        students_cache[key] = id_student
                    
                    batch.append((data_grade.grade, data_grade.date_of_mark, id_student))

                    if len(batch) >= settings.SIZE_BATCH:
                        await connect.executemany(
                            """
                            INSERT INTO Grades (grade, date_of_mark, id_student) VALUES ($1, $2, $3)
                            """,
                            batch
                        )
                        batch.clear()
                
                if batch:
                    await connect.executemany(
                        """
                        INSERT INTO Grades (grade, date_of_mark, id_student) VALUES ($1, $2, $3)
                        """,
                        batch
                    )

    return {
        "status": "ok",
        "records_loaded": count_records,
        "students": count_students
    }



