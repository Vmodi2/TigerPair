#!/usr/bin/env python

# -----------------------------------------------------------------------
# stable_marriage.py
# -----------------------------------------------------------------------

from sqlalchemy import update
from database import students as students_table, alumni as alumni_table, matches as matches_table
from config import db

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


def get_rankings(id):
    students = [(student.studentid, student.studentacademicsmajor,
                 student.studentcareerdesiredfield) for student in get_unmatched_students(id)]
    alumni = [(alum.aluminfoemail, alum.alumacademicsmajor, alum.alumcareerfield)
              for alum in get_unmatched_alumni(id)]
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


def create_new_matches(id):
    students_alumni = get_rankings(id)
    used_alums = set()
    student_alum = {}

    for student in students_alumni:
        for alum, score in students_alumni[student]:
            if alum not in used_alums:
                used_alums.add(alum)
                student_alum[student] = alum

                new_match = matches_table(student, student_alum[student], id)
                db.session.add(new_match)

                student = students_table.query.filter_by(
                    studentid=student).first()
                student.matched = 1

                alum = alumni_table.query.filter_by(
                    aluminfoemail=alum).first()
                alum.matched += 1
                break
    db.session.commit()


def get_matches(id):
    matches_list = matches_table.query.filter_by(group_id=id)
    matches_list = [(match.studentid, match.aluminfoemail)
                    for match in matches_list]
    db.session.commit()
    return matches_list


def get_alumni(id):
    return [alum for alum in alumni_table.query.filter_by(group_id=id)]


def get_alum(email):
    alum = alumni_table.query.filter_by(aluminfoemail=email).first()
    matches = matches_table.query.filter_by(aluminfoemail=email).all()
    return alum, matches


def get_students(id):
    return [student for student in students_table.query.filter_by(group_id=id)]


def get_student(netid):
    student = students_table.query.filter_by(studentid=netid).first()
    matches = matches_table.query.filter_by(studentid=netid).all()
    print(matches)
    return student, matches


def get_unmatched_students(id):
    return students_table.query.filter_by(matched=0).filter_by(group_id=id)


def get_unmatched_alumni(id):
    return alumni_table.query.filter_by(matched=0).filter_by(group_id=id)


def create_one(id, studentid, aluminfoemail):
    students_table.query.filter_by(studentid=studentid).first().matched = 1
    alumni_table.query.filter_by(
        aluminfoemail=aluminfoemail).first().matched += 1
    new_match = matches_table(studentid, aluminfoemail, id)
    db.session.add(new_match)
    db.session.commit()


def clear_matches(id):
    db.session.query(matches_table).delete()
    students = students_table.query.filter_by(group_id=id)
    for student in students:
        student.matched = 0
    alumni = alumni_table.query.filter_by(group_id=id)
    for alum in alumni:
        alum.matched = 0
    db.session.commit()


def clear_match(student, alum):
    db.session.query(matches_table).filter_by(studentid=student).delete()
    student = students_table.query.filter_by(studentid=student).first()
    alum = alumni_table.query.filter_by(aluminfoemail=alum).first()
    assert (student.matched == 1)
    assert (alum.matched >= 1)
    student.matched = 0
    alum.matched -= 1
    db.session.commit()


if __name__ == '__main__':
    create_new_matches()
