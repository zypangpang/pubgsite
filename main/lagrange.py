import random

def create_lagrange_key(key_bits, num, least_num, password=None):
    '''create password with key_bits bits.
       key_bits is recommended to be no more than 45.
       In num keys at least least_num keys can solve the password.
       If password is not None then the password is same as given.
       return password and list of keys (x,y).
    '''
    f = []
    for i in range(least_num):
        f.append(random.randint(1<<key_bits, 1<<(key_bits+1)))
    #the last element in f is the password
    if password is not None:
        f[-1] = password
    keys = []
    '''
    xs = []
    while len(keys) < num:
        x = random.randint(1<<key_bits, 1<<(key_bits+1))
        if x in xs:
            continue
        xs.append(x)
    '''
    x = 0
    for i in range(num):
        x += 1
        y = 0
        for j in range(least_num):
            y = y * x + f[j]
        keys.append((x,y))
    return f[-1], keys

def solve_lagrange(keys, least_num):
    '''using keys to get password.
       if the amount of keys is less than least_num then solve fail, return -1.
       if there are keys with same x then return -2.
       else return the password.
    '''
    xs = []
    for key in keys:
        if key[0] in xs:
            return -2
        else:
            xs.append(key[0])

    if len(keys) < least_num:
        return -1

    password = 0.0
    l = least_num
    for i in range(l):
        t = keys[i][1]
        a = 1
        b = 1
        for j in range(l):
            if i != j:
                a *= (0 - keys[j][0])
                b *= (keys[i][0] - keys[j][0])
        t = t * a / b
        password += t

    return int(password+0.5)

if __name__ == '__main__':
    c = 0
    n = 1000
    for i in range(n):
        pwd, keys = create_lagrange_key(45, 5, 3)#, password=12345)
        pwd2 = solve_lagrange(keys[0:3], 3)
        if pwd == pwd2:
            c += 1
    print("{}/{}".format(c,n))
