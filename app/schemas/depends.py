from fastapi import Query
from app import schemas

def get_grade_params(target_grade: int = Query(2, gt=1, lt=6), count: int = Query(3, gt=0)) -> schemas.GradeParams:
    return schemas.GradeParams(target_grade=target_grade, count=count)