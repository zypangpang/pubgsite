import rsa
import random
import prime
import time
import re

player_list = []

# set bound of map
map_bound_x = 100
map_bound_y = 100
rank_total_num = 18

def random_position(map_bound_x, map_bound_y):
    '''
    :param map_bound_x: horizontal bound of the map ( [) )
    :param map_bound_y: vertical bound of the map ( [) )
    :return: randomly generated position with format [x, y]
    '''
    position_x = random.random() * map_bound_x
    position_y = random.random() * map_bound_y
    return [position_x, position_y]

def random_rank(rank_total_num):
    '''
    :param rank_total_num: total number of rank classes
    :return randomly generated rank ranging from 0 to rank_total_num( [] ):
    '''
    return int(random.random() * (rank_total_num + 1))

class Player:
    def __init__(self, id, rank, rsa_private, rsa_public, position):
        self.id = id
        self.rsa_private = rsa_private
        self.rsa_public = rsa_public
        self.position_x = position[0]
        self.position_y = position[1]

    def set_position(self, position):
        self.position_x = position[0]
        self.position_y = position[1]

    def get_id(self):
        return self.id

    def get_position(self):
        return [self.position_x, self.position_y]

    def print_info(self):
        print('The player has id {}'.format(self.id))
        print('His\Her private key is {}'.format(self.rsa_private))
        print('His\Her public key is {}'.format(self.rsa_public))
        print('He\She has position {:4.2f} and {:4.2f}\n'.format(self.position_x, self.position_y))

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
    print('Now printing status of all players')
    for player in player_list:
        player.print_info()

def initialize(count = 5):
    '''initialize {count} players and save to player_list'''

    # generate {count} number of rsa keys
    rsa_list = rsa.get_RSAKeyList(1024, count)

    # generate players and save to player_list
    for i in range(count):
        random_player = Player(i, rsa_list[i]['prk'], rsa_list[i]['puk'], random_position(map_bound_x, map_bound_y))
        player_list.append(random_player)


if __name__ == '__main__':
    initialize(5)
    print_all_player_status()
    set_player_position(3,[2,3])
    print_all_player_status()
    print(get_player_position(3))
    print(get_player_position(1))
    print(get_player_position(6))