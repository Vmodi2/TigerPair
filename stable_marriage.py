#!/usr/bin/env python


from database import Database

weight_vector = (1, 3)
student_list = ('StudentInfoNameFirst', 'StudentAcademicsMajor', 'StudentCareerDesiredField')
alum_list = ('AlumInfoNameFirst', 'AlumAcademicsMajor', 'AlumCareerField')

def get_ranking(student):
    if 'rankings' not in get_ranking.__dict__:
        get_ranking.rankings = get_rankings(weight_vector)
    try:
        return get_ranking.rankings[student]
    except:
        return None

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

def selectall_query(list, table):
    return f'SELECT {", ".join(list)} FROM {table} WHERE Matched IS NULL'

def create_new_matches():
    students_alumni = get_rankings()
    used_alums = set()
    student_alum = {}

    db = Database()
    db.connect()
    # can make this much more efficient (LATER) by keeping track of all the values in lists and making database server call only once
    for student in students_alumni:
        for alum, score in students_alumni[student]:
            if alum not in used_alums:
                used_alums.add(alum)
                student_alum[student] = alum
                
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

                break
    db.disconnect()

def get_matches():
    db = Database()
    db.connect()

    query_string = """
    SELECT *
    FROM matches
    """
    matches = db.execute_get(query_string)

    query_string = """
    SELECT AlumInfoNameFirst
    FROM alumni
    WHERE Matched IS NULL
    """
    unmatched_alumni = db.execute_get(query_string)

    query_string = """
    SELECT StudentInfoNameFirst
    FROM students
    WHERE Matched IS NULL
    """
    unmatched_students = db.execute_get(query_string)
    print(unmatched_students)

    db.disconnect()
    return matches, unmatched_alumni, unmatched_students

def clear_matches():
    db = Database()
    db.connect()
    
    query_string = """
    DELETE FROM matches
    """
    db.execute_set(query_string, ())

    query_string ="""
    UPDATE students
    SET Matched=NULL
    """
    db.execute_set(query_string, ())

    query_string ="""
    UPDATE alumni
    SET Matched=NULL
    """
    db.execute_set(query_string, ())
    
    db.disconnect()
def clear_match(student, alum):
    db = Database()
    db.connect()

    query_string = """
    DELETE FROM matches
    WHERE StudentInfoNameFirst = %s
    """
    db.execute_set(query_string, (student,))

    query_string ="""
    UPDATE students
    SET Matched=NULL
    WHERE StudentInfoNameFirst = %s
    """
    db.execute_set(query_string, (student,))

    query_string ="""
    UPDATE alumni
    SET Matched=NULL
    WHERE AlumInfoNameFirst = %s
    """
    db.execute_set(query_string, (alum,))

    db.disconnect()
    

    

if __name__ == '__main__':
    create_new_matches()
    print(get_matches()[0])