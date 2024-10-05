from concrete import fhe
import numpy as np
import random

# NOTE: this is 
class AntiTamperComparison:
    def __init__(self, at_x=None, at_y=None, op_res_width = 8, at_res_width=8):
        # SCHEMA: minuend - subtrahend = x - y >= 0?
        # + If the difference is >= 0, the shielded data is
        #   to be decrypted

        # NOTE: all of this is calculated on the client side.

        self.op_pack_mask = (1<<(op_res_width- 1)) - 1
        self.at_pack_mask = (1<<(at_res_width- 1)) - 1
        self.at_res_mask = (1<<(at_res_width - 1)) - 1

        if at_x == None:
            at_x = (random.randint(0, 256) & \
                      self.at_pack_mask)

        if at_y == None:
            at_y = (random.randint(0, 256) & \
                      self.at_pack_mask)

        self.at_x = at_x
        self.at_y = at_y
        
        self.sub_at = (at_x - at_y) & self.at_res_mask

    def get_table(self):
        # NOTE: we are using the constant 8 because of them
        (0x80 << 8)

    def get_args(self, x_full, y_full):
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

        x_value = x_full & (2**(self.pack_width) - 1)
        x = (x_value << 8) + self.at_x

        y_value = y_full & (2**(self.pack_width) - 1)
        y = (y_value << 8) + self.at_y

        return x, y



@fhe.compiler({"x":"encrypted", "y":"encrypted"})
def compare_one(x, y):
    return x - y


    

    



