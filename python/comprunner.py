from engine import *
import orjson
from os.path import exists
import time; 
from datetime import date
""" This is used to run the game, and it also will produce outputs consumable by unity."""
""" It is slow, but plays with time controls that you will see in the tournament. Don't use any command line arguments """

LOAD_BONUS = .3 # bonus time for loading and unloading.

PLAYER_COUNT = 4 # must match the count below.

def session_name(players):
    if(not exists("../games/")):
        os.mkdir("../games/")
    today = date.today()
    d1 = today.strftime("%m-%d-game-")
    idx = 0
    while(os.path.isdir("../games/" + (d1 + str(idx)))):
        idx += 1
    os.mkdir("../games/"+d1+str(idx))
    return "../games/" + (d1 + str(idx)) + "/"

def masked_filename(d,player_idx):
    return d + "in" + str(player_idx) + ".json"

def state_filename(d,tick):
    return d + str(tick) + ".json"

def out_file_name(d,tick,player_idx):
    return d + str(tick) + "out" + str(player_idx) + ".json"

def runais(world_state,players,player_discovery,tick,sname):
    # make the json to pass to subprocesses
    REALTIME_PRIORITY_CLASS = 0x00000100
    
    collated_orders = []
    for team in range(PLAYER_COUNT):
        write_state_for_tick(world_state,players,player_discovery,team,tick,sname)
        pid = subprocess.Popen([sys.executable, "comprunner.py", str(team), str(tick), sname],creationflags=REALTIME_PRIORITY_CLASS | subprocess.DETACHED_PROCESS).pid
        start_time = time.time()
        while(time.time() < start_time + 1 + LOAD_BONUS):
            try:
                if(exists(out_file_name(sname,tick,team))):
                    with open(out_file_name(sname,tick,team)) as f:
                        for c in orjson.loads(f.read()):
                            c["team"] = team
                            collated_orders.append(c)
                    print("returned ok. Execution time:" + str(time.time() - start_time))
                    break
            except Exception as e:
                #sys.stdout.flush()
                pass
    
        if(time.time() >= start_time + 1 + LOAD_BONUS):
            sys.stdout.flush()
            print("AI has timed out.")
    
    return collated_orders

def write_state_for_tick(world_state,players,player_discovery,i,tick,session):
    with open(masked_filename(session,i), 'wb') as outfile:
        d = {}
        add_to_discovered(world_state,player_discovery[i],i)
        masked = mask_with_discovered(jsoncopy(world_state),player_discovery[i])
        d["world_state"] = masked
        d["players"] = strip_team_info(jsoncopy(players),i)
        outfile.write(orjson.dumps(d))

def fetchPname(team_idx):
    p = subprocess.Popen([sys.executable, "comprunner.py", str(team_idx), "-1"], stdout=subprocess.PIPE)
    out, err = p.communicate()
    return out.decode("utf-8")

def play():

    sys.stdout.flush()
    world_state, players, generatedIDs, player_discovery = new_game(PLAYERS, SEED, shuffle)
    tick = 0
    #render(world_state)

    for i in range(4):
        players[i]["name"] = fetchPname(i)
    
    sname = session_name(players)

    while(True):
        collated_orders = []
        print("tick",tick)
        sys.stdout.flush()
        with open(state_filename(sname,tick), 'wb') as outfile:
            d = {}
            d["world_state"] = world_state
            d["players"] = players
            outfile.write(orjson.dumps(d))

        collated_orders = runais(world_state,players,player_discovery,tick,sname)

        ex_moves = []
        result = process(collated_orders,world_state,players,tick,generatedIDs,ex_moves)
        # write the moves.
        with open(sname + str(tick) + "move.json", 'w') as outfile:
            json.dump(ex_moves, outfile)
        
        if(not(result is False)):
            print("Game ended.")
            print(result)
            break
        sys.stdout.flush()
        tick += 1

def execmove(p):
    if(sys.argv[2] == "-1"):
        print(p.name())
        return

    with open(masked_filename(sys.argv[3], sys.argv[1])) as f:
        data = orjson.loads(f.read())
    moves = p.run(data["world_state"],data["players"],int(sys.argv[1]))
    with open(out_file_name(sys.argv[3],sys.argv[2],int(sys.argv[1])), "wb") as f:
        f.write(orjson.dumps(moves))


# no arg, execute game.
# else,
# arg[1] is "team"
# arg[2] is "tick"
# arg[3] is "session (where to save file)"
# if tick is -1 just write the name.

PLAYERS = [True,True,True,True]
SEED = None
shuffle = False
if len(sys.argv) == 1:
    play()
elif "0" == sys.argv[1]:
    import ai.archbtw.archbtw as p
    execmove(p)
elif "1" in sys.argv[1]:
    import ai.archbtw.archbtw as p
    execmove(p)
elif "2" in sys.argv[1]:
    import ai.archbtw.archbtw as p
    execmove(p)
elif "3" in sys.argv[1]:
    import ai.archbtw.archbtw as p
    execmove(p)


