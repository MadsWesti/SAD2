import random

#til at finde p... finder det naeste primtal stoerre end N
def get_prime_larger_than(N):
    next_int = N+1
    if is_prime(next_int):
        return next_int
    else:
        return get_prime(next_int)

#checker om et tal er et primtal.
def is_prime(n):
    if n <= 3:
        return n >= 2
    if n % 2 == 0 or n % 3 == 0:
        return False
    for i in range(5, int(n ** 0.5) + 1, 6):
        if n % i == 0 or n % (i + 2) == 0:
            return False
    return True

# finder en unvirsal hashing function, det er stadig collisions en gang i mellem... jeg ved ikke om det er meningen at den skal vaere collision-fri eller ej.
def get_hash():
    A = range(0,10)
    N = len(A) 
    p = get_prime_larger_than(N)
    a = random.randrange(5,p)# i hvilket interval vaelges der??? 
    b = random.randrange(5,p)#
    B = [((a*x + b) % p) % N for x in A]
    print "a = "+str(a), "b = " + str(b), "N = "+str(N), "p = "+str(p)
    print B

get_hash()
