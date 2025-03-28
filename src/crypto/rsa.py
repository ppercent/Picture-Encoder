# SOURCES
# https://www.askpython.com/python/examples/rsa-algorithm-in-python
# https://youtu.be/wcbH4t5SJpg
# https://youtu.be/qdylJqXCDGs, http://stackoverflow.com/questions/6325576/how-many-iterations-of-rabin-miller-should-i-use-for-cryptographic-safe-primes
# https://youtu.be/NcPdiPrY_g8
# https://www.geeksforgeeks.org/weak-rsa-decryption-chinese-remainder-theorem/

import random
import base64

def mod_exp(base, exponent, modulus):
    if modulus == 1:
        return 0  # Anything mod 1 is always 0

    base = base % modulus  # Ensure base is within the valid range

    if exponent < 0:
        base = modular_inverse(base, modulus)  # Compute modular inverse
        exponent = -exponent  # Convert exponent to positive

    result = 1
    while exponent > 0:
        if exponent % 2 == 1:  # If exponent is odd
            result = (result * base) % modulus
        exponent //= 2  # Divide exponent by 2
        base = (base * base) % modulus  # Square the base

    return result

def modular_inverse(number, modulus):
    """Computes the modular inverse of 'number' under modulo 'modulus' using the Extended Euclidean Algorithm."""
    gcd, inverse, _ = extended_gcd(number, modulus)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")  # Inverse exists only if gcd(number, modulus) == 1
    return inverse % modulus

def extended_gcd(a, b):
    """
    Extended Euclidean Algorithm:
    Returns gcd(a, b) and the coefficients x, y such that ax + by = gcd(a, b).
    """
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y


def miller_rabin(n):
    if n == 2:
        return True

    if n % 2 == 0:
        return False #Pas un nombre premier

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

def generate_keys(gui, key_size):
    p, q = 0, 0

    # Loop to generate p
    while not p:
        rng = random.getrandbits(key_size)
        if miller_rabin(rng):
            p = rng

    # Loop to generate q
    while not q:
        rng = random.getrandbits(key_size)
        if miller_rabin(rng):
            q = rng
    n, r = p * q, (p - 1) * (q - 1)

    e = 2 # le minimum est de 2

    while e < r:
        if extended_gcd(e, r)[0] == 1:
            break
        else:
            e += 1

    d = mod_exp(e, -1, r)

    public_key_string = ','.join((str(encode_base_64(e)), str(encode_base_64(n))))
    private_key_string = ','.join((str(encode_base_64(d)), str(encode_base_64(p)), str(encode_base_64(q))))

    gui.debug_draw_key_generated(public_key_string, private_key_string)

def encode_base_64(key):
    """
    Code un nombre en base 10 en base 64
    """
    key = str(key)
    key_bytes = key.encode("ascii")
    base64_bytes = base64.b64encode(key_bytes)
    base64_key = base64_bytes.decode("ascii")
    return base64_key


def decode_base_64(base64_char):
    """
    Decode un nombre en base 64 en base 10
    """

    base64_bytes = base64_char.encode("ascii")
    key_bytes = base64.b64decode(base64_bytes)
    key = key_bytes.decode("ascii")
    return int(key)

def decode_text(base64_text):
    """
    Dechiffre une chaîne de nombres en base 64 en chaine de caracteres
    """
    key = []
    for element in tuple([x for x in base64_text.split(",")]):
        key.append(decode_base_64(element))
    return key

# Implementation of the Chinese Remainder Theorem 
def chinese_remainder_theorem(dq, dp, p, q, c): 
      
    # Message part 1 
    m1 = mod_exp(c, dp, p) 
      
    # Message part 2 
    m2 = mod_exp(c, dq, q) 
      
    qinv = modular_inverse(q, p) 
    h = (qinv * (m1 - m2)) % p 
    m = m2 + h * q 
    return m 


def encrypt(message_input, public_key):
    """
    Encrypte une chaine de caracteres en nombre encryptes avec la RSA
    """
    encrypted = ''
    for char in message_input:
        num = mod_exp(ord(char),public_key[0],public_key[1])
        encrypted += (str(encode_base_64(num)) + ',') 
    return encrypted[:len(encrypted)-1]

def decrypt(cipher_input, private_key):
    """
    Decrypte des nombre encryptes avec la RSA en une chaine de caracteres 
    """
    dec_str = ""
    cipher_input = cipher_input.split(',')
    dp = mod_exp(private_key[0], 1, private_key[1] - 1) 
    dq = mod_exp(private_key[0], 1, private_key[2] - 1) 
    for base64num in cipher_input:
        base10num = decode_base_64(base64num)
        char = chinese_remainder_theorem(dq, dp, private_key[1], private_key[2], base10num)
        dec_str = dec_str + chr(char)
    return dec_str

# public_key,private_key=generate_keys(size)            
# print('public key: ', public_key,'private key: ', private_key)
# public_key,private_key=decode_text(public_key),decode_text(private_key) 
# print(public_key,private_key)
# encryptedMessage=encrypt(message, public_key)
# print(encryptedMessage)
# decryptedMessage=decrypt(encryptedMessage,private_key)
# print(decrypt(encryptedMessage,private_key))
# print(time.time()-debut)
