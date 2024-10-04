from concrete import fhe
import numpy as np
import time


comp_table_nested = np.array(
    [
        # xl_gt_yl -> (xl > yl)
        [
            # yh_leq_xh -> (yh <= xh)
            [
                [
                    0, # yh_neq_xh -> (yh < xh)
                    0, # yh_eq_xh -> (yh == xh)
                ]
            ],
            # yh_gt_xh -> (yh > xh)
            [
                [
                    1, # yh_neq_xh -> (yh > xh)
                    1, # yh_eq_xh -> not possible
                ]
            ]
        ],
        # xl_leq_yl -> (xl <= yl)
        [
            # yh_leq_xh -> (yh <= xh)
            [
                [
                    0, # yh_neq_xh -> (yh < xh)
                    1, # yh_eq_xh -> (yh == xh)
                ]
            ],
            # yh_gt_xh -> (yh > xh)
            [
                [
                    1, # yh_neq_xh -> (yh < xh)
                    1, # yh_eq_xh -> not possible
                ]
            ]
        ]
    ]
)

comp_table = fhe.LookupTable(
    comp_table_nested.flatten()
)


@fhe.compiler({"x_low":"encrypted",
               "x_high":"encrypted",
               "y_low":"encrypted",
               "y_high":"encrypted"})
def timer_comparison(x_low,
                       x_high,
                       y_low,
                       y_high):

    # ? y >= x if
    # x_low <= y_low and:
    #     y_high >= x_high
    # x_low >= y_low and:
    #     y_high > x_high
    
    xl_leq_yl = (x_low <= y_low)
    yh_eq_xh = (x_high == y_high)
    yh_gt_xh = (y_high > x_high)

    return comp_table[4*(xl_leq_yl) + 2*yh_gt_xh + yh_eq_xh]
    

inputset = [(0xff,)*4, ]
circuit = timer_comparison.compile(inputset)

def test_decrypt():
    lut = comp_table_nested.flatten()
    print("Flattened comparison lookup table:")
    print(str(lut))
    
    def test(x_low, x_high, y_low, y_high):
        xl_leq_yl = 1 if (x_low <= y_low) else 0
        yh_eq_xh = 1 if (x_high == y_high) else 0
        yh_gt_xh = 1 if (y_high > x_high) else 0

        print("x_low:", x_low)
        print("x_high:", x_high)
        print("")
        print("y_low:", y_low)
        print("y_high:", y_high)

        print(">"*40)

        print("xl_leq_yl:", xl_leq_yl)
        print("yh_eq_xh:", yh_eq_xh)
        print("yh_gt_xh:", yh_gt_xh)

        result = lut[4*(xl_leq_yl) + 2*yh_gt_xh + yh_eq_xh]

        print("result: ", result)
        return result

    assert(test(0xff, 0xff, 0xff, 0xff) == 1)
    assert(test(0xff, 0xfe, 0xff, 0xff) == 1)
    assert(test(0xff, 0xfe, 0xff, 0xfd) == 0)
    assert(test(0xfe, 0xff, 0xff, 0xfe) == 0)
    
test_compare_nocrypt()

def test_compare_encrypted(circuit):
    result = circuit.encrypt_run_decrypt(0xff, 0xff, 0xff, 0xff)
    assert(result == 1)

    result = circuit.encrypt_run_decrypt(0xfe, 0xff, 0xff, 0xff)
    assert(result == 1)

    result = circuit.encrypt_run_decrypt(0xfe, 0xff, 0xfd, 0xff)
    assert(result == 0)
    
    result = circuit.encrypt_run_decrypt(0xfe, 0xff, 0xff, 0xfe)
    assert(result == 0)


test_compare_encrypted(circuit)
