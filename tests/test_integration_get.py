import pytest
from app.main import app
import fixture
from fastapi.testclient import TestClient

client = TestClient(app)

# ======== Функция more_than_three_twos ========
# Проверка на корректное поведение
@pytest.mark.asyncio
async def test_get_students_more_than_three_twos_successful(monkeypatch):
    mk_get_conn = fixture.mock_get_connect(js=[{"full_name": "Иванов Иван Иванович", "count_twos": 4}])
    monkeypatch.setattr("app.database.get_connect", mk_get_conn)

    response = client.get("/students/more-than-3-twos")
    data = response.json()

    assert response.status_code == 200
    assert 'json' in response.headers['Content-Type']
    assert len(data) == 1
    assert data[0]["full_name"] == "Иванов Иван Иванович"
    assert data[0]["count_twos"] == 4

# Проверка на корректное поведение при пустом возврате
@pytest.mark.asyncio
async def test_get_students_more_than_three_twos_returns_empty_result(monkeypatch):
    monkeypatch.setaattr("app.database.get_connect", lambda: fixture.mock_get_connect)

    response = client.get("/students/more-than-3-twos")
    data = response.json()

    assert response.status_code == 200
    assert 'json' in response.headers['Content-Type']
    assert data == []

# Проверка при получении ошибки от БД
@pytest.mark.asyncio
async def test_get_students_more_than_three_twos_db_function_error(monkeypatch):
    mk_get_conn = fixture.mock_get_connect(js=[{"Error": "Ошибка в функции БД"}])
    monkeypatch.setattr("app.database.get_connect", mk_get_conn)

    response = client.get("/students/more-than-3-twos")
    
    assert response.status_code == 400
    assert "Ошибка выполнения функции" in response.json()["detail"]

# Проверка на некорректность полученного JSON
@pytest.mark.asyncio
async def test_get_students_more_than_three_twos_invalid_json(monkeypatch):
    mk_get_conn = fixture.mock_get_connect(js="not json")
    monkeypatch.setattr("app.database.get_connect", mk_get_conn)

    response = client.get("/students/more-than-3-twos")

    assert response.status_code == 500
    assert "Ошибка парсинга JSON из БД" in response.json()["detail"]


# ======== Функция less_than_five_twos ========
# Проверка на корректное поведение
@pytest.mark.asyncio
async def test_get_students_less_than_five_twos_successful(monkeypatch):
    mk_get_conn = fixture.mock_get_connect(js=[{"full_name": "Иванов Иван Иванович", "count_twos": 4}])
    monkeypatch.setattr("app.database.get_connect", mk_get_conn)

    response = client.get("/students/less-than-5-twos")
    data = response.json()

    assert response.status_code == 200
    assert 'json' in response.headers['Content-Type']
    assert len(data) == 1
    assert data[0]["full_name"] == "Иванов Иван Иванович"
    assert data[0]["count_twos"] == 4

# Проверка на корректное поведение при пустом возврате
@pytest.mark.asyncio
async def test_get_students_less_than_five_twos_returns_empty_result(monkeypatch):
    monkeypatch.setaattr("app.database.get_connect", lambda: fixture.mock_get_connect)

    response = client.get("/students/less-than-5-twos")
    data = response.json()

    assert response.status_code == 200
    assert 'json' in response.headers['Content-Type']
    assert data == []

# Проверка при получении ошибки от БД
@pytest.mark.asyncio
async def test_get_students_less_than_five_twos_db_function_error(monkeypatch):
    mk_get_conn = fixture.mock_get_connect(js=[{"Error": "Ошибка в функции БД"}])
    monkeypatch.setattr("app.database.get_connect", mk_get_conn)

    response = client.get("/students/less-than-5-twos")
    
    assert response.status_code == 400
    assert "Ошибка выполнения функции" in response.json()["detail"]

# Проверка на некорректность полученного JSON
@pytest.mark.asyncio
async def test_get_students_less_than_five_twos_invalid_json(monkeypatch):
    mk_get_conn = fixture.mock_get_connect(js="not json")
    monkeypatch.setattr("app.database.get_connect", mk_get_conn)

    response = client.get("/students/less-than-5-twos")

    assert response.status_code == 500
    assert "Ошибка парсинга JSON из БД" in response.json()["detail"]
