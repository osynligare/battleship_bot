import argparse
import json
import os
import time
from random import choice

command_file = 'command.txt'
place_ship_file = 'place.txt'
game_state_file = 'state.json'
output_path = '.'
map_size = 0


def main(player_key):
    global map_size
    
    # state before
    if os.path.isfile('stateb.json'):
        with open('stateb.json', 'r') as inf:
            stateb = json.load(inf)

    # state now
    with open(os.path.join(output_path, game_state_file), 'r') as f_in:
        state = json.load(f_in)

    if state['Phase'] == 1:
        if os.path.isfile('stateb.json'):
            os.remove('stateb.json')
        if os.path.isfile('commandb.json'):
            os.remove('commandb.json')
        if os.path.isfile('tiles.json'):
            os.remove('tiles.json')
        if os.path.isfile('shieldhit.json'):
            os.remove('shieldhit.json')

    # write state to stateb.json
    with open('stateb.json', 'w') as outf:
        json.dump(state,outf)

    # command before
    if os.path.isfile('commandb.json'):
        with open('commandb.json', 'r') as inf:
            commandb = json.load(inf)
    else:
        commandb = [-1,-1,-1]
        
    map_size = state['MapDimension']
    
    # score every tiles
    temp = []
    for i in range(map_size):
        for j in range(map_size):
            if j==0:
                temp.append([])
            temp[len(temp)-1].append(2) 

    if not os.path.isfile('tiles.json'):
        with open('tiles.json', 'w') as outf:
            json.dump(temp,outf)

    with open('tiles.json', 'r') as inf:
        tiles = json.load(inf)

    if state['Phase'] == 1:
        place_ships()
    else:
        fire_shot(state, stateb, tiles, commandb)

def shipsAlive(ships):
    shipList = []     #list number avail command
    for i in range(5):
        if not ships[i]['Destroyed']:
            shipList.append(i)
    
    return shipList

def fireAvailable(state):
    command = [1]
    ships = shipsAlive(state['PlayerMap']['Owner']['Ships'])
    if 0 in ships:
        command.append(7)       #seeker missile
    if 1 in ships:
        command.append(2)       #double shot vertical
    if 2 in ships:
        command.append(6)       #diagonal cross shot
    if 3 in ships:
        command.append(3)       #corner shot horizontal
        command.append(4)       #corner shot
    if 4 in ships:
        command.append(5)       #horizontal cross shot

    return command

def output_shot(x, y, move):
    
    if move != 8:
        with open('commandb.json', 'w') as outf:
            com = [move,x,y]
            json.dump(com, outf)

    with open(os.path.join(output_path, command_file), 'w') as f_out:
        f_out.write('{},{},{}'.format(move, x, y))
        f_out.write('\n')
    pass

def resetAll(tiles, cellScore):
    for i in range(map_size):
        for j in range(map_size):
            if tiles[i][j] != 0:
                tiles[i][j] = 2
    for i in range(map_size):       # for missed tiles
        for j in range(map_size):
            if cellScore[i][j] == -1:
                if i==0:
                    if tiles[i+1][j] != 0:
                        tiles[i+1][j] = 1
                elif i==map_size-1:
                    if tiles[i-1][j] != 0:
                        tiles[i-1][j] = 1
                else:
                    if tiles[i+1][j] != 0:
                        tiles[i+1][j] = 1
                    if tiles[i-1][j] != 0:
                        tiles[i-1][j] = 1
                if j==0:
                    if tiles[i][j+1] != 0:
                        tiles[i][j+1] = 1
                elif j==map_size-1:
                    if tiles[i][j-1] != 0:
                        tiles[i][j-1] = 1
                else:
                    if tiles[i][j+1] != 0:
                        tiles[i][j+1] = 1
                    if tiles[i][j-1] != 0:
                        tiles[i][j-1] = 1

def missedTiles(tiles, cellScore):
    for i in range(map_size):       # for missed tiles
        for j in range(map_size):
            if cellScore[i][j] == -1:
                if i==0:
                    if tiles[i+1][j] != 0 and tiles[i+1][j] != 3:
                        tiles[i+1][j] = 1
                elif i==map_size-1:
                    if tiles[i-1][j] != 0 and tiles[i-1][j] != 3:
                        tiles[i-1][j] = 1
                else:
                    if tiles[i+1][j] != 0 and tiles[i+1][j] != 3:
                        tiles[i+1][j] = 1
                    if tiles[i-1][j] != 0 and tiles[i-1][j] != 3:
                        tiles[i-1][j] = 1
                if j==0:
                    if tiles[i][j+1] != 0 and tiles[i][j+1] != 3:
                        tiles[i][j+1] = 1
                elif j==map_size-1:
                    if tiles[i][j-1] != 0 and tiles[i][j-1] != 3:
                        tiles[i][j-1] = 1
                else:
                    if tiles[i][j+1] != 0 and tiles[i][j+1] != 3:
                        tiles[i][j+1] = 1
                    if tiles[i][j-1] != 0 and tiles[i][j-1] != 3:
                        tiles[i][j-1] = 1

def fire_shot(state, stateb, tiles, commandb):
    # To send through a command please pass through the following <code>,<x>,<y>
    
    move = 1
    opponent_map = state['OpponentMap']['Cells']
    map_size = state['MapDimension']

    cellScore = []
    
    for cell in opponent_map:       # give score on every tiles
        if cell['Y'] == 0:
            cellScore.append([])
        if not cell['Damaged'] and not cell['Missed']:
            cellScore[len(cellScore)-1].append(0) #-1=missed, 1=damaged
        elif cell['Damaged']:
            cellScore[len(cellScore)-1].append(1) #-1=missed, 1=damaged
        else: #cell missed
            cellScore[len(cellScore)-1].append(-1) #-1=missed, 1=damaged

    # open shieldhit
    if os.path.isfile('shieldhit.json'):
        with open('shieldhit.json', 'r') as inf:
            shield = json.load(inf)
        if shield['charge'] != 1:
            shield['charge'] -= 1
            os.remove('shieldhit.json')
            # rewrite ngurangin charge
            with open('shieldhit.json', 'w') as outf:
                json.dump(shield,outf)

    targets = []

    if commandb == [-1,-1,-1]:              # first time
        for i in range(map_size):
            for j in range(map_size):
                valid_cell = i, j
                targets.append(valid_cell)
    else:   
        x = commandb[1]
        y = commandb[2]

        Nship = 0
        for ship in state['OpponentMap']['Ships']:
            if not ship['Destroyed']:
                Nship += 1

        Nshipbef = 0
        for ship in stateb['OpponentMap']['Ships']:
            if not ship['Destroyed']:
                Nshipbef += 1

        print (Nship)
        print (Nshipbef)


        if Nship < Nshipbef:            # a ship is destroyed
            tiles[x][y] = 0
            resetAll(tiles, cellScore)
        else:
            if commandb[0] == 1:        # single shot
                if cellScore[x][y] == 1:        # damaged
                    tiles[x][y] = 0
                    if x!=0 and x!=map_size-1:
                        if cellScore[x+1][y] == 1:
                            if tiles[x-1][y] != 0:
                                tiles[x-1][y] = 5
                            if x+2<map_size:
                                if tiles[x+2][y]!=0:
                                    tiles[x+2][y] = 4
                        elif cellScore[x-1][y] == 1:
                            if tiles[x+1][y] != 0:
                                tiles[x+1][y] = 5
                            if x-2>=0:
                                if tiles[x-2][y]!=0:
                                    tiles[x-2][y] = 4
                        else:
                            if tiles[x+1][y] != 0:
                                tiles[x+1][y] = 3
                            if tiles[x-1][y] != 0:
                                tiles[x-1][y] = 3
                    else:
                        if x==0:
                            if tiles[x+1][y] != 0:
                                tiles[x+1][y] = 3
                        elif x==map_size-1:
                            if tiles[x-1][y] != 0:
                                tiles[x-1][y] = 3

                    if y!=0 and y!=map_size-1:
                        if cellScore[x][y+1] == 1:
                            if tiles[x][y-1] != 0:
                                tiles[x][y-1] = 5
                            if y+2<map_size:
                                if tiles[x][y+2]!=0:
                                    tiles[x][y+2] = 4
                        elif cellScore[x][y-1] == 1:
                            if tiles[x][y+1] != 0:
                                tiles[x][y+1] = 5
                            if y-2>=0:
                                if tiles[x][y-2]!=0:
                                    tiles[x][y-2] = 4
                        else:
                            if tiles[x][y+1] != 0:
                                tiles[x][y+1] = 3
                            if tiles[x][y-1] != 0:
                                tiles[x][y-1] = 3
                    else:
                        if y==0:
                            if tiles[x][y+1] != 0:
                                tiles[x][y+1] = 3
                        elif y==map_size-1:
                            if tiles[x][y-1] != 0:
                                tiles[x][y-1] = 3
                elif cellScore[x][y] == -1:         # missed
                    tiles[x][y] = 0
                    if x==0:
                        if tiles[x+1][y] != 0:
                            tiles[x+1][y] = 1
                    elif x==map_size-1:
                        if tiles[x-1][y] != 0:
                            tiles[x-1][y] = 1
                    else:
                        if tiles[x+1][y] != 0:
                            tiles[x+1][y] = 1
                        if tiles[x-1][y] != 0:
                            tiles[x-1][y] = 1
                    if y==0:
                        if tiles[x][y+1] != 0:
                            tiles[x][y+1] = 1
                    elif y==map_size-1:
                        if tiles[x][y-1] != 0:
                            tiles[x][y-1] = 1
                    else:
                        if tiles[x][y+1] != 0:
                            tiles[x][y+1] = 1
                        if tiles[x][y-1] != 0:
                            tiles[x][y-1] = 1
                elif cellScore[x][y] == 2:          # shielded
                    resetAll(tiles, cellScore)
                    tiles[x][y] = -1
                    shieldDict = {
                        'charge' : (state['Round']/7) % 3,
                        'X' : x,
                        'Y' : y
                        }

                    if not os.path.isfile('shieldhit.json'):
                        with open('shieldhit.json', 'w') as outf:
                            json.dump(shieldDict, outf)

            elif (commandb[0] == 7):        # seeker shot
                opponent_mapb = stateb['OpponentMap']['Cells']
                cellScoreb = []
                
                for cell in opponent_mapb:       # give score on every tiles
                    if cell['Y'] == 0:
                        cellScoreb.append([])
                    if not cell['Damaged'] and not cell['Missed']:
                        cellScoreb[len(cellScoreb)-1].append(0) #-1=missed, 1=damaged
                    elif cell['Damaged']:
                        cellScoreb[len(cellScoreb)-1].append(1) #-1=missed, 1=damaged
                    else: #cell missed
                        cellScoreb[len(cellScoreb)-1].append(-1) #-1=missed, 1=damaged

                for i in range (map_size):
                    for j in range (map_size):
                        if (cellScore[i][j] != cellScoreb[i][j]):
                            x = i
                            y = j
                            break

                changeTiles(tiles,cellScore,map_size,x,y)

            elif (commandb[0] == 2):
                opponent_mapb = stateb['OpponentMap']['Cells']
                cellScoreb = []
                
                for cell in opponent_mapb:       # give score on every tiles
                    if cell['Y'] == 0:
                        cellScoreb.append([])
                    if not cell['Damaged'] and not cell['Missed']:
                        cellScoreb[len(cellScoreb)-1].append(0) #-1=missed, 1=damaged
                    elif cell['Damaged']:
                        cellScoreb[len(cellScoreb)-1].append(1) #-1=missed, 1=damaged
                    else: #cell missed
                        cellScoreb[len(cellScoreb)-1].append(-1) #-1=missed, 1=damaged

                for i in range (map_size):
                    for j in range (map_size):
                        if (cellScore[i][j] != cellScoreb[i][j]):
                            x = i
                            y = j
                            changeTiles(tiles,cellScore,map_size,x,y)

    with open('tiles.json', 'w') as outf:
        json.dump(tiles,outf)

    print ('\n', tiles)
    #findMax
    max = 0

    for i in range(map_size):
            for j in range(map_size):
                if tiles[i][j] > max:
                    max = tiles[i][j]

    Nship = 0
    for ship in state['OpponentMap']['Ships']:
        if not ship['Destroyed']:
            Nship += 1

    if state['PlayerMap']['Owner']['Energy'] >= state['PlayerMap']['Owner']['Ships'][0]['Weapons'][1]['EnergyRequired'] and max <=2 and 7 in fireAvailable(state):
        move = 7
    elif (Nship == 1 or (not 0 in shipsAlive(state['PlayerMap']['Owner']['Ships']))) and state['PlayerMap']['Owner']['Energy'] >= state['PlayerMap']['Owner']['Ships'][1]['Weapons'][1]['EnergyRequired'] and max <=2 and 2 in fireAvailable(state):
        max = 1
        # for i in range(1, map_size-1):
        #     for j in range(1, map_size-1):
        #         if tiles[i][j] > max and tiles[i-1][j] != 0 and tiles[i+1][j] != 0:
        #             max = tiles[i][j]
        move = 2


    if os.path.isfile('shieldhit.json'):
        if shield['charge'] == 1:
            if max <= 2:
                os.remove('shieldhit.json')
                targets = shield['X'], shield['Y']
                if move == 2:
                    move = 1
    elif move !=2:
        for i in range(map_size):
            for j in range(map_size):
                if (tiles[i][j]==max):
                    valid_cell = i, j
                    targets.append(valid_cell)
    elif move == 2:
        for i in range(1, map_size-1):
            for j in range(1, map_size-1):
                if (tiles[i][j]==max) and (tiles[i][j-1] != 0 and tiles[i][j+1] != 0) and (tiles[i][j-1] == 2 or tiles[i][j+1] == 2):
                    valid_cell = i, j
                    targets.append(valid_cell)
    
    i = 0
    useShield = False
    if not state['PlayerMap']['Owner']['Shield']['Active'] and state['PlayerMap']['Owner']['Shield']['CurrentCharges'] > 1 :
        while not useShield and i<len(state['PlayerMap']['Cells']) :
            if state['PlayerMap']['Cells'][i]['Hit'] != stateb['PlayerMap']['Cells'][i]['Hit'] :
                if state['PlayerMap']['Cells'][i]['Occupied'] :
                    useShield = True
            i += 1

    target = choice(targets)
    print(target)
    if not useShield :
        output_shot(target[0], target[1], move)
    else :
        place_shield(state['PlayerMap']['Owner']['Ships'])
    return

def changeTiles(tiles,cellScore,map_size,x,y):
    tiles[x][y] = 0
    if cellScore[x][y] == 1:
        if x!=0 and x!=map_size-1:
            if cellScore[x+1][y] == 1:
                if tiles[x-1][y] != 0:
                    tiles[x-1][y] = 5
                if x+2<map_size:
                    if tiles[x+2][y]!=0:
                        tiles[x+2][y] = 4
            elif cellScore[x-1][y] == 1:
                if tiles[x+1][y] != 0:
                    tiles[x+1][y] = 5
                if x-2>=0:
                    if tiles[x-2][y]!=0:
                        tiles[x-2][y] = 4
            else:
                if tiles[x+1][y] != 0:
                    tiles[x+1][y] = 3
                if tiles[x-1][y] != 0:
                    tiles[x-1][y] = 3
        else:
            if x==0:
                if tiles[x+1][y] != 0:
                    tiles[x+1][y] = 3
            elif x==map_size-1:
                if tiles[x-1][y] != 0:
                    tiles[x-1][y] = 3

        if y!=0 and y!=map_size-1:
            if cellScore[x][y+1] == 1:
                if tiles[x][y-1] != 0:
                    tiles[x][y-1] = 5
                if y+2<map_size:
                    if tiles[x][y+2]!=0:
                        tiles[x][y+2] = 4
            elif cellScore[x][y-1] == 1:
                if tiles[x][y+1] != 0:
                    tiles[x][y+1] = 5
                if y-2>=0:
                    if tiles[x][y-2]!=0:
                        tiles[x][y-2] = 4
            else:
                if tiles[x][y+1] != 0:
                    tiles[x][y+1] = 3
                if tiles[x][y-1] != 0:
                    tiles[x][y-1] = 3
        else:
            if y==0:
                if tiles[x][y+1] != 0:
                    tiles[x][y+1] = 3
            elif y==map_size-1:
                if tiles[x][y-1] != 0:
                    tiles[x][y-1] = 3


    elif cellScore[x][y] == -1:
        if x==0:
            if tiles[x+1][y] != 0:
                tiles[x+1][y] = 1
        elif x==map_size-1:
            if tiles[x-1][y] != 0:
                tiles[x-1][y] = 1
        else:
            if tiles[x+1][y] != 0:
                tiles[x+1][y] = 1
            if tiles[x-1][y] != 0:
                tiles[x-1][y] = 1
        if y==0:
            if tiles[x][y+1] != 0:
                tiles[x][y+1] = 1
        elif y==map_size-1:
            if tiles[x][y-1] != 0:
                tiles[x][y-1] = 1
        else:
            if tiles[x][y+1] != 0:
                tiles[x][y+1] = 1
            if tiles[x][y-1] != 0:
                tiles[x][y-1] = 1

def place_shield(player_ships):
    shieldLoc = (0,0)

    for ship in player_ships :
        # shield is only applied to currently being damaged ship
        if not ship['Destroyed'] :
            # check the undestroyed ship whether the ship has taken any damage
            i = 0
            healthyShip = True
            while i<len(ship['Cells']) and healthyShip :
                healthyShip = not ship['Cells'][i]['Hit']
                i+=1
            
            # if the ship is being damaged, 
            # set the shield location target (shieldLoc) to a shipcell next to the damaged spot
            if not healthyShip :
                hitState = ship['Cells'][0]['Hit']
                j = 1
                while hitState == ship['Cells'][j]['Hit'] :
                    healthyShip = not ship['Cells'][j]['Hit']
                    j+=1     
                if hitState : shieldLoc = ship['Cells'][j-1]['X'], ship['Cells'][j-1]['Y']
                else : shieldLoc = ship['Cells'][j]['X'], ship['Cells'][j]['Y']
                break

    output_shot(shieldLoc[0], shieldLoc[1], 8)
    print (shieldLoc)

    return

def place_ships():
    # Please place your ships in the following format <Shipname> <x> <y> <direction>
    # Ship names: Battleship, Cruiser, Carrier, Destroyer, Submarine
    # Directions: north east south west

    ships = ['Battleship 9 0 north',
             'Destroyer 9 9 south',
             'Carrier 9 4 west',
             'Submarine 0 0 east',
             'Cruiser 0 9 south'
             ]

    with open(os.path.join(output_path, place_ship_file), 'w') as f_out:
        for ship in ships:
            f_out.write(ship)
            f_out.write('\n')
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('PlayerKey', nargs='?', help='Player key registered in the game')
    parser.add_argument('WorkingDirectory', nargs='?', default=os.getcwd(), help='Directory for the current game files')
    args = parser.parse_args()
    assert (os.path.isdir(args.WorkingDirectory))
    output_path = args.WorkingDirectory
    main(args.PlayerKey)
