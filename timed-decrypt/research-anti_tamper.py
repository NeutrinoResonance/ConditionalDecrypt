from concrete import fhe
import numpy as np
import random

# NOTE: this is 
class AntiTamperComparison:
    def __init__(self, at_x=None, at_y=None,
                 op_pack_width = 8, at_pack_width=8,
                 MAX_TABLE_SIZE=0xffff):
        # SCHEMA: minuend - subtrahend = x - y >= 0?
        # + If the difference is >= 0, the shielded data is
        #   to be decrypted

        # NOTE: all of this is calculated on the client side.

        self.MAX_TABLE_SIZE = MAX_TABLE_SIZE

        self.at_pack_width = at_pack_width
        self.op_pack_width = op_pack_width

        self.op_pack_mask = (1<<(op_pack_width- 1)) - 1
        self.op_res_mask = (1<<(op_pack_width)) - 1
        self.at_pack_mask = (1<<(at_pack_width- 1)) - 1
        self.at_res_mask = (1<<(at_pack_width)) - 1

        self.res_signed_mask = (1<<(self.op_pack_width-1))

        if at_x == None:
            at_x = (random.randint(0, 256) & \
                      self.at_pack_mask)

        if at_y == None:
            at_y = (random.randint(0, 256) & \
                      self.at_pack_mask)

        self.at_x = at_x
        self.at_y = at_y
        
        self.sub_at = (at_x - at_y) & self.at_res_mask

    def get_at_comp_table(self):
        # NOTE: we are using the constant 8 because of the
        # fact that the maximum table size is 0xffff entries
        table = [0] * self.MAX_TABLE_SIZE
        # table = fhe.zeros(self.MAX_TABLE_SIZE)
        
        for res in range(0, (1<<self.op_pack_width)):
            res_packed = self.pack_res(res)
            idx = res_packed + self.sub_at

            # y > x
            res_signed = (res & self.res_signed_mask)
            
            if (res_signed != 0) or (res == 0):
                table[idx] = 1
        
        return fhe.LookupTable(table)
        # return fhe.LookupTable(table)
        # return table
    
    def pack_res(self, result):
        res_value = result & self.op_res_mask
        res = (res_value << self.at_pack_width)
        return res
    
    def pack_op(self, operand):
        op_value = operand & self.op_pack_mask
        op = (op_value << self.at_pack_width)

        return op

    def get_args(self, x_total, y_total):
        # SIMPLIFEID SCHEMA:
        # x = [0, x[:7], 0, x_at[:7]] # EXPLANATION: NOTE A
        # y = [0, y[:7], 0, y_at[:7]] # EXPLANATION: NOTE B

        # SCHEMA:
        # + The minuend is provided to and by the flag server.
        #   
        # + The subtrahend is provided to the comparator 
        #   server. It is encrypted.

        # NOTE A: the anti-tamper value for the subtrahend 
        # will be packed with its value, encrypted, and placed
        # on the comparator server

        # NOTE B: the anti-tamper value for the minuend will 
        # be encrypted, and the flag server will left-shift 
        # the relevant byte of the time by 8, encrypted, and 
        # FHE-added to that encrypted anti-tamper value
        
        x = self.pack_op(x_total) + self.at_x

        y = self.pack_op(y_total) + self.at_y

        return x, y
    
    def dump_args(self, x, y):
        print(f"Hex x:{x:04x}")
        print(f"Hex y:{y:04x}")
        print(f"Binary x:{x:016b}")
        print(f"Binary y:{y:016b}")

    def dump_result(self, result):
        print(f"Hex result:{result:04x}")
        print(f"Binary result:{result:016b}")
        print(">"*40)

gen = AntiTamperComparison(0x43, 0x42)
comp_lut = gen.get_at_comp_table()

@fhe.compiler({"x":"encrypted", "y":"encrypted"})
def compare_byte_at(x, y):
    diff_at = x - y
    
    return comp_lut[diff_at]

def get_input_set():
    print("Generating inputset to facilitate `concrete`")
    print("learning the variable input range")

    gen = AntiTamperComparison(at_x=0xff, at_y=0xfe)
    x_input, y_input = gen.get_args(0xfe, 0xff)
    
    values = [(x_input, y_input)]
    return values
    
    
# inputset = [(0xffff & (1<<15-1),)*2]
inputset = get_input_set()
# NOTE: we take into account
circuit = compare_byte_at.compile(inputset)
    

def test_at():
    
    x, y = gen.get_args(0x34, 0x33)
    result = circuit.encrypt_run_decrypt(x, y)
    import pdb ; pdb.set_trace()
    



if __name__ == "__main__":
    test_at()
