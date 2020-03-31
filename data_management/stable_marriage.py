from database import get_rankings, Database

weight_vector = (1, 3)

def get_ranking(student):
    if 'rankings' not in get_ranking.__dict__:
        get_ranking.rankings = get_rankings(weight_vector)
    try:
        return get_ranking.rankings[student]
    except:
        return None

def get_rankings(weight_vector):
    db = Database(app)
    db.connect()
    students = db.execute(selectall_query("students"), ())
    alumni = db.execute(selectall_query("alumni"), ())
    db.disconnect()
    
    students_alumni = {}
    for i in range(len(students)):
        student_alumni = []
        # assuming index 0 netid, index 1 is major, index 2 is career
        for j in range(len(alumni)):
            # can easily use this form to generalize to any number of features (columns will definitely change so keep an eye on range() especially)
            score = sum(weight_vector[k] * (1 if students[i][k + 1] == alumni[j][k + 1] else 0) for k in range(len(students[i]) - 1))
            student_alumni.append((alumni[j][0], score))
        students_alumni[students[i][0]] = student_alumni

    # sort rankings
    for student in students_alumni:
        students_alumni[student].sort(key=lambda x: x[1], reverse=True)

    return students_alumni

def selectall_query(table):
    return f'SELECT * FROM {table}'

if __name__ == '__main__':
    print(get_ranking("christine"))
    print(get_ranking("bill"))
    print(get_ranking("will"))