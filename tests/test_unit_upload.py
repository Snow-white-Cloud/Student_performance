import pytest
import fixture
from app.routers import upload
from unittest.mock import AsyncMock

# Проверка количества вызовов, очищения батча и аргументов вставки
@pytest.mark.asyncio
async def test_flush_batch_grades_know_stud_clear_batch():
    mk_connect = fixture.mock_connect(return_data=None)
    batch = [(3, "13.01.2024", 1)]

    await upload.flush_batch_grades_know_stud(connect=mk_connect, batch_grades_know_stud=batch)

    mk_connect.transaction.assert_called_once()
    mk_connect.executemany.assert_called_once_with([(3, "13.01.2024", 1)])
    assert batch == []


# Ошибка при вставке в БД
@pytest.mark.asyncio
async def test_flush_batch_grades_know_stud_raises_exception_on_db_error():
    mk_connect = fixture.mock_connect(return_data=None)
    mk_connect.executemany = AsyncMock(side_effect=Exception("DB error"))
    batch = [(3, "13.01.2024", 1)]

    with pytest.raises(Exception) as info:
        await upload.flush_batch_grades_know_stud(connect=mk_connect, batch_grades_know_stud=batch)
    
    assert batch != []
    assert "DB error" in str(info.value)

# Проверка количества вызовов, очищения батча и аргументов вставки
@pytest.mark.asyncio
async def test_flush_batch_grades_unknow_stud_correct_batch():
    mk_connect = fixture.mock_get_connect(return_data=[{"id": 1, "full_name": "Иван Иванович Иванов", "study_group": "103V"}])
    batch = [
        ("Иван Иванович Иванов", "103V", 3, "13.01.2024"),
        ("Иван Иванович Иванов", "103V", 5, "13.01.2024")
    ]
    students_cache = dict()

    await upload.flush_batch_grades_unknow_stud(connect=mk_connect, batch_grades_unknow_stud=batch, students_cache=students_cache)

    mk_connect.transaction.call_count == 2
    mk_connect.executemany.call_count == 2
    mk_connect.executemany.assert_called_with([(3, "13.01.2024", 1), (5, "13.01.2024", 1)])
    mk_connect.fetch.assert_called_once()
    assert students_cache == {("Иван Иванович Иванов", "103V"): 1}
    assert batch == []

# Ошибка при вставке в БД
@pytest.mark.asyncio
async def test_flush_batch_grades_unknow_stud_raises_exception_on_db_error():
    mk_connect = fixture.mock_get_connect(return_data=None)
    mk_connect.executemany = AsyncMock(side_effect=Exception("DB error"))
    batch = [("Иван Иванович Иванов", "103V", 3, "13.01.2024")]

    with pytest.raises(Exception) as info:
        await upload.flush_batch_grades_unknow_stud(connect=mk_connect, batch_grades_know_stud=batch, students_cache=dict())
    
    assert batch != []
    assert "DB error" in str(info.value)
