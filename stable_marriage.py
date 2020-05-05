#!/usr/bin/env python

# -----------------------------------------------------------------------
# stable_marriage.py
# -----------------------------------------------------------------------

from sqlalchemy import update
from database import students as students_table, alumni as alumni_table, matches as matches_table
from config import db


def get_ranking(student):
    if 'rankings' not in get_ranking.__dict__:
        get_ranking.rankings = get_rankings(weight_vector)
    try:
        return get_ranking.rankings[student]
    except:
        return None


def get_rankings(id):
    weight_vector = (1, 3)
    # NEED to vectorize this, esp for "X1/2/3" where order is unimportant
    student_weightings = {
        'academics_major': 5,
        'career_field': 10,
        'academics_certificate1': 3,
        'academics_certificate2': 2,
        'academics_certificate3': 1,
        'extracurricular1': 3,
        'extracurricular2': 2,
        'extracurricular3': 1
    }
    alum_weightings = {
        'academics_major': 5,
        'career_field': 10,
        'academics_certificate1': 3,
        'academics_certificate2': 2,
        'academics_certificate3': 1,
        'extracurricular1': 3,
        'extracurricular2': 2,
        'extracurricular3': 1
    }

    students = get_unmatched_students(id)
    alumni = get_unmatched_alumni(id)

    file = open('output.txt', 'w')
    students_alumni = {}
    for student in students:
        student_alumni = []
        for alum in alumni:
            score = 0
            for attr, weight in student_weightings.items():
                student_val = getattr(student, attr)
                alum_val = getattr(alum, attr.replace(
                    'student', 'alum').replace('desired', ''))
                score += weight * \
                    (not not student_val and not not alum_val and student_val == alum_val)
                f = attr
                h = student_val
                g = attr.replace(
                    'student', 'alum').replace('desired', '')
                mam = alum_val
                c = not not student_val and not not alum_val and student_val == alum_val
                d = weight * c
                file.write(f"""{f}\n{h}\n{g}\n{mam}\n{c}\n{d}""")
            student_alumni.append((alum.info_email, score))
        students_alumni[student.studentid] = student_alumni

    # sort rankings
    for student in students_alumni:
        students_alumni[student].sort(key=lambda x: x[1], reverse=True)

    return students_alumni


def create_new_matches(id):
    students_alumni = get_rankings(id)
    used_alums = set()
    student_alum = {}

    matches = set()

    for student in students_alumni:
        for alum, score in students_alumni[student]:
            if alum not in used_alums:
                used_alums.add(alum)
                student_alum[student] = alum

                new_match = matches_table(student, student_alum[student], id)
                db.session.add(new_match)
                matches.add(new_match)

                student = students_table.query.filter_by(
                    studentid=student).first()
                student.matched = 1

                alum = alumni_table.query.filter_by(
                    info_email=alum).first()
                alum.matched += 1
                break
    db.session.commit()
    return matches


def get_matches(id):
    matches_list = matches_table.query.filter_by(group_id=id)
    matches_list = [(match.studentid, match.info_email)
                    for match in matches_list]
    db.session.commit()
    return matches_list


def get_alumni(id):
    return [alum for alum in alumni_table.query.filter_by(group_id=id)]


def get_alum(email):
    alum = alumni_table.query.filter_by(info_email=email).first()
    matches = matches_table.query.filter_by(info_email=email).all()
    return alum, matches


def get_students(id):
    return [student for student in students_table.query.filter_by(group_id=id)]


def get_student(netid):
    student = students_table.query.filter_by(studentid=netid).first()
    matches = matches_table.query.filter_by(studentid=netid).all()
    # print(matches)
    return student, matches


def get_unmatched_students(id):
    return students_table.query.filter_by(matched=0).filter_by(group_id=id)


def get_unmatched_alumni(id):
    return alumni_table.query.filter_by(matched=0).filter_by(group_id=id)


def create_one(id, studentid, info_email):
    students_table.query.filter_by(studentid=studentid).first().matched = 1
    alumni_table.query.filter_by(
        info_email=info_email).first().matched += 1
    new_match = matches_table(studentid, info_email, id)
    db.session.add(new_match)
    db.session.commit()


def clear_matches(id):
    db.session.query(matches_table).filter_by(group_id=id).delete()
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
    alum = alumni_table.query.filter_by(info_email=alum).first()
    assert (student.matched == 1)
    assert (alum.matched >= 1)
    student.matched = 0
    alum.matched -= 1
    db.session.commit()


def delete_student(id, studentid):
    db.session.query(students_table).filter_by(
        studentid=studentid).first().group_id = -1
    match = matches_table.query.filter_by(studentid=studentid)
    row = match.first()
    if row is not None:
        clear_match(studentid, row.info_email)
    db.session.commit()


def delete_alum(id, info_email):
    db.session.query(alumni_table).filter_by(
        info_email=info_email).first().group_id = -1
    # Check and reset matches table
    match = matches_table.query.filter_by(info_email=info_email)
    row = match.first()
    if row is not None:
        clear_match(row.studentid, info_email)
    db.session.commit()


if __name__ == '__main__':
    create_new_matches(336)
