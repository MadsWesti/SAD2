import re, math
import random
import time
import sys
from collections import OrderedDict
import operator

# CONFIGURATION
file_actors = "data/actors.txt"
file_roles = "data/roles.txt"
file_movies = "data/movies.txt"
number_of_movies_threshold = 0
min_rank = 0.0

## Naive
naive = False

## MinHashing
minhash = False
k = 3 # hash functions

## LSH
lsh = False
b = 10 # bands
bu = 1 # buckets
### Remember to set the k value in MinHashing

bbit = False
num_of_bits = 3

def parse_data_actors():
    movies_dict = OrderedDict()
    actors_dict = {}
    movies = {}
    actors = {}
    characteristic_matrix = {}

    #parse actors
    with open(file_actors) as f:
        for line in f:
            actor = re.split(',', line)
            a_id = int(actor[0])
            first_name = actor[1][1:-1]
            last_name = actor[2][1:-1]
            number_of_movies = int(actor[4])
            if number_of_movies > number_of_movies_threshold:
                actors_dict[a_id] = first_name+" "+last_name

    #parse movies
    with open(file_movies) as f:
        for line in f:
            movie = re.split(',', line)
            m_id = int(movie[0].strip())
            name = movie[1]
            rank = movie[-2].strip()
            if rank == "NULL":
                continue
            if float(rank) >= min_rank:
                movies_dict[m_id] = name

    #parse roles
    with open(file_roles) as f:
        for line in f:
            role = re.split(',', line)
            actor_id = int(role[0].strip())
            movie_id = int(role[1].strip())
            if movie_id not in movies_dict:
                continue
            if actor_id not in actors_dict:
                continue
            m_i = len(movies)
            if movie_id not in movies:
                movies[movie_id] = m_i
            else:
                m_i = movies[movie_id]
            a_i = len(actors)
            if actor_id not in actors:
                actors[actor_id] = a_i
            else:
                a_i = actors[actor_id]

            key = a_i, m_i
            if key not in characteristic_matrix:
                characteristic_matrix[key] = None

    #swithing key and value
    m = [0]*len(movies)
    a = [0]*len(actors)
    for m_id in movies:
        m[movies[m_id]] = movies_dict[m_id]

    for a_id in actors:
        a[actors[a_id]] = actors_dict[a_id] 
    print("   " + str(len(movies)) + " movies (with rank >= " + str(min_rank) + ")")
    print("   " + str(len(actors)) + " actors")
    print("   " + str(len(characteristic_matrix)) + " 1's in characteristic matrix")

    return characteristic_matrix, m, a


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


def calculate_jaccard(matrix, movies, actors):
    similarity = {}
    n = len(actors)
    m = len(movies)
    for i in range(0, n):
        for j in range(i + 1, n):
            x = 0.0
            y = 0.0
            for d in range(0,m):
                if (i, d) in matrix and (j, d) in matrix:
                    x += 1.0
                elif (i, d) in matrix or (j, d) in matrix:
                    y += 1.0
            similarity[actors[i],actors[j]] = x/(x+y)
    return similarity 


def create_sig_matrix(matrix, m, n, k):
    hashes = []
    p = get_first_prime_larger_than(m)
    signature_matrix = [[float('Inf')]*k for i in range(0, n)]
    for i in range(0, k):
        hashes.append(get_hash_variables(p))

    for i, j in matrix:
        for pi, (a,b) in enumerate(hashes):
            hash_value = (a*j+b)%p%m
            if hash_value < signature_matrix[i][pi]:
                signature_matrix[i][pi] = hash_value
    return signature_matrix, hashes


def approximate_jaccard_lsh(matrix, movies, actors, K, bands):
    similarity = {}
    n = len(actors)
    m = len(movies)
    signature_matrix, hash_functions = create_sig_matrix(matrix, m, n, K)
    M = K
    r = M/bands
    print("   rows per band = " + str(r))
    c = n #number of signatures
    p = int(c*bu) #number of buckets
    #create buckets
    buckets = []
    for i in range(0, bands):
        buckets.append([])
        for j in range(0, p):
            buckets[i].append([])

    #Hash to buckets
    for i in range(0, bands):
        a, b = hash_functions[i*r]
        for j in range(0,n):
            start_index = i*r
            int_list = ''.join(str(x) for x in signature_matrix[j][start_index:start_index+r])
            hashed_val = (a*int(int_list)+b)%p
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
    for i, j in candidate_pairs:
        similarity[actors[i],actors[j]] = 0.0
        for pi in range(0, k):
            if signature_matrix[i][pi] == signature_matrix[j][pi]:
                similarity[actors[i],actors[j]] += 1

    for (a1, a2) in similarity:
        similarity[a1, a2] /= float(K)
    return similarity


def approximate_jaccard_minhash(matrix, movies, actors, k):
    similarity = {}
    n = len(actors)
    m = len(movies)
    signature_matrix, _ = create_sig_matrix(matrix, m, n, k)
    for i in range(0,n):
        for j in range(i + 1, n):
            similarity[actors[i],actors[j]] = 0.0
            for pi in range(0, k):
                if signature_matrix[i][pi] == signature_matrix[j][pi]:
                    similarity[actors[i],actors[j]] += 1
    #calculating fractions                    
    for (a1, a2) in similarity:
        similarity[a1, a2] /= float(k)
    return similarity


def approximate_jaccard_minhash_bbit(matrix, movies, actors, k, b):
    similarity = {}
    n = len(actors)
    m = len(movies)
    signature_matrix, _ = create_sig_matrix(matrix, m, n, k)

    for i in range(0, len(signature_matrix)):
        for j in range(0, len(signature_matrix[0])):
            signature_matrix[i][j] = convert_to_bbit(signature_matrix[i][j], b)
    #calculate similarity1
    for i in range(0,n):
        for j in range(i + 1, n):
            similarity[actors[i],actors[j]] = 0.0
            for pi in range(0, k):
                if signature_matrix[i][pi] == signature_matrix[j][pi]:
                    similarity[actors[i],actors[j]] += 1
    #calculating fractions                    
    for (a1, a2) in similarity:
        similarity[a1, a2] /= float(k)
    return similarity

def convert_to_bbit(value,b):
    binary = bin(value)
    if len(binary) > b + 2: 
        return int(binary[-b:])
    else:
        print "b = 1, since input does not contain enough bits"
        return int(binary[-1])


print("Parsing data - ")
start = time.time()
matrix, movies, actors = parse_data_actors()
print("   took "+str(time.time() - start)+" seconds\n")


# print len(matrix), len(movies), len(actors)

# for j in range(0,len(movies)):
#     sys.stdout.write(str(movies[j])+" ")
#     for i in range(0,len(actors)):
#         if (i,j) in matrix:
#             sys.stdout.write('1')
#         else:
#             sys.stdout.write('0')
#     sys.stdout.write('\n')

if naive:
    print("Running naive")
    start = time.time()
    jaccard = calculate_jaccard(matrix, movies, actors)
    print("   took "+str(time.time() - start)+" seconds\n")

if minhash:
    print("Running Min Hashing")
    print("   k (hash functions) = " + str(k))
    start = time.time()
    jaccard_approx = approximate_jaccard_minhash(matrix, movies, actors, k)
    max_value = max(jaccard_approx.values())
    print("   Max value is: " + str(max_value))
    print("   took "+str(time.time() - start)+" seconds\n")


if lsh:
    print("Running LSH")
    print("   k (hash functions) = " + str(k))
    print("   bands = " + str(b))
    print("   bucket fraction = " + str(bu))
    jaccard_approx = {}
    jaccard_approx = {}
    start = time.time()
    jaccard_approx = approximate_jaccard_lsh(matrix, movies, actors, k, b)
    sorted_jaccard = sorted(jaccard_approx.items(), key=operator.itemgetter(1), reverse=True)
    print("   took "+str(time.time() - start)+" seconds\n")
    for i in range(0,100):
        print sorted_jaccard[i]

if bbit:
    print("Running b-bit")
    print("   k (hash functions) = " + str(k))
    print("   b bits = " + str(num_of_bits))
    jaccard_approx = {}
    start = time.time()
    jaccard_approx = approximate_jaccard_minhash_bbit(matrix, movies, actors, k, num_of_bits)
    max_value = max(jaccard_approx.values())
    print("   Max value is: " + str(max_value))
    print("   took "+str(time.time() - start)+" seconds\n")

if naive and (bbit or minhash):
    for (r1,r2) in jaccard:
        value = jaccard[r1,r2]
        approx = jaccard_approx[r1,r2]
        diff = abs(value - approx)
        print "compare (" +r1.strip()+"-"+r2.strip()+"): "+ "\nvalue: " +str(value)+"\napproximate: "+ str(approx) +"\ndifference: "+ str(diff)+"\n"

