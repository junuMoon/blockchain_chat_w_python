from random import randint

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        print(f"n % i: {n, i}")
        if n % i == 0:
            return False
    return True

def find_primes(start, end):
    pr1 = pr2 = 0
    while not is_prime(pr1):
        pr1 = randint(start, end - 1)
    while not is_prime(pr2):
        pr2 = randint(start, end - 1)
    return pr1, pr2

def gcd(a, b):
    while b:
        print(f"b: {b}\ta%b: {a % b}")
        a, b = b, a % b
    return a
        

def find_e(phi):
    e = None
    for i in range(2, phi):
        if gcd(phi, i) == 1:
            e = i
            break
    return e


def find_d(phi, e):
    for i in range(phi // e, phi):
        print(f"i: {i}\t phi // e: {phi // e}")
        if e * i % phi == 1:
            break
    return i

def generate_keys():
    n, e, d = 0, None, None
    while e is None or d is None:
        prime1, prime2 = find_primes(1000, 10000)
        n = prime1 * prime2
        phi = (prime1 - 1) * (prime2 - 1)
        e = find_e(phi)
        d = find_e(phi, e)
    return n, e, d

def get_mod(msg, exp, n):
    result = msg
    for i in range(1, exp):
        result = (result * msg) % n 
        print(result)
    return result

def encrypt(msg, e, n):
    return get_mod(msg, e, n)

def encrypt(msg, d, n):
    return get_mod(msg, d, n)

def main():
    message: int = int(input('integer to encrypt'))
    n, e, d = generate_keys()
    