# SOURCES
# https://www.askpython.com/python/examples/rsa-algorithm-in-python
# https://youtu.be/wcbH4t5SJpg
# https://youtu.be/qdylJqXCDGs, http://stackoverflow.com/questions/6325576/how-many-iterations-of-rabin-miller-should-i-use-for-cryptographic-safe-primes
# https://youtu.be/NcPdiPrY_g8
# https://www.geeksforgeeks.org/weak-rsa-decryption-chinese-remainder-theorem/

import random
import time

debut=time.time()

size=1024
message=r"""Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. N"""

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
    encrypted_list = []
    for char in message_input:
        #num = (ord(char) ** public_key[0]) % public_key[1]
        num = mod_exp(ord(char),public_key[0],public_key[1])
        encrypted_list.append((num))
    return encrypted_list


def decrypt(cipher_input, private_key):
    dec_str = ""
    dp = mod_exp(private_key[0], 1, private_key[1] - 1) 
    dq = mod_exp(private_key[0], 1, private_key[2] - 1) 
    for num in cipher_input:
        char = chinese_remainder_theorem(dq, dp, private_key[1], private_key[2], num)
        dec_str = dec_str + chr(char)
    return dec_str

p,q=generate_keys()            
n, r = p * q, (p - 1) * (q - 1)

e, d = 2, 2  # leurs minimum est de 2

while e < r:
    if extended_gcd(e, r)[0] == 1:
        break
    else:
        e += 1

d = mod_exp(e, -1, r)

print(time.time()-debut)
private_key = (d, p, q)
public_key = (e, n)
encryptedEmoji=encrypt(message, public_key)
#print(encryptedEmoji)
decryptedEmoji=decrypt(encryptedEmoji,private_key)
#print(decrypt(encryptedEmoji,private_key))
print(time.time()-debut)
