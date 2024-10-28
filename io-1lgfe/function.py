from secrets import randbelow
import numpy as np

# IMPORTANT: need to implement the PRNG in
# _Indistinguishability Obfuscation from Simple-to-State Hard
# Problems: New Assumptions, New Techniques, and Simplification_ by 
# Romain Gay, Aayush Jain, Huija Lin, Amit Sahai,
# which seems to ensure that the public parameters are
# linked with the MSK via dot-product


# Parameters
n = 128 # count of terms / max degree of polynomial
q = 2**31 - 1 # coefficient modulus
sec_param = 128 # Also known as lambda, the "security parameter"
                # The larger this parameter gets, the greater
                # security is conferred. In other words, the larger
                # this is, the more operations (usually branching operations)
                # will have to be performed in order to recover the plaintext

def setup():
    msk_vector = np.random.randint(0, q, size=n) # Master secret key (MSK)
    public_params = np.random.randint(0, q, size=(n,n)) # Public parameter
    return msk_vector, public_params

def encrypt(m, public_params):
    error = np.random.randint(0, q, size=n)        # LWE error / noise vector
    cipher_text = np.dot(public_params, m) + error # LWE ciphertext

    return cipher_text

def get_result_vector(function):
    return np.array([function(i) for i in range(n)])

def function_key_gen(msk, function, public_params):
    f_result_vector = get_result_vector(function)
    smudge_noise = randbelow(q)
    # TODO: replace randbelow with the custom linear PRNG
    # introduced in the first part of the paper (referred to
    # by the name "NG")
    
    f_sk = np.dot(f_result_vector, msk) - smudge_noise
    # FSK (functional secret key),
    # derived in part from the MSK,
    # mutated with the smudging
    # noise.
    
    # NOTE: in the paper, the smudging noise is implied to be larger
    # than the normal noise

    return f_sk

def round_modulus(number):
    return int(number % q)

def decrypt(cipher_text, f_sk, f_result_vector):
    result = np.dot(cipher_text, f_result_vector) + f_sk
    return round_modulus(result)


def test_one():
    # Example usage
    s, pp = setup()
    x = np.random.randint(0, q, size=n)  # Plaintext vector
    print("x: ", x)
    ctxt = encrypt(x, pp)

    # Define function f (for example, sum function)
    f = lambda i: 1 if i % 2 == 0 else 0  # Example function vector
    f_vector = get_result_vector(f)
    sk_f = function_key_gen(s, f, pp)

    # Decrypt with function-specific key
    result = decrypt(ctxt, sk_f, f_vector)
    print("Decrypted function result:", result)

if __name__ == "__main__":
    test_one()
