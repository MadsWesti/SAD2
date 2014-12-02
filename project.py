import re
import operator


def is_meta_character(role):
    result = False
    metas = ["Himself", "", "Herself", "Themselves", "Additional Voices", "Narrator", "Extra", "Host", "Undetermined Role", "Cameo appearance"]
    if role in metas:
        result = True
    return result


def clean(role):
    role = re.split('\ \#[0-9]', role)[0] # Takes care of 'Person #2'
    role = re.split('\ \(', role)[0] # Takes care of 'Merchant (1990)'
    role = re.split('\ \[', role)[0] # Takes care of 'Merchant (1990)'
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


def calculate_score2(rankings, average, n_genre):
    rankings_good = []
    rankings_bad = []
    for ranking in rankings:
        if ranking > average:
            rankings_good.append(ranking)
        else:
            rankings_bad.append(ranking)

    score = sum(rankings_good)/n_genre - sum(rankings_bad)/n_genre
    return score*100, len(rankings_good), len(rankings_bad)

filename = "imdb-r.txt"
roles = {}
movies = {}
all_rankings = []
pair_result = {}

def pair_parse_data():
    with open(filename) as f:
        #counter = 0 # debugging
        for line in f:
            #if counter == 100000: # debugging
                #break # debugging
            if line.strip()[0:10] == "LOCK TABLE":
                tabletype = line.strip()[13:-8].strip()
                continue


            if tabletype == "movies":
                movie_id = re.split(',', line)[0].strip()
                rank = re.split(',', line)[-2].strip()

                if rank == "NULL":
                    continue

                rank = float(rank)
                
                all_rankings.append(rank)
                movies[movie_id] = [], rank
                    

            if tabletype == "roles":
                #counter += 1 # debugging
                movie_id = re.split(',', line)[0].strip()
                role = re.split(',', line)[2].strip().strip("'")

                if movie_id in movies:
                    role = clean(role) # removes suffices like (1999-2003)
                    if is_meta_character(role): # Removes roles like "Herself" "Himself"
                        continue
                    movies[movie_id][0].append(role)
                else:
                    continue


def parse_data():
    with open(filename) as f:
        counter = 0 # debugging
        for line in f:
            if counter == 100000: # debugging
                break # debugging
            if line.strip()[0:10] == "LOCK TABLE":
                tabletype = line.strip()[13:-8].strip()
                continue


            if tabletype == "movies":
                movie_id = re.split(',', line)[0].strip()
                rank = re.split(',', line)[-2].strip()

                if rank == "NULL":
                    continue

                rank = float(rank)
                
                movies[movie_id] = rank
                    

            if tabletype == "roles":
                counter += 1 # debugging
                movie_id = re.split(',', line)[0].strip()
                role = re.split(',', line)[2].strip().strip("'")

                if movie_id in movies:
                    rank = float(movies[movie_id])
                else:
                    continue

                role = clean(role) # removes suffices like (1999-2003)

                if is_meta_character(role): # Removes roles like "Herself" "Himself"
                    continue
     
                all_rankings.append(rank)
                if role in roles:
                    roles[role].append(rank)
                else:
                    roles[role] = [rank]



def print_singletons():
    n_total = len(all_rankings)
    average = sum(all_rankings)/float(n_total)

    for role in roles:

        roles[role] = calculate_score1(roles[role])  
        
    print("calculating score done")

    sorted_roles = sorted(roles.items(), key=operator.itemgetter(1), reverse=True)

    print("Sorting done")

    for i in range(0,10):
        if i < len(sorted_roles):
            print(sorted_roles[i])


def create_pairs():
    for movie in movies:
        #print(movie)
        for role in movies[movie][0]:
            if role not in roles:
                roles[role] = {}
            for role2 in movies[movie][0]:
                if role == role2:
                    break
                if role > role2:
                    break
                if role2 in roles[role]:
                    roles[role][role2].append(movies[movie][1])
                else:
                    roles[role][role2] = [movies[movie][1]]

pair_parse_data()
print("parsing done")
create_pairs()

for role in roles:
    root = roles[role]
    for role2 in root:
        result = calculate_score1(root[role2])
        if result[0] > 0.1:
            pair_result[role, role2] = result


sorted_roles = sorted(pair_result.items(), key=operator.itemgetter(1), reverse=True)

for role in sorted_roles:
    print(role)
