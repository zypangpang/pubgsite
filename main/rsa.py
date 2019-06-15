# coding:utf-8
import random
import prime
import time
import re

from . import models

def encryption(message, prk):
    '''Encrypt the int message into an int number using prk'''
    return pow(message, prk[1], prk[0])

def segment_encryption(message, seg_len, prk):
    '''Encrypt the string message into an int list using prk'''
    result = []
    msg_len = len(message)
    i = 0
    while i * seg_len < msg_len:
        lo_bound = i * seg_len
        up_bound = min((i+1)*seg_len, msg_len)
        msg_num = 0
        for j in range(lo_bound, up_bound):
            msg_num = (msg_num << 8) + ord(message[j])
        result.append(pow(msg_num, prk[1], prk[0]))
        i += 1
    return result

def decryption(secret, puk):
    '''Decrypt the int message into an int number using puk'''
    return pow(secret, puk[1], puk[0])

def segment_decryption(secret, puk):
    '''Decrypt the int list into a string message using puk'''
    result = ""
    for secret_seg in secret:
        msg_seg = pow(secret_seg, puk[1], puk[0])
        temp = ""
        while msg_seg > 0:
            temp += chr(msg_seg & 0xFF)
            msg_seg >>= 8
        result += temp[::-1]
    return result

def get_RSAKeyList(n, count):
    '''make a list with length = count and key bits = n'''
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
    '''input the from_id and to_id, return the check is True or False'''
    user_id = [from_id, to_id]
    user = []
    puk = []
    prk = []
    room_id = []
    massage = []
    secret = []
    decrypted_massage = []
    decrypted_room_id = []

    for i in range(0,2):
        try:
            user.append(models.Users.objects.get(id=user_id[i]))
        except:
            return False

    for i in range(0,2):
        puk.append(user[i].public_key)
        prk.append(user[i].private_key)
        room_id.append(user[i].room.id)
        massage.append("hello, this is private no.{} from room {}, "
            "the time is {}".format(user_id[i], room_id[i], time.time()))
        secret.append(segment_encryption(massage[i], 40, prk[i]))
        decrypted_massage.append(segment_decryption(massage[i], puk[i]))
        try:
            a = re.search("room [0-9]+", decrypted_massage[i])
            decrypted_room_id.append(a.group(0))
        except:
            return False

    if decrypted_room_id[0] == decrypted_room_id[1]:
        return True
    else:
        return False

'''
if __name__ == '__main__':

    start = time.time()
    RSAKey = get_RSAKeyList(1024, 10)[0]
    print((time.time()-start)/10)

    #RSAKey = get_RSAKeyList(1024, 1)[0]
    print("Enter the message: ")
    message = input()
    print("Message: ", message)
    secret = segment_encryption(message, 80, RSAKey['prk']) #less than n/8
    print("Encrypted message: ", secret)
    message = segment_decryption(secret, RSAKey['puk'])
    print("Decrypted message: ", message)
'''
