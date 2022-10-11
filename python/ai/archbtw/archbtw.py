"""
Turtle. Protect vils with archers.
difficulty: easy but not TOO easy
"""

from ai.shitutils import *

ARC_RANGE = 8

def name():
    return "ArchBTW"

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

# take advatange of team index to build - always builds in same spot
# returns the build location and stand position (JOJO REFERENCE?)
def tcbldpair(idx,size):
    if(idx == 0):
        return [[0,0],[1,3]]
    if(idx == 1):
        return[[size-3,size-3],[size-2,size-4]]
    if(idx == 2):
        return[[size-3,0],[size-2,3]]
    if(idx == 3):
        return[[0,size-3],[1,size-4]]

# mine res1 if we can, otherwise, mine res2.
def peasant_routine(world_state,peasant,res1,res2):
    pdir = path_to([peasant["x"],peasant["y"]],world_state,lambda x: x is not None and x != "u" and x["type"] == res1)

    if(pdir == None):
        pdir = path_to([peasant["x"],peasant["y"]],world_state,lambda x: x is not None and x != "u" and x["type"] == res2)

    if(pdir == None): # no path to anything, return.
        return {}

    # see if we can harvest anything.
    if(world_state[pdir[0]][pdir[1]] is None):
        return {"id":peasant["id"],"command":"m","arg":[pdir[0] - peasant["x"] ,pdir[1] - peasant["y"]]}
    elif(world_state[pdir[0]][pdir[1]]["type"] in [res1,res2]):
        return {"id":peasant["id"],"command":"k","arg":world_state[pdir[0]][pdir[1]]["id"]}
    return {}

# mine res1 if we can, otherwise, mine res2.
def builder_routine(world_state,peasant,wood, needs_construction):
    if(needs_construction):
        constr_command = do_construction(peasant["id"],peasant["x"],peasant["y"],world_state)
        if(constr_command != {}):
            return constr_command

    # make sure we can support the population.
    if(countpop(world_state,peasant["team"]) > (-3 + getpopcap(world_state,peasant["team"]))):
        return move_and_build(peasant["id"],peasant["x"],peasant["y"],world_state,"h")

    if(wood < 70):
        return peasant_routine(world_state,peasant,"t","g")

    # no building required. we should build an archery range.
    return move_and_build(peasant["id"],peasant["x"],peasant["y"],world_state,"r")


# first - attack anyone in range.
# second - move to a position that is next to a peasant to protect them.
# may smother peasants with love but this is a shitAI using shitutils after all
def archer_command(world_state,archer):
    for dx in range(-ARC_RANGE,ARC_RANGE+1):
        for dy in range(-ARC_RANGE,ARC_RANGE+1):
            if(abs(dx) + abs(dy) <= ARC_RANGE and not (dx+archer["x"] < 0 or dx+archer["x"] >= len(world_state) or dy+archer["y"] < 0 or dy+archer["y"] >= len(world_state))):
                if(world_state[archer["x"] + dx][archer["y"] + dy] is not None and world_state[archer["x"] + dx][archer["y"] + dy] != "u"):
                    if (world_state[archer["x"] + dx][archer["y"] + dy]["team"] not in [-1,archer["team"]]):
                        id = archer["id"]
                        arg = world_state[archer["x"] + dx][archer["y"] + dy]["id"]
                        # attack this.
                        return {"id":id,"command":"k","arg":arg}
    
    # no danger.
    # move to the nearest peasant. (if it's an enemy peasant we will kill it lmao)
    cdir = path_to([archer["x"],archer["y"]],world_state, lambda x: x is not None and x != "u" and x["type"] == "v")

    # see if we can attack anything.
    if(cdir is not None):
        return {"id":archer["id"],"command":"m","arg":[cdir[0] - archer["x"] ,cdir[1] - archer["y"]]}
    return {}


def opening(world_state,players,team_idx,v0,tc):
    # copy pasted code suck my dick it's a sample
    if(len(tc) == 0):
        # see if we're at build site.
        if([v0["x"],v0["y"]] != tcbldpair(team_idx, len(world_state))[1]):
            to_w = path_to_coord([v0["x"],v0["y"]],world_state,tcbldpair(team_idx,len(world_state))[1])
            if(to_w is not None):
                return [{"id":v0["id"],"command":"m","arg":[to_w[0] - v0["x"],to_w[1] - v0["y"]]}]
        else:
            return [{"id":v0["id"],"command":"w","arg":tcbldpair(team_idx,len(world_state))[0]}]
    
    if(not tc[0]["constructed"]):
        return [{"id":v0["id"],"command":"f","arg":tc[0]["id"]}]
    return {}

def run(world_state,players,team_idx):
    # get a list of all our duders
    vils = get_tiles(world_state,lambda x: x["team"] == team_idx and x["type"] == "v")
    # crazy shit: sort the villagers so that their tasks are "somewhat" stable.
    # i.e. the first villager is usually always going to stay the same between frames.
    # if u read this you can steal it cause it's totally a good idea
    vils = sorted(vils,key=lambda x: x["id"])
    arcs = get_tiles(world_state,lambda x: x["team"] == team_idx and x["type"] == "a")
    infs = get_tiles(world_state,lambda x: x["team"] == team_idx and x["type"] == "i")
    hous = get_tiles(world_state,lambda x: x["team"] == team_idx and x["type"] == "h")
    rans = get_tiles(world_state,lambda x: x["team"] == team_idx and x["type"] == "r")
    tows = get_tiles(world_state,lambda x: x["team"] == team_idx and x["type"] == "w")

    needs_construction = False
    for x in world_state:
        for y in x:
            if(y is not None and y != "u" and y["team"] == team_idx and (y["type"] in ["w","r","b","s","h"]) and not y["constructed"]):
                needs_construction = True

    
    # opening (defined as one peasant, no finished TC)
    if(len(vils) == 1 and (len(tows) == 0 or not tows[0]["constructed"])):
       return opening(world_state,players,team_idx,vils[0],tows)

    # opening is done.
    commands = []

    # vil 0 always gets gold.
    if(len(vils) > 0):
        commands.append(peasant_routine(world_state,vils[0],"g","r"))

    # vil 1 is construction.
    if(len(vils) > 1):
        commands.append(builder_routine(world_state,vils[1],players[team_idx]["wood"],needs_construction))

    if(len(vils) > 2):
    # rest fetch based on ID.
        for v in vils[2:]:
            if(v["id"] % 2 == 0):
                commands.append(peasant_routine(world_state,v,"g","t"))
            else:
                commands.append(peasant_routine(world_state,v,"t","g"))

    # archers should ideally stand next to a peasant to protect them.
    for a in arcs:
        commands.append(archer_command(world_state,a))

    # infantry can use archer code too becuz lazy and also no time left
    for i in infs:
        commands.append(archer_command(world_state,i))

    if(len(tows) > 0):
        # always train peasants.
        commands.append({"id":tows[0]["id"],"command":"p","arg":None})

    for r in rans:
        # always train archers.
        commands.append({"id":r["id"],"command":"p","arg":None})

    # train archers if we can.
    return commands

