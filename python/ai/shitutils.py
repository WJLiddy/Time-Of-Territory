"""couple of shitty util functions for u"""
# they are short and sweet but shit and slow
# use if you want to

# coord -> int, used so we can put coord into a python set 
def coord_to_int(coord):
    return coord[0]*10000 + coord[1]

# true if OOB or the something is in the tile.
# unexplored tiles are considered open.
def occupied(x,y,world_state):
    return x < 0 or x >= len(world_state) or y < 0 or y >= len(world_state) or (world_state[x][y] is not None and world_state[x][y] != "u")

# true if oob or there's a building here.
# unexplored tiles are considered closed.
def oob_or_bld(x,y,world_state):
    return x < 0 or x >= len(world_state) or y < 0 or y >= len(world_state) or ((world_state[x][y] is not None) and (world_state[x][y] == "u" or (world_state[x][y]["type"] in ["b","r","w","h","s"])))

# returns the path to the nearest tile that has a clear path + satisfies the function.
# for example, if you want to find the nearest tree we can cut down, pass lambda l: l["type"] == "t"
# as this is a shitutil, if no tile satisfies the function, it will return None, and take most of your processing time doing it.
# it will also assume unexplored tiles are open.
def path_to(start,world_state, function):
    queue = [[start]]
    visited = set()
    while(len(queue) > 0):
        path = queue.pop(0)
        # if this is the dest, return the first step in the path. (path would return the whole path)
        if(function(world_state[path[-1][0]][path[-1][1]])):
            return path[1]
            
        if(coord_to_int(path[-1]) not in visited and ((path[-1] == start) or not occupied(path[-1][0],path[-1][1],world_state))):
            visited.add(coord_to_int(path[-1]))
            for x in [-1,0,1]:
                for y in [-1,0,1]:
                    # fix -1 index wrapping..
                    if((x != 0 or y != 0) and (path[-1][0]+x != -1) and (path[-1][1]+y != -1) and (path[-1][0]+x != len(world_state)) and (path[-1][1]+y != len(world_state))):
                        new_path = list(path)
                        new_path.append([path[-1][0]+x,path[-1][1]+y])
                        queue.append(new_path)
    return None


# True if can we build building with the top-left @ x,y of size (size), otherwise, false.
def valid_build_site(world_state,x,y,size):
    for xtest in range(x, x+size):
        for ytest in range(y, y+size):
            if(occupied(xtest,ytest,world_state)):
                return False
    return True

# returns the path to the coordinate. It is okay if it is occupied -> it will still get the path there.
def path_to_coord(start,world_state, end):
    queue = [[start]]
    if(start == end):
        return None
    visited = set()
    while(len(queue) > 0):
        path = queue.pop(0)
        # if this is the dest, return the first step in the path. (path would return the whole path)
        if(end == path[-1]):
            return path[1]
            
        if(coord_to_int(path[-1]) not in visited and ((path[-1] == start) or not occupied(path[-1][0],path[-1][1],world_state))):
            visited.add(coord_to_int(path[-1]))
            for x in [-1,0,1]:
                for y in [-1,0,1]:
                    # fix -1 index wrapping..
                    if((x != 0 or y != 0) and ((path[-1][0]+x) != -1 and (path[-1][1]+y) != -1)):
                        new_path = list(path)
                        new_path.append([path[-1][0]+x,path[-1][1]+y])
                        queue.append(new_path)
    return None

# Shitty algorithm to find open area of size (SIZE) near x,y where we can build something
# it does a quick check to avoid building next to another building as well
def find_good_buildsite(world_state,x,y,size):
    search_size = 1
    itrs = 100
    while(itrs > 0):
        for dx in range(-search_size,search_size):
            for dy in range(-search_size,search_size):
                # check the coord at x+dx,y+dy
                if(valid_build_site(world_state,x+dx,y+dy,size)):
                    # quick and dirty check to see if we are not touching another building
                    if(not oob_or_bld(x+dx+-1,y+dy,world_state) and not oob_or_bld(x+dx,y+dy+-1,world_state)):
                        return [x+dx,y+dy]
        search_size += 1
        itrs -= 1
    return None

# return all units on the map that satisfy a criteria
# keep in mind buildings occupy many tiles.
def get_tiles(world_state,function):
    unit_list = []
    for xidx, x in enumerate(world_state):
        for yidx, y in enumerate(x):
            if(y is not None and y != "u" and function(y)):
                y["x"] = xidx
                y["y"] = yidx
                unit_list.append(y)
    return unit_list

def countpop(world_state, team):
    pop = 0
    buildings_counted = set()
    for x in range(len(world_state)):
        for y in range(len(world_state[x])):
            if(world_state[x][y] is not None and world_state[x][y] != "u" and (world_state[x][y]["type"]) in ["v","a","i","c"] and world_state[x][y]["team"] == team):
                pop += 1
            if(world_state[x][y] is not None and world_state[x][y] != "u" and (world_state[x][y]["type"] in ["w","r","b","s"]) and world_state[x][y]["team"] == team and world_state[x][y]["traintime"] > 0 and world_state[x][y]["id"] not in buildings_counted):
                pop += 1
                buildings_counted.add(world_state[x][y]["id"])
    return pop

def getpopcap(world_state,team):
    pop = 0
    for x in range(len(world_state)):
        for y in range(len(world_state[x])):
            if(world_state[x][y] is not None and world_state[x][y] != "u" and world_state[x][y]["type"] in ["h","w"] and world_state[x][y]["constructed"] and world_state[x][y]["team"] == team):
                pop += 1
    return pop