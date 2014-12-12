import random


movie_count = 388226
role_count = 343261
movies_per_role = 10


def create_random_movie(id):
    name = "r" + str(id)
    year = random.randrange(1960,2014)
    score = random.randrange(0,10)
    length = random.randrange(30,200)
    return str(id) + ",'" + name + "'," + str(year) + "," + str(score) + "," + str(length)


def create_random_role(id):
    movie_id = random.randrange(0,movie_count)
    name = "r" + str(id)
    return str(id) + "," + str(movie_id) + ",'" + name + "'"



print("LOCK TABLES `movies` WRITE;")
for i in range(0,movie_count):
    print(create_random_movie(i))

print("LOCK TABLES `roles` WRITE;")
for i in range(0,role_count):
    for j in range(0,movies_per_role):
        print(create_random_role(i))
