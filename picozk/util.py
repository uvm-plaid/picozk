gensym_num = 0
def gensym(x):
    global gensym_num
    gensym_num = gensym_num + 1
    return f'{x}_{gensym_num}'

def decode_int(bits):
    return int("".join(str(x) for x in bits), 2)

def encode_int(i, field):
    bitwidth = get_bits_for_field(field)
    bit_format = f'{{0:0{bitwidth}b}}'
    return [int(b) for b in bit_format.format(i)]

def get_bits_for_field(field):
    n = 1
    while 2**n < field:
        n += 1
    return n

# OLD CODE that might be useful later

# Monkey-patching Galois

# def mk_defer(new_fn, old_fn):
#     def defer_fn(x, y):
#         if isinstance(x, Wire):
#             return new_fn(x, y)
#         elif isinstance(y, Wire):
#             return new_fn(y, x)
#         else:
#             return old_fn(x, y)
#     return defer_fn

# galois.Array.__add__ = mk_defer(Wire.__add__, galois.Array.__add__)
# galois.Array.__mul__ = mk_defer(Wire.__mul__, galois.Array.__mul__)
# galois.Array.__radd__ = mk_defer(Wire.__radd__, galois.Array.__radd__)
# galois.Array.__rmul__ = mk_defer(Wire.__rmul__, galois.Array.__rmul__)
