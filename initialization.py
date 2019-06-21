import rsa
import random
import prime
import time
import re
import sqlite3
import sqlite3
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "main\\db.sqlite3")

print(db_path)

conn = sqlite3.connect("D:\\git_project\\pubgsite\\db.sqlite3")

conn.commit()



player_list = []

# set bound of map
map_bound_x = 100
map_bound_y = 100
rank_num = 19 #0-18
room_num = 4 #0-3

class Player:
    def __init__(self, id, rank, group_id, position, private_key, public_key,
                 mill_rand, mill_prime, room_id, user_id, is_commander=False):
        self.id = id
        self.rank = rank
        self.group_id = group_id
        self.is_commander = is_commander
        self.position_x = position[0]
        self.position_y = position[1]
        self.private_key = private_key
        self.public_key = public_key
        self.mill_rand = mill_rand
        self.mill_prime = mill_prime
        self.room_id = room_id
        self.user_id = user_id

    def get_id(self):
        return self.id

    def get_position(self):
        return [self.position_x, self.position_y]

    def set_position(self, position):
        self.position_x = position[0]
        self.position_y = position[1]

    def print_info(self):
        print('The player has id {} user_id {} and rank {}'.format(self.id, self.user_id, self.rank))
        print('He\She has group_id {} and room_id {}'.format(self.group_id, self.room_id))
        print('His\Her private key is {}'.format(self.private_key))
        print('His\Her public key is {}'.format(self.public_key))
        print('His\Her millionaire random is {}'.format(self.mill_rand))
        print('His\Her millionaire prime is {}'.format(self.mill_prime))
        print('He\She has position {:4.2f} and {:4.2f}\n'.format(self.position_x, self.position_y))

class Box:
    def __init__(self, id, password, position):
        self.id = id
        self.password = password
        self.position_x = position[0]
        self.position_y = position[1]



def random_position(map_bound_x, map_bound_y):
    '''
    :param map_bound_x: horizontal bound of the map ( [) )
    :param map_bound_y: vertical bound of the map ( [) )
    :return: randomly generated position with format [x, y]
    '''
    position_x = random.randint(0, map_bound_x)
    position_y = random.randint(0, map_bound_y)
    return [position_x, position_y]

def set_player_position(player_id, updated_position):
    '''
    :param player_id: id of the updated player
    :param updated_position: has format [x, y]
    :return: true if successful otherwise false
    '''
    if(updated_position[0] > map_bound_x or updated_position[1] > map_bound_y):
        print('Position out of map bound')
        return False

    for player in player_list:
        if(player.get_id() == player_id):
            player.set_position(updated_position)
            return True
    return False

def get_player_position(player_id):
    '''
    :param player_id: id of the searched player
    :return: [x, y] if found otherwise None
    '''
    for player in player_list:
        if(player.get_id() == player_id):
            return player.get_position()
    return None

def print_all_player_status():
    cursor = conn.execute("select * from \"main_users\"")
    conn.commit()
    rows = cursor.fetchall()
    print(rows)

def insert_player_to_database():
    statement = "INSERT INTO main_users VALUES(?,?,?,?,?,?,?,?,?,?,?,?) "
    data = []
    for player in player_list:
        single_data = (player.id, player.rank, player.group_id, player.is_commander,
                       player.position_x, player.position_y,
                       player.public_key, player.private_key,
                       player.mill_rand, player.mill_prime,
                       player.room_id, player.user_id)
        data.append(single_data)
    conn.executemany(statement, data)
    conn.commit()

def initialize(count = 5):
    '''initialize {count} players and save to player_list'''

    # generate {count} number of rsa keys
    rsa_list = rsa.get_RSAKeyList(1024, count)



    # generate players and save to player_list
    for i in range(count):


        id = i
        rank = random.randint(0, rank_num) # [0, rank_num - 1]
        group_id = i # every player has unique group_id when initialized

        position = random_position(map_bound_x, map_bound_y)

        mill_rand = None
        mill_prime = None

        room_id = random.randint(0, room_num)
        user_id = None

        is_commander = False

        player = Player(id=i, rank=rank, group_id=group_id,
                        position=position,
                        private_key=rsa_list[i]['prk'], public_key=rsa_list[i]['puk'],
                        mill_rand=mill_rand, mill_prime=mill_prime,
                        room_id=room_id, user_id=user_id, is_commander=is_commander)
        player_list.append(player)


if __name__ == '__main__':
    initialize(5)
    insert_player_to_database()
    print_all_player_status()
    set_player_position(3,[2,3])
    print_all_player_status()
    print(get_player_position(3))
    print(get_player_position(1))
    print(get_player_position(6))