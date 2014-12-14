import re, math
import random
import time


# CONFIGURATION
filename = "rnd_50_500.txt"

## Calculations to run:
naive = True
lsh = True
minhash = True
dummy = True

## Number of hash functions (k) and bands (b)
k = 6
b = 3


def get_first_prime_larger_than(N):
    next_int = N+1
    if is_prime(next_int):
        return next_int
    else:
        return get_first_prime_larger_than(next_int)


def is_prime(n):
    if n <= 3:
        return n >= 2
    if n % 2 == 0 or n % 3 == 0:
        return False
    for i in range(5, int(n ** 0.5) + 1, 6):
        if n % i == 0 or n % (i + 2) == 0:
            return False
    return True


def get_hash_variables(p):
    a = random.randrange(1,p)
    b = random.randrange(0,p)
    return a, b


def is_meta_character(role):
    result = False
    metas = ["Himself", "", "Herself", "Themselves", "Additional Voices", "Narrator", "Extra", "Host", "Undetermined Role", "Cameo appearance"]
    if role in metas:
        result = True
    return result


def clean(role):
    role = re.split('\ \#[0-9]', role)[0] # Takes care of 'Person #2'
    role = re.split('\ \(', role)[0] # Takes care of 'Merchant (1990)'
    role = re.split('\ \[', role)[0] # Takes care of 'Merchant [1990]'
    return role


def parse_data():
    roles = {}
    movies_table = {}
    movies = {}
    roles = {}
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
                if movies_table[movie_id] >= 7.0:

                    m_i = len(movies)
                    if movie_id not in movies:
                        movies[movie_id] = m_i
                    else:
                        m_i = movies[movie_id]
                                         
                    if role not in roles:
                        r_i = len(roles)
                        roles[role] = r_i    
                     
                    key = (r_i, m_i)
                    if key not in characteristic_matrix:
                        characteristic_matrix[key] = None
    #initialise for proper length
    m = [0]*len(movies)
    r = [0]*len(roles)

    #change role and movies dictionaries to list i.e. changing from id lookup to index lookup.
    for m_id in movies:
        m[movies[m_id]] = m_id

    for role in roles:
        r[roles[role]] = role 

    return characteristic_matrix, m, r
            

def calculate_jaccard(matrix, movies, roles):
    similarity = {}
    n = len(roles)
    m = len(movies)
    for i in range(0,n):
        for j in range(i + 1, n):
            x = 0.0
            y = 0.0
            for k in range(0, m):
                if (i, k) in matrix and (j, k) in matrix:
                    x += 1.0
                elif (i, k) in matrix or (j, k) in matrix:
                    y += 1.0
            similarity[roles[i],roles[j]] = x/(x+y)
    return similarity 


def create_sig_matrix(matrix, m, n, k):
    hashes = []
    p = get_first_prime_larger_than(m)
    signature_matrix = [[float('Inf')]*n for i in range(0, k)]
    for i in range(0, k):
        hashes.append(get_hash_variables(p))

    for i, j in matrix:
        for pi, (a,b) in enumerate(hashes):
            hash_value = (a*j+b)%p%m
            if hash_value < signature_matrix[pi][i]:
                signature_matrix[pi][i] = hash_value
    return signature_matrix, hashes


def approximate_jaccard_lsh(matrix, movies, roles, K, bands):
    print("   " + str(len(matrix)))
    similarity = {}
    n = len(roles)
    m = len(movies)
    signature_matrix, hash_functions = create_sig_matrix(matrix, m, n, K)
    print("   signature_matrix done!")
    M = K
    r = M/bands
    c = len(signature_matrix[0]) #number of signatures
    p = c #number of buckets
    
    #create buckets
    buckets = []
    for i in range(0, bands):
        buckets.append([])
        for j in range(0, p):
            buckets[i].append([])

    #Hash to buckets
    for i in range(0, bands):
        a, b = hash_functions[i*r]
        for j in range(0, c):
            v = ""
            for k in range(0,r):
                g = str(signature_matrix[i*r + k][j])
                v += g
            hashed_val = (a*int(v)+b)%p
            buckets[i][hashed_val].append(j)

    #Find candidate pairs
    candidate_pairs = set([])
    for band in buckets:
        for bucket in band:
            for i in bucket:
                for j in bucket:
                    if i < j:
                        candidate_pairs.add((i,j))
    print("   Number of candidate pairs: "+str(len(candidate_pairs)))

    # calculate similarity between candidate pairs
    for i,j in candidate_pairs: 
        similarity[roles[i],roles[j]] = 0.0
        for pi in range(0, k):
            if signature_matrix[pi][i] == signature_matrix[pi][j]:
                similarity[roles[i],roles[j]] += 1

    for (r1, r2) in similarity:
        similarity[r1, r2] /= float(K)

    return similarity


def approximate_jaccard_minhash(matrix, movies, roles, k):
    similarity = {}
    n = len(roles)
    m = len(movies)
    signature_matrix, _ = create_sig_matrix(matrix, m, n, k)
    
    for i in range(0, n):
        for j in range(i + 1, n):
            similarity[roles[i],roles[j]] = 0.0
            for pi in range(0, k):
                if signature_matrix[pi][i] == signature_matrix[pi][j]:
                    similarity[roles[i],roles[j]] += 1
    
    #calculating fractions                    
    for (r1, r2) in similarity:
        similarity[r1, r2] /= float(k)
    return similarity
    

print("Parsing data - " + filename)
start = time.time()
matrix, movies, roles = parse_data()

print("   took "+str(time.time() - start)+" seconds\n")

if naive:
    print("Running naive")
    start = time.time()
    jaccard = calculate_jaccard(matrix, movies, roles )
    print("   took "+str(time.time() - start)+" seconds\n")

if minhash:
    print("Running Min Hashing")
    jaccard_approx = {}
    start = time.time()
    jaccard_approx = approximate_jaccard_minhash(matrix, movies, roles, k)
    print("   took "+str(time.time() - start)+" seconds\n")


if lsh:
    print("Running LSH")
    jaccard_approx = {}
    start = time.time()
    jaccard_approx = approximate_jaccard_lsh(matrix, movies, roles, k, b)
    print("   took "+str(time.time() - start)+" seconds\n")



"""
for (r1,r2) in jaccard:
    value = jaccard[r1,r2]
    approx = jaccard_approx[r1,r2]
    diff = abs(value - approx)
    print "compare (" +r1+"-"+r2+"): "+ "\nvalue: " +str(value)+"\napproximate: "+ str(approx) +"\ndifference: "+ str(diff)+"\n"


"""
