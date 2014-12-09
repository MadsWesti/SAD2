import re, math
import random

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
    a = random.randrange(0,p)
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

def calculate_rank(rankings, average):
    n = float(len(rankings))
    X = sum(rankings)/n
    k = 10
    C = average
    return X*n/(n+k)+C*k/(n+k), len(rankings)
    #return X, len(rankings)

def calculate_score1(rankings):
    n = len(rankings)
    n_total = float(len(all_rankings))
    score = n/n_total*sum(rankings)/float(n)*100
    return score, n


def calculate_score2(rankings):
    rankings_good = []
    rankings_bad = []
    n = len(rankings)
    for ranking in rankings:
        if ranking > average:
            rankings_good.append(ranking)
        else:
            rankings_bad.append(ranking)

    score = 100*(sum(rankings_good)/n_total - sum(rankings_bad)/n_total)
    return score, len(rankings_good), len(rankings_bad)



movies = {}


def parse_data():
    filename = "toy/toy_4k.txt"
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

def create_sig_matrix(k, movies, roles, matrix):
    hashes = []
    N = len(movies)
    p = get_first_prime_larger_than(N)
    signature_matrix = [[float('Inf')]*len(roles) for i in range(0, k)]
    for i in range(0, k):
        hashes.append(get_hash_variables(p))

    print(hashes)
    print("N: " + str(N) + "    p: " + str(p))
    for j in range(0, N):
        for r in range(0, len(roles)):
            if (roles[r],movies[j]) in matrix:
                for i,(a,b) in enumerate(hashes):
                    hash_value = (a*j+b)%p%N
                    if hash_value < signature_matrix[i][r]:
                        signature_matrix[i][r] = hash_value
                        #print(signature_matrix) # debugging
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
            #print(str(r1) + " " + str(r2)) # debugging
            for i in range(0, len(matrix)):
                if matrix[i][r1] == matrix[i][r2]:
                    if (r1,r2) in sim:
                        sim[r1,r2] += 1
                    else:
                        sim[r1,r2] = 1
                        
            
    return sim


#M, m, r = dummy_data()
M, m, r = parse_data()
sig_matrix = create_sig_matrix(10, m, r, M)
#print(sig_matrix)
jaccard = calculate_jaccard_approx(sig_matrix, r)
print(jaccard)
