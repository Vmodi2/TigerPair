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
    return f'SELECT {", ".join(list)} FROM {table}'

def get_matches():
    students_alumni = get_rankings()
    used_alums = set()
    sad_students = set()

    student_alum = {}
    for student in students_alumni:
        for alum, score in students_alumni[student]:
            no_match = True
            if alum not in used_alums:
                no_match = False
                used_alums.add(alum)
                student_alum[student] = alum
                break
        if no_match:
            student_alum[student] = "No match :("
            sad_students.add(student)
    return student_alum


if __name__ == '__main__':
    print(get_matches())