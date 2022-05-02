""" Move randomly, even submitting illegal inputs.
difficulty: babby with training wheels"""
from ai.shitutils import *
import random

def name():
    return "random"

# randomly issue a command, most of the time, these are not even valid so rejected.
def run(world_state,players,team_idx):
    cmds = []
    # every possible order
    all_orders = ["m","k","f","p","u","b","r","s","w","h"]
    # unit vectors + ID of everyone on our team as args.

    dir_opts = [[-1,0],[1,0],[0,-1],[0,1]] + list(map(lambda x: x["id"], get_tiles(world_state,lambda x: x["team"] == team_idx)))
    #print(dir_opts)
    for u in get_tiles(world_state,lambda x: x["team"] == team_idx):
        cmds.append({"id":u["id"],"command":random.choice(all_orders),"arg":random.choice(dir_opts)})
    return cmds