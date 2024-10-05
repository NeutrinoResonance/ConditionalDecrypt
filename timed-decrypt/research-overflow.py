from concrete import fhe
import numpy as np

# GOAL: determine whether the anti-tamper scheme of
# adding a security value (a tag, potentially?) to
# 

@fhe.compiler({"x_low":"encrypted",
               "y_low":"encrypted"})
def test_sub_overflow(x_low, y_low):
    total =  x_low - y_low
    # total_bits = fhe.bits(total)
    # bits = [total_bits[i] for i in range(0, 16)]
    # return (bits, total)
    # ValueError: Function 'test_sub_overflow' returned '[<concrete.fhe.tracing.tracer.Tracer object at 0x7ff32c981de0>, <concrete.fhe.tracing.tracer.Tracer object at 0x7ff32c982050>, <concrete.fhe.tracing.tracer.Tracer object at 0x7ff32c9822c0>, <concrete.fhe.tracing.tracer.Tracer object at 0x7ff32c982530>, <concrete.fhe.tracing.tracer.Tracer object at 0x7ff32c9827d0>, <concrete.fhe.tracing.tracer.Tracer object at 0x7ff32c982a40>, <concrete.fhe.tracing.tracer.Tracer object at 0x7ff32c982cb0>, <concrete.fhe.tracing.tracer.Tracer object at 0x7ff32c982f20>, <concrete.fhe.tracing.tracer.Tracer object at 0x7ff32c983190>, <concrete.fhe.tracing.tracer.Tracer object at 0x7ff32c983400>, <concrete.fhe.tracing.tracer.Tracer object at 0x7ff32c983670>, <concrete.fhe.tracing.tracer.Tracer object at 0x7ff32c9838e0>, <concrete.fhe.tracing.tracer.Tracer object at 0x7ff32c983b50>, <concrete.fhe.tracing.tracer.Tracer object at 0x7ff32c983dc0>, <concrete.fhe.tracing.tracer.Tracer object at 0x7ff32c9a8070>, <concrete.fhe.tracing.tracer.Tracer object at 0x7ff32c9a8280>]', which is not supported

    # return fhe.bits(total)[0:15]

    # return total >> 1

    return total
    

# inputset = [(0xff,)*2]



class OperandGenerator:
    def __init__(self, at_x=None, at_y=None,
                 op_pack_width = 8,
                 at_pack_width = 8):
        self.op_pack_mask = (1<<(op_pack_width- 1)) - 1
        self.at_pack_mask = (1<<(at_pack_width- 1)) - 1
        self.at_res_mask = (1<<(at_pack_width - 1)) - 1

        if at_x == None:
            at_x = (random.randint(0, 256) & \
                      self.at_pack_mask)

        if at_y == None:
            at_y = (random.randint(0, at_x) & \
                      self.at_pack_mask)

        self.at_x = at_x
        self.at_y = at_y
        
        self.sub_at = (at_x - at_y) & self.at_res_mask

    def pack(self, x_total, y_total):
        x_value = x_total & self.op_pack_mask
        x = (x_value << 8) + self.at_x

        y_value = y_total & self.op_pack_mask
        y = (y_value << 8) + self.at_y

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

def get_input_set():
    print("Generating inputset to facilitate `concrete`")
    print("learning the variable input range")

    gen = OperandGenerator(at_x=0xff, at_y=0xff)

    values = [gen.pack(0xff, 0xff)]
    return values
    
    
# inputset = [(0xffff & (1<<15-1),)*2]
inputset = get_input_set()
# NOTE: we take into account
circuit = test_sub_overflow.compile(inputset)

def run_sub_tests():
    result = circuit.encrypt_run_decrypt(0xff, 0xff)
    assert (result == 0 )


    """
    Hex x:4343
    Hex y:4343
    Binary x:0100001101000011
    Binary y:0100001101000011
    Hex result:0000
    Binary result:0000000000000000
    """

    gen = OperandGenerator(0x43, 0x43)
    
    x, y = gen.pack(0x43, 0x43)
    gen.dump_args(x, y)
    result = circuit.encrypt_run_decrypt(x, y)
    gen.dump_result(result)

    """
    Hex x:4543
    Hex y:4343
    Binary x:0100010101000011
    Binary y:0100001101000011
    Hex result:0200
    Binary result:0000001000000000
    """

    x, y = gen.pack(0x45, 0x43)
    gen.dump_args(x, y)
    result = circuit.encrypt_run_decrypt(x, y)
    gen.dump_result(result)

    """
    Hex x:4342
    Hex y:4343
    Binary x:0100001101000010
    Binary y:0100001101000011
    Hex result:ffff
    Binary result:1111111111111111
    """

    gen = OperandGenerator(0x42, 0x43)
    
    x, y = gen.pack(0x43, 0x43)
    gen.dump_args(x, y)
    result = circuit.encrypt_run_decrypt(x, y)
    gen.dump_result(result)

    """
    Hex x:4343
    Hex y:4342
    Binary x:0100001101000011
    Binary y:0100001101000010
    Hex result:0001
    Binary result:0000000000000001
    """

    gen = OperandGenerator(0x43, 0x42)
    
    x, y = gen.pack(0x43, 0x43)
    gen.dump_args(x, y)
    result = circuit.encrypt_run_decrypt(x, y)
    gen.dump_result(result)


    """
    Hex x:4343
    Hex y:4442
    Binary x:0100001101000011
    Binary y:0100010001000010
    Hex result:ff01
    Binary result:1111111100000001
    """
    
    gen = OperandGenerator(0x43, 0x42)
    
    x, y = gen.pack(0x43, 0x44)
    gen.dump_args(x, y)
    result = circuit.encrypt_run_decrypt(x, y)
    gen.dump_result(result)


    """
    Hex x:4342
    Hex y:4443
    Binary x:0100001101000010
    Binary y:0100010001000011
    Hex result:feff
    Binary result:1111111011111111
    """
    # NOTE: high byte is off by one.
    # The implication is that life is easier if the security
    # tag for the minuend is greater than that of the
    # subtrahend
    gen = OperandGenerator(0x42, 0x43)
    
    x, y = gen.pack(0x43, 0x44)
    gen.dump_args(x, y)
    result = circuit.encrypt_run_decrypt(x, y)
    gen.dump_result(result)

    
    # import pdb ; pdb.set_trace()

    """

    print(">> Now running ultra-negative AT parameter tests")
    x, y = gen.pack(0x4300, 0x4400)
    gen.dump_args(x, y)
    
    for i in range(1, 255):
        gen = OperandGenerator(0, i)
        x, y = gen.pack(0x43, 0x44)
        result = circuit.encrypt_run_decrypt(x, y)
        
        if (result & 0xff00) != 0xff:
            gen.dump_args(x, y)
            gen.dump_result(result)

    """
        

if __name__ == "__main__":
    run_sub_tests()
