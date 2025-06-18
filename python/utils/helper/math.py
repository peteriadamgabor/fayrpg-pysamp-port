def is_point_in_ashlar(xs, ys, zs, x1, y1, z1, x2, y2, z2):
    if is_between_floats(xs, x1, x2) and is_between_floats(ys, y1, y2) and is_between_floats(zs, z1, z2):
        return True
    return False


def is_between_floats(f, f1, f2):
    if f1 == f2:
        return f == f1
    elif f1 > f2:
        return f2 <= f <= f1
    else:
        return f1 <= f <= f2

