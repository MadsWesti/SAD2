import re, math
import random
import time
import sys
from collections import OrderedDict
import operator

# CONFIGURATION

number_of_movies_threshold = 20
min_rank = 0.0

## Naive
naive = False

## MinHashing
minhash = False
k = 10 # hash functions

## LSH
lsh = True
b = 5 # bands
bu = 1 # buckets
### Remember to set the k value in MinHashing

def parse_data_actors():
    movies = OrderedDict()
    actors = OrderedDict()
    roles = OrderedDict()
    characteristic_matrix = {}

    #parse actors
    with open("data/actors.txt") as f:
        for line in f:
            actor = re.split(',', line)
            a_id = int(actor[0])
            first_name = actor[1][1:-1]
            last_name = actor[2][1:-1]
            number_of_movies = int(actor[4])
            if number_of_movies > number_of_movies_threshold:
                actors[a_id] = first_name+" "+last_name

    #parse movies
    with open("data/movies.txt") as f:
        for line in f:
            movie = re.split(',', line)
            m_id = int(movie[0].strip())
            movies[m_id] = []

    #parse roles
    with open("data/roles.txt") as f:
        for line in f:
            role = re.split(',', line)
            actor_id = int(role[0].strip())
            movie_id = int(role[1].strip())
            if movie_id not in movies:
                continue
            if actor_id not in actors:
                continue
            key = actor_id, movie_id
            if key not in characteristic_matrix:
                characteristic_matrix[key] = None 
    return characteristic_matrix, movies, actors


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
    for a_i in actors:
        for a_j in actors:
            if a_i < a_j:
                x = 0.0
                y = 0.0
                for m in movies:
                    if (a_i, m) in matrix and (a_j, m) in matrix:
                        x += 1.0
                    elif (a_i, m) in matrix or (a_j, m) in matrix:
                        y += 1.0
                similarity[actors[a_i],actors[a_j]] = x/(x+y)
    return similarity 


def create_sig_matrix(matrix, m, n, k):
    hashes = []
    p = get_first_prime_larger_than(m)
    signature_matrix = [[float('Inf')]*k for i in range(0, n)]
    for i in range(0, k):
        hashes.append(get_hash_variables(p))

    for a_i, m_j in matrix:
        i = actor_index[a_i]
        j = movie_index[m_j]
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
        for j, a_j in enumerate(actors):
            start_index = i*r
            int_list = ''.join(str(x) for x in signature_matrix[j][start_index:start_index+r])
            hashed_val = (a*int(int_list)+b)%p
            buckets[i][hashed_val].append(a_j)

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
    for a_i,a_j in candidate_pairs:
        i = actor_index[a_i]
        j = actor_index[a_j]
        similarity[actors[a_i],actors[a_j]] = 0.0
        for pi in range(0, k):
            if signature_matrix[i][pi] == signature_matrix[j][pi]:
                similarity[actors[a_i],actors[a_j]] += 1

    for (a1, a2) in similarity:
        similarity[a1, a2] /= float(K)

    return similarity


def approximate_jaccard_minhash(matrix, movies, roles, k):
    similarity = {}
    n = len(roles)
    m = len(movies)
    signature_matrix, _ = create_sig_matrix(matrix, m, n, k)

    for i, a_i in enumerate(actors):
        for j, a_j in enumerate(actors):
            if a_i < a_j:
                similarity[actors[a_i],actors[a_j]] = 0.0
                for pi in range(0, k):
                    if signature_matrix[i][pi] == signature_matrix[j][pi]:
                        similarity[roles[i],roles[j]] += 1
    #calculating fractions                    
    for (a1, a2) in similarity:
        similarity[a1, a2] /= float(k)
    return similarity

def approximate_jaccard_minhash_bbit(matrix, movies, roles, k):
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

def convert_to_bbit(value,b):
    return bin(value)[-b:]


print("Parsing data - ")
start = time.time()
matrix, movies, actors = parse_data_actors()
print("   took "+str(time.time() - start)+" seconds\n")

actor_index = {}
for i,a in enumerate(actors):
    actor_index[a] = i
movie_index = {}
for i,m in enumerate(movies):
    movie_index[m] = i

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
    for i in range(0,20):
        print sorted_jaccard[i]


# a_i = 104245
# a_j = 160787
# x = 0.0
# y = 0.0
# count = 0
# for m in movies:
#     if (a_i, m) in matrix and (a_j, m) in matrix:
#         x += 1.0
#     elif (a_i, m) in matrix or (a_j, m) in matrix:
#         y += 1.0
# print x
# sim = x/(x+y)
# print sim


# for (r1,r2) in jaccard_approx:
#     value = jaccard[r1,r2]
#     approx = jaccard_approx[r1,r2]
#     diff = abs(value - approx)
#     print "compare (" +r1.strip()+"-"+r2.strip()+"): "+ "\nvalue: " +str(value)+"\napproximate: "+ str(approx) +"\ndifference: "+ str(diff)+"\n"

