import re, math, time
import random

#til at finde p... finder det naeste primtal stoerre end N
def get_prime_larger_than(N):
    next_int = N+1
    if is_prime(next_int):
        return next_int
    else:
        return get_prime_larger_than(next_int)

#checker om et tal er et primtal.
def is_prime(n):
    if n <= 3:
        return n >= 2
    if n % 2 == 0 or n % 3 == 0:
        return False
    for i in range(5, int(n ** 0.5) + 1, 6):
        if n % i == 0 or n % (i + 2) == 0:
            return False
    return True

# finder en unvirsal hashing function, det er stadig collisions en gang i mellem... jeg ved ikke om det er meningen at den skal vaere collision-fri eller ej.
def get_hash_variables(N):
    #A = range(0,10)
    #N = len(A) 
    p = get_prime_larger_than(N)
    a = random.randrange(0,p)# i hvilket interval vaelges der??? 
    b = random.randrange(0,p)#
    #B = [((a*x + b) % p) % N for x in A]
    return a, b, p


def is_meta_character(role):
    result = False
    metas = ["Himself", "", "Herself", "Themselves", "Additional Voices", "Narrator", "Extra", "Host", "Undetermined Role", "Cameo appearance"]
    if role in metas:
        result = True
    return result


movies = {}

def parse_data():
    filename = "toy/toy_1k.txt"
    roles = {}
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
    characteristic_matrix = {}
    characteristic_matrix["r1",1] = 1
    characteristic_matrix["r1",2] = 1
    characteristic_matrix["r1",3] = 1
    characteristic_matrix["r2",2] = 1
    characteristic_matrix["r2",3] = 1
    characteristic_matrix["r3",3]  = 1
    return characteristic_matrix, [1,2,3], ["r1", "r2", "r3"]

def create_sig_matrix(k, movies, roles, matrix):
    hashes = []
    signature_matrix = [[float('Inf')]*len(roles) for i in range(0, k)]
    for i in range(0, k):
        hashes.append(get_hash_variables(len(movies)))

    print(hashes)
    print(len(movies))
    for j in range(0, len(movies)):
        for r in range(0, len(roles)):
            if (roles[r],movies[j]) in matrix:
                for i,(a,b,p) in enumerate(hashes):
                    hash_value = (a*j+b)%p%len(movies)
                    if hash_value < signature_matrix[i][r]:
                        signature_matrix[i][r] = hash_value
                        print(signature_matrix)
    return signature_matrix

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
    
def calculate_jaccard_approx(matrix, roles):
    sim = {}
    for r1 in range(0, len(roles)):
        for r2 in range(0, r1):
            print(str(r1) + " " + str(r2))
            for i in range(0, len(matrix)):
                if matrix[i][r1] == matrix[i][r2]:
                    if (r1,r2) in sim:
                        sim[r1,r2] += 1
                    else:
                        sim[r1,r2] = 1
                        
            
    return sim


M, m, r = dummy_data()
sig_matrix = create_sig_matrix(2, m, r, M)
print(sig_matrix)
jaccard = calculate_jaccard_approx(sig_matrix, r)
print(jaccard)

