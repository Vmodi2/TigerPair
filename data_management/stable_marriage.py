from database import get_rankings

weight_vector = (1, 3)

def get_ranking(student):
    if 'rankings' not in get_ranking.__dict__:
        get_ranking.rankings = get_rankings(weight_vector)
    try:
        return get_ranking.rankings[student]
    except:
        return None
    

if __name__ == '__main__':
    print(get_ranking("christine"))
    print(get_ranking("bill"))
    print(get_ranking("will"))