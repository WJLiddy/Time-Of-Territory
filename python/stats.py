"""game params and small helper methods"""

# health, attack of things
TREE_HEALTH = 50
GOLD_HEALTH = 250

VIL_HEALTH = 20
VIL_ATK = 1

INF1_HEALTH = 30
INF1_ATK = 2

INF2_HEALTH = 60
INF2_ATK = 3

INF3_HEALTH = 90
INF3_ATK = 4

ARC_RANGE = 8
ARC1_HEALTH = 25
ARC1_ATK = 1

ARC2_HEALTH = 35
ARC2_ATK = 2

ARC3_HEALTH = 45
ARC3_ATK = 3

CAV1_HEALTH = 45
CAV1_ATK = 3

CAV2_HEALTH = 90
CAV2_ATK = 4

CAV3_HEALTH = 135
CAV3_ATK = 5

# production costs
VIL_COST_GOLD = 10
VIL_COST_WOOD = 0

INF_COST_GOLD = 20
INF_COST_WOOD = 0

ARC_COST_GOLD = 10
ARC_COST_WOOD = 10

CAV_COST_GOLD = 40
CAV_COST_WOOD = 0

# production time
PRODUCTION_TIME = 15

# upgrade costs (base cost * level)
UPGRADE2_MULT = 10
UPGRADE3_MULT = 20

# building costs:
HOUSE_COST = 30
BARRACKS_COST = 50
RANGE_COST = 70
STABLE_COST = 90
TOWNHALL_COST = 200

# building hps:
HOUSE_HP = 40
BARRACKS_HP = 60
RANGE_HP = 60
STABLE_HP = 60
TOWNHALL_HP = 80

# line of sight
LINE_OF_SIGHT = 8

# probably easier to dump all this in a dict and return but eh, the damage is done

def max_building_health(building):
    if(building == "h"):
        return HOUSE_HP
    elif(building == "b"):
        return BARRACKS_HP
    elif(building == "r"):
        return RANGE_HP
    elif(building == "s"):
        return STABLE_HP
    elif(building == "w"):
        return TOWNHALL_HP
    else:
        raise Exception("HP: Invalid building type:" + building)

def building_size(building):
    if(building == "h"):
        return 2
    elif(building == "b"):
        return 3
    elif(building == "r"):
        return 3
    elif(building == "s"):
        return 3
    elif(building == "w"):
        return 3
    else:
        raise Exception("Size: Invalid building type:" + building)

def building_cost(unit):
    if(unit == "r"):
        return RANGE_COST
    elif(unit == "s"):
        return STABLE_COST
    elif(unit == "h"):
        return HOUSE_COST
    elif(unit == "b"):
        return BARRACKS_COST
    elif(unit == "w"):
        return TOWNHALL_COST
    raise Exception("Can't build " + unit)

def production_cost(building):
    if(building == "r"):
        return [ARC_COST_GOLD,ARC_COST_WOOD]
    if(building == "b"):
        return [INF_COST_GOLD,INF_COST_WOOD]
    if(building == "s"):
        return [CAV_COST_GOLD,CAV_COST_WOOD]
    if(building == "w"):
        return [VIL_COST_GOLD,VIL_COST_WOOD]

    raise Exception("Can't Produce at" + building)

def attack_power(unit,team,players):
    if(unit == "v"):
        return VIL_ATK
    if(unit == "i"):
        if(players[team]["inf_level"] == 1):
            return INF1_ATK
        if(players[team]["inf_level"] == 2):
            return INF2_ATK
        if(players[team]["inf_level"] == 3):
            return INF3_ATK
    if(unit == "a"):
        if(players[team]["arc_level"] == 1):
            return ARC1_ATK
        if(players[team]["arc_level"] == 2):
            return ARC2_ATK
        if(players[team]["arc_level"] == 3):
            return ARC3_ATK
    if(unit == "c"):
        if(players[team]["cav_level"] == 1):
            return CAV1_ATK
        if(players[team]["cav_level"] == 2):
            return CAV2_ATK
        if(players[team]["cav_level"] == 3):
            return CAV3_ATK
    raise Exception("Invalid unit type:" + unit)

def upgrade_for_building(building):
    if(building == "r"):
        return "arc_level"
    if(building == "b"):
        return "inf_level"
    if(building == "s"):
        return "cav_level"
    raise Exception("No upgrade for " + building)

def production_for_building(building):
    if(building == "r"):
        return "a"
    if(building == "b"):
        return "i"
    if(building == "s"):
        return "c"
    if(building == "w"):
        return "v"
    raise Exception("No production for " + building)

def health_for_unit(unit,team,players):
    if(unit == "v"):
        return VIL_HEALTH
    if(unit == "i"):
        if(players[team]["inf_level"] == 1):
            return INF1_HEALTH
        if(players[team]["inf_level"] == 2):
            return INF2_HEALTH
        if(players[team]["inf_level"] == 3):
            return INF3_HEALTH
    if(unit == "a"):
        if(players[team]["arc_level"] == 1):
            return ARC1_HEALTH
        if(players[team]["arc_level"] == 2):
            return ARC2_HEALTH
        if(players[team]["arc_level"] == 3):
            return ARC3_HEALTH
    if(unit == "c"):
        if(players[team]["cav_level"] == 1):
            return CAV1_HEALTH
        if(players[team]["cav_level"] == 2):
            return CAV2_HEALTH
        if(players[team]["cav_level"] == 3):
            return CAV3_HEALTH
    raise Exception("Invalid unit type:" + unit)

def is_unit(t):
    return t in ["v","i","a","c"]

def is_building(t):
    return t in ["h","b","r","s","w"]