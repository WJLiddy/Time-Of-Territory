import sys
from engine import *
from render import *
import orjson

#===============================================================================
#===============================================================================
""" Use this file to test development of your AI."""

"""First, add your imports here"""
import ai.goldpls.goldpls as goldpls
import ai.random.random as random
import ai.russian.russian as russian
import ai.archbtw.archbtw as archbtw
import ai.horseradish.horseradish as horseradish

"""Second, set up who's playing in the match. Must have four items. (None is okay)"""
PLAYERS = [russian, horseradish, goldpls, archbtw]

"""Third, set the seed (optional, but None will generate a random one)"""
SEED = None

""" Then just run engine.py. Arguments you can supply:"""
""" Engine.py : Runs the game as fast as possible, prints only the tick count. """
""" Engine.py -r : Draws game state"""
""" Engine.py -f0 : Show only what first AI can see."""
""" Engine.py -f1 : Show only what second AI can see."""
""" Engine.py -f2 : Show only what third AI can see."""
""" Engine.py -f3 : Show only what fourth AI can see."""
""" Engine.py -d : Adds a delay which makes the game run slower, may work well with the renderer so you can visualize"""
""" Engine.py -s : Randomly reorders the AI (this will be used in competition)."""

#===============================================================================
#===============================================================================

print_game = "-r" in sys.argv
delay = "-d" in sys.argv
shuffle = "-s" in sys.argv
FOW1 = "-f0" in sys.argv
FOW2 = "-f1" in sys.argv
FOW3 = "-f2" in sys.argv
FOW4 = "-f3" in sys.argv

def play():
    world_state, players, generatedIDs, player_discovery = new_game(PLAYERS, SEED, shuffle)
    FOW_to_render = [FOW1,FOW2,FOW3,FOW4]

    tick = 0
    while(True):
        collated_orders = []

        for i in range(4):
            if(PLAYERS[i] is not None):
                add_to_discovered(world_state,player_discovery[i],i)
                masked = mask_with_discovered(jsoncopy(world_state),player_discovery[i])
                for c in PLAYERS[i].run(masked,strip_team_info(jsoncopy(players),i),i):
                    c["team"] = i
                    collated_orders.append(c)

        ex_moves = []
        result = process(collated_orders,world_state,players,tick,generatedIDs, ex_moves)
        if(not(result is False)):
            print("Game ended.")
            print(result)
            break

        print("tick:", tick)

        if(print_game):
            disp_world_state = jsoncopy(world_state)
            mask = set()
            for i in range(4):
                if(FOW_to_render[i]):
                    mask = mask.union(player_discovery[i])
            if(len(mask) > 0):
                disp_world_state = mask_with_discovered(disp_world_state,mask)
            
            # Clear screen based on terminal (windows terminals have cls, others have clear)
            os.system('cls||clear')
            print(players)
            render(disp_world_state)
        sys.stdout.flush()
        if(delay):
            time.sleep(1)
            
        tick += 1

play()
