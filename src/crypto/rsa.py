# SOURCES
# https://www.askpython.com/python/examples/rsa-algorithm-in-python
# https://youtu.be/wcbH4t5SJpg
# https://youtu.be/qdylJqXCDGs, http://stackoverflow.com/questions/6325576/how-many-iterations-of-rabin-miller-should-i-use-for-cryptographic-safe-primes

# character size indication
# chinese remainder theorem

import random

size=1024
message=r"""Sure! Let's dive deeper into the mathematics behind each function in the program. This will help clarify how the operations work, especially in the context of cryptography, particularly RSA-like encryption. ◌󠇯"""

def gcd(a, b):
    while a > 0:
        b = b % a
        (a, b) = (b, a)
    return b

def mod_exp(base, power, mod):
    result = 1
    while power > 0:
        # If power is odd
        if power % 2 == 1:
            result = (result * base) % mod

        # Divide the power by 2
        power = power // 2
        # Multiply base to itself
        base = (base * base) % mod

    return result

def miller_rabin(n):
    if n == 2:
        return True

    if n % 2 == 0:
        return False

    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2
    for _ in range(40):
        a = random.randrange(2, n - 1)
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_keys():
    p, q = 0, 0

    # Loop to generate p
    while not p:
        rng = random.getrandbits(size)
        if miller_rabin(rng):
            p = rng

    # Loop to generate q
    while not q:
        rng = random.getrandbits(size)
        if miller_rabin(rng):
            q = rng

    return p, q

p,q=generate_keys()            

n, r = p * q, (p - 1) * (q - 1)

e, d = 2, 2  # leurs minimum est de 2

while e < r:
    if gcd(e, r) == 1:
        break
    else:
        e += 1

d = y = pow(e, -1, r)

private_key = (d, n)
public_key = (e, n)


def encrypt(message_input, public_key):
    encrypted_list = []
    for char in message_input:
        #num = (ord(char) ** public_key[0]) % public_key[1]
        num = mod_exp(ord(char),public_key[0],public_key[1])
        encrypted_list.append((num))
    return encrypted_list


def decrypt(cipher_input, private_key):
    dec_str = ""
    for num in cipher_input:
        char = mod_exp(num,private_key[0],private_key[1])
        dec_str = dec_str + chr(char)
    return dec_str


encryptedEmoji=encrypt(message, public_key)
print(encryptedEmoji)
print(decrypt(encryptedEmoji,private_key))
