from fastapi import APIRouter, Depends
from app import schemas
from app.database import get_connect
import json

router = APIRouter(prefix="/students", tags=["students", "grades"])

@router.get("/more-than-3-twos")
async def more_than_three_twos(params: schemas.GradeParams = Depends(schemas.get_grade_params)) -> schemas.GetStudentsCountGrades:
    async with get_connect() as connect:
        query = "SELECT grades_more_than($target_grade, $count)"
        json_str = await connect.fetchval(query, params.dict(by_alias=True))

        data = json.loads(json_str)
        validated_data = schemas.GetStudentsCountGrades.parse_obj(data)
        return validated_data


@router.get("/less-than-5-twos")
async def less_than_five_twos(params: schemas.GradeParams = Depends(schemas.get_grade_params)) -> schemas.GetStudentsCountGrades:
    async with get_connect() as connect:
        query = "SELECT grades_less_than($target_grade, $count)"
        json_str = await connect.fetchval(query, params.dict(by_alias=True))

        data = json.loads(json_str)
        validated_data = schemas.GetStudentsCountGrades.parse_obj(data)
        return validated_data