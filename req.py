import logic
import time
import requests

myCode = 948914
#if a game is already started --> otherwise uncomment
gameId = 150
baseUrl = "http://192.168.191.239:"
port = "8080"
urlMake, urlMove, urlHoney, urlEnergy, urlSkip = [baseUrl + port + x for x in ['/train/makeGame', '/train/move', '/train/convertNectarToHoney', '/train/feedBeeWithNectar', '/train/skipATurn']]
GameurlMake, GameurlMove, GameurlHoney, GameurlEnergy, GameurlSkip = [baseUrl + port + x for x in ['/makeGame', '/move', '/convertNectarToHoney', '/feedBeeWithNectar', '/skipATurn']]
NUM_ROWS, NUM_COLUMNS = 27, 9
def makeMove(gameId, direction, distance):
    dict = {"gameId": gameId,
            "playerId": myCode,
            "direction": direction,
            "distance": distance
    }
    r = requests.post(url=urlMove, json=dict)
    return r.json()

def joinGame(url, gameId, playerId):

    url += f'/joinGame?playerId={playerId}&gameId={gameId}'
    r = requests.get(url = url)
    return r.json()

def skipTurn(gameId):
    dict = {"gameId": gameId,
            "playerId": myCode
    }
    r = requests.post(url=urlSkip, json=dict)
    return r.json()

def convertNectarToHoney(gameId, honey):
    dict = {"gameId": gameId,
            "playerId": myCode,
            "amountOfHoneyToMake": honey
    }
    r = requests.post(url=urlHoney, json=dict)
    return r.json()

def convertNectarToEnergy(gameId, nectar):
    dict = {"gameId": gameId,
            "playerId": myCode,
            "amountOfNectarToFeedWith": nectar
    }
    r = requests.post(url=urlEnergy, json=dict)
    return r.json()

def makeGame(playerId, playerSpot):
    dict = {'playerId': playerId,
            'playerSpot': playerSpot}
    r = requests.post(url=urlMake, json=dict)
    return r.json()


#executes the turn given a dictionary which contains the needed info
def executeTurn(turn):
    if turn['type'] == 'move':
        return makeMove(gameId, turn['direction'], turn['distance'])
    elif turn['type'] == 'convertNectarToHoney':
        return convertNectarToHoney(gameId, turn['amountOfHoneyToMake'])
    elif turn['type'] == 'convertNectarToEnergy':
        return convertNectarToEnergy(gameId, turn['amountOfNectarToFeedWith'])
    elif turn['type'] == 'skip':
        return skipTurn(gameId)


def gamemakeMove(gameId, direction, distance):
    dict = {"gameId": gameId,
            "playerId": myCode,
            "direction": direction,
            "distance": distance
    }
    r = requests.post(url=GameurlMove, json=dict)
    return r.json()

def gameskipTurn(gameId):
    dict = {"gameId": gameId,
            "playerId": myCode
    }
    r = requests.post(url=GameurlSkip, json=dict)
    return r.json()

def gameconvertNectarToHoney(gameId, honey):
    dict = {"gameId": gameId,
            "playerId": myCode,
            "amountOfHoneyToMake": honey
    }
    r = requests.post(url=GameurlHoney, json=dict)
    return r.json()

def gameconvertNectarToEnergy(gameId, nectar):
    dict = {"gameId": gameId,
            "playerId": myCode,
            "amountOfNectarToFeedWith": nectar
    }
    r = requests.post(url=GameurlEnergy, json=dict)
    return r.json()




#executes the turn given a dictionary which contains the needed info
def gameexecuteTurn(turn):
    if turn['type'] == 'move':
        return gamemakeMove(gameId, turn['direction'], turn['distance'])
    elif turn['type'] == 'convertNectarToHoney':
        return gameconvertNectarToHoney(gameId, turn['amountOfHoneyToMake'])
    elif turn['type'] == 'convertNectarToEnergy':
        return gameconvertNectarToEnergy(gameId, turn['amountOfNectarToFeedWith'])
    elif turn['type'] == 'skip':
        return gameskipTurn(gameId)


#class for a tile
class Tile:
    def __init__(self, data):
        self.row = data['row']
        self.column = data['column']
        self.itemType = data['tileContent']['itemType']
        self.numOfItems = data['tileContent']['numOfItems']

    def print_tile(self):
        print(str(self.row) + " " + str(self.column) + " " + str(self.itemType) + " " + str(self.numOfItems))

#pulls the tile from the json
def tiles(r, row, col):
    map = r['map']['tiles']
    for el in map[row]:
        if el['column'] == col:
            return el



if __name__ == "__main__":
    URL = 'http://192.168.191.239:8080'
    game = joinGame(URL, gameId, myCode)
    #gameId = game["gameId"]
    print(f"Starting game with id {gameId}..")
    worldMap = [[Tile(tiles(game, i, j)) for j in range(9)] for i in range(27)]
    prev_b_nec = 1000
    ind = 0

    player = 'player1'
    opponent = 'player2'
    
    HIVE_X, HIVE_Y = (0, 0) if player == 'player1' else (26, 8)

    while True:
        print("Player x, y, energy, nectar: ", game[player]['x'], game[player]['y'], game[player]["energy"], game[player]["nectar"])

        if ind < 60 and game[player]["nectar"] >= 90 and  game[player]['x'] == HIVE_X and game[player]['y'] == HIVE_Y:
            print("Getting honey.")
            game = gameconvertNectarToHoney(gameId, 4)
        
        elif ind >= 60 and game[player]["nectar"] >= 90 and  game[player]['x'] == HIVE_X and game[player]['y'] == HIVE_Y:
            print("Getting honey")
            game = gameconvertNectarToHoney(gameId, 3)


        elif game[player]["nectar"] != 0 and  game[player]['x'] == HIVE_X and game[player]['y'] == HIVE_Y and game[player]["energy"] < 99:
            print("Getting energy.")
            game = gameconvertNectarToEnergy(gameId, min((100 - game[player]["energy"]) // 2,  game[player]["nectar"]))

        elif game[player]["nectar"] >= prev_b_nec:
            print("Going base")
            # ret to base
            ret_path = logic.shortest_path_to_base(game[player]['x'], game[player]['y'], game[player]['energy'], game[player]['nectar'], worldMap, NUM_ROWS, NUM_COLUMNS, HIVE_X, HIVE_Y, game["player2"]["x"], game["player2"]["y"])

            print(ret_path)
            game = gameexecuteTurn(ret_path[0])
        else:
            print("Getting nectar")
            # best_line

            bline, b_nec = logic.best_line(game[player]['x'], game[player]['y'], game[player]['energy'], game[player]['nectar'], worldMap, NUM_ROWS, NUM_COLUMNS, game["player2"]["x"], game["player2"]["y"])
            print(bline)
            prev_b_nec = b_nec
            game = gameexecuteTurn(bline[0])

        if "map" not in game:
            # game finished
            print(game)
            break

        worldMap = [[Tile(tiles(game, i, j)) for j in range(9)] for i in range(27)]
        ind += 1
        # time.sleep(1)
    print(f"Game finished at turn {ind}")