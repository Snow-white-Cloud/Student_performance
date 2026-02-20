from pydantic import BaseModel, Field, validator
from typing import List
from datetime import date, datetime


# Схема для функций аналитики отметок
class GradeParams(BaseModel):
    target_grade: int = Field(2, gt=1, lt=6, description="Искомая отметка") # можно добавить алиасы
    count: int = Field(3, gt=0, description="Количество искомых оценок")

# Схема элемента ответа функции аналитики отметок
class InfoStudentCountGrades(BaseModel):
    full_name: str = Field(..., max_length=100, description="Полное имя студента")
    count_twos: int = Field(..., ge=0, description="Количество двоек")

# Схема для списка (JSON) элементов
class GetStudentsCountGrades(BaseModel):
    __root__: List[InfoStudentCountGrades]


# Схема для строки из csv файла для батчевой загрузки
class CsvDataGrade(BaseModel):
    full_name: str = Field(..., max_length=100, alias="ФИО", description="Полное имя студента")
    study_group: str = Field(..., max_length=4, alias="Номер группы", description="Учебная группа студента")
    grade: int = Field(..., gt=1, lt=6, alias="Оценка", description="Отметка")
    date_of_mark: date = Field(..., alias="Дата", description="Дата получения отметки")

    @validator("date_of_mark", pre=True)
    def parse_date_of_mark(cls, val_date):
        if isinstance(val_date, date):
            return val_date
        try:
            return datetime.strptime(val_date, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError(f"Invalid date format: {val_date}, expected DD.MM.YYYY")


# Схема для ответа после батчевой загрузки
class UploadResponse(BaseModel):
    status: str = Field(..., description="Статус")
    records_loaded: int = Field(..., ge=0, description="Количество загруженных записей (строк)")
    students: int = Field(..., ge=0, description="Общее количество студентов")




# Артефакты разработки (скоро будут убраны)
"""# Модели валидации для таблицы студентов, база
class StudentBase(BaseModel):
    full_name: str = Field(..., max_length=100, description='Полное имя студента')
    group: str = Field(..., max_length=4, description='Учебная группа студента')

# Чтение из таблицы студентов
class StudentRead(StudentBase):
    id: int = Field(..., description='Собственный уникальный ключ')

# Создание записи таблицы студентов
class StudentCreate(StudentBase):
    pass


# Модели валидации для таблицы отметок, база
class GradeBase(BaseModel):
    grade: int = Field(..., gt=1, lt=6, description='Отметка')
    date_of_mark: date = Field(..., description='Дата получения отметки')
    id_student: int = Field(..., description='Студент, получивший отметку')

# Чтение из таблицы отметок
class GradeRead(GradeBase):
    id: int = Field(..., description='Собственный уникальный ключ')

# Создание записи в таблице отметок
class GradeCreate(GradeBase):
    pass
"""