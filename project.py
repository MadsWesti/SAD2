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

filename = "imdb-r.txt"
#filename = "toy.txt"
movie_genres = {}
genres_roles = {}
movie_rankings = {}
average = 0

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
                    if role in genres_roles[genre]:
                        count = genres_roles[genre][role][1]
                        avg = genres_roles[genre][role][0]
                        genres_roles[genre][role][1] += 1
                        genres_roles[genre][role][0] = (avg*count+rank)/(count+1)
                    else:
                        genres_roles[genre][role] = [rank, 1]
            #else:
                #print(str(movie_id) + " is not in movie_genres dictionary")


for g in sorted(genres_roles):
    print("GENRE: " + g)

    sorted_g = sorted(genres_roles[g].items(), key=operator.itemgetter(1), reverse=True)

    for i in range(0,10):
        if i < len(sorted_g):
            print(sorted_g[i])


