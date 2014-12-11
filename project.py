import re, math
import random
import time
import sys


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


def dummy_data():
    characteristic_matrix = {}
    characteristic_matrix["1",0] = 1
    characteristic_matrix["1",1] = 1
    characteristic_matrix["1",5] = 1
    characteristic_matrix["1",6] = 1

    characteristic_matrix["2",2] = 1
    characteristic_matrix["2",3] = 1
    characteristic_matrix["2",4] = 1

    characteristic_matrix["3",0] = 1
    characteristic_matrix["3",5] = 1
    characteristic_matrix["3",6] = 1

    characteristic_matrix["4",1] = 1
    characteristic_matrix["4",2] = 1
    characteristic_matrix["4",3] = 1
    characteristic_matrix["4",4] = 1

    m = range(0,7)
    movies = {}
    for i in m:
        movies[i] = len(movies)
    r = ["1", "2", "3", "4"]
    roles = {}
    for j in r:
        roles[j] = len(roles) 

    return characteristic_matrix, movies, roles 


def create_dummy_data(r, M):
    roles = []
    for i in range(0,r):
        roles.append("r"+str(i))
    movies = range(0,M)
    matrix = {}
    for r in roles:
        appearing_number_of_movies = random.randint(1,M)
        movie_index =[random.randint(0,M) for p in range(0,appearing_number_of_movies)]
        for i in movie_index:
            matrix[r,i] = 1
    # for m in movies:
    #     for r in roles:
    #         if (r,m) in matrix:
    #             sys.stdout.write('  1')
    #         else:
    #             sys.stdout.write('  0')   
    #     print 
    return matrix, movies, roles

def parse_data():
    filename = "imdb-r.txt"
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
                if movies_table[movie_id] > 7.0:

                    if movie_id not in movies:
                        movies[movie_id] = len(movies)
                    
                    if role not in roles:
                        roles[role] = len(roles)
                    
                    key = (role,movie_id)
                    if key not in characteristic_matrix:
                        characteristic_matrix[key] = 1
    return characteristic_matrix, movies, roles
            

def calculate_jaccard(matrix, movies, roles):
    similarity = {}
    for r1 in roles:
        for r2 in roles:
            if r1 < r2:
                x = 0.0
                y = 0.0
                for m in movies:
                    if (r1, m) in matrix and (r2, m) in matrix:
                        x += 1.0
                    elif (r1, m) in matrix or (r2, m) in matrix:
                        y += 1.0
                similarity[r1,r2] = x/(x+y)
    return similarity 


def create_sig_matrix(matrix, movies, roles, k):
    hashes = []
    N = len(movies)
    p = get_first_prime_larger_than(N)
    signature_matrix = [[float('Inf')]*len(roles) for i in range(0, k)]
    for i in range(0, k):
        hashes.append(get_hash_variables(p))

    #print(hashes)
    #print("N: " + str(N) + "    p: " + str(p))
    count = 0
    for role, m_id in matrix:
        j = movies[m_id]
        r = roles[role]
        for i,(a,b) in enumerate(hashes):
            hash_value = (a*j+b)%p%N
            if hash_value < signature_matrix[i][r]:
                signature_matrix[i][r] = hash_value
    return signature_matrix, hashes


def approximate_jaccard_lsh(matrix, movies, roles, k, b):
    signature_matrix, hash_functions = create_sig_matrix(matrix, movies, roles, k)
    # print "signatures created!"
    M = len(signature_matrix)
    r = M/b
    c = len(signature_matrix[0])
    #buckets = [[[]]*(c/2)]*b
    buckets = []
    for i in range(0, b):
        buckets.append([])
        for j in range(0, c/2):
            buckets[i].append([])

    for i in range(0,b):
        a,b = hash_functions[i*r]
        for j in range(0,c):
            v = ""
            for k in range(0,r):
                g = str(signature_matrix[i*r + k][j])
                v += g
            hashed_val = (a*int(v)+b)%(c/2)
            buckets[i][hashed_val].append(j)
    visited = {}
    temp_dict = {}
    for band in buckets:
        for bucket in band:
            for r1 in bucket:
                for r2 in bucket:
                    if r1 < r2 and (r1,r2) not in visited:
                        print "comparing", r1, r2 

                        temp_dict[r1,r2] = 0.0
                        for i in range(0, len(signature_matrix)):
                            if signature_matrix[i][r1] == signature_matrix[i][r2]:
                                if (r1,r2) in temp_dict:
                                    temp_dict[r1,r2] += 1
                                else:
                                    temp_dict[r1,r2] = 1
                        visited[r1,r2] = None

    similarity = {}
    for (r1,r2) in temp_dict:
        similarity[r1,r2] = float(temp_dict[(r1,r2)])/float(k)

    return similarity


def approximate_jaccard_simple(matrix, movies, roles, k):
    signature_matrix, hash_functions = create_sig_matrix(matrix, movies, roles, k)
    temp_dict = {}
    for r1 in roles:
        for r2 in roles:
            #print(str(r1) + " " + str(r2)) # debugging
            if r1 < r2:
                temp_dict[r1,r2] = 0.0
                for i in range(0, len(signature_matrix)):
                    if signature_matrix[i][roles[r1]] == signature_matrix[i][roles[r2]]:
                        if (r1,r2) in temp_dict:
                            temp_dict[r1,r2] += 1
                        else:
                            temp_dict[r1,r2] = 1
    similarity = {}
    for (r1,r2) in temp_dict:
        similarity[r1,r2] = float(temp_dict[(r1,r2)])/float(k)

    return similarity
    

start = time.time()
M, m, r = dummy_data()
#M, m, r = parse_data()
print("done creating data in "+str(time.time() - start)+" seconds")

start = time.time()
jaccard = []
jaccard = calculate_jaccard(M, m, r)
print("done calculating in "+str(time.time() - start)+" seconds")

start = time.time()
jaccard_approx = approximate_jaccard_lsh(M, m, r, 3, 1)
print("done approximating in "+str(time.time() - start)+" seconds\n")

# for (r1,r2) in jaccard:
#      value = jaccard[r1,r2]
#      approx = jaccard_approx[r1,r2]
#      diff = abs(value - approx)
#      print "compare (" +r1+"-"+r2+"): "+ "\nvalue: " +str(value)+"\napproximate: "+ str(approx) +"\ndifference: "+ str(diff)+"\n"




