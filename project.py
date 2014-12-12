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
    characteristic_matrix[0,0] = 1
    characteristic_matrix[0,1] = 1
    characteristic_matrix[0,5] = 1
    characteristic_matrix[0,6] = 1

    characteristic_matrix[1,2] = 1
    characteristic_matrix[1,3] = 1
    characteristic_matrix[1,4] = 1

    characteristic_matrix[2,0] = 1
    characteristic_matrix[2,5] = 1
    characteristic_matrix[2,6] = 1

    characteristic_matrix[3,1] = 1
    characteristic_matrix[3,2] = 1
    characteristic_matrix[3,3] = 1
    characteristic_matrix[3,4] = 1

    r = ["r1", "r2", "r3", "r4"]
    m = range(0,7)

    return characteristic_matrix, m, r 


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
                        m_i = len(movies)
                        movies[movie_id] = m_i
                                         
                    if role not in roles:
                        r_i = len(roles)
                        roles[role] = r_i    
                     
                    if (r_i, m_i) not in characteristic_matrix:
                        characteristic_matrix[r_i, m_i] = 1
    #initialise for proper length
    m = [0]*len(movies)
    r = [0]*len(roles)

    #change role and movies dictionaries to list i.e. changing from id lookup to index lookup.
    for m_id in movies:
        m[movies[m_id]] = m_id

    for role in roles:
        r[roles[role]] = role 

    #debugging
    # print "testing length\n"
    # print "Movies:"
    # print "Dict:", len(movies), "List:", len(m)
    # print ""
    # print "Roles:"
    # print "Dict:", len(roles), "List:", len(r)

    # for i,m_id in enumerate(m):
    #     if i != movies[m_id]:
    #         print "error"

    # for i,role in enumerate(r):
    #     if i != roles[role]:
    #         print "error"

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


def create_sig_matrix(matrix, movies, roles, k):
    hashes = []
    N = len(movies)
    p = get_first_prime_larger_than(N)
    signature_matrix = [[float('Inf')]*len(roles) for i in range(0, k)]
    for i in range(0, k):
        hashes.append(get_hash_variables(p))

    #print(hashes)
    #print("N: " + str(N) + "    p: " + str(p))
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
    similarity = {}
    n = len(roles)
    m = len(movies)
    for i in range(0, n):
        for j in range(i + 1, n):
            similarity[roles[i],roles[j]] = 0.0
            for pi in range(0, k):
                if signature_matrix[k][i] == signature_matrix[k][j]:
                    similarity[roles[i],roles[j]] += 1
    
    #calculating fractions                    
    for (r1, r2) in similarity:
        similarity[r1, r2] /= float(k)
    return similarity
    

start = time.time()
M, m, r = dummy_data()
#M, m, r = parse_data()
print("done creating data in "+str(time.time() - start)+" seconds")

start = time.time()
jaccard = calculate_jaccard(M, m, r)
print("done calculating in "+str(time.time() - start)+" seconds")

#start = time.time()
#jaccard_approx = approximate_jaccard_simple(M, m, r, 3)
#print("done approximating in "+str(time.time() - start)+" seconds\n")

for (r1,r2) in jaccard:
      value = jaccard[r1,r2]
      approx = 0# jaccard_approx[r1,r2]
      diff = abs(value - approx)
      print "compare (" +r1+"-"+r2+"): "+ "\nvalue: " +str(value)+"\napproximate: "+ str(approx) +"\ndifference: "+ str(diff)+"\n"




