from .import rsa_jz as rsa
import json
from . import lagrange
import random
import sqlite3
import os.path
from . import models


print('have a try')
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir))
db_name = "db.sqlite3"

conn = sqlite3.connect(db_path + "/" + db_name)

conn.commit()



player_list = []
column_set = ['id', 'rank', 'group_id', 'is_commander', 'position_x', 'position_y',
                       'public_key', 'private_key', 'mill_rand', 'mill_prime',
                       'room_id', 'user_id', 'rsa_n', 'vote_to', 'box_key_x','box_key_y',
                       'position']
unreachable_map_point = []

def read_unreachable_map_point():
    positions = [line.strip().split() for line in open('main/forbiddenCoord.txt').readlines()]
    for position in positions:
        unreachable_map_point.append((int(position[0]), int(position[1])))

read_unreachable_map_point()

def constraint_check(attribute, value):
    '''
    :param attribute: name of the column
    :param value: value of the column
    :return: whether the value matches the constraints of attribute
    '''
    if(attribute not in column_set):
        print('No such attribute')
        return False

    if(attribute == 'rank'):
        return (value >= 1 and value <= 19)
    elif(attribute == 'room_id'):
        return (value >= 0 and value <= 3)
    elif(attribute == 'position'):
        flag = ((value[0], value[1]) not in unreachable_map_point)
        return (flag and value[0] >= 1 and value[0] <= 23 and value[1] >= 1 and value[1] <= 23)
    elif(attribute == 'mill_rand' or attribute == 'mill_prime'):
        return (value != None and value != "")
    else:
        return True


def set_player_attribute(player_id, attribute, updated_value, value_type):
    '''
    :param player_id: id of the updated player
    :param attribute: the attribute to update
    :param updated_value: new value of the attribute
    :param value_type: type of the value,
            three of them should be specified: string, bool
    :return: true if successful otherwise false
    '''
    if (attribute not in column_set):
        print('No such attribute')
        return False
    if (not constraint_check(attribute, updated_value)):
        print('Invalid updated value {}'.format(updated_value))
        return False


    # check if player with player_id exists in main_users
    cursor = conn.execute("select count(*) from \"main_users\" where id = {}".format(player_id))
    conn.commit()
    count = cursor.fetchall()[0][0]
    if(count != 1):
        if(count == 0):
            print('No such player')
        else:
            print('{} player with the same id {}. So return None'.format(count, player_id))
        return False
    else:
        # set the value of the attribute of player with player_id
        if(value_type == 'bool'):
            if(updated_value == 'TRUE' or updated_value == 'True' or updated_value == 'true'):
                statement = 'UPDATE main_users SET {}=1 where id={}'.format(attribute, player_id)
            else:
                statement = 'UPDATE main_users SET {}=0 where id={}'.format(attribute, player_id)
        elif(value_type == 'string'):
            statement = 'UPDATE main_users SET {}=\"{}\" where id={}'.format(attribute, updated_value, player_id)
        elif(value_type == 'position'):
            statement = 'UPDATE main_users SET position_x={}, position_y={} where id={}'.format(updated_value[0], updated_value[1], player_id)
        else:
            statement = 'UPDATE main_users SET {}={} where id={}'.format(attribute, updated_value, player_id)
        print(statement)
        cursor = conn.execute(statement)
        conn.commit()
        return True

def get_player_attribute(player_id, attribute = '*'):
    '''
    :param player_id: id of the searched player
    :param attribute: the attribute you want to find
    :return: value of attribute if found otherwise None
    '''

    if(attribute not in column_set):
        print('No such attribute')
        return None

    statement = "select {} from \"main_users\" where id = {}".format(attribute, player_id)
    cursor = conn.execute(statement)
    conn.commit()
    rows = cursor.fetchall()
    if(len(rows) == 0):
        print("No such player")
        return None
    elif(len(rows) == 1):
        return rows[0][0]
    else:
        print('{} player with the same id {}. So return None'.format(len(rows), player_id))
        return None

def print_all_player_status():
    cursor = conn.execute("select * from \"main_users\"")
    conn.commit()
    rows = cursor.fetchall()
    for row in rows:
        print(row)

def print_all_box_status():
    cursor = conn.execute("select * from \"main_box\"")
    conn.commit()
    rows = cursor.fetchall()
    for row in rows:
        print(row)

'''
def initialize_player(count = 5):

    # generate {count} number of rsa keys
    rsa_list = rsa.get_RSAKeyList(1024, count)
    # generate millionaire data
    # To be Done #

    statement = "INSERT INTO main_users VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?) "

    player_list = []
    # generate players and save to player_list
    for i in range(count):
        id = i
        rank = random.randint(1, 20) # [1, rank_num ]
        group_id = i # To be investigated

        is_commander = False

        position_x = random.randint(0, map_bound_x)
        position_y = random.randint(0, map_bound_y)

        public_key = str(rsa_list[i]['puk'][1])
        private_key = str(rsa_list[i]['prk'][1])

        mill_rand = "temp" # To be investigated
        mill_prime = "tempaswell" # To be investigated

        room_id = random.randint(1, 4) # To be investigated
        user_id = str(i) # To be investigated

        rsa_n = str(rsa_list[i]['puk'][0])
        vote_to = -1
        player = (id, rank, group_id, is_commander, position_x, position_y,
                       public_key, private_key, mill_rand, mill_prime,
                       room_id, user_id, rsa_n, vote_to)
        player_list.append(player)

    conn.executemany(statement, player_list)
    conn.commit()
'''

'''
def initialize_box(count = 5):
    statement = "INSERT INTO main_box VALUES(?,?,?,?) "

    box_list = []

    # generate boxes and save to box_list
    for i in range(count):
        id = i

        password = "temp"

        position_x = random.randint(0, map_bound_x)
        position_y = random.randint(0, map_bound_y)

        box = (id, password, position_x, position_y)
        box_list.append(box)

    conn.executemany(statement, box_list)
    conn.commit()
'''

def initialize_rank():
    # initialize rank
    for i in range(1, 6):
        user = models.Users.objects.get(id=i)
        if (user.rank == -1):
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


def initialize_lagrange():
    num = 5  # create num keys
    least_num = 3  # at least least_num keys can open the box

    password, keys = lagrange.create_lagrange_key(40, num, least_num)

    models.Box.objects.password = password
    for i in range(1, 6):
        user = models.Users.objects.get(id=i)
        user.box_key_x = keys[i-1][0]
        user.box_key_y = keys[i-1][1]


def initialize_mill():
    for i in range(1, 6):
        mill_rand = str(random.getrandbits(233))
        mill_prime = "temp"

        set_player_attribute(i, 'mill_rand', mill_rand, 'string')
        set_player_attribute(i, 'mill_prime', mill_prime, 'string')

def initialize_position():
    # initialize position
    for i in range(1, 6):
        position_x = random.randint(1, 24)
        position_y = random.randint(1, 24)
        while (not constraint_check('position', (position_x, position_y))):
            position_x = random.randint(1, 24)
            position_y = random.randint(1, 24)
        set_player_attribute(i, 'position', (position_x, position_y), 'position')

def change_system_status():
    statement = 'UPDATE main_systemparam SET intValue=1'
    conn.execute(statement)
    conn.commit()

def check_system_status():
    global_state=models.SystemParam.objects.get(key="global_status")
    return global_state.intValue != 0
    #statement = "select intValue from main_systemparam"
    #cursor = conn.execute(statement)
    #conn.commit()
    #rows = cursor.fetchall()
    #return (int(rows[0][0]) != 0)

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

    if(not check_system_status()):
        initialize()
    player_id = player_id - 1
    position_list = []
    for i in range(1, 6):
        position_x = get_player_attribute(i, 'position_x')
        position_y = get_player_attribute(i, 'position_y')
        position_list.append((position_x, position_y))

    user_name_list = ['pangzaiyu', 'yangyinuo', 'xujunzhou', 'gaoming', 'panhainan']
    res_dict = {}
    other_player = {}
    for i in range(0, 5):
        if(i != player_id):
            info = {}
            info['position'] = [position_list[i][0], position_list[i][1]]
            info['known'] = 0
            other_player[user_name_list[i]] = info
    res_dict['player'] = user_name_list[player_id]
    res_dict['position'] = [position_list[player_id][0], position_list[player_id][1]]
    res_dict['other_players'] = other_player
    return json.dumps(res_dict)


if __name__ == '__main__':
    # print(unreachable_map_point)
    # initialize()
    print(check_system_status())

