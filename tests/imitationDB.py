import datetime

class ImitationDB:  
    def __init__(self, data=None):
        self.students = list()
        self.grades = list()
        if "students" in data:
            self.students = data["students"]
        if "grades" in data:
            self.grades = data["grades"]

    async def fetch(self, query):
        if "Students" in query:
            return self.students
        return []
    
    async def executemany(self, query, params):
        if "Grades" in query:
            id = max([r["id"] for r in self.grades]) + 1
            for row in params:
                self.grades += [{"id": id, "grade": row[0], "date_of_mark": row[1], "id_student": row[2]}]
                id += 1
        
        elif "Students" in query:
            id = max([r["id"] for r in self.students]) + 1
            params = list(set(params))
            for row in params:
                self.students += [{"id": id, "full_name": row[0], "study_group": row[1]}]
                id += 1
    
    async def transaction(self):
        class T:
            async def __aenter__(self): return self
            async def __aexit__(self, *args): return False
        return T()
    
async def imitation_connect_emptyDB():
    class Connect:
        async def __aenter__(self): return ImitationDB()
        async def __aexit__(self, *args): return False
    return Connect

async def imitation_connect_fullDB():
    data = {
        "students": [
            {"id": 1, "full_name": "Иванов Иван Иванович", "study_group": "001А"},
            {"id": 2, "full_name": "Петрова Мария Сергеевна", "study_group": "002Б"},
            {"id": 3, "full_name": "Сидоров Алексей Дмитриевич", "study_group": "003В"},
            {"id": 4, "full_name": "Кузнецова Ольга Викторовна", "study_group": "004Г"},
            {"id": 5, "full_name": "Михайлов Кирилл Андреевич", "study_group": "005Д"},
            {"id": 6, "full_name": "Лебедева Светлана Алексеевна", "study_group": "006Е"},
            {"id": 7, "full_name": "Борисов Виктор Александрович", "study_group": "007Ж"},
            {"id": 8, "full_name": "Григорьева Анастасия Васильевна", "study_group": "008З"},
            {"id": 9, "full_name": "Новиков Дмитрий Викторович", "study_group": "009И"},
            {"id": 10, "full_name": "Андреева Екатерина Юрьевна", "study_group": "010К"}
        ],
        "grades": [
            {"id": 1, "grade": 4, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 1},
            {"id": 2, "grade": 5, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 2},
            {"id": 3, "grade": 3, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 1},
            {"id": 4, "grade": 2, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 3},
            {"id": 5, "grade": 4, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 4},
            {"id": 6, "grade": 4, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 2},
            {"id": 7, "grade": 3, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 5},
            {"id": 8, "grade": 5, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 3},
            {"id": 9, "grade": 2, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 1},
            {"id": 10, "grade": 3, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 4},
            {"id": 11, "grade": 4, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 5},
            {"id": 12, "grade": 5, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 6},
            {"id": 13, "grade": 4, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 6},
            {"id": 14, "grade": 2, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 2},
            {"id": 15, "grade": 3, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 7},
            {"id": 16, "grade": 5, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 1},
            {"id": 17, "grade": 4, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 8},
            {"id": 18, "grade": 3, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 3},
            {"id": 19, "grade": 2, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 9},
            {"id": 20, "grade": 5, "date_of_mark": datetime.strptime("27.04.2024", "%d.%m.%Y").date(), "id_student": 10}
        ]
    }
    
    class Connect:
        async def __aenter__(self): return ImitationDB(data=data)
        async def __aexit__(self, *args): return False
    return Connect

