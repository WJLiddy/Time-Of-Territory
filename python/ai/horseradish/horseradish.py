"""
Identical to russian, but trains cavalry
townhall
then-
alternate one vil and one inf. Send the inf to attack.
have a random peasant build a house if needed.
difficulty: toddler+"""
from ai.shitutils import *

def name():
    return "Hrsrdsh"

# take advatange of team index to build - always builds in same spot
# returns the build location and stand position (JOJO REFERENCE?)
def barbldpair(idx,size):
    if(idx == 0):
        return [[0,0],[1,3]]
    if(idx == 1):
        return[[size-3,size-3],[size-2,size-4]]
    if(idx == 2):
        return[[size-3,0],[size-2,3]]
    if(idx == 3):
        return[[0,size-3],[1,size-4]]

def houbldpair(idx,size):
    if(idx == 0):
        return [[3,0],[3,2]]
    if(idx == 1):
        return[[size-5,size-2],[size-4,size-3]]
    if(idx == 2):
        return[[size-5,0],[size-4,2]]
    if(idx == 3):
        return[[3,size-2],[3,size-3]]

# tries to mine gold. if can't mine gold, get trees. otherwise do nothing.
def try_mine_gold(world_state,peasant):
    pdir = path_to([peasant["x"],peasant["y"]],world_state,lambda x: x is not None and x != "u" and x["type"] == "g")

    if(pdir == None): # no path to a gold, trees will do
        pdir = path_to([peasant["x"],peasant["y"]],world_state,lambda x: x is not None and x != "u" and x["type"] == "t")

    if(pdir == None): # no path to anything, return.
        return {}

    # see if we can harvest anything.
    if(world_state[pdir[0]][pdir[1]] is None):
        return {"id":peasant["id"],"command":"m","arg":[pdir[0] - peasant["x"] ,pdir[1] - peasant["y"]]}
    elif(world_state[pdir[0]][pdir[1]]["type"] in ["t","g"]):
        return {"id":peasant["id"],"command":"k","arg":world_state[pdir[0]][pdir[1]]["id"]}
    return {}

def can_upgrade(cur_level,gold):
    if(cur_level == 1):
        return gold >= 400
    if(cur_level == 2):
        return gold >= 800
    return False

# attack anyone visible. if no one is visible, go to the opposing base.
def cav_rush(world_state,cav, enemy_exists):
    ret = []
    # attack anyone we see.
    cdir = None
    scout_dest = None
    if(enemy_exists):
        cdir = path_to([cav["x"],cav["y"]],world_state,lambda x: x is not None and x != "u" and x["team"] != cav["team"] and x["team"] != -1)
    if(cdir == None):
        # no one here. let's explore spawn locations.
        for v in range(4):
            scout_dest = barbldpair(v,len(world_state))[0]
            if(world_state[scout_dest[0]][scout_dest[1]] == "u" and cdir == None):
                cdir = path_to_coord([cav["x"],cav["y"]],world_state,scout_dest)
        if(cdir == None): # no path to anything, return.
            return {}

    # see if we can attack anything.
    if(world_state[cdir[0]][cdir[1]] is None):
        ret.append({"id":cav["id"],"command":"m","arg":[cdir[0] - cav["x"] ,cdir[1] - cav["y"]]})

        if(scout_dest != None):
            # move was good, can we move again?
            cdir2 = path_to_coord([cdir[0],cdir[1]],world_state,scout_dest)

            if(cdir2 is not None and world_state[cdir2[0]][cdir2[1]] is None):
                ret.append({"id":cav["id"],"command":"m","arg":[cdir2[0] - cdir[0] ,cdir2[1] - cdir[1]]})

    elif(world_state[cdir[0]][cdir[1]]["type"] is not None):
        ret.append({"id":cav["id"],"command":"k","arg":world_state[cdir[0]][cdir[1]]["id"]})
    return ret


def run(world_state,players,team_idx):
    # get a list of all our duders
    vs = get_tiles(world_state,lambda x: x["team"] == team_idx and x["type"] == "v")
    iz = get_tiles(world_state,lambda x: x["team"] == team_idx and x["type"] == "c")
    hs = get_tiles(world_state,lambda x: x["team"] == team_idx and x["type"] == "h")
    bs = get_tiles(world_state,lambda x: x["team"] == team_idx and x["type"] == "s")

    # check if enemies exist
    es = get_tiles(world_state,lambda x: x["team"] != team_idx and x["team"] != 1)
    
    # opening (defined as one peasant and we don't have all three buildings.)
    if(len(vs) == 1):
        v0 = vs[0]

        # copy pasted code suck my dick it's a sample
        if(len(bs) == 0):
            # see if we're at build site.
            if([v0["x"],v0["y"]] != barbldpair(team_idx, len(world_state))[1]):
                to_w = path_to_coord([v0["x"],v0["y"]],world_state,barbldpair(team_idx,len(world_state))[1])
                return [{"id":v0["id"],"command":"m","arg":[to_w[0] - v0["x"],to_w[1] - v0["y"]]}]
            else:
                return [{"id":v0["id"],"command":"s","arg":barbldpair(team_idx,len(world_state))[0]}]

        if(not bs[0]["constructed"]):
            return [{"id":v0["id"],"command":"f","arg":bs[0]["id"]}]

        if(len(hs) == 0):
            # see if we're at build site.
            # see if we're at build site.
            if([v0["x"],v0["y"]] != houbldpair(team_idx, len(world_state))[1]):
                to_w = path_to_coord([v0["x"],v0["y"]],world_state,houbldpair(team_idx,len(world_state))[1])
                return [{"id":v0["id"],"command":"m","arg":[to_w[0] - v0["x"],to_w[1] - v0["y"]]}]
            else:
                return [{"id":v0["id"],"command":"h","arg":houbldpair(team_idx,len(world_state))[0]}]

        if(not hs[0]["constructed"]):
            return [{"id":v0["id"],"command":"f","arg":hs[0]["id"]}]

    # opening is done.
    commands = []
    # all villagers get gold. (trees if no gold found).
    for v in vs:
        commands.append(try_mine_gold(world_state,v))

    for i in iz:
        commands.extend(cav_rush(world_state,i, len(es) > 0))

    if(len(bs) > 0):
        if(can_upgrade(players[team_idx]["inf_level"],players[team_idx]["gold"])):
            commands.append({"id":bs[0]["id"],"command":"u","arg":None})
            print("upgrading")
        else:
            commands.append({"id":bs[0]["id"],"command":"p","arg":None})
    return commands

