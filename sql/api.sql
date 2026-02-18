-- Функция нахождения студентов, у которых количество целевых оценок больше заданного
CREATE OR REPLACE FUNCTION grades_more_than(target_grade INTEGER, min_count INTEGER)
RETURNS JSON
LANGUAGE plpgsql
STABLE AS $$
DECLARE
    info_students JSON;
BEGIN
    SELECT COALESCE(json_agg(json_build_object(
        'full_name', s.full_name,
        'count_twos', count_grades)), '[]') INTO info_students
    FROM (
        SELECT s.full_name, COUNT(*) AS count_grades
        FROM Grades g
        INNER JOIN Students s ON g.id_student = s.id
        WHERE g.grade = target_grade
        GROUP BY s.full_name
        HAVING COUNT(*) > min_count
    ) sub
    ORDER BY full_name;

    RETURN info_students;

-- EXCEPTION
--    WHEN 
END;
$$;


-- Функция нахождения студентов, у которых количество целевых оценок меньше заданного
CREATE OR REPLACE FUNCTION grades_less_than(target_grade INTEGER, max_count INTEGER)
RETURNS JSON
LANGUAGE plpgsql
STABLE AS $$
DECLARE
    info_students JSON;
BEGIN
    WITH sub AS (
        SELECT s.full_name, COUNT(*) AS count_grades
        FROM Grades g
        INNER JOIN Students s ON s.id = g.id_student
        WHERE g.grade = target_grade
        GROUP BY s.full_name
        HAVING COUNT(g.grade) < max_count
        ORDER BY s.full_name, count_grades;
    );

    SELECT json_agg(json_build_object(
        'full_name', full_name,
        'count_twos', count_grades
    )) INTO info_students
    FROM sub;

    IF info_students IS NULL THEN 
        RETURN '[]'::JSON
    ELSE
        RETURN info_students
    END IF;

-- EXCEPTION
--    WHEN 
END;
$$;