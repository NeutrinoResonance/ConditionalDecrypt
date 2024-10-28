import numpy as np

# Define modulus for batching and polynomial degree (should be a power of 2)
q = 786433            # Large prime modulus for plaintext space
poly_degree = 8       # Example polynomial degree, must be a power of 2 for efficient NTT

# Helper function to compute modular inverse via Extended Euclidean Algorithm
def mod_inverse(a, m):
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    return x1 + m0 if x1 < 0 else x1

# Step 1: Prime factors for CRT (chosen so they multiply to q)
crt_moduli = [17, 31, 769]  # Small CRT primes that divide q-1
crt_slots = len(crt_moduli)

# Step 2: Encode integers into slots using CRT
def encode_crt(values, crt_moduli):
    """Encodes a list of integers into CRT representation."""
    crt_values = []
    for mod in crt_moduli:
        crt_values.append([v % mod for v in values])
    return crt_values

# Step 3: Decode back from CRT representation
def decode_crt(crt_values, crt_moduli):
    """Decodes from CRT representation back to original integers."""
    M = np.prod(crt_moduli)  # Product of all CRT moduli (should equal or divide q)
    decoded_values = []
    for i in range(len(crt_values[0])):  # For each slot
        x = 0
        for j in range(len(crt_moduli)):
            m_j = crt_moduli[j]
            M_j = M // m_j
            x += crt_values[j][i] * M_j * mod_inverse(M_j, m_j)
        decoded_values.append(x % M)  # Reduce mod M
    return decoded_values

# Sample data to batch
values = [1, 2, 3, 4, 5, 6, 7, 8]
print("Original values:", values)

# Encode using CRT
crt_encoded = encode_crt(values, crt_moduli)
print("Encoded CRT values:", crt_encoded)

# Homomorphic addition (adding 5 to each slot)
for mod_values in crt_encoded:
    for i in range(len(mod_values)):
        mod_values[i] = (mod_values[i] + 5) % crt_moduli[crt_encoded.index(mod_values)]

# Homomorphic multiplication (multiplying each slot by 3)
for mod_values in crt_encoded:
    for i in range(len(mod_values)):
        mod_values[i] = (mod_values[i] * 3) % crt_moduli[crt_encoded.index(mod_values)]

# Decode back to original values after addition and multiplication
result = decode_crt(crt_encoded, crt_moduli)
print("Decoded values after addition and multiplication:", result)
