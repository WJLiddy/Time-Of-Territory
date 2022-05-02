from stats import *
# render bs
TREE = '\033[32m'
GOLD = '\033[33m'
NORM = '\033[37m'
# teamcolors
teamcols = {
    -2: NORM,
    0: "\033[31m", # RED
    1: "\033[34m", # BLUE
    2: "\033[35m", # PURPLE
    3: "\033[36m", # CYAN
}
    
def render(world_state):
    # render the world
    for y in range(len(world_state)):
        for x in range(len(world_state[y])):
            if world_state[x][y] is not None:
                if(world_state[x][y] == "u"):
                    print(" ", end="")
                elif(world_state[x][y]["type"] == "t"):
                    print(TREE + world_state[x][y]["type"], end="")
                elif(world_state[x][y]["type"] == "g"):
                    print(GOLD + world_state[x][y]["type"], end="")
                elif(is_building(world_state[x][y]["type"]) and world_state[x][y]["constructed"]):
                    print(teamcols[world_state[x][y]["team"]] + world_state[x][y]["type"].upper(), end="")
                else:
                    print(teamcols[world_state[x][y]["team"]] + world_state[x][y]["type"], end="")
            else:
                print(NORM + ".", end="")
        print(NORM)