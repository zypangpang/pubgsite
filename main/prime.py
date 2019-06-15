# coding:utf-8
import math
import random

# 扩展欧几里得算法求模反元素
def ex_euclid(a, b, l):
    if b == 0:
        l[0] = 1
        l[1] = 0
        l[2] = a
    else:
        ex_euclid(b, a % b, l)
        temp = l[0]
        l[0] = l[1]
        l[1] = temp - a // b * l[1]

# 求模反元素
def mod_inverse(a, b):
    l = [0, 0, 0]
    if a < b:
        a, b = b, a
    ex_euclid(a, b, l)
    if l[1] < 0:
        l[1] = a + l[1]
    return l[1]

# n为要检验的大数，a < n，k = n - 1
def miller_rabin_witness(a, n):
    if n == 1:
        return False
    if n == 2:
        return True
    k = n - 1
    q = int(math.floor(math.log(k, 2)))
    while q > 0:
        m = k // 2 ** q
        if k % 2 ** q == 0 and m % 2 == 1:
            break
        q = q - 1
    if pow(a, n - 1, n) != 1:
        return False
    b1 = pow(a, m, n)
    for i in range(1, q + 1):
        if b1 == n - 1 or b1 == 1:
            return True
        b2 = b1 ** 2 % n
        b1 = b2
    if b1 == 1:
        return True
    return False

# Miller-Rabin素性检验算法,检验8次
def prime_test_miller_rabin(p, k):
    while k > 0:
        a = random.randint(1, p - 1)
        if not miller_rabin_witness(a, p):
            return False
        k = k - 1
    return True

# 判断num是否与prime_arr中的每一个数都互质
def prime_each(num, prime_arr):
    for prime in prime_arr:
        remainder = num % prime
        if remainder == 0:
            return False
    return True

# 从begin到end内所有的质数
def get_con_prime_array(begin, end):
    array = []
    for i in range(begin, end):
        flag = judge_prime(i)
        if flag:
            array.append(i)
    return array

# 判断一个数是不是质数
def judge_prime(number):
    temp = int(math.sqrt(number))
    for i in range(2, temp + 1):
        if number % i == 0:
            return False
    return True

# 生成count个与质数数组都互质的n bit大数
def get_rand_prime_arr(n, count):
    arr = get_con_prime_array(2, 100000)
    prime = []
    while len(prime) < count:
        num = random.randint(1<<n, 1<<(n+1))
        if num % 2 == 0:
            num = num + 1
        while True:
            if prime_each(num, arr) and prime_test_miller_rabin(num, 8):
                if num not in prime:
                    prime.append(num)
                break
            num = num + 2
    return prime
