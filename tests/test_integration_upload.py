from imitationDB import imitation_connect_emptyDB
from app.main import app
import app.database
from fastapi.testclient import TestClient
import pytest
from io import BytesIO

client = TestClient(app)

# Корректный файл обрабатывается и записывается правильно
@pytest.mark.asyncio
async def test_upload_csv_batch_processes_valid_csv_file_correctly(monkeypatch):
    monkeypatch.setattr(app.database, 'get_connect', lambda: imitation_connect_emptyDB)
    with open("./data/upload_correct.csv") as csvfile:
        response = client.post("/upload-grades/", files={"file": ("upload_correct.csv", csvfile, "text/csv")})
    data = response.json()
    
    assert response.status_code == 200
    assert 'json' in response.headers['Content-Type']
    assert data["status"] == "ok"
    assert data["records_loaded"] == 20
    assert data["students"] == 10

# Проверка на ошибку при некорректном типе файла
@pytest.mark.asyncio
async def test_upload_csv_batch_non_csv_file(monkeypatch):
    monkeypatch.setattr(app.database, 'get_connect', lambda: imitation_connect_emptyDB)
    with open("./data/error.gif") as csvfile:
        response = client.post("/upload-grades/", files={"file": ("error.gif", csvfile, "text/csv")})
    
    assert response.status_code == 400
    assert "Некорректный тип файла" in response.json()["detail"]

# Проверка на ошибку при неправильной кодировке
@pytest.mark.asyncio
async def test_upload_csv_batch_file_with_bad_utf8_encoding(monkeypatch):
    monkeypatch.setattr(app.database, 'get_connect', lambda: imitation_connect_emptyDB)
    with open("./data/upload_incorrect_encoding.csv", "wb") as f:
        f.write(b"\xff\xff\xff\xff\xff")    

    with open("./data/upload_incorrect_encoding.csv") as csvfile:
        response = client.post("/upload-grades/", files={"file": ("file.csv", csvfile, "text/csv")})
    
    assert response.status_code == 400
    assert "Невозможно декодировать файл" in response.json()["detail"]

# Проверка на пропуск невалидных строк
@pytest.mark.asyncio
async def test_upload_csv_batch_skips_invalid_rows_in_csv(monkeypatch):
    monkeypatch.setattr(app.database, 'get_connect', lambda: imitation_connect_emptyDB)
    csv_data = "Дата;Номер группы;ФИО;Оценка\n" \
    "Иванов Иван Иванович;103А;3" \
    "01.01.2024;Иванов Иван Иванович;103А;3"
    csvfile = BytesIO(csv_data.encode("utf-8"))
    response = client.post("/upload-grades/", files={"file": ("invalid.csv", csvfile, "text/csv")})
    data = response.json()
    
    assert response.status_code == 200
    assert 'json' in response.headers['Content-Type']
    assert data["status"] == "ok"
    assert data["records_loaded"] == 1
    assert data["students"] == 1

# Проверка поведения при пустом файле
@pytest.mark.asyncio
async def test_upload_csv_batch_empty_csv(monkeypatch):
    monkeypatch.setattr(app.database, 'get_connect', lambda: imitation_connect_emptyDB)
    csv_data = ""
    csvfile = BytesIO(csv_data.encode("utf-8"))
    response = client.post("/upload-grades/", files={"file": ("empty.csv", csvfile, "text/csv")})
    data = response.json()
    
    assert response.status_code == 200
    assert 'json' in response.headers['Content-Type']
    assert data["status"] == "ok"
    assert data["records_loaded"] == 0
    assert data["students"] == 0

# Проверка корректной работы при большом объёме данных
@pytest.mark.asyncio
async def test_upload_csv_batch_many_data(monkeypatch):
    monkeypatch.setattr(app.database, 'get_connect', lambda: imitation_connect_emptyDB)
    csv_data = "Дата;Номер группы;ФИО;Оценка\n" \
    "Иванов Иван Иванович;103А;3;2024-01-01"
    csvfile = BytesIO(csv_data.encode("utf-8"))
    response = client.post("/upload-grades/", files={"file": ("corrupt.csv", csvfile, "text/csv")})
    data = response.json()
    
    assert response.status_code == 200
    assert 'json' in response.headers['Content-Type']
    assert data["status"] == "ok"
    assert data["records_loaded"] == 0
    assert data["students"] == 0