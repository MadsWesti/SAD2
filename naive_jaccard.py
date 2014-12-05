import re, math, time


def is_meta_character(role):
    result = False
    metas = ["Himself", "", "Herself", "Themselves", "Additional Voices", "Narrator", "Extra", "Host", "Undetermined Role", "Cameo appearance"]
    if role in metas:
        result = True
    return result


def parse_data():
    filename = "toy.txt"
    roles = {}
    movies = {}
    with open(filename) as f:
        for line in f:
            if line.strip()[0:10] == "LOCK TABLE":
                tabletype = line.strip()[13:-8].strip()
                continue

            if tabletype == "movies":
                movie_id = int(re.split(',', line)[0].strip())
                rank = re.split(',', line)[-2].strip()

                if rank == "NULL":
                    continue

                rank = float(rank)
                movies[movie_id] = rank

            if tabletype == "roles":
                movie_id = int(re.split(',', line)[1].strip())
                role = re.split(',', line)[2].strip().strip("'")
                
                if movie_id not in movies:
                    continue

                if is_meta_character(role):
                    continue

                if movies[movie_id] > 7.0:
                    if role in roles:
                        roles[role].add(movie_id)
                    else:
                        roles[role] = set([movie_id])
    return roles        


def dummy_data():
    roles = {}
    roles["r1"] = set([1,2,3])
    roles["r2"] = set([2,3])
    roles["r3"] = set([3])
    return roles    


def calculate_jaccard(s1 , s2):
    return float(len(s1.intersection(s2)))/float(len(s1.union(s2)))


def calculate_role_similarity(roles):
    similarity = {}
    for r1 in roles:
        for r2 in roles:
            if r1 >= r2:
                continue
            similarity[(r1,r2)] = calculate_jaccard(roles[r1], roles[r2])
    return similarity


start = time.time()
roles = parse_data()
#roles = dummy_data()
similarity = calculate_role_similarity(roles)

for pair in similarity:
    if similarity[pair] > 0.5:
        print pair, similarity[pair]
