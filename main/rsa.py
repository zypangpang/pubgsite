# coding:utf-8
import random
import prime
import time

# m^e = c (mod n)
def encryption(message, puk):
    return pow(message, puk[1], puk[0])

def segment_encryption(message, seg_len, puk):
    result = []
    msg_len = len(message)
    i = 0
    while i * seg_len < msg_len:
        lo_bound = i * seg_len
        up_bound = min((i+1)*seg_len, msg_len)
        msg_num = 0
        for j in range(lo_bound, up_bound):
            msg_num = (msg_num << 8) + ord(message[j])
        result.append(pow(msg_num, puk[1], puk[0]))
        i += 1
    return result

# c^d = m (mod n)
def decryption(secret, prk):
    return pow(secret, prk[1], prk[0])

def segment_decryption(secret, prk):
    result = ""
    for secret_seg in secret:
        msg_seg = pow(secret_seg, prk[1], prk[0])
        temp = ""
        while msg_seg > 0:
            temp += chr(msg_seg & 0xFF)
            msg_seg >>= 8
        result += temp[::-1]
    return result

def get_RSAKeyList(n, count):
    RSAKeyList = []
    prime_arr = prime.get_rand_prime_arr(n, 2*count)
    e_arr = prime.get_rand_prime_arr(n>>3, count)
    for i in range(count):
        RSAKey = {}
        p = prime_arr[2*i]
        q = prime_arr[2*i+1]
        while p == q:
            q = random.choice(prime_arr)
        n = p * q
        s = (p - 1) * (q - 1)
        e = e_arr[i]
        d = prime.mod_inverse(e, s)
        print("p = ", p, ",q = ", q)
        print("n = ", n)
        print("e = ", e, ",d = ", d)
        puk = [n, e]
        prk = [n, d]
        RSAKey['puk'] = puk
        RSAKey['prk'] = prk
        RSAKeyList.append(RSAKey)
    return RSAKeyList

def check(from_id, to_id):
    #判断from_id用户归属是否正确
    #获取两个用户的公钥私钥
    #根据用户id与时间戳建立消息
    #加解密
    #结果正确，认证成功
    pass

if __name__ == '__main__':

    start = time.time()
    RSAKey = get_RSAKeyList(1024, 10)[0]
    print((time.time()-start)/10)

    #RSAKey = get_RSAKeyList(1024, 1)[0]
    print("Enter the message: ")
    message = input()
    print("Message: ", message)
    secret = segment_encryption(message, 80, RSAKey['puk']) #less than n/8
    print("Encrypted message: ", secret)
    message = segment_decryption(secret, RSAKey['prk'])
    print("Decrypted message: ", message)
