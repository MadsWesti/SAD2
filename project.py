import re
import operator


filename = "imdb-r.txt"
save = False
roles_dict = {}

with open(filename) as f:
    for line in f:
        if line.strip() == "LOCK TABLES `roles` WRITE;":
            save = True
            continue

        if save == True:
            role = re.split(',', line)[2].strip()
            #print(role)
            if role in roles_dict:
                roles_dict[role] += 1
            else:
                roles_dict[role] = 1

sorted_list = sorted(roles_dict.items(), key=operator.itemgetter(1))

for thing in sorted_list:
    print(thing)
