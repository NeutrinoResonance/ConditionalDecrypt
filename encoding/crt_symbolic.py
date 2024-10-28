import sympy as sp
import numpy as np

# Define parameters for RLWE system
N = 8  # Degree of the polynomial (power of 2 for CRT batching)
q = 786433  # Large prime modulus for plaintext space
x = sp.symbols('x')
# poly_ring = sp.polys.domains.ZZ.map([x**N + 1])  # Polynomial ring modulus x^N + 1
# NOTE: ^^ this fails

# poly_ring = sp.poly(x ** N + 1)
poly_modulus = x**N + 1  # Polynomial ring modulus x^N + 1

# Small CRT moduli that divide q-1
crt_moduli = [17, 31, 769]  # CRT primes that divide q-1
crt_polymod = [sp.poly(poly_modulus, modulus=mod) for mod in crt_moduli]
M = np.prod(crt_moduli)  # Product of all CRT moduli (for decoding)

# Helper function to compute modular inverse (for CRT reconstruction)
def mod_inverse(a, m):
    return sp.mod_inverse(a, m)
"""
def mod_inverse(a, m):
    return sp.mod_inverse(a, m)
"""

# Step 1: CRT-based Encoding
def encode_crt(values, crt_moduli):
    """Encodes a list of integers into CRT representation using the given moduli."""
    crt_values = []
    for mod in crt_moduli:
        crt_values.append([v % mod for v in values])
    return crt_values

"""
# Step 1: CRT-based Encoding into Polynomial Form
def encode_crt(values, crt_moduli):
    #Encodes a list of integers into CRT representation using the given moduli.
    crt_values = []
    for mod in crt_moduli:
        poly = sp.Poly.from_list(values, gens=x, modulus=mod)
        crt_values.append(poly)
    return crt_values
"""

# Step 2: CRT-based Decoding
def decode_crt(crt_values, crt_moduli):
    """Decodes from CRT representation back to original integers using CRT reconstruction."""
    decoded_values = []
    for i in range(len(crt_values[0])):  # For each slot
        x = 0
        for j in range(len(crt_moduli)):
            m_j = crt_moduli[j]
            M_j = M // m_j
            x += crt_values[j][i] * M_j * mod_inverse(M_j, m_j)
        decoded_values.append(x % M)
    return decoded_values

"""
def decode_crt(crt_values, crt_moduli):
    # Decodes from CRT polynomial representation back to original integers using CRT reconstruction.
    decoded_coeffs = []
    for i in range(len(crt_values[0].all_coeffs())):  # For each polynomial coefficient
        x = 0
        for j in range(len(crt_moduli)):
            m_j = crt_moduli[j]
            M_j = M // m_j
            coeff = crt_values[j].all_coeffs()[i]  # Get coefficient at position i for modulus j
            x += coeff * M_j * mod_inverse(M_j, m_j)
        decoded_coeffs.append(x % M)
    return decoded_coeffs

"""

# Step 3: Encode data into polynomials using CRT
values_a = [1, 2, 3, 4, 5, 6, 7, 8]  # Example data for polynomial A
values_b = [8, 7, 6, 5, 4, 3, 2, 1]  # Example data for polynomial B

crt_encoded_a = encode_crt(values_a, crt_moduli)
crt_encoded_b = encode_crt(values_b, crt_moduli)
print("CRT Encoded Polynomial A:", crt_encoded_a)
print("CRT Encoded Polynomial B:", crt_encoded_b)

# Step 4: Polynomial Multiplication (Homomorphic Multiplication in CRT space)
def crt_polynomial_multiplication(crt_poly_a, crt_poly_b, crt_moduli):
    """Multiply two polynomials in CRT form, modulo each CRT modulus."""
    crt_result = []
    for k in range(len(crt_moduli)):
        mod = crt_moduli[k]
        # Polynomial multiplication under each modulus
        result_mod_k = [(crt_poly_a[k][i] * crt_poly_b[k][i]) % mod for i in range(len(crt_poly_a[k]))]
        
        # NOTE: making the crt_poly's into a SymPy Poly and *'ing them
        # together is not effective due to the fact that SymPy will re-map
        # numerical coefficients to their congruent negativ values among
        # other problems
        
        print("For modulus %d: %s" % (mod, str(result_mod_k)))
        crt_result.append(result_mod_k)
    return crt_result
"""
def crt_polynomial_multiplication(crt_poly_a, crt_poly_b, crt_moduli, crt_polymod):
    # Multiply two polynomials in CRT form, modulo x^N + 1 and each CRT modulus.
    crt_result = []
    for k in range(len(crt_moduli)):
        mod = crt_moduli[k]
        polymod = crt_polymod[k]
        poly_a = crt_poly_a[k]
        poly_b = crt_poly_b[k]
        
        # Polynomial multiplication modulo x^N + 1 and mod
        # poly_product = (poly_a * poly_b).trunc(mod) % poly_modulus
        # NOTE: we don't need trunc here as sp.Poly.from_list() had
        # its modulus argument set

        # poly_product = (poly_a * poly_b) % polymod
        # print("For modulus %d: (coefficients) %s", mod, str(poly_product.all_coeffs()))
        # crt_result.append(poly_product)

        # Polynomial multiplication
        poly_product = poly_a * poly_b
        
        # Reduce coefficients modulo `mod` and polynomial modulo `x^N + 1`
        reduced_coeffs = [(coeff % mod) for coeff in poly_product.all_coeffs()]
        print("For modulus %d: (coefficients) %s" % (mod, str(reduced_coeffs)))
        # Convert the list of reduced coefficients back to a polynomial with modulus
        reduced_poly = sp.Poly.from_list(reduced_coeffs, gens=x, modulus=mod) % polymod
        print("For modulus %d: (after-poly coefficients) %s" % (mod, str(reduced_poly.all_coeffs())))
        crt_result.append(reduced_poly)
    return crt_result

"""

crt_result = crt_polynomial_multiplication(crt_encoded_a, crt_encoded_b, crt_moduli)
print("CRT Result after Multiplication:", crt_result)

# Step 5: Decode the result back to retrieve the original values
decoded_result = decode_crt(crt_result, crt_moduli)
print("Decoded Result after Multiplication:", decoded_result)
