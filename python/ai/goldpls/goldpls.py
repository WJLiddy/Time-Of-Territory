"""build a townhall on first turn and just harvest as much gold as possible. 
BUT IT GETS CRAZY: have one peasant cut trees and build houses. 
difficulty: babby plus"""
from ai.shitutils import *

def name():
    return "goldpls"

# a few compound commands.

# this moves to a suitable building location and builds it.
# send the peasant's ID and coords and the building type to build => and the peasant will build your thing somewhere close-ish.
# make sure you have enough resources to do this.
def move_and_build(id,x,y,world_state,b):
    bsize = 3
    
    if(b == "h"):
        bsize = 2
    
    build_site = find_good_buildsite(world_state,x,y,bsize)
    
    if(build_site == None):
        return {} # empty command.
    
    if (abs(x - build_site[0]) <= 1 and abs(y - build_site[1]) <= 1):
        return {"id":id,"command":b,"arg":build_site}
    else:
        dest = path_to_coord([x,y],world_state,build_site)
        if(dest != None):
            return {"id":id,"command":"m","arg":[dest[0]-x,dest[1]-y]}
    return {}

# any building that is not completed, this peasant will fix.
def do_construction(id,x,y,world_state):
    pdir = path_to([x,y],world_state,lambda x: (x is not None) and x != "u" and (x["type"] in ["w","r","s","b","h"]) and (not x["constructed"]))

    if((pdir is not None) and world_state[pdir[0]][pdir[1]] is None):
        return {"id":id,"command":"m","arg":[pdir[0] - x ,pdir[1] - y]}

    if((pdir is not None) and not world_state[pdir[0]][pdir[1]]["constructed"]):
        return {"id":id,"command":"f","arg":world_state[pdir[0]][pdir[1]]["id"]}

    return {}

def first_peasant_routine(p,world_state,players,team_idx):
    # start building a house if we can.
    if(players[team_idx]["wood"] > 30):
        return move_and_build(p["id"],p["x"],p["y"],world_state,"h")
    # do construction if there's anything unfinished.
    elif do_construction(p["id"],p["x"],p["y"],world_state) != {}:
        return do_construction(p["id"],p["x"],p["y"],world_state)
    # otherwise cut trees.
    else:
        pdir = path_to([p["x"],p["y"]],world_state,lambda x: x is not None and x != "u" and x["type"] == "t")

        if((pdir is not None) and world_state[pdir[0]][pdir[1]] is None):
            return {"id":p["id"],"command":"m","arg":[pdir[0] - p["x"] ,pdir[1] - p["y"]]}

        if((pdir is not None) and world_state[pdir[0]][pdir[1]]["type"] == "t"):
            return {"id":p["id"],"command":"k","arg":world_state[pdir[0]][pdir[1]]["id"]}
    
    return {}

def run(world_state,players,team_idx):
    # get a list of all our duders
    my_peasants = get_tiles(world_state,lambda x: x["team"] == team_idx and x["type"] == "v")
    my_townhall = get_tiles(world_state,lambda x: x["team"] == team_idx and x["type"] == "w")
    my_houses = get_tiles(world_state,lambda x: x["team"] == team_idx and x["type"] == "h")
    
    # first turn, only have one unit, build a townhall
    if(len(my_townhall) == 0 and len(my_peasants) == 1):
        return [move_and_build(my_peasants[0]["id"],my_peasants[0]["x"],my_peasants[0]["y"],world_state,"w")]

    # build townhall if it is not done.
    if(len(my_townhall) > 0 and len(my_peasants) == 1 and not my_townhall[0]["constructed"]):
        return [{"id":my_peasants[0]["id"],"command":"f","arg":my_townhall[0]["id"]}]

    # now we have a tc and a house.
    # first peasant cuts trees and builds houses. (but only if we have two villagers, someone needs to be on gold full time)
    # rest mine gold.
    commands = []
    if(len(my_peasants) > 1):
        commands.append(first_peasant_routine(my_peasants[0],world_state,players,team_idx))
        my_peasants.pop(0)

    # all peasants should harvest whatever is close to them
    for peasant in my_peasants[0:]:
        pdir = path_to([peasant["x"],peasant["y"]],world_state,lambda x: x is not None and x != "u" and x["type"] == "g")

        if(pdir == None): # no path to a gold, trees will do
            pdir = path_to([peasant["x"],peasant["y"]],world_state,lambda x: x is not None and x != "u" and x["type"] == "t")

        if(pdir == None): # no path to anything, return.
            continue

        # see if we can harvest anything.
        if(world_state[pdir[0]][pdir[1]] is None):
            commands.append({"id":peasant["id"],"command":"m","arg":[pdir[0] - peasant["x"] ,pdir[1] - peasant["y"]]})
        elif(world_state[pdir[0]][pdir[1]]["type"] in ["t","g"]):
            commands.append({"id":peasant["id"],"command":"k","arg":world_state[pdir[0]][pdir[1]]["id"]})
    
    # always train new peasants.
    if(len(my_townhall) > 0):
        commands.append({"id":my_townhall[0]["id"],"command":"p","arg":None})
    return commands

