from pydantic import BaseModel, RootModel, Field, field_validator
from typing import List
from datetime import date, datetime


# Схема для функций аналитики отметок
class GradeParams(BaseModel):
    target_grade: int = Field(2, gt=1, lt=6, description="Искомая отметка")
    count: int = Field(3, gt=0, description="Количество искомых оценок")

# Схема элемента ответа функции аналитики отметок
class InfoStudentCountGrades(BaseModel):
    full_name: str = Field(..., max_length=100, description="Полное имя студента")
    count_twos: int = Field(..., ge=0, description="Количество двоек")

# Схема для списка (JSON) элементов
class GetStudentsCountGrades(RootModel[List[InfoStudentCountGrades]]):
    pass


# Схема для строки из csv файла для батчевой загрузки
class CsvDataGrade(BaseModel):
    full_name: str = Field(..., max_length=100, alias="ФИО", description="Полное имя студента")
    study_group: str = Field(..., max_length=4, alias="Номер группы", description="Учебная группа студента")
    grade: int = Field(..., gt=1, lt=6, alias="Оценка", description="Отметка")
    date_of_mark: date = Field(..., alias="Дата", description="Дата получения отметки")

    @field_validator("date_of_mark", mode="before")
    def parse_date_of_mark(cls, val_date):
        if isinstance(val_date, date):
            return val_date
        try:
            return datetime.strptime(val_date, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError(f"Invalid date format: {val_date}, expected DD.MM.YYYY")
        
    @field_validator("date_of_mark")
    def check_not_future(cls, val_date):
        if val_date > date.today():
            raise ValueError("Дата не может быть в будущем")
        return val_date


# Схема для ответа после батчевой загрузки
class UploadResponse(BaseModel):
    status: str = Field(..., description="Статус")
    records_loaded: int = Field(..., ge=0, description="Количество загруженных записей (строк)")
    students: int = Field(..., ge=0, description="Общее количество студентов")