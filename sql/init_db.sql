-- Таблица со студентами 
CREATE TABLE IF NOT EXISTS Students (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    group CHAR(4) NOT NULL,
);
COMMENT ON TABLE Students IS 'Информация по студентам';
COMMENT ON COLUMN Students.id IS 'Собственный уникальный ключ';
COMMENT ON COLUMN Students.full_name IS 'Полное имя студента';
COMMENT ON COLUMN Students.group IS 'Учебная группа студента';


-- Таблица отметок студентов
CREATE TABLE IF NOT EXISTS Grades (
    id SERIAL PRIMARY KEY,
    grade SMALLINT CHECK (grade > 1 AND grade < 6),
    date_of_mark DATE NOT NULL,
    id_student INTEGER NOT NULL,

    FOREIGN KEY id_student REFERENCES Students(id) ON DELETE CASCADE,
);
COMMENT ON TABLE Grades IS 'Отметки учащихся';
COMMENT ON COLUMN Grades.id IS 'Собственный уникальный ключ';
COMMENT ON COLUMN Grades.grade IS 'Отметка (2-5)';
COMMENT ON COLUMN Grades.date_of_mark IS 'Дата получения отметки';
COMMENT ON COLUMN Grades.id_student IS 'Студент, получивший отметку';