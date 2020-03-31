#!/usr/bin/env python


from database import Database

weight_vector = (1, 3)
student_list = ('StudentInfoNameFirst', 'StudentAcademicsMajor', 'StudentCareerDesiredField')
alum_list = ('AlumInfoNameFirst', 'AlumAcademicsMajor', 'AlumCareerField')

# Finds matching fields (i.e. major, career) between students and alumni and returns a dictionary of student->list of alum/score tuples
def get_rankings():
    db = Database()
    db.connect()
    students = db.execute_get(selectall_query(student_list, "students"))
    alumni = db.execute_get(selectall_query(alum_list, "alumni"))
    db.disconnect()

    students_alumni = {}
    for i in range(len(students)):
        student_alumni = []
        # assuming index 0 netid, index 1 is major, index 2 is career
        for j in range(len(alumni)):
            # can easily use this form to generalize to any number of features (columns will definitely change so keep an eye on range() especially)
            score = sum(weight_vector[k] if students[i][k + 1] == alumni[j][k + 1] else 0 for k in range(len(weight_vector)))
            student_alumni.append((alumni[j][0], score))
        students_alumni[students[i][0]] = student_alumni

    # sort rankings
    for student in students_alumni:
        students_alumni[student].sort(key=lambda x: x[1], reverse=True)

    return students_alumni

# Returns student->list of alum/score tuple for given student
def get_ranking(student):
    if 'rankings' not in get_ranking.__dict__:
        get_ranking.rankings = get_rankings(weight_vector)
    try:
        return get_ranking.rankings[student]
    except:
        return None

# Helper function to select all unmatched students
def selectall_query(list, table):
    return f'SELECT {", ".join(list)} FROM {table} WHERE Matched IS NULL'

# Runs the "stable marriage" algorithm and returns a dictionary of student->alum or student->"No match :(" if #students > #alumni
def create_matches():
    students_alumni = get_rankings()
    used_alums = set()
    sad_students = set()
    happy_students = set()

    student_alum = {}
    for student in students_alumni:
        no_match = True
        for alum, score in students_alumni[student]:
            if alum not in used_alums:
                no_match = False
                used_alums.add(alum)
                student_alum[student] = alum
                happy_students.add(student)
                break
        if no_match:
            student_alum[student] = "No match :("
            sad_students.add(student)
    
    db = Database()
    db.connect()
    # Joe- updates wouldn't work (always added a new row) with WHERE NOT EXISTS(SELECT * FROM matches WHERE StudentInfoNameFirst=%s)
    # and with ON DUPLICATE KEY UPDATE AlumInfoNameFirst = %s
    for student in student_alum:
        query_string = """
        INSERT INTO matches
        VALUES (%s, %s);
        """
        db.execute_set(query_string, (student, student_alum[student]))

        query_string = """
        UPDATE students
        SET Matched=True
        WHERE StudentInfoNameFirst = %s
        """
        db.execute_set(query_string, (student,))

        query_string = """
        UPDATE alumni
        SET Matched=True
        WHERE AlumInfoNameFirst = %s
        """
        db.execute_set(query_string, (student_alum[student],))
    db.disconnect()

# Retrieves all entries from the matches table
def get_matches():
    db = Database()
    db.connect()
    query_string = f"""
    SELECT *
    FROM matches
    """
    matches = db.execute_get(query_string)
    db.disconnect()
    return matches

# Deletes all entries in the matches table
def clear_matches():
    db = Database()
    db.connect()
    query_string = f"""
    DELETE FROM matches
    """
    db.execute_set(query_string, ())
    query_string = f"""
    UPDATE students
    SET Matched=NULL
    """
    db.execute_set(query_string, ())
    query_string = f"""
    UPDATE alumni
    SET Matched=NULL
    """
    db.execute_set(query_string, ())
    db.disconnect()

# Unit testing
if __name__ == '__main__':
    print(get_matches())