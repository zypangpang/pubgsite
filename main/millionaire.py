import rsa
import random
import math
# import Crypto
# from crypto import Util

class User():
    
    def __init__(self, id):
        self.id = id
        self.rank = self.generateRank()
        (self.public_key, self.__private_key) = rsa.newkeys(512)
        self.vote = -1
        # c = rsa.core.encrypt_int(233,self.__private_key.e,self.__private_key.n)
        # x = rsa.core.decrypt_int(c,self.__private_key.d,self.__private_key.n)
        # print(c)
        # print(x)
        # temp = random.getrandbits(512)
        # print(temp)

    def __str__(self):
        # print(self.__private_key.n)
        return "id: %d Rank: %d \n%s \n%s" % (self.id,self.rank,self.__private_key,self.public_key)

    def generateRank(self):
        return random.randint(0,18)
    
    def is_prime(self, num, test_count):
        if num == 1:
            return False
        if test_count >= num:
            test_count = num - 1
        for x in range(test_count):
            val = random.randint(1, num - 1)
            # print("val: %d, num: %d"%(val,num))
            if pow(val, num-1, num) != 1:
                return False
        return True

    def generate_big_prime(self,n):
        found_prime = False
        while not found_prime:
            p = random.randint(2**(n-1), 2**n)
            if self.is_prime(p, 1000):
                return p

    def millEncrypt(self,bob):
        self.randIntX = random.getrandbits(233)
        return rsa.core.encrypt_int(self.randIntX, bob.__private_key.e, bob.__private_key.n)

    def millToBob(self,bob):
        return self.millEncrypt(bob) - self.rank

    def millDecrypt(self,msg):
        return rsa.core.decrypt_int(msg,self.__private_key.d,self.__private_key.n)

    def millCalMsgToA(self,pnl):
        notDone = True
        msgToA = []
        while notDone:
            notDone = False
            # print("fuck")
            (tpub,tpri) = rsa.newkeys(200)
            self.curPrime = tpri.p
            # print("shit %d"%(self.curPrime))
            msgToA = [x%self.curPrime for x in pnl]
            for i in range(19):
                # print("msgToA[%d]: %d"%(i,msgToA[i]))
                if notDone:
                    break
                for j in range(19):
                    if i == j:
                        continue
                    # print("msgToA[%d]: %d"%(j,msgToA[j]))
                    if abs(msgToA[i] - msgToA[j]) < 3:
                        # print("fuck1")
                        notDone = True
                        break
                if msgToA[i] < 2:
                    # print("fuck2")
                    notDone = True
                if msgToA[i] > self.curPrime - 3:
                    # print("fuck3")
                    notDone = True
            # print("notDone: %d"%(notDone))
        # print("ahhhhhh")
        for i in range(19):
            if i < self.rank:
                msgToA[i] = msgToA[i] - 1
            elif i > self.rank:
                msgToA[i] = msgToA[i] + 1
        return msgToA
    
    def millToAlice(self,msg):
        rankList = list(range(0,19))
        randList = [msg+x for x in rankList]
        possibleNumList = [self.millDecrypt(x) for x in randList]
        msgToA = self.millCalMsgToA(possibleNumList)
        return msgToA,self.curPrime

    def millGetResult(self,msg,prime):
        remainder = self.randIntX % prime
        if remainder == msg[self.rank]:
            return 0
        elif remainder > msg[self.rank]:
            return 1
        else:
            return -1
        return -2
        

def findLeader(s):
    setP = []
    setQ = []
    setR = []
    n = len(s)
    if n == 1:
        return s[0]
    print("millionaire begin")
    for x in range(n):
        if x == 0:
            setQ.append(s[0])
            continue
        print("comparing %d of rank %d and %d of rank %d "%(0,s[0].rank,x,s[x].rank))
        compareResult = millionaire(s[0],s[x])
        print("result of user %d with user %d is %d"%(0,x,compareResult))
        if compareResult == -1:
            setR.append(s[x])
        elif compareResult == 0:
            setQ.append(s[x])
        else:
            setP.append(s[x])

    if len(setR) > 0:
        return findLeader(setR)
    if len(setQ) == 1:
        return s[0]

    setV = []
    for user in s:
        if setQ.count(user) != 0:
            setV.append(user)
    return voteLeader(setQ,setV)

def millionaire(a,b):
    msgToB = a.millToBob(b)
    msgToA,primeOfB = b.millToAlice(msgToB)
    result = a.millGetResult(msgToA,primeOfB)
    return result
    # return random.randint(-1,1)

def voteLeader(cs,vs):
    # genUser = User(0)
    # p = genUser.generate_big_prime(512)
    # q = genUser.generate_big_prime(512)
    # while q == p:
    #     q = genUser.generate_big_prime(512)
    (pub,pri) = rsa.newkeys(16)
    # la = int((pri.p-1)*(pri.q-1)/lcm((pri.p-1),(pri.q-1)))
    la = int((pri.p-1)*(pri.q-1))
    # al = 1
    # be = 1
    # g = ((al*pri.n+1)*pow(be,pri.n))%pow(pri.n,2)
    print(pri.n)
    g = int(pri.n + 1)
    print("g: %d"%g)
    print("la: %d"%la)
    print("n: %d"%pri.n)
    print("pow(pri.n,2): %d"%(pow(pri.n,2)))
    # print(L(pow(g,la) % pow(pri.n,2), pri.n) % pri.n)
    # mu = int(mod_inverse(L(pow(g,la) % pow(pri.n,2), pri.n), pri.n) % pri.n)
    mu = int(mod_inverse(la, pri.n) % pri.n)
    print("mu: %d"%mu)
    print((pri.p-1)*(pri.q-1))
    # mu = L(pow(g,la) % pow(pri.n,2), pri.n) % pri.n
    
    nc = len(cs)
    nv = len(vs)
    base = nv + 2
    if base < 10:
        base = 10
    print("base: %d"%base)
    cList = []
    for c in range(nc):
        cList.append(c)
    for v in vs:
        v.vote = cList[random.randint(0,len(cList)-1)]
        print("vote: %d to %d"%(v.id,cs[v.vote].id))
    
    votes = []
    tUser = User(0)
    eMessage = 0
    tem = 0
    for i in range(nv):
        # print(pow(base,vs[i].vote))
        tm = int(pow(base,vs[i].vote))
        r = tUser.generate_big_prime(4)
        # print("fuck")
        # m1 = int(pow(g,tm) % pow(pri.n,2))
        # print("fuck1 r:%d"%r)
        # # print(pow(r,pri.n))
        # m2 = int(pow(r,pri.n) % pow(pri.n,2))
        # print("fuck2")
        m = int(((pow(g,tm)) * (pow(r,pri.n))) % pow(pri.n,2))
        print("ahhhhhh")
        print(tm)
        print(g)
        print(pri.n)
        print(((pow(g,tm) % pow(pri.n,2)) * (pow(r,pri.n) % pow(pri.n,2))) % pow(pri.n,2))
        print(m)
        print(r)
        print(la)
        print(pow(pri.n,2))
        print(mu)
        print((L(pow(m,la,pow(pri.n,2)), pri.n) * mu) % pri.n)
        print("shit")
        votes.append(m)
        eMessage = (eMessage + m) % pow(pri.n,2)
        tem = tem + tm
    print("em: %d"%eMessage)
    print(tem)
    etem = int(((pow(g,tem)) * (pow(r,pri.n))) % pow(pri.n,2))
    print(int(((pow(g,tem)) * (pow(r,pri.n))) % pow(pri.n,2)))
    detem = (L(pow(etem,la,pow(pri.n,2)), pri.n) * mu) % pri.n
    
    dMessage = (L(pow(eMessage,la,pow(pri.n,2)), pri.n) * mu) % pri.n
    print("dm:%d"%dMessage)
    print(detem)
    print(dMessage)
    dMessage = detem
    results = []
    for i in range(nc):
        print
        tr = dMessage % base
        results.append(tr)
        dMessage = (dMessage - tr) / base
    print(results)
    leaderIndex = results.index(max(results))
    return cs[leaderIndex]

def lcm(a, b):
    return a * b / math.gcd(a, b)

def L(u,n):
    return (u-1)/n

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


# ranks = ["列兵", "上等兵", "下士", "中士", "上士", "四级军士长", "三级军士长", "二级军士长", "一级军士长", "少尉", "中尉", "上尉", "少校", "中校", "上校", "大校", "少将", "中将", "上将"]
# # testUser = User(0)
# # print(testUser)
# # print(ranks[testUser.rank])
#
# # print(pow(2,47,3))
# n = 5
# users = []
# for x in range(n):
#     users.append(User(x))
#     print(users[x])
# print("finding leader")
# # leader = findLeader(users)
# vs = [users[0],users[1],users[2]]
# cs = [users[3],users[4]]
# leader = voteLeader(cs,vs)
# print(leader)