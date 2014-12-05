import re, math, time


def is_meta_character(role):
    result = False
    metas = ["Himself", "", "Herself", "Themselves", "Additional Voices", "Narrator", "Extra", "Host", "Undetermined Role", "Cameo appearance"]
    if role in metas:
        result = True
    return result


def parse_data():
    filename = "imdb-r.txt"
    roles = {}
    movies_table = {}
    movies = []
    roles = []
    characteristic_matrix = {}


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
                movies_table[movie_id] = rank

            if tabletype == "roles":
                movie_id = int(re.split(',', line)[1].strip())
                role = re.split(',', line)[2].strip().strip("'")
                
                if movie_id not in movies_table: 
                    continue

                if is_meta_character(role):
                    continue

                if movies_table[movie_id] > 7.0:
                    movies.append(movie_id)
                    roles.append(role)
                    key = (role,movie_id)
                    if key not in characteristic_matrix:
                        characteristic_matrix[key] = 1
    return characteristic_matrix, movies, roles
            

def dummy_data():
    characteristic_matrix = {}
    characteristic_matrix["r1",1] = 1
    characteristic_matrix["r1",2] = 1
    characteristic_matrix["r1",3] = 1
    characteristic_matrix["r2",2] = 1
    characteristic_matrix["r2",3] = 1
    characteristic_matrix["r3",3]  = 1
    return characteristic_matrix, [1,2,3], ["r1", "r2", "r3"]


def calculate_jaccard(matrix, movies, roles):
    similarity = {}
    for r1 in roles:
        for r2 in roles:
            if r1 < r2:
                x = 0
                y = 0
                for m in movies:    
                    if (r1, m) in matrix and (r2, m) in matrix:
                        x += 1
                    elif (r1, m) in matrix or (r2, m) in matrix:
                        y += 1
                        
                similarity[r1,r2] = float(x)/float(x+y) 
    return similarity

def approximate_jaccard():
    pass

matrix, movies, roles = parse_data()
#matrix, movies, roles = dummy_data()

similarity = calculate_jaccard(matrix, movies, roles)

for pair in similarity:
    if similarity[pair] >= 0.5:
        print pair, " -- " + str(similarity[pair])