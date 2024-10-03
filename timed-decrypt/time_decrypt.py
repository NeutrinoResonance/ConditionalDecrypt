from concrete import fhe
import numpy as np
import time

"""
def make_base_comp_lut():
    # For x:uint16, y:uint16
    total = [2]*0xffff
    # All negative subtractions
    # mean x > y
    for i in range(1, 0x8000):
        total[i] = 1
    
    total[0] = 0

    return fhe.LookupTable(total)
"""

def make_base_comp_lut():
    # lhs | rhs
    total = [0] * 0xffff

    for i in range(0xff):
        for j in range(0xff):
            if i > j:
                total[(i<<8) + j] = 0
            if i < j:
                total[(i<<8) + j] = 1
            else:
                total[(i<<8) + j] = 2

    return total

bc = make_base_comp_lut()

# level_one_lut = fhe.LookupTable(
#     0,
#     1,
    
# )

# ? y >= x if
# x_low > y_low and:
#     y_high > x_high
# x_low < y_low and:
#     y_high > x_high
# x_low == y_low and:
#     y_high >= x_high


# xlow == ylow

# Input: xh_eq_yh <- BETA must match
xcond_xl_leq_yl_and_yh_leq_xh = fhe.LookupTable(
    [
        # xh_neq_yh =>
        #    yh < xh and xl <= yl
        0,
        # xh_neq_yh =>
        #    yh < xh and xl <= yl
        0
    ]
)
# Input: xh_eq_yh <- BETA must match
xcond_xl_leq_yl_and_yh_gt_xh = fhe.LookupTable(
    [
        # xh_neq_yh =>
        #    yh <= xh and yh > xh
        1,
        # xh_eq_yh =>
        #    yh == xh and yh > xh
        1
    ]
)
# Input: xh_eq_yh <- BETA must match
xcond_xl_g_yl_and_yh_leq_xh = fhe.LookupTable(
    [
        # xh_neq_yh =>
        #    xl > yl and yh < xh
        0,
        # xh_eq_yh =>
        #    xl > yl and yh == xh
        0
    ]
)
# Input: xh_eq_yh <- BETA must match
xcond_xl_g_yl_and_yh_gt_xh = fhe.LookupTable(
    [
        # xh_neq_yh =>
        #    xl > yl and yh > xh
        1,
        # xh_eq_yh =>
        #    xl > yl and yh > xh
        1
    ]
)


# Input: yh_gt_xh <- ALPHA must match
xcond_xl_leq_yl = fhe.LookupTable(
    [
        # <= yh_leq_xh
        xcond_xl_leq_yl_and_yh_leq_xh,
        # <= yh_gt_xh
        xcond_xl_leq_yl_and_yh_gt_xh
    ]
)
# Input: yh_gt_xh <- ALPHA must match
xcond_xl_g_yl = fhe.LookupTable(
    [
        # <= yh_leq_xh
        xcond_xl_g_yl_and_yh_leq_xh,
        # <= yh_gt_xh
        xcond_xl_g_yl_and_yh_gt_xh,
    ]
)
"""
# ex: start[xl_leq_y][yh_gt_xh]
orig_start = fhe.LookupTable(
    [
        # xl_leq_yl ?
        xcond_xl_leq_yl,
        xcond_xl_g_yl
    ]
)
# IMPORTANT: you cannot have lookup tables more than 2 deep!
"""

"""
# Flattening iteration one
flattened_one = fhe.LookupTable(
    [
        [
            # <= yh_leq_xh
            xcond_xl_leq_yl_and_yh_leq_xh,
            # <= yh_gt_xh
            xcond_xl_leq_yl_and_yh_gt_xh
        ],
        [
            # xl_leq_yl ?
            xcond_xl_leq_yl,
            xcond_xl_g_yl
        ]
    ]
)
"""

# Flattening iteration two
"""
flattened_two = fhe.LookupTable(
    [
        # [
            # <= yh_leq_xh
            xcond_xl_leq_yl_and_yh_leq_xh,
            # <= yh_gt_xh
            xcond_xl_leq_yl_and_yh_gt_xh,
        # ],
        # [
            # xl_leq_yl ?
            xcond_xl_leq_yl,
            xcond_xl_g_yl
        # ]
    ]
)
# NOTE: still not flat enough
"""
"""
flattened_three = fhe.LookupTable(
    [
        # [
            # <= yh_leq_xh
            # xcond_xl_leq_yl_and_yh_leq_xh,
        [
        # <= yh_leq_xh
        xcond_xl_leq_yl_and_yh_leq_xh,
        # <= yh_gt_xh
        xcond_xl_leq_yl_and_yh_gt_xh
        ],
            # <= yh_gt_xh
            # xcond_xl_leq_yl_and_yh_gt_xh,
        [
        # <= yh_leq_xh
        xcond_xl_g_yl_and_yh_leq_xh,
        # <= yh_gt_xh
        xcond_xl_g_yl_and_yh_gt_xh,
        ],
        # ],
        # [
            # xl_leq_yl ?
            # xcond_xl_leq_yl,
        [
        # <= yh_leq_xh
        xcond_xl_leq_yl_and_yh_leq_xh,
        # <= yh_gt_xh
        xcond_xl_leq_yl_and_yh_gt_xh
        ],
            # xcond_xl_g_yl
        [
        # <= yh_leq_xh
        xcond_xl_g_yl_and_yh_leq_xh,
        # <= yh_gt_xh
        xcond_xl_g_yl_and_yh_gt_xh,
    ]
        # ]
    ]
)
"""

flattened_four = np.array(
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

start = fhe.LookupTable(
    flattened_four.flatten()
)

# quit()


import pdb ; pdb.set_trace()

@fhe.compiler({"x_low":"encrypted",
               "x_high":"encrypted",
               "y_low":"encrypted",
               "y_high":"encrypted"})
def timer_finished_big(x_low,
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

    # return start[2*(2*xl_leq_yl) + yh_gt_xh)+yh_eq_xh]

    return start[4*(xl_leq_yl) + 2*yh_gt_xh + yh_eq_xh]

    # return start[xl_leq_yl][yh_gt_xh][yh_eq_xh]
    # return start[0][1][1]
    

# inputset = ([0xffffffff] * 2 ,)
# inputset = [(0xfffff,)*4]
inputset = [(0xff,)*4, ]
circuit = timer_finished_big.compile(inputset)

def test_decrypt():
    lut = flattened_four.flatten()
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
    
test_decrypt()
# quit()

def test(circuit):
    """
    # current = int(time.time())
    result = circuit.encrypt_run_decrypt(0xffff, 0xffff,
                                         0xffff, 0xffff)
    # print("result:", str(result))
    import pdb ; pdb.set_trace()

    result = circuit.encrypt_run_decrypt(0xfffe, 0xffff,
                                         0xffff, 0xffff)
    import pdb ; pdb.set_trace()
    """

    # current = int(time.time())
    result = circuit.encrypt_run_decrypt(0xff, 0xff, 0xff, 0xff)
    assert(result == 1)
    # print("result:", str(result))
    import pdb ; pdb.set_trace()

    result = circuit.encrypt_run_decrypt(0xfe, 0xff, 0xff, 0xff)
    assert(result == 1)
    import pdb ; pdb.set_trace()

    result = circuit.encrypt_run_decrypt(0xfe, 0xff, 0xfd, 0xff)
    assert(result == 0)
    import pdb ; pdb.set_trace()
    
    result = circuit.encrypt_run_decrypt(0xfe, 0xff, 0xff, 0xfe)
    assert(result == 0)
    import pdb ; pdb.set_trace()


test(circuit)
