from fastapi import APIRouter, UploadFile, File, HTTPException
from app import schemas
import csv
from app.config import settings
from app.database import get_connect
from io import StringIO
import logging


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload-grades", tags=["upload"])

# Логика батчевой (как для студентов, так и для отметок) загрузки данных с таблицу
@router.post("/", response_model=schemas.UploadResponse)
async def upload_csv_batch(file: UploadFile = File(...)): # Требуем файл
    # Основные проверки для файла
    if file.content_type != "text/csv":
        logger.warning("Тип файла не CSV")
        raise HTTPException(status_code=400, detail="Некорректный тип файла. Допустим формат CSV")
    
    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        logger.warning("Невозможно декодировать файл")
        raise HTTPException(status_code=400, detail="Невозможно декодировать файл. Убедитесь, что использован UTF-8")

    f = StringIO(text)
    reader = csv.DictReader(f, delimiter=';')
    logger.info("Файл готов к работе")

    count_students = 0 # Общее количество студентов в БД 
    count_records = 0 # Количество загруженных записей
    try:
        async with get_connect() as connect:
            async with connect.transaction():
                batch_grades_know_stud = [] # Батч для отметок, у которых студенты уже внесены в таблицу
                batch_grades_unknow_stud = [] # Батч для отметок и студентов, которые встречаются впервые. Для него размер меньше

                # Настройка кэша для известных студентов для ускорения поиска,
                # для уменьшения количества запросов к БД,
                # т.к. нам во входных данных неизвестны id студентов
                records = await connect.fetch("SELECT id, full_name, study_group FROM Students")
                students_cache = { (r["full_name"], r["study_group"]): r["id"] for r in records }
                logger.info("Получены все известные студенты")

                # Логика обработки строк
                for row in reader:
                    try:
                        data_grade = schemas.CsvDataGrade(**row)
                        count_records += 1
                    except Exception as error:
                        logger.exception(f"Ошибка валидации строки {row}: {error}")
                        continue
                    
                    # Если рассматриваемый студент есть в БД, то данные об его отметке копим в batch_grades_know_stud;
                    # если неизвестен, то в батче batch_grades_unknow_stud
                    key = (data_grade.full_name, data_grade.study_group)
                    if key in students_cache:
                        batch_grades_know_stud.append((data_grade.grade, data_grade.time_of_mark, students_cache[key]))
                    else:
                        batch_grades_unknow_stud.append((data_grade.full_name, data_grade.study_group, data_grade.grade, data_grade.time_of_mark))

                    # Переполнение batch_grades_know_stud
                    if len(batch_grades_know_stud) >= settings.SIZE_BATCH: 
                        logger.debug(f"Вставка полного батча с известными студентами размером {len(batch_grades_know_stud)}")
                        await flush_batch_grades_know_stud(connect, batch_grades_know_stud)
                    
                    # Переполнение batch_grades_unknow_stud
                    if len(batch_grades_unknow_stud) >= settings.SIZE_BATCH_NEW_STUD:
                        logger.debug(f"Вставка полного батча с неизвестными студентами размером {len(batch_grades_unknow_stud)}")
                        await flush_batch_grades_unknow_stud(connect, batch_grades_unknow_stud, students_cache)

                # Догрузка остатков
                if batch_grades_know_stud:
                    logger.debug(f"Вставка остаточного батча с известными студентами размером {len(batch_grades_know_stud)}")
                    await flush_batch_grades_know_stud(connect, batch_grades_know_stud)
                if batch_grades_unknow_stud:
                    logger.debug(f"Вставка остаточного батча с неизвестными студентами размером {len(batch_grades_unknow_stud)}")
                    await flush_batch_grades_unknow_stud(connect, batch_grades_unknow_stud, students_cache)
                count_students = len(students_cache)
                logger.info("Валидные данные успешно обработаны")

    except HTTPException:
        raise

    except Exception as error:
        logger.exception(f"Неожиданная ошибка при обработке /upload-grades: {error}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
    

    return schemas.UploadResponse(
        status = "ok",
        records_loaded = count_records,
        students = count_students
    )


# Батчевая загрузка отметок дуже внесённых в БД студентов
async def flush_batch_grades_know_stud(connect, batch_grades_know_stud: list):
    try:
        await connect.executemany(
            """
            INSERT INTO Grades (grade, date_of_mark, id_student) VALUES ($1, $2, $3)
            """,
            batch_grades_know_stud
        )
        logger.debug("Батч для известных студентов вставлен")
        batch_grades_know_stud.clear()
    
    except Exception as error:
        logger.exception(f"Ошибка вставки отметок известных студентов: {error}")
        raise


# Батчевая загрузка неизвестных для БД студентов и их отметок
async def flush_batch_grades_unknow_stud(connect, batch_grades_unknow_stud: list, students_cache: dict):
    # Формирование батч для загрузки студентов
    new_students = list(set([(batch[0], batch[1]) for batch in batch_grades_unknow_stud]))

    try:
        await connect.executemany(
            """
            INSERT INTO Students (full_name, study_group) VALUES ($1, $2)
            ON CONFLICT (full_name, study_group) DO NOTHING
            """,
            new_students
        )
        logger.debug("Неизвестные студенты вставлены")

        # Обновление кэша студентов
        records = await connect.fetch(
            """
            SELECT id, full_name, study_group FROM Students
            WHERE (full_name, study_group) = ANY($1::(varchar, char(4))[])
            """,
            new_students)
        for r in records:
            students_cache[(r.full_name, r.study_group)] = r.id
        logger.debug("Обновлён кеш известных студентов")

        # Батчевая загрузка отметок
        await connect.executemany(
            """
            INSERT INTO Grades (grade, date_of_mark, id_student) VALUES ($1, $2, $3)
            """,
            [(batch[2], batch[3], students_cache[(batch[0], batch[1])]) for batch in batch_grades_unknow_stud]
        )
        logger.debug("Отметки вставлены")
        
        batch_grades_unknow_stud.clear()

    except Exception as error:
        logger.exception(f"Ошибка вставки неизвестных студентов или их отметок: {error}")
        raise