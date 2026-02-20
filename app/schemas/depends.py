from fastapi import Query
from app import schemas

# Получение валидных параметров для функций more_than_three_twos и less_than_five_twos
def get_grade_params(target_grade: int = Query(2, gt=1, lt=6), count: int = Query(3, gt=0)) -> schemas.GradeParams:
    return schemas.GradeParams(target_grade=target_grade, count=count)