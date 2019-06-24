# coding:utf-8
import random
from . import prime
import time
import re

from . import models

#public_key = e, private_key = d, rsa_n = n

def encryption(message, n, d):
    '''Encrypt the int message into an int number using prk[n,d]'''
    return pow(message, d, n)

def segment_encryption(message, seg_len, n, d):
    '''Encrypt the string message into an int list using prk[n,d]'''
    result = []
    msg_len = len(message)
    i = 0
    while i * seg_len < msg_len:
        lo_bound = i * seg_len
        up_bound = min((i+1)*seg_len, msg_len)
        msg_num = 0
        for j in range(lo_bound, up_bound):
            msg_num = (msg_num << 8) + ord(message[j])
        result.append(pow(msg_num, d, n))
        i += 1
    return result

def decryption(secret, n, e):
    '''Decrypt the int message into an int number using puk[n, e]'''
    return pow(secret, e, n)

def segment_decryption(secret, n, e):
    '''Decrypt the int list into a string message using puk[n, e]'''
    result = ""
    for secret_seg in secret:
        msg_seg = pow(secret_seg, e, n)
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
        '''
        print("p = ", p, ",q = ", q)
        print("n = ", n)
        print("e = ", e, ",d = ", d)
        '''
        RSAKey['n'] = n
        RSAKey['e'] = e
        RSAKey['d'] = d
        RSAKeyList.append(RSAKey)
    return RSAKeyList

def two_way_certificate(from_id, to_id):
    '''input the from_id and to_id, if succeed then return 1, else return 0'''
    user_id = [from_id, to_id]
    user = []
    n = []
    e = []
    d = []
    room_id = []
    massage = []
    secret = []
    decrypted_massage = []
    decrypted_room_id = []

    for i in range(0,2):
        try:
            user.append(models.Users.objects.get(user_id=user_id[i]))
        except:
            return 0

    for i in range(0,2):
        e.append(int(user[i].public_key))
        d.append(int(user[i].private_key))
        n.append(int(user[i].rsa_n))
        room_id.append(user[i].room.id)
        massage.append("hello, this is private no.{} from room {}, "
            "the time is {}".format(user_id[i], room_id[i], time.time()))
        secret.append(segment_encryption(massage[i], 40, n[i], d[i]))
        decrypted_massage.append(segment_decryption(secret[i], n[i], e[i]))
        try:
            a = re.search("room [0-9]+", decrypted_massage[i])
            decrypted_room_id.append(a.group(0))
        except:
            return 0

    if decrypted_room_id[0] == decrypted_room_id[1]:
        return 1
    else:
        return 0

def merge_user_group(id1, id2):
    #change all user with group_id=max(id1.group_id, id2.group_id) to min(,)
    group1 = models.Users.objects.get(user_id=id1).group_id
    group2 = models.Users.objects.get(user_id=id2).group_id
    if group1 == group2:
        return
    else:
        from_group = max(group1, group2)
        to_group = min(group1, group2)
    user_list = models.Users.objects.all()
    for u in user_list:
        if u.group_id == from_group:
            u.group_id = to_group
            u.save()

'''
if __name__ == '__main__':

    start = time.time()
    RSAKey = get_RSAKeyList(1024, 10)[0]
    print((time.time()-start)/10)

    #RSAKey = get_RSAKeyList(1024, 1)[0]
    print("Enter the message: ")
    message = input()
    print("Message: ", message)
    secret = segment_encryption(message, 80, RSAKey['n'], RSAKey['d']) #less than n/8
    print("Encrypted message: ", secret)
    message = segment_decryption(secret, RSAKey['n'], RSAKey['e'])
    print("Decrypted message: ", message)
'''
