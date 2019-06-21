import rsa
import random
import prime
import time
import re
import sqlite3
import sqlite3
import os.path


db_path = os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir))
db_name = "db.sqlite3"

conn = sqlite3.connect(db_path + "\\" + db_name)

conn.commit()



player_list = []
column_set = ['id', 'rank', 'group_id', 'is_commander', 'position_x', 'position_y',
                       'public_key', 'private_key', 'mill_rand', 'mill_prime',
                       'room_id', 'user_id', 'rsa_n', 'vote_to']
unreachable_map_point = []

# set bound of map
map_bound_x = 100
map_bound_y = 100

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
    elif(attribute == 'position_x'):
        return (value >= 0 and value <= map_bound_x)
    elif(attribute == 'position_y'):
        return (value >= 0 and value <= map_bound_y)
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
        return None
    if (not constraint_check(attribute, updated_value)):
        print('Invalid updated value {}'.format(updated_value))


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

def initialize_player(count = 5):
    '''initialize {count} players and save to player_list'''

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

def initialize():
    # initialize rank
    for i in range(1, 6):
        rank = get_player_attribute(i, 'rank')
        if(rank == -1):
            set_player_attribute(i, 'rank', random.randint(1, 20), 'int')

    # initialize RSA
    rsa_list = rsa.get_RSAKeyList(1024, 5)
    for i in range(1, 6):
        public_key = str(rsa_list[i-1]['puk'][1])
        private_key = str(rsa_list[i-1]['prk'][1])
        rsa_n = str(rsa_list[i-1]['puk'][0])

        set_player_attribute(i, 'public_key', public_key, 'string')
        set_player_attribute(i, 'private_key', private_key, 'string')
        set_player_attribute(i, 'rsa_n', rsa_n, 'string')

    # initialize MILL
    for i in range(1, 6):
        mill_rand = str(random.getrandbits(233))
        mill_prime = "temp"

        set_player_attribute(i, 'mill_rand', mill_rand, 'string')
        set_player_attribute(i, 'mill_prime', mill_prime, 'string')

    # initialize lagrange



    position_list = []
    for i in range(1, 6):
        position_x = get_player_attribute(i, 'position_x')
        position_y = get_player_attribute(i, 'position_y')
        position_list.append((position_x, position_y))



if __name__ == '__main__':
    initialize()
