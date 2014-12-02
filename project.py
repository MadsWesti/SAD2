import re
import operator


def is_meta_character(role):
    result = False
    metas = ["Himself", "", "Herself", "Themselves", "Additional Voices", "Narrator", "Extra"]
    if role in metas:
        result = True
    return result


def clean(role):
    role = re.split('\ \#[0-9]', role)[0] # Takes care of 'Person #2'
    role = re.split('\ \(', role)[0] # Takes care of 'Merchant (1990)'
    return role


def calculate_rank(rankings, average):
    n = float(len(rankings))
    X = sum(rankings)/n
    k = 10
    C = average
    return X*n/(n+k)+C*k/(n+k), len(rankings)
    #return X, len(rankings)


def calculate_score1(rankings, average, n_genre):
    n = len(rankings)
    score = n/n_genre*sum(rankings)/float(n)*100
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
#filename = "toy.txt"
movie_genres = {}
genres_roles = {}
movie_rankings = {}
all_rankings = {}

with open(filename) as f:
    for line in f:
        if line.strip()[0:10] == "LOCK TABLE":
            tabletype = line.strip()[13:-8].strip()
            continue


        if tabletype == "movies":
            movie_id = re.split(',', line)[0].strip()
            rank = re.split(',', line)[-2].strip()

            if rank == "NULL":
                continue

            rank = float(rank)
            
            movie_rankings[movie_id] = rank
                
        

        if tabletype == "movies_genres":
            movie_id = re.split(',', line)[0].strip()
            genre = re.split(',', line)[1].strip().strip("'")

            if movie_id in movie_genres:
                movie_genres[movie_id].append(genre)
            else:
                movie_genres[movie_id] = [genre]

            if genre not in genres_roles:
                genres_roles[genre] = {}
                all_rankings[genre] = []


        if tabletype == "roles":
            movie_id = re.split(',', line)[0].strip()
            role = re.split(',', line)[2].strip().strip("'")
            if movie_id in movie_rankings:
                rank = float(movie_rankings[movie_id])
            else:
                #rank = float(0)
                continue

            role = clean(role)

            if is_meta_character(role):
                continue
 
            if movie_id in movie_genres: # Error with movie 111
                genres = movie_genres[movie_id]

                for genre in genres:
                    all_rankings[genre].append(rank)
                    if role in genres_roles[genre]:
                        genres_roles[genre][role].append(rank)
                    else:
                        genres_roles[genre][role] = [rank]
            #else:
                #print(str(movie_id) + " is not in movie_genres dictionary")



for g in sorted(genres_roles):

    average = sum(all_rankings[g])/float(len(all_rankings[g]))
    n_genre = len(all_rankings[g])

    for role in genres_roles[g]:
        #genres_roles[g][role] = calculate_rank(genres_roles[g][role], average)
        #genres_roles[g][role] = calculate_score1(genres_roles[g][role], average, n_genre)  
        genres_roles[g][role] = calculate_score2(genres_roles[g][role], average, n_genre)  

    print("GENRE: " + g + "   avg: " + str(average))

    sorted_g = sorted(genres_roles[g].items(), key=operator.itemgetter(1), reverse=True)

    for i in range(0,10):
        if i < len(sorted_g):
            print(sorted_g[i])


