# Time Of Territory
One peasant. One footman. A dangerous world. And your python skills.

# Objective
Write a python script that outperforms everyone else's in this empire-building game.

The game takes place on a 96x96 grid. Each player starts in a corner of the map (up to 4 players) with just one villager and one soldier.

Explore your surroundings, build your town, wreck your opponents cities, and slay some skeletons. Oh, and pray your python script doesn't crash.

Last player standing wins.

# The Overview
This is a turn-based game (in the vein of original Warcraft) where each player is controlled by a python script. The python script is sent the game state, and may return a "command" for each unit and building. You win once all the opponent's units and buildings are destroyed. Skeletons will spawn intermittently and harass players, getting stronger and stronger as the game goes on.

The fundamental unit of ToT is the "tick". Each tick, every player will be sent the game state and their python script will be given 1 second to decide how to command each unit and building. If the script crashes, gets stuck, or takes too long, the player forfeits their turn, but are still in the game.

Here's an overview of each of your subjects:

## Villager

<img src="https://user-images.githubusercontent.com/8826899/165211430-71e6f704-45c5-4411-bf97-509cc83326ae.png" width="150" height="100" />

The backbone of your empire, these units are able to harvest resources, as well as build and repair structures. If you like committing war crimes, they can double as soldiers as well.

| HP  | POWER | COST | PRODUCE AT   |
|-----|-------|------|--------------|
| 20  | 1     | 10G  | to**w**nhall |

They have the special command **f** which fixes a damaged building (or constructs an unfinished one)

They may also issue commands **w**, **b**, **r**, **s**, and **h** which construct a to**w**nhall, **b**arracks, **r**ange, **s**table, or **h**ouse.

Constructing a building immediately takes the resources required, and spawns the building at the coordinates specified in the argument. (see "Construction")

If a **v**illager attacks (command: __k__) a **t**ree or a **g**old, they will harvest one resource of that type.

## Infantry

<img src="https://user-images.githubusercontent.com/8826899/165211443-08fa1748-c26b-4c12-8554-1afe92921698.png" width="150" height="100" />

The basic soldier. Not terribly strong, but cheap to produce.

| HP  | POWER | COST | PRODUCE AT   |HP (LVL 2)| POWER (LVL 2)|HP (LVL 3)| POWER (LVL 3)|
|-----|-------|------|--------------|----------|--------------|----------|--------------|
| 30  | 2     | 20G  | **b**arracks | 60       | 3            | 90       | 4            |

They only know two commands: attac**k** and **m**ove. They can attack diagonal tiles.

## Archer

<img src="https://user-images.githubusercontent.com/8826899/165211452-1452fbda-4962-49bf-b1da-d94d9b3395a6.png" width="150" height="100" />

Can attack any unit within 8 tiles of it.

| HP  | POWER | COST | PRODUCE AT   |HP (LVL 2)| POWER (LVL 2)|HP (LVL 3)| POWER (LVL 3)|
|-----|-------|------|--------------|----------|--------------|----------|--------------|
| 25  | 1     |10G10W| **r**ange    | 35       | 2            | 45       | 3            |

Like the infantry, they only know two commands: attac**k** and **m**ove.

The line of sight to the target cannot be obstructed: as long as it's within 8 tiles, the attack will land.

Note that range is calcuated without diagonals, which means that valid targets must be in the "green" area in this diagram.

<img src="https://user-images.githubusercontent.com/8826899/165218087-b2116e41-848b-415f-b44a-38ce50d2caad.png" width="100" height="100" />

## Cavalry

<img src="https://user-images.githubusercontent.com/8826899/165211461-d9647638-7022-44fd-91e9-5a045a76a28b.png" width="150" height="100"/>

Can make an extra move per turn. Strong, but expensive.

| HP  | POWER | COST | PRODUCE AT   |HP (LVL 2)| POWER (LVL 2)|HP (LVL 3)| POWER (LVL 3)|
|-----|-------|------|--------------|----------|--------------|----------|--------------|
| 45  | 3     | 40G  | **s**table   | 90       | 4            | 135      | 5            |

To use the extra move feature, you can submit another move command that will be executed after the first one. This only works with moves: no move + attack, for example.

## Construction

There are five types of buildings. (These are pretty simple, so you don't get any embedded pictures).

to**w**nhall: **p**roduces **v**illagers and counts for 9 housing.
**b**arracks: **p**roduces **i**nfantry and **u**pgrades them as well.
**r**ange: **p**roduces **a**rchers and **u**pgrades them as well.
**s**table: **p**roduces **c**avalry and **u**pgrades them as well.
**h**ouse: Counts for 4 housing. 

When constructed, a building will start at half health and be incapable of providing housing, producing units or upgrading units.
When the building is brought to full health using the **v**illager's **f** command, it will be able to function normally.
Even if the building is later damaged, it will still function normally as long as it was brought to full health previously.

you can check if a building is constructed by looking at the "constructed" key. All buildings will have this.

|              | HP  | COST | HOUSING | SIZE |
|--------------|-----|------|---------|------|
| to**w**nhall | 80  | 200W | 9       | 3x3  |
| **b**arracks | 60  | 50W  | 0       | 3x3  |
| **r**ange    | 60  | 70W  | 0       | 3x3  |
| **s**table   | 60  | 90W  | 0       | 3x3  |
| **h**ouse    | 40  | 30W  | 4       | 2x2  |

## Upgrading

**b**arracks, **r**anges, and **s**tables can be issued a **u** command. If you have the resources, all units will immediately be promoted to the next level, which increases max HP and Power. Units have a max level of 3.

The cost to upgrade is 10 * the base unit cost for upgrade to level 2, and
20 * the base unit cost for upgrade to level 3.

For example, getting the first archer upgrade costs 100W and 100G (since an archer costs 10W and 10g)

## Resources

Ez pz, you have wood and gold. Trees have 50 HP (and thus take 50 villager attacks to take down). Gold has 250 HP.

Trees and gold are on the team -1.

## Skeletons

Every 500 ticks, skeleton archers will spawn in empty tiles near the middle of the map. They are equivalent to a normal archer at level 1.
Skeletons will attack any player unit or building within range. If there's nothing within range, they will pick an edge tile of the map and walk to it.
To get to their destination, they will attack trees and gold.

Skeletons are on team -2.

(Skeletons exist primarily to make sure the game ends sometime around ~3000 ticks, or 30 minutes)

|TICK | COUNT |
|-----|-------|
| 500 | 8     |
|1000 | 16    |
|1500 | 32    |
|2000 | 64    |
|2500 | 128   |
|3000 | 256   |

If there are still (somehow) multiple players alive after tick 3000, 512 skeletons will spawn every hundred turns until only one player is left.

# The Commands
Each unit and building can receive one command per turn. Except Cavalry, but we will get to that later. 

Commands are of the form `{"id": X, "command": Y, "arg": Z}`.

You do not have to issue a command each turn - if you want the unit or building to do nothing, just don't send any commands.

Military units only have two possible commands:

**m**ove: move one tile in any direction. Diagonals are valid.

**k**ill: attack a unit, building, or resource.

Villagers can do these things, but also

**w**,**b**,**r**,**s**, and **h**: construct a building, see "Command order and Syntax".

**f**: fix a building or construct an unfinished one.

Building commands:

To**w**nhalls, **b**arracks, **r**anges, and **s**tables can produce units with **p** if there is enough housing available and you can pay for the training of the unit. See "Production".

**b**arracks, **r**anges, and **s**tables can also increase the level of produced units with __u__, see "Upgrades"

## Exploration (a human mind)

Tiles need to be explored. By default, each building and unit can see 8 tiles in any given direction.

An unexplored tile appears as the string "u" in the world state.

Once a tile is explored, you will always be able to see what's in it.
(I wanted to add full fledged fog of war, but that would require y'all to store the tiles you have seen already, and I really wanted to make it so you don't need to save any state between calls to your AI. So this is a compromise.

## Production

All buildings have a key "traintime". If this is zero, you can train a unit, if it's nonzero, a unit is being trained. It decrements by one every turn and produces a unit near the building when it becomes zero. You can only train one unit at a time.

Issuing a "p" command to a building that is already training something will do nothing.

## Command order and Syntax

All commands are just python dicts. They have the format
{"command":\_, "id":\_, "arg":\_}

Your AI function will return a list of these commands. They will be sorted by id later, so it doesn't really matter what order they are in.

Also, if your AI submits an invalid command, don't fret: it will just be ignored. Though, you can still only send one command per unit.


command must be a string containing a single character (picked from below).

id is the integer id of the unit you would like to command, which you get from world_state.

arg is the argument. Some commands need this, see below.

Commands are parsed in the following order. Units with a lower ID get their moves executed first.

**k**ill

arg: the ID of the unit you want to attack.

If a villager attacks a resource, it will be harvested.

Units cannot attack themselves.

**b**,**r**,**s**,**t**,**h** (the construction commands)

arg: the top-left coordinate of the building. 

Will fail if you don't have enough resources.

sending (0,0) will build at the top left corner of the map.

Keep in mind your villager must be adjacent to the building to start construction. 

**f**ix

arg: the building ID. like with construction, you must be next to the building.

either fixes a damaged building, or construct one that isn't constructed.

Unlike other games, this costs no resources to do.

**m**ove 

(note that this command is iterated over and over again until no new moves are detected - if a unit is stuck behind another unit that intends to move, it will take it's spot)

arg: the delta you'd like to move the character, as a two-integer list. [-1,1] moves the unit up and to the right.

If and only if the commanded unit is a cavalry, two of these commands can be executed if two are received.

**p**roduction

arg: None (just provide the python type `None`)

All units take 15 turns to produce. Trying to produce at a building that is already training a unit does nothing.

**u**pgrades

arg: None (just prove the python type `None`)

If you can afford it, instantly upgrades all units to the next level and future units will spawn at this level as well.
To upgrade infanty, use at a barracks, etc, etc.

## Inputs

You must write two functions in your python file.

name() should just return the name of your AI. Keep it under 8 characters. Pretty simple. If you name your AI "Dwight" then...

def name():
    return "Dwight"
    
Then, there's run: run(world_state,players,team_idx):

world_state is a 96x96 array. It can only possibly contain one of four objects:

None (there's nothing here)

"u" (this tile is unexplored)

{"type":String, "hp":Int, "team": Int, "id": Int} (a unit or resource)

{"constructed": Bool, "traintime": Int, "type":String, "hp":Int ,"team":Int ,"id":Int} (a building)


world state is oriented as such:

X + ->

Y

|

V

Players returns a list of players, with keys arc_level, inf_level, cav_level that shows what level each unit is.

Player_idx is your team number.

You will also get keys for wood and gold for your player_idx in the players array.


## Sample AIs

**Probably the easiest way to understand how to write an AI is to look at the sample ones.** I've provided 5.

Random - submits a random move. It will submit illegal ones too. It does not care. (you should be able to crush this)

GoldPls - builds houses and collects as much gold as it can.

Russian - rushes you with infantry, doesn't even care about building a townhall. Tries to upgrade inf as well.

HorseRadish - like russian, but uses cav.

ArchBTW - the strongest of the bunch, trains villagers and uses archers to defend them. Capable of building multiple ranges.

Of course, your AIs can (and probably should?) train multiple types of units rather than sticking to one, but what do I know.

These all rely on the "shitutils.py" module, which uh, while basic and effective, are slow and not terribly good and you should probably reimplement or even better, just don't use. But you don't have to. It's a free country.


## Running the game

I suggest using debugrunner.py to develop your AI - it renders everything in your terminal and will show you stack traces if you end up crashing.

The top of debugrunner.py has some hints for how to use it, and some neato command line arguments, like showing fog of war and rendering the game in your terminal.

When you're ready for primetime, use comprunner.py. It will run the game and save it in the games/ directory. You can use the unity exe attached to watch playback of these games.

## Other bits

The competition is on June 18 or 19.

Don't write any files or use any sockets please. I would have done this in lua but nobody knows lua LOL

We will have a single elimation tournament bracket of strictly 1v1 games - best of three.

We will also have a free for all, where three games will be played. Your rank is just your survival time.

1st place: 5 pts
2nd place: 3 pts
3rd place: 1 pt

If you find a bug in the engine, you _can_ exploit it, but you would be WAY cooler if you told me about it so i could fix it. (or send a PR if you wanna go above and beyond)

## Handicap

For the sake of having a more balanced contest, some players will get handicaps, which is going to be a % discount on training units.

This is not yet implemented and the actual %s are TBD.

## CHANGELOG
0.2
- Modify skeleton spawn rate, making it FAR more aggressive
- Modify skeleton pathfinding
- Fix possible late game crash
- Increase gold per map
- Fix bugs in sample AIs
- Write WAY more documenation

## TODO
- run AI from arbitrary game state
- saved games are FREAKIN HUGE
- add handicap
- arrow animation looks pretty bad
- no death animations
- no fow
- you should be able to click minimap to move it
- renderer isn't as fast as I'd like
- cavlary animations work, but look like trash
- no code for handling ties  
- no real tests so some shit is prolly borked
