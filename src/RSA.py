# SOURCES
# https://www.askpython.com/python/examples/rsa-algorithm-in-python
# https://youtu.be/wcbH4t5SJpg

def gcd(a, b):
    while a > 0:
        b = b % a
        (a, b) = (b, a)
    return b


def modInverse(A, M):
    if gcd(A, M) > 1:
        # modulo inverse does not exist
        return -1
    for X in range(1, M):
        if ((A % M) * (X % M)) % M == 1:
            return X
    return -1


p, q = 13, 11  # p=prime number, q=prime number INPUT HERE

n, r = p * q, (p - 1) * (q - 1)

e, d = 2, 2  # leurs minimum est de 2

while e < r:
    if gcd(e, r) == 1:
        break
    else:
        e += 1

d = modInverse(e, r)

private_key = (d, n)
public_key = (e, n)


def encrypt(message_input, public_key):
    encrypted_list = []
    for char in message_input:
        num = (ord(char) ** public_key[0]) % public_key[1]
        encrypted_list.append(num)
    return encrypted_list


def decrypt(cipher_input, private_key):
    dec_str = ""
    for num in cipher_input:
        char = (num ** private_key[0]) % private_key[1]
        dec_str = dec_str + chr(char)
    return dec_str


