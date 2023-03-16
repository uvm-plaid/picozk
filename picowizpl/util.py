gensym_num = 0
def gensym(x):
    global gensym_num
    gensym_num = gensym_num + 1
    return f'{x}_{gensym_num}'

def decode_int(bits):
    return int("".join(str(x) for x in reversed(bits)), 2)

def encode_int(i, field):
    bitwidth = get_bits_for_field(field)
    bit_format = f'{{0:0{bitwidth}b}}'
    return [int(b) for b in reversed(bit_format.format(i))]

def get_bits_for_field(field):
    n = 1
    while 2**n < field:
        n += 1
    return n
