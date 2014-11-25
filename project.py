import re
import operator


filename = "imdb-r.txt"
movie_genres = {}
genres_roles = {}

with open(filename) as f:
    for line in f:
        if line.strip()[0:10] == "LOCK TABLE":
            type = line.strip()[13:-8].strip()
            continue

        

        if type == "movies_genres":
            movie_id = re.split(',', line)[0].strip()
            genre = re.split(',', line)[1].strip().strip("'")
            if movie_id in movie_genres:
                movie_genres[movie_id].append(genre)
            else:
                movie_genres[movie_id] = [genre]

            if genre not in genres_roles:
                genres_roles[genre] = {}


        if type == "roles":
            movie_id = re.split(',', line)[0].strip()
            role = re.split(',', line)[2].strip().strip("'")
            if movie_id in movie_genres:
                genres = movie_genres[movie_id]

                for genre in genres:
                    if role in genres_roles[genre]:
                        genres_roles[genre][role] += 1
                    else:
                        genres_roles[genre][role] = 1


for g in genres_roles:
    print("GENRE: " + g)

    sorted_g = sorted(genres_roles[g].items(), key=operator.itemgetter(1))

    for role in sorted_g:
        print(role)

