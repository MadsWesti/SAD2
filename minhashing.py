import re, math, time
import random
import numpy

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
similarity = calculate_role_similarity(roles)
signature_matrix = []
similarity_matrix = []
hashes = {}

i = 0
for role in roles:
    print(role)


# Creating the hash functions (well really just their variables)
for i in range(0, 10):
    hashes[i] = get_hash_variables(i)


# Creating the signature matrix
N = len(movies)
for m in range(0, N):
    tmp = []
    for i in hashes:
        a, b, p = hashes[i]
        hash_value = (a*m+b)%p%N
        tmp.append(hash_value)
    signature_matrix.append(tmp)

signature_matrix_T = numpy.transpose(signature_matrix)
similarity_matrix = numpy.dot(signature_matrix, signature_matrix_T)
print(similarity_matrix)

print(len(similarity_matrix))


#for pair in similarity:
    #if similarity[pair] > 0.01 and similarity[pair] != 1.0:
        #print pair, similarity[pair]
