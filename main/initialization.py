import json
import random
import sqlite3
import os.path
from . import models
from . import lagrange
from . import rsa_jz as rsa



print('have a try')
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir))
db_name = "db.sqlite3"

conn = sqlite3.connect(db_path + "/" + db_name)

conn.commit()



player_list = []

unreachable_map_point = []

def read_unreachable_map_point():
    positions = [line.strip().split() for line in open('main/forbiddenCoord.txt').readlines()]
    for position in positions:
        unreachable_map_point.append((int(position[0]), int(position[1])))

read_unreachable_map_point()

def constraint_check(value):
    '''
    :param attribute: name of the column
    :param value: value of the column
    :return: whether the value matches the constraints of attribute
    '''
    flag = ((value[0], value[1]) not in unreachable_map_point)
    return (flag and value[0] >= 1 and value[0] <= 23 and value[1] >= 1 and value[1] <= 23)


def initialize_rank():
    # initialize rank
    for i in range(1, 6):
        user = models.Users.objects.get(id=i)
        user.group_id = i
        if user.rank == -1:
            user.rank = random.randint(1, 20)
        user.save()


def initialize_rsa():
    rsa_list = rsa.get_RSAKeyList(1024, 5)
    for i in range(1, 6):
        public_key = str(rsa_list[i - 1]['e'])
        private_key = str(rsa_list[i - 1]['d'])
        rsa_n = str(rsa_list[i - 1]['n'])

        user = models.Users.objects.get(id=i)
        user.public_key = public_key
        user.private_key = private_key
        user.rsa_n = rsa_n
        user.save()


def initialize_lagrange():
    num = 5  # create num keys
    least_num = 3  # at least least_num keys can open the box

    password, keys = lagrange.create_lagrange_key(40, num, least_num)

    models.Box.objects.all().update(password=password)

    for i in range(1, 6):
        user = models.Users.objects.get(id=i)
        user.box_key_x = keys[i-1][0]
        user.box_key_y = keys[i-1][1]
        user.save()


def initialize_mill():
    for i in range(1, 6):
        mill_rand = str(random.getrandbits(233))
        mill_prime = "temp"

        user = models.Users.objects.get(id=i)
        user.mill_rand = mill_rand
        user.mill_prime = mill_prime
        user.save()


def initialize_position():
    # initialize position
    for i in range(1, 6):
        position_x = random.randint(1, 24)
        position_y = random.randint(1, 24)
        while (not constraint_check((position_x, position_y))):
            position_x = random.randint(1, 24)
            position_y = random.randint(1, 24)

        user = models.Users.objects.get(id=i)
        user.position_x = position_x
        user.position_y = position_y
        user.save()

def change_system_status():
    global_state=models.SystemParam.objects.get(key="global_status")
    global_state.intValue = 1
    global_state.save()

def check_system_status():
    global_state=models.SystemParam.objects.get(key="global_status")
    print(f'global status{global_state.intValue}')
    return global_state.intValue != 0


def initialize():
    change_system_status()
    initialize_rank()
    initialize_rsa()
    initialize_lagrange()
    initialize_mill()
    initialize_position()

def get_all_positions(player_id):
    '''
    :param player_id: the player_id is expected to be in [0, 4]
    :return:
    '''
    if not check_system_status():
        print('init')
        initialize()
    player_id = player_id - 1
    position_list = []
    for i in range(1, 6):
        user = models.Users.objects.get(id=i)
        position_x = user.position_x
        position_y = user.position_y
        position_list.append((position_x, position_y))

    user_name_list = ['pangzaiyu', 'yangyinuo', 'xujunzhou', 'gaoming', 'panhainan']
    res_dict = {}
    other_player = {}
    for i in range(0, 5):
        if i != player_id:
            info = {}
            info['position'] = [position_list[i][0], position_list[i][1]]
            info['known'] = 0
            other_player[user_name_list[i]] = info
    res_dict['player'] = user_name_list[player_id]
    res_dict['position'] = [position_list[player_id][0], position_list[player_id][1]]
    res_dict['otherPlayers'] = other_player
    print(res_dict)
    return json.dumps(res_dict)




