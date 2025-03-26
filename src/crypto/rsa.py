import random
import time
import base64

class RSA:
    def __init__(self, size=128):
        self.size = size
    
    def mod_exp(self, base, exponent, modulus):
        if modulus == 1:
            return 0
        base = base % modulus
        if exponent < 0:
            base = self.modular_inverse(base, modulus)
            exponent = -exponent
        result = 1
        while exponent > 0:
            if exponent % 2 == 1:
                result = (result * base) % modulus
            exponent //= 2
            base = (base * base) % modulus
        return result

    def modular_inverse(self, number, modulus):
        gcd, inverse, _ = self.extended_gcd(number, modulus)
        if gcd != 1:
            raise ValueError("Modular inverse does not exist")
        return inverse % modulus

    def extended_gcd(self, a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = self.extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y

    def miller_rabin(self, n):
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

    def generate_keys(self):
        p, q = 0, 0
        while not p:
            rng = random.getrandbits(self.size)
            if self.miller_rabin(rng):
                p = rng
        while not q:
            rng = random.getrandbits(self.size)
            if self.miller_rabin(rng):
                q = rng
        n, r = p * q, (p - 1) * (q - 1)
        e = 2
        while e < r:
            if self.extended_gcd(e, r)[0] == 1:
                break
            else:
                e += 1
        d = self.mod_exp(e, -1, r)
        public_key_string = ','.join((str(e), str(n)))
        private_key_string = ','.join((str(d), str(p), str(q)))
        return self.encode_base_64(public_key_string), self.encode_base_64(private_key_string)

    def encode_base_64(self, key):
        key_bytes = key.encode("ascii")
        base64_bytes = base64.b64encode(key_bytes)
        return base64_bytes.decode("ascii")

    def decode_base_64(self, base64_key):
        base64_bytes = base64_key.encode("ascii")
        key_bytes = base64.b64decode(base64_bytes)
        return tuple([int(x) for x in key_bytes.decode("ascii").split(",")])

    def chinese_remainder_theorem(self, dq, dp, p, q, c):
        m1 = self.mod_exp(c, dp, p)
        m2 = self.mod_exp(c, dq, q)
        qinv = self.modular_inverse(q, p)
        h = (qinv * (m1 - m2)) % p
        return m2 + h * q

    def encrypt(self, message_input, public_key):
        return [self.mod_exp(ord(char), public_key[0], public_key[1]) for char in message_input]

    def decrypt(self, cipher_input, private_key):
        dec_str = ""
        dp = self.mod_exp(private_key[0], 1, private_key[1] - 1)
        dq = self.mod_exp(private_key[0], 1, private_key[2] - 1)
        for num in cipher_input:
            char = self.chinese_remainder_theorem(dq, dp, private_key[1], private_key[2], num)
            dec_str += chr(char)
        return dec_str

if __name__ == "__main__":
    rsa = RSA()
    message = "Lorem"
    public_key, private_key = rsa.generate_keys()
    print('public key:', public_key, 'private key:', private_key)
    public_key, private_key = rsa.decode_base_64(public_key), rsa.decode_base_64(private_key)
    encrypted_message = rsa.encrypt(message, public_key)
    print("Encrypted message:", encrypted_message)
    decrypted_message = rsa.decrypt(encrypted_message, private_key)
    print("Decrypted message:", decrypted_message)
