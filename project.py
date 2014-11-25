import re
import operator


def is_unwanted(role):
    result = True
    if role == "":
        result = False
    if role == "Himself":
        result = False
    if role == "Herself":
        result = False
    return result

filename = "imdb-r.txt"
#filename = "toy.txt"
movie_genres = {}
genres_roles = {}

with open(filename) as f:
    for line in f:
        if line.strip()[0:10] == "LOCK TABLE":
            tabletype = line.strip()[13:-8].strip()
            continue

        

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

            if not is_unwanted(role):
                continue
 
            if movie_id in movie_genres: # Error with movie 111
                genres = movie_genres[movie_id]

                for genre in genres:
                    if role in genres_roles[genre]:
                        genres_roles[genre][role] += 1
                    else:
                        genres_roles[genre][role] = 1
            #else:
                #print(str(movie_id) + " is not in movie_genres dictionary")


for g in genres_roles:
    print("GENRE: " + g)

    sorted_g = sorted(genres_roles[g].items(), key=operator.itemgetter(1), reverse=True)

    for i in range(0,10):
        if i < len(sorted_g):
            print(sorted_g[i])


