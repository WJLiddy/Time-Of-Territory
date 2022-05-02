"""Accepts inputs and updates the world state. You can peek through this file, but it's not necessary."""

""" engine.py will not run with any renderer"""
""" engine.py -r will run the python renderer"""
""" engine.py -rd will run the python renderer (with a delay so it's easier to see)"""
""" engine.py -u will run in unity mode (you should not need to call this)"""

# ENGINE v0.2

from perlin import PerlinNoiseFactory
import random, sys, os, time, copy, json, subprocess
from stats import *
import orjson
##!! QUICK REFERENCE !!##

# resources:
# t - tree
# g - gold

# units:
# v - villager
# i - infantry
# c - cavalry
# a - archer

# buildings
# b - barracks (trains i),
# r - range (trains a)
# s - stable (trains c)
# w - toWnhall (trans v)
# h - house (needed for pop)
# (buildings take up multiple tiles, but all share the same ID and hp)

# orders
# m - move
# k - kill
# f - fix
# p - produce
# u - upgrade units (max lvl 3)
# pass the building ID to build.

# process(game_state, players) called every tick to accept your moves.

##!! GAME STATE !!##


# unitID is the ID returned from the game_state
# command is either "k", "f", "m", "p", "u", or "e"
# target is either an ID or a list of coordinates.

# m => move to tile [x,y]. Must be only one tile away. Diagonals okay. For cavalry, issue two of these commands. 
# [unitId, "m", [0,1]] would move unitID down and right one tile.

# k => attack a unit, building, or resource, must be adjacent (diagonals ok) or within range if archer.
# [unitId, "k", target] where unitId and target are IDs. peasants should speciify the ID of a resource if they want to harvest.

# f => fix building named unitID. Must be only one tile away. Peasants only.
# [unitId, "f", buildingID] will add 1 HP to building ID every tick.

# (b,r,s,t,h) => construct building named unitID. Must be only one tile away. Peasants only.
# [unitId, "b", [0,0]] will start work on a barracks with the top left corner at [0,0]
# this only creates the base of the building, "fix" must be called on each subsequent frame.

# p => produce a unit, can only be called on buildings. If the building is already producing nothing happens.
# [unitId, "p", nil] would produce a villager if unitID is a townhall.

# u => buy upgrade, only applicable to barracks, range, and stable. If all upgrades are maxed out, nothing happens.
# [unitId, "u", nil] would buy an upgrade if unitID is a barracks.



# generation params
# what freq of perlin noise to use for trees.
# lower generally better, (but less grouped trees)
PERLIN_TREE_SCALE = 0.1 
# how many trees to generate. 0 = 50/50 trees.
PERLIN_TREE_THRESH = 0.15
# how big is the initial spawn area.
SPAWN_ZONE = 8
# how many gold deposits to try to place
GOLD_DEPOSITS = 128

LEGAL_MOVES = [[-1,0],[0,-1],[1,0],[0,1],[-1,-1],[-1,1],[1,-1],[1,1]]

SKEL_TICKS = [0,4,8,16,32,64,128]

SKEL_MAX = 256
# idmax
ID_MAX = 2 ** 30

# map size
MAP_SIZE = 96

def generate_ID(generated):
    val = random.randint(0,ID_MAX)
    while(val in generated):
        val = random.randint(0,ID_MAX)
    generated.add(val)
    return val 

# generate the initial condition.
# size must be divisible by two.
# reviewed
def gen_world(size,seed):
    if(seed is not None):
        random.seed(seed)
    
    pnf = PerlinNoiseFactory(2, octaves=2)
    new_world_state = []
    new_players = []
    new_generated = set()

    # first, we begin by generating NONEs for the whole world.
    for x in range(size):
        xl = []
        for y in range(size):
            xl.append(None)
        new_world_state.append(xl)

    # then, we generate one corner. This generates a first pass at trees.
    for x in range(size//2):
        for y in range(size//2):
            if(pnf(x/(PERLIN_TREE_SCALE * size),y/(PERLIN_TREE_SCALE * size)) > PERLIN_TREE_THRESH):
                new_world_state[x][y] = {"type":"t","hp":TREE_HEALTH,"team":-1,"id":-1}

    # put gold down where we can.
    cur_deposits = GOLD_DEPOSITS
    while (cur_deposits >= 0):
        x = random.randint(0,size//2)
        y = random.randint(0,size//2)
        if(new_world_state[x][y] == None):
            new_world_state[x][y] = {"type":"g","hp":GOLD_HEALTH,"team":-1,"id":-1}
        cur_deposits -= 1

    # then, create the spawn area.
    for x in range(SPAWN_ZONE):
        for y in range(SPAWN_ZONE):
            new_world_state[x][y] = None

    # now, create all four corners of the world.
    for x in range(size//2):
        for y in range(size//2):
            new_world_state[size-1-x][y] = copy.deepcopy(new_world_state[x][y])
            new_world_state[size-1-x][size-1-y] = copy.deepcopy(new_world_state[x][y])
            new_world_state[x][size-1-y] = copy.deepcopy(new_world_state[x][y])

    # generate IDs for every entity in the world.
    for x in range(size):
        for y in range(size):
            if(new_world_state[x][y] != None):
                new_world_state[x][y]["id"] = generate_ID(new_generated)

    # finally, spawn initial players.
    new_world_state[1][1] = {"type":"v","hp":VIL_HEALTH,"team":0,"id":generate_ID(new_generated)}
    new_world_state[SPAWN_ZONE-1][SPAWN_ZONE-1] = {"type":"i","hp":INF1_HEALTH,"team":0,"id":generate_ID(new_generated)}
    new_players.append({"cav_level":1,"inf_level":1,"arc_level":1,"gold":0,"wood":TOWNHALL_COST+HOUSE_COST})

    new_world_state[size-2][size-2] ={"type":"v","hp":VIL_HEALTH,"team":1,"id":generate_ID(new_generated)}
    new_world_state[size + -(SPAWN_ZONE)][size + -(SPAWN_ZONE)] = {"type":"i","hp":INF1_HEALTH,"team":1,"id":generate_ID(new_generated)}
    new_players.append({"cav_level":1,"inf_level":1,"arc_level":1,"gold":0,"wood":TOWNHALL_COST+HOUSE_COST})

    new_world_state[size-2][1] = {"type":"v","hp":VIL_HEALTH,"team":2,"id":generate_ID(new_generated)}
    new_world_state[size + -(SPAWN_ZONE)][SPAWN_ZONE-1] ={"type":"i","hp":INF1_HEALTH,"team":2,"id":generate_ID(new_generated)}
    new_players.append({"cav_level":1,"inf_level":1,"arc_level":1,"gold":0,"wood":TOWNHALL_COST+HOUSE_COST})

    new_world_state[1][size-2] = {"type":"v","hp":VIL_HEALTH,"team":3,"id":generate_ID(new_generated)}
    new_world_state[SPAWN_ZONE-1][size + -(SPAWN_ZONE)] ={"type":"i","hp":INF1_HEALTH,"team":3,"id":generate_ID(new_generated)}
    new_players.append({"cav_level":1,"inf_level":1,"arc_level":1,"gold":0,"wood":TOWNHALL_COST+HOUSE_COST})

    return new_world_state, new_players, new_generated

# reviewed
def adjacent_building_locs(building_size, xoff, yoff):
    locs = []
    for x_adj in range(-1,building_size+1):
        for y_adj in range(-1,building_size+1):
            if((x_adj < 0 or x_adj == building_size) or (y_adj < 0 or y_adj == building_size)):
                locs.append([xoff+x_adj,yoff+y_adj])
    return locs

# reviewed
def occupied(world_state, x, y, size):
    for dx in range(x, x + size):
        for dy in range(y, y + size):
            if(dx < 0 or dy < 0 or dx >= len(world_state) or dy >= len(world_state)):
                return True
            if(world_state[dx][dy] != None):
                return True
    return False

# reviewed
def player_spawn_area(world_state,idx):
    if(idx == 0):
        return [0,0]
    if(idx == 1):
        return [len(world_state)-1,len(world_state)-1]
    if(idx == 2):
        return [len(world_state)-1,0]
    if(idx == 3):
        return [0,len(world_state)-1]
    raise Exception("Invalid player index.")

# reviewed
def get_spawn_locs(world_state, xoff, yoff, building_size, player_idx):
    locs = []
    for loc in adjacent_building_locs(building_size, xoff, yoff):
        if(occupied(world_state, loc[0], loc[1], 1)):
            continue
        locs.append(loc)

    spawnloc = player_spawn_area(world_state,player_idx)
    locs = sorted(locs, key=lambda x: pow(spawnloc[0] - x[0],2) + pow(spawnloc[1] - x[1],2))
    return locs

# reviewed
def handle_production(commands,world_state,players,emap, ex_moves):
  for c in commands:
        if(c["command"] == "p"):
            # try to produce something. (check if emap because it might have been killed.)
            if((c["id"] in emap) and emap[c["id"]][1]["type"] in ["r","s","b","w"]):
                building = emap[c["id"]]
                team = building[1]["team"]
                enough_gold = players[team]["gold"] >= production_cost(building[1]["type"])[0]
                enough_wood = players[team]["wood"] >= production_cost(building[1]["type"])[1]
                enough_pop = countpop(world_state,team) < countpopcap(world_state,team)

                if(building[1]["traintime"] == 0 and enough_gold and enough_wood and enough_pop):
                    # we can train something
                    players[team]["gold"] -= production_cost(building[1]["type"])[0]
                    players[team]["wood"] -= production_cost(building[1]["type"])[1]
                    building[1]["traintime"] = PRODUCTION_TIME + 1

# reviewed
def handle_upgrades(commands,world_state,players,emap, ex_moves):
  for c in commands:
        if(c["command"] == "u"):
            if((c["id"] in emap) and emap[c["id"]][1]["type"] in ["r","s","b"]):

                # get the params
                building = emap[c["id"]]
                team = building[1]["team"]

                # string for category
                upgrade_cat = upgrade_for_building(building[1]["type"])

                gold_cost = production_cost(building[1]["type"])[0] * UPGRADE2_MULT
                wood_cost = production_cost(building[1]["type"])[1] * UPGRADE2_MULT

                if(players[team][upgrade_cat] == 2):
                    gold_cost = production_cost(building[1]["type"])[0] * UPGRADE3_MULT
                    wood_cost = production_cost(building[1]["type"])[1] * UPGRADE3_MULT

                if(players[team][upgrade_cat] == 3):
                    gold_cost = 1000000000
                    wood_cost = 1000000000

                enough_gold = players[team]["gold"] >= gold_cost
                enough_wood = players[team]["wood"] >= wood_cost

                if(enough_gold and enough_wood):
                    # we can produce something.
                    players[team]["gold"] -= gold_cost
                    players[team]["wood"] -= wood_cost
                    players[team][upgrade_cat] += 1

# reviewed
def in_range(attackerid,defenderid,emap,world_state):
    atk_coord = emap[attackerid][0]
    def_coords = [emap[defenderid][0]]

    # if the defender is a building, we expand the list of valid targets. (emap returns top left.)
    if(is_building(emap[defenderid][1]["type"])):
        for dx in range(building_size(emap[defenderid][1]["type"])):
            for dy in range(building_size(emap[defenderid][1]["type"])):
                def_coords.append([def_coords[0][0]+dx,def_coords[0][1]+dy])

    for def_coord in def_coords:
        if(emap[attackerid][1]["type"] == "a"):
            if((abs(atk_coord[0] - def_coord[0]) + abs(atk_coord[1] - def_coord[1])) <= ARC_RANGE):
                return True
        elif (abs(atk_coord[0] - def_coord[0]) <= 1) and (abs(atk_coord[1] - def_coord[1]) <= 1):
            return True

    return False

# reviewed
def handle_kills(commands, world_state, players, emap, ex_moves):
    for c in commands:
        if(c["command"] == "k"):
            if((c["id"] in emap) and (c["arg"] in emap) and is_unit(emap[c["id"]][1]["type"]) and in_range(c["id"],c["arg"],emap,world_state) and (c["id"] != c["arg"])):
                ex_moves.append(c)
                attacker = emap[c["id"]]
                defender = emap[c["arg"]]
                a_power = attack_power(attacker[1]["type"], attacker[1]["team"], players)
                defender[1]["hp"] -= a_power
                if(attacker[1]["type"] == "v" and defender[1]["type"] == "t"):
                    players[attacker[1]["team"]]["wood"] += 1
                if(attacker[1]["type"] == "v" and defender[1]["type"] == "g"):
                    players[attacker[1]["team"]]["gold"] += 1

    # clean up anything that died.
    for x in range(len(world_state)):
        for y in range(len(world_state[x])):
            if(world_state[x][y] is not None and world_state[x][y]["hp"] <= 0):
                # if a building was destroyed, we only need to remove from emap once.
                if world_state[x][y]["id"] in emap:
                    del emap[world_state[x][y]["id"]]
                world_state[x][y] = None

# reviewed
def handle_construction(commands, world_state, players, emap, generated, ex_moves):
    for c in commands:
        if(is_building(c["command"])):
            # try to buy.
            # make sure unit exists/still alive, and is a peasant.
            if(c["id"] in emap and emap[c["id"]][1]["type"] == "v"):
                builder = emap[c["id"]][1]
                builder_loc = emap[c["id"]][0]
                loc = c["arg"]
                build_site_ok = not occupied(world_state, loc[0], loc[1], building_size(c["command"]))
                builder_pos_ok = builder_loc in adjacent_building_locs(building_size(c["command"]), loc[0], loc[1])
                # is this an ok build site and are close enough to the build site?
                if(build_site_ok and builder_pos_ok):
                    # do we have the money?
                    if(players[builder["team"]]["wood"] >= building_cost(c["command"])):
                        # are we adjancent to the build site?
                        # build went through, valid site and enough money.
                        ex_moves.append(c)
                        players[builder["team"]]["wood"] -= building_cost(c["command"])
                        bld_base = {"constructed": False, "traintime": 0, "type":c["command"],"hp":max_building_health(c["command"]) / 2,"team":builder["team"],"id":generate_ID(generated)}
                        for x in range(building_size(c["command"])):
                            for y in range(building_size(c["command"])):
                                world_state[loc[0] + x][loc[1] + y] = bld_base

# reviewed
# emap not accurate anymore after this for moved units -> does this cause problems?
def handle_movement(commands, world_state, players, emap, ex_moves):
    moves_issued_count = 1
    moves_already_issued = {}
    while(moves_issued_count > 0):
        moves_issued_count = 0
        for c in commands:
            unit_exists = c["id"] in emap and is_unit(emap[c["id"]][1]["type"])
            unit_is_cav = c["id"] in emap and emap[c["id"]][1]["type"] == "c"
            # move if we haven't moved before OR we moved once already and we're a cavalry.
            if(c["command"] == "m" and c["arg"] in LEGAL_MOVES and ((c["id"] not in moves_already_issued) or (moves_already_issued[c["id"]] == 1 and unit_is_cav))):
                # make sure unit exists/still alive
                if(unit_exists):
                    unit_loc = emap[c["id"]][0]
                    unit_targ = [unit_loc[0] + c["arg"][0], unit_loc[1] + c["arg"][1]]
                    # move to an empty space if we can.
                    if(not occupied(world_state,unit_targ[0],unit_targ[1],1)):
                        # move is valid, so move it.
                        world_state[unit_loc[0]][unit_loc[1]] = None
                        world_state[unit_targ[0]][unit_targ[1]] = emap[c["id"]][1]

                        if(c["id"] not in moves_already_issued):
                            moves_already_issued[c["id"]] = 0
                        
                        moves_already_issued[c["id"]] += 1
                        emap[c["id"]] = (unit_targ, emap[c["id"]][1])
                        moves_issued_count += 1
                        ex_moves.append(c)

# reviewed
def handle_repairs(commands, world_state, players, emap, ex_moves):
    for c in commands:
        if(c["command"] == "f"):
            # make unit is a peasant that is still alive and building is also still alive.
            if((c["id"] in emap) and (emap[c["id"]][1]["type"] == "v") and (c["arg"] in emap) and is_building(emap[c["arg"]][1]["type"])):
                ex_moves.append(c)
                builder = emap[c["id"]][1]
                building = emap[c["arg"]][1]
                # build went through, fix
                building["hp"] += 1
                if(building["hp"] == max_building_health(building["type"])):
                    building["constructed"] = True
                building["hp"] = min(building["hp"], max_building_health(building["type"]))

# reviewed
def game_over(world_state, team_idx):
    # check if game is over.
    for x in range(len(world_state)):
        for y in range(len(world_state[x])):
            if(world_state[x][y] is not None and world_state[x][y]["team"] == team_idx):
                return False
    return True

# reviewed
def upkeep(world_state, players, generated):
    seen_buildings = set()
    # this will always reach the top left of a building first.
    for x in range(len(world_state)):
        for y in range(len(world_state)):
            if(world_state[x][y] is not None and is_building(world_state[x][y]["type"]) and (not world_state[x][y]["id"] in seen_buildings)):
                seen_buildings.add(world_state[x][y]["id"])
                if(world_state[x][y]["traintime"] == 1):
                    # train unit.
                    type_to_make = production_for_building(world_state[x][y]["type"])
                    loc = get_spawn_locs(world_state, x, y, building_size(world_state[x][y]["type"]), world_state[x][y]["team"])
                    if(len(loc) > 0):
                        new_unit = {"type":type_to_make,"hp":health_for_unit(type_to_make,world_state[x][y]["team"],players),"team":world_state[x][y]["team"],"id":generate_ID(generated)}
                        world_state[loc[0][0]][loc[0][1]] = new_unit
                world_state[x][y]["traintime"] = max(world_state[x][y]["traintime"]-1,0)

    # check for game ends.
    survival_map = []
    for i in range(len(players)):
        survival_map.append(not game_over(world_state, i))
    return survival_map

# get rid of duplicate commands and also get rid of commands that control other players.
def legal_commands(commands, emap):
    legal_commands = []
    ids_ordered = {}
    for c in commands:
        # unit exists...
        if(c["id"] in emap):
            # unit is on the senders' team...
            if(emap[c["id"]][1]["team"] == c["team"]):
                # unit has not been ordered already, or unit is a stacked move.
                if((c["id"] not in ids_ordered) or (c["command"] == "m" and ids_ordered[c["id"]] == "m")):
                    legal_commands.append(c)
                    ids_ordered[c["id"]] = c["command"]
    return legal_commands

def command_valid(command):
    # command wasn't a dict
    if(not isinstance(command,dict)):
        return False
    # command was missing an argument
    if(not "arg" in command or not "id" in command or not "command" in command):
        return False
    # command id was not int or command was not string
    if(not isinstance(command["id"], int) or not isinstance(command["command"], str)):
        return False

    # arg was not a coordinate when it needed to be.
    if(is_building(command["command"]) or command["command"] == "m"):
        if(not isinstance(command["arg"], list) or len(command["arg"]) != 2):
            return False
        if(not isinstance(command["arg"][0], int) or not isinstance(command["arg"][1], int)):
            return False

    # arg was not an ID when it needed to be.
    if(command["command"] == "k" or command["command"] == "f"):
        if(not isinstance(command["arg"], int)):
            return False
    
    return True

def countpop(world_state, team):
    pop = 0
    buildings_counted = set()
    for x in range(len(world_state)):
        for y in range(len(world_state[x])):
            if(world_state[x][y] is not None and is_unit(world_state[x][y]["type"]) and world_state[x][y]["team"] == team):
                pop += 1
            if(world_state[x][y] is not None and is_building(world_state[x][y]["type"]) and world_state[x][y]["team"] == team and world_state[x][y]["traintime"] > 0 and world_state[x][y]["id"] not in buildings_counted):
                pop += 1
                buildings_counted.add(world_state[x][y]["id"])
    return pop

def countpopcap(world_state,team):
    pop = 0
    for x in range(len(world_state)):
        for y in range(len(world_state[x])):
            if(world_state[x][y] is not None and world_state[x][y]["type"] in ["h","w"] and world_state[x][y]["constructed"] and world_state[x][y]["team"] == team):
                pop += 1
    return pop

# make unit map that maps IDs to the unit and the position of that unit.
# returns a list => [0] is coord [1] is unit itself.
def emap_from_worldstate(world_state):
    emap = {}
    for x in range(len(world_state)):
        for y in range(len(world_state[x])):
            if(world_state[x][y] is not None and (not world_state[x][y]["id"] in emap)):
                emap[world_state[x][y]["id"]] = ([x,y], world_state[x][y])
    return emap

def add_to_discovered(world_state,discovered,player_idx):
    for x in range(len(world_state)):
        for y in range(len(world_state)):
            if(world_state[x][y] is not None and world_state[x][y]["team"] == player_idx):
                for dx in range(-LINE_OF_SIGHT,1+LINE_OF_SIGHT):
                    for dy in range(-LINE_OF_SIGHT,1+LINE_OF_SIGHT):
                        if((abs(dx) + abs(dy)) <= LINE_OF_SIGHT and (x+dx) >= 0 and (y+dy) >= 0 and (x+dx) < len(world_state) and (y+dy) < len(world_state)):
                            idx = ((dy+y) * len(world_state)) + (dx+x)
                            discovered.add(idx)

def mask_with_discovered(world_state,discovered):
    for x in range(len(world_state)):
        for y in range(len(world_state)):
            idx = (y * len(world_state)) + x
            if(idx not in discovered):
                world_state[x][y] = "u"
    return world_state


def spawn_skeletons_for_area(world_state,region_start,region_end,idx,count,new_generated):
    coords = []
    for x in range(region_start[0],region_end[0]):
        for y in range(region_start[1],region_end[1]):
            if(world_state[x][y] is None):
                coords.append([x,y])
    
    spawnloc = player_spawn_area(world_state,idx)

    sortedcoords = sorted(coords, key=lambda x: pow(spawnloc[0] - x[0],2) + pow(spawnloc[1] - x[1],2))
    sortedcoords.reverse()
    # now we have the sorted coords.
    # spawn them in the middle of the map, by max distance from spawn.
    for i in range(count):
        if(i == len(sortedcoords)):
            # no more room on the map (shouldn't happen)
            return
        
        s  = {"type":"a","hp":ARC1_HEALTH,"team":-2,"id":generate_ID(new_generated)}
        world_state[sortedcoords[i][0]][sortedcoords[i][1]] = s

def spawn_skeletons(world_state,tick,new_generated):
    to_spawn = 0
    if(tick > 3000 and (tick % 100) == 0):
        to_spawn = SKEL_MAX
    elif((tick % 500) == 0):
        to_spawn = SKEL_TICKS[tick // 500]

    if(to_spawn > 0):
        spawn_skeletons_for_area(world_state,[0,0],[len(world_state)//2,len(world_state)//2],0,to_spawn,new_generated)
        spawn_skeletons_for_area(world_state,[len(world_state)//2,len(world_state)//2],[len(world_state),len(world_state)],1,to_spawn,new_generated)
        spawn_skeletons_for_area(world_state,[len(world_state)//2,0],[len(world_state),len(world_state)//2],2,to_spawn,new_generated)
        spawn_skeletons_for_area(world_state,[0,len(world_state)//2],[len(world_state)//2,len(world_state)],3,to_spawn,new_generated)

def sign(x):
    if(x == 0):
        return 0
    if(x > 0):
        return 1
    return -1

def skele_moves(world_state):
    moves = []
    for x in range(len(world_state)):
        for y in range(len(world_state[x])):
            if(world_state[x][y] is not None and world_state[x][y]["type"] == "a" and world_state[x][y]["team"] == -2):

                # scan for attackers, we pick one randonmly
                targets = []
                for dx in range(-ARC_RANGE,1+ARC_RANGE):
                    for dy in range(-ARC_RANGE,1+ARC_RANGE):
                        if((abs(dx) + abs(dy)) <= ARC_RANGE and (x+dx) >= 0 and (y+dy) >= 0 and (x+dx) < len(world_state) and (y+dy) < len(world_state)):
                            if(world_state[x+dx][y+dy] is not None and world_state[x+dx][y+dy]["team"] >= 0):
                                targets.append([x+dx,y+dy])


                # pick a target randomly if one in range
                if(len(targets) > 0):
                    targ = random.choice(targets)
                    c = {"command":"k","id":world_state[x][y]["id"],"arg":world_state[targ[0]][targ[1]]["id"]}
                    moves.append(c)
                    continue

                modulo = len(world_state) // 2
                # use the ID to choose the move spot for skeles
                x_idx = world_state[x][y]["id"] % modulo
                y_idx = (world_state[x][y]["id"] // modulo) % modulo

                # zero out one of the values.
                if((x_idx + y_idx) % 2 == 0):
                    x_idx = 0
                else:
                    y_idx = 0


                if(x >= modulo):
                    x_idx = len(world_state)-1-x_idx

                if(y >= modulo):
                    y_idx = len(world_state)-1-y_idx

                
                # x_idx, y_idx this is where the skele should go.

                step = [sign(x_idx - x),sign(y_idx - y)]
                if(x == x_idx and y == y_idx):
                    continue
                
                if(world_state[x+step[0]][y+step[1]] is not None and world_state[x+step[0]][y+step[1]]["team"] != -2):
                    c = {"command":"k","id":world_state[x][y]["id"],"arg":world_state[x+step[0]][y+step[1]]["id"]}
                    moves.append(c)
                else:
                    c = {"command":"m","id":world_state[x][y]["id"],"arg":step}
                    moves.append(c)

    return moves


def process(commands, world_state, players, tick, generatedIDs, ex_moves):

    emap = emap_from_worldstate(world_state)

    # first, we need to parse commands. 
    # assert every command has correct arguments: id, command, arg and has right data type
    valid_commands = filter(command_valid, commands)

    # check to make sure commands don't cheat, and remove duplicates.
    l_commands = legal_commands(valid_commands, emap)
    
    # Now, sort by ID, (low ID gets executed first)
    sorted_commands = sorted(l_commands, key=lambda x: x["id"])

    # add skeleton moves (always last)
    sorted_commands.extend(skele_moves(world_state))

    # K=> Handle any K's first, these are attacks and they should be excecuted no matter what.
    handle_kills(sorted_commands, world_state, players, emap, ex_moves)

    # (b,r,s,t,h)=> Now, handle construction.
    handle_construction(sorted_commands,world_state,players,emap,generatedIDs, ex_moves)

    # F=> After that, see if any repairs go through.
    handle_repairs(sorted_commands,world_state,players,emap, ex_moves)

    # M=> Move any and all units.
    handle_movement(sorted_commands,world_state,players,emap, ex_moves)

    # p=> Now, handle training.
    handle_production(sorted_commands,world_state,players,emap, ex_moves)

    # p=> Now, handle upgrades
    handle_upgrades(sorted_commands,world_state,players,emap, ex_moves)

    # upkeep ->do productions,detect wins, spawn skeletons.
    teams_alive = upkeep(world_state, players, generatedIDs)

    if(teams_alive.count(True) == 1):
        # stop, game is over.
        return teams_alive.index(True)

    # finally, spawn skeletons if we can.
    spawn_skeletons(world_state,tick,generatedIDs)
    
    # game still going
    return False

def remove_team(t,world_state):
    for x in range(len(world_state)):
        for y in range(len(world_state)):
            if(world_state[x][y] is not None and world_state[x][y]["team"] == t):
                world_state[x][y] = None

def new_game(ais, seed, shuffle):
    world_state, players, generatedIDs = gen_world(MAP_SIZE,seed)

    if(shuffle):
        random.shuffle(ais)
    # delete players with no AI.
    for i in range(4):
        if(ais[i] is None):
            ais[i] = None
            remove_team(i,world_state)

    player_discovery = [set(),set(),set(),set()]

    return  world_state, players, generatedIDs, player_discovery

def jsoncopy(d):
    return orjson.loads(orjson.dumps(d))

def strip_team_info(players, target_idx):
    for i in range(4):
        if(i != target_idx and players[i] != None):
            del players[i]["wood"]
            del players[i]["gold"]
    return players