# These will support ~2**32 output values
PRESET_MODULI = [
    0xFFFFFFFB, # 4,294,967,291
    0xFFFFFFEF, # 4,294,967,279
    0xFFFFFFDB, # 4,294,967,259
    0xFFFFFFC5, # 4,294,967,237
    0xFFFFFFB3 # 4,294,967,219
]

class LookupTable:
    def __init__(self, tag_bits = 8, io_bits={"storage": 32, "result":8}, tag=0xfe, modulus=PRESET_MODULI[0]):
        """ Returns an encrypted and somewhat authenticated lookup table
        io_bits: the number of bits in the input and output numbers
        tag: the tag used to authenticate that the check performed
             on a specific entry in the array did, in fact, correspond
             to a key-match
        """
        
        self.tag = tag
        self.tag_bits = tag_bits
        self.io_bits = io_bits
        self.array = []
        self.mod = modulus

    def mod_inverse(self, a, m):
        m0, x0, x1 = m, 0, 1
        
        while a > 1:
            q = a // m
            m, a = a % m, m
            x0, x1 = x1 - q * x0, x0
        
        return x1 + m0 if x1 < 0 else x1


    def get_outputs(self, function):
        outputs = []
        inputs = []
        max_input_value = 2**self.io_bits["result"]
        for i in range(0, max_input_value):
            output = function(i)
            
            inputs.append(i)
            outputs.append(output)
        
        return (inputs, outputs)

    def tag_outputs(self, outputs):
        # shift_idx = self.io_bits
        shift_idx = self.io_bits["storage"] - self.tag_bits
        return [output | ((self.tag) << shift_idx) for output in outputs]

    def check_inverse(self, x, tagged_output, inverse):
        array_entry = tagged_output * inverse % self.mod
        decrypted = array_entry * x % self.mod
        
        print(">> Checking encryption of hash map entry: ")
        print(".. key: %d (hex: %x)" % (x, x))
        print(".. tagged value: %d (hex: %x)" % (tagged_output, tagged_output))
        print(".. inverse mod %d: %d (hex: %x) " % (self.mod, inverse, inverse))
        print(".. tagged_value * inverse %% %d: %d (hex:%x)" % \
              (self.mod, array_entry, array_entry))
        print(".. entry * key mod %d: %d (hex:%x)" % (self.mod, decrypted,
                                                      decrypted))

        if decrypted != tagged_output:
            import pdb ; pdb.set_trace()

    def generate(self, function):
        (inputs, outputs) = self.get_outputs(function)
        tagged_outputs = self.tag_outputs(outputs)

        inverses = []

        for (x, tagged_output) in zip(inputs, tagged_outputs):
            # IMPORTANT: convert the lookup key to a hash because otherwise
            # inputs like 1 will have an inverse of 1 which will leak the tag

            # IMPORTANT: multiplying keys of 0 with the 
            inverse = self.mod_inverse(x, self.mod)
            inverses.append(inverse)

            product = tagged_output * inverse % self.mod
            self.array.append(product)

            if x != 1:
                self.check_inverse(x, tagged_output, inverse)

        import pdb ; pdb.set_trace()
        


if __name__ == "__main__":
    lt = LookupTable()
    
    def is_even(x):
        return 1 if x % 2 == 0 else 0
    
    lt.generate(is_even)

        

        
        
