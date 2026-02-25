from fastapi import APIRouter, Depends, HTTPException
from app.schemas import schemas
from app.schemas import depends
from app.database import get_connect
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/students", tags=["grades"])

# Поиск студентов, у которых количество искомых отметок БОЛЬШЕ заданного
@router.get("/more-than-3-twos", response_model=schemas.GetStudentsCountGrades)
async def more_than_three_twos(params: schemas.GradeParams = Depends(depends.get_grade_params_more)): # Параментры: искомая отметка target_grade и их количество count
    try:
        async with get_connect() as connect:
            # Получение студентов и количества их искомых отметок (со всеми условиями)
            query = "SELECT grades_more_than($1, $2)"
            json_str = await connect.fetchval(query, params.target_grade, params.count)
            logger.info("Получен JSON после SQL функции")
            
            # Если студентов нет
            if not(json_str) or json_str == '[]':
                return schemas.GetStudentsCountGrades([])

            # Ошибка чтения
            data = json.loads(json_str)
            if isinstance(data, dict) and "Error" in data:
                logger.error(f"Ошибка функции БД: {data['Error']}", exc_info=True)
                raise HTTPException(status_code=400, detail=f"Ошибка выполнения функции")
            
            # Валидация JSON и возврат
            validated_data = schemas.GetStudentsCountGrades.parse_obj(data)
            logger.info("JSON расшифрован и валидирован")
            return validated_data
    
    except json.JSONDecodeError as error:
        logger.exception(f"Ошибка парсинга JSON из БД: {error}")
        raise HTTPException(status_code=500, detail="Ошибка обработки данных")

    except HTTPException:
        raise

    except Exception as error:
        logger.exception(f"Неожиданная ошибка при обработке /students/more-than-3-twos: {error}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


# Поиск студентов, у которых количество искомых отметок МЕНЬШЕ заданного
@router.get("/less-than-5-twos", response_model=schemas.GetStudentsCountGrades)
async def less_than_five_twos(params: schemas.GradeParams = Depends(depends.get_grade_params_less)): # Параментры: искомая отметка target_grade и их количество count
    try:
        async with get_connect() as connect:
            # Получение студентов и количества их искомых отметок (со всеми условиями)
            query = "SELECT grades_less_than($1, $2)"
            json_str = await connect.fetchval(query, params.target_grade, params.count)
            logger.info("Получен JSON после SQL функции")

            # Если студентов нет
            if not(json_str) or json_str == '[]':
                return schemas.GetStudentsCountGrades([])

            # Ошибка чтения
            data = json.loads(json_str)
            if isinstance(data, dict) and "Error" in data:
                logger.error(f"Ошибка функции БД: {data['Error']}", exc_info=True)
                raise HTTPException(status_code=400, detail=f"Ошибка выполнения функции")

            # Валидация JSON и возврат
            validated_data = schemas.GetStudentsCountGrades.parse_obj(data)
            logger.info("JSON расшифрован и валидирован")
            return validated_data
    
    except json.JSONDecodeError as error:
        logger.exception(f"Ошибка парсинга JSON из БД: {error}")
        raise HTTPException(status_code=500, detail="Ошибка обработки данных")

    except HTTPException:
        raise

    except Exception as error:
        logger.exception(f"Неожиданная ошибка при обработке /students/less-than-5-twos: {error}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")