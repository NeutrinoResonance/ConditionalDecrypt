import sympy as sp
from sympy.abc import x # <=> sp.Symbol("x")
import random

# NOTE: increasing q from 97 to 997 still resulted in
# Decryption of message >>>>>>>>>>>>>>>>>>>>
# Ciphertext: Poly(124*x**3 + 82*x**2 + 40*x - 51, x, modulus=997)
# Ciphertext * SK: 
# 	Poly(124*x**6 + 206*x**5 + 370*x**4 - 472*x**3 + 275*x**2 + 18*x - 153, x, modulus=997)
# Ciphertext * SK poly% Poly(x**4 + 1, x, modulus=997) =
# 	Poly(-472*x**3 + 151*x**2 - 188*x + 474, x, modulus=997) 
# ^^ % 5 = Poly(x**2 - x - 1, x, modulus=5)
# IDEAS:
# 1) change the max-degree (n)
# 2) change the seed to eliminate randomness
# 3) instead of adding two integers, only add 1

class BFV:
    # def __init__(self, n=4, q=97, t=5, seed=[1, 1, 2, 3]):
    # def __init__(self, n=4, q=97, t=5, seed=[1,0,1,0]):
    # def __init__(self, n=4, q=97, t=5, seed=None):
    def __init__(self, n=4, q=97, t=9, seed=None):
        self.n = n # Max-degree of polynomials (QUESTION: cryptographic?)
        self.q = q # Modulus (QUESTION: cryptographic?)
        self.t = t # Plaintext modulus

        self.seed = seed

        self.mod = self.get_poly_mod()
        # The polynomial modulus

        self.sk, self.pk = self.generate_keys()

    def get_poly_mod(self):
        return sp.poly(x ** self.n + 1, modulus=self.q) # x^n + 1

    def random_poly(self):
        terms = self.seed
        if self.seed == None:
            # terms = [random.randint(0, self.q-1) for _ in range(self.n)]
            # terms = [random.randint(-self.t, self.t) for _ in range(self.n)]
            # terms = [random.randint(-1, 1) for _ in range(self.n)]
            terms = [0 for _ in range(self.n)]

        poly = sp.Poly(terms, x, modulus=self.q)
        
        print("Generated random polynomial " + (">"*20))
        print(poly)
        print(">"*40)

        return poly

    def poly_mod(self, f):
        """
        # print("Modulus by polynomial " + (">" * 20))
        # print("Poly before:" + str(f))
        # print("Poly modulus:" + str(self.mod))
        
        poly_post_mod = sp.poly(f % self.mod, modulus=self.q)

        # print("After modulus:" + str(poly_post_mod))

        return poly_post_mod
        """
        # Reduce the polynomial by X^n + 1
        reduced_poly = f % self.mod
    
        # Reduce each coefficient mod q and handle negative coefficients
        reduced_coeffs = [(coeff % self.q + self.q) % self.q for coeff in reduced_poly.all_coeffs()]
    
        # Return the new polynomial with reduced coefficients
        return sp.Poly(reduced_coeffs, x, modulus=self.q)

    def generate_keys(self):
        # sk = self.random_poly()
        sk = sp.Poly([1], x, modulus=self.q)
        error_poly = self.random_poly()
        pk = self.poly_mod(sk * error_poly)

        print("Key generation: " + (">"*20))
        print("Secret key:" + str(sk))
        print("Error polynomial:" + str(error_poly))
        print("Public key:" + str(pk))
        return (sk, pk)

    def normalize_coefficients(self, term, modulus=None):
        moduli = {"t": self.t,
                  "q": self.q}
        norm_modulus = moduli.get(modulus, modulus)

        import pdb ; pdb.set_trace()
        
        coeffs = [(coeff % norm_modulus) for coeff in term.all_coeffs()]
        norm_poly = sp.Poly.from_list(coeffs, gens=term.gens,
                                      modulus=norm_modulus)
        return norm_poly

    def encode(self, message):
        return sp.Poly(message, x, modulus=self.q)

    def encrypt(self, message_poly):
        # Message polynomial (message m must be a polynomial in R_t)
        # message_poly = sp.Poly(m, x)
        # PROBLEM: Poly(x + 12, x, domain='ZZ')

        print("Encryption of message " + (">"*20))
        print("Message polynomial:" + str(message_poly))
        
        # Added security polynomial. Technically, this may be an
        # extra error term
        error_poly = self.random_poly()

        print("Random error poly:" + str(error_poly))
        
        # Encrypt: c = pk * r + msg (mod q)
        cipher_text = self.poly_mod(self.pk * error_poly + message_poly)

        print("Returned ciphertext:" + str(cipher_text))
        return cipher_text

    def decrypt(self, cipher_text):
        # Decrypt: enc(m) = (c * sk) mod (x^n + 1, q)
        # decrypt_poly = (cipher_text * self.sk) % self.mod
        # NOTE: ^^ ugly

        print("Decryption of message " + (">" * 20))
        print("Ciphertext: " + str(cipher_text))

        sk_mul = cipher_text * self.sk
        print("Ciphertext * SK: \n\t" + str(sk_mul))
        decrypt_poly = self.poly_mod(sk_mul)
        print("Ciphertext * SK poly%% %s =\n\t%s " % (str(self.mod),
                                                      decrypt_poly))
        
        # top_decrypt_poly = self.poly_mod(decrypt_poly) % self.t
        # NOTE: ^^ decrypt_poly is in GF(97) and taking the modulus
        # of that is not defined
        top_decrypt_poly = sp.poly(decrypt_poly, modulus=self.t)
        print("^^ %% %s = %s" % (str(self.t), str(top_decrypt_poly)))
        print("Normalized decryption: %s" % (
            str(self.normalize_coefficients(top_decrypt_poly, "t"))))
        return top_decrypt_poly

    def add(self, first, second):
        print("[OP] Addition" + (">" * 20))
        print("First: " + str(first))
        print("Second: " + str(second))
        result = first + second

        print("first + second:" + str(result))
        mod_result = self.poly_mod(result)
        print("first + second poly%% %s = %s" % (str(self.mod),
                                                str(mod_result)))
        return mod_result

    def mul(self, first, second):
        result = first * second
        top_result = self.poly_mod(result)
        return top_result

    

def first_test():
    print(">"* 40)
    bfv = BFV()
    # first_array = [1, 12]
    # second_array = [2, 10]
    # PROBLEM: these are larger than 4, so t=4 =>
    #    no decryption is possible
    # enc_first = bfv.encode([1,2])
    # enc_second = bfv.encode([1,1])
    enc_first = bfv.encode([1])
    enc_second = bfv.encode([1])
    enc_result = enc_first + enc_second
    
    cipher_first = bfv.encrypt(enc_first)
    cipher_second = bfv.encrypt(enc_second)
    
    print("Plaintext: %s + %s == %s" % (enc_first, enc_second, enc_result))
    print("Encrypted: %s + %s = ?" % (str(cipher_first),
                                      str(cipher_second)))

    cipher_result = bfv.add(cipher_first, cipher_second)
    dec_result = bfv.decrypt(cipher_result)
    import pdb ; pdb.set_trace()

    print("Decrypted result: ")
    print("\t->")

def second_test():
    print(">"* 40)
    bfv = BFV()
    enc_first = bfv.encode([2])
    cipher_first = bfv.encrypt(enc_first)
    dec_result = bfv.decrypt(cipher_first)
    
    import pdb ; pdb.set_trace()
    
    
    
if __name__ == "__main__":
    # first_test()
    second_test()
