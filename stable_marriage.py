#!/usr/bin/env python

# -----------------------------------------------------------------------
# stable_marriage.py
# -----------------------------------------------------------------------

from database import students, alumni, matches

weight_vector = (1, 3)
student_list = ('StudentInfoNameFirst', 'StudentAcademicsMajor',
                'StudentCareerDesiredField')
alum_list = ('AlumInfoNameFirst', 'AlumAcademicsMajor', 'AlumCareerField')


def get_ranking(student):
    if 'rankings' not in get_ranking.__dict__:
        get_ranking.rankings = get_rankings(weight_vector)
    try:
        return get_ranking.rankings[student]
    except:
        return None


def get_rankings():
    students = students.query.all()
    alumni = alumni.query.all()
    
    students_alumni = {}
    for i in range(len(students)):
        student_alumni = []
        # assuming index 0 netid, index 1 is major, index 2 is career
        for j in range(len(alumni)):
            # can easily use this form to generalize to any number of features (columns will definitely change so keep an eye on range() especially)
            score = sum(weight_vector[k] if students[i][k + 1] == alumni[j]
                        [k + 1] else 0 for k in range(len(weight_vector)))
            student_alumni.append((alumni[j][0], score))
        students_alumni[students[i][0]] = student_alumni

    # sort rankings
    for student in students_alumni:
        students_alumni[student].sort(key=lambda x: x[1], reverse=True)

    return students_alumni

def create_new_matches():
    students_alumni = get_rankings()
    used_alums = set()
    student_alum = {}

    # can make this much more efficient (LATER) by keeping track of all the values in lists and making database server call only once
    for student in students_alumni:
        for alum, score in students_alumni[student]:
            if alum not in used_alums:
                used_alums.add(alum)
                student_alum[student] = alum

                new_match = matches(student, student_alum[student])
                db.session.add(new_match)
                db.session.commit()

                student = students.query.filter_by(studentid=student)
                student.matched = 1
                db.session.commit()

                alum = alumni.query.filter_by(aluminfoemail=student_alum[student])
                alum.matched = 1
                db.session.commit()
                
                break

def get_matches():
    matches_list = matches.query.all()
    unmatched_alumni = alumni.query.filter_by(matched=0)
    unmatched_students = students.query.filter_by(matched=0)

    return matches_list, unmatched_alumni, unmatched_students


''' TODO: CONVERT TO SQLALCHEMY '''
def clear_matches():
    query_string = """
    DELETE FROM matches
    """
    conn.execute_set(query_string, ())

    query_string = """
    UPDATE students
    SET Matched=NULL
    """
    conn.execute_set(query_string, ())

    query_string = """
    UPDATE alumni
    SET Matched=NULL
    """
    conn.execute_set(query_string, ())
    
''' TODO: CONVERT TO SQLALCHEMY '''
def clear_match(student, alum):
    query_string = """
    DELETE FROM matches
    WHERE StudentInfoNameFirst = %s
    """
    conn.execute_set(query_string, (student,))

    query_string = """
    UPDATE students
    SET Matched=NULL
    WHERE StudentInfoNameFirst = %s
    """
    conn.execute_set(query_string, (student,))

    query_string = """
    UPDATE alumni
    SET Matched=NULL
    WHERE AlumInfoNameFirst = %s
    """
    conn.execute_set(query_string, (alum,))

if __name__ == '__main__':
    create_new_matches()
    print(get_matches()[0])
