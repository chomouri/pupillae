import random
import re

# Third-party modules:

# Local modules:

# Function WAI:
def roll_3d6():
    """Rolls 3d6"""
    total = 0
    for i in range(3):
        roll = random.randint(1, 6)
#        print(f"Rolling 1d6: {roll}")
        total += roll
    return total

# Function WAI:
def roll_4d6d():
    """Rolls 4d6, drops lowest"""
    total = []
    for i in range(4):
        roll = random.randint(1, 6)
#        print(f"Rolling 1d6: {roll}")
        total.append(roll)
    total.sort()
    del total[0]
    return sum(total)

def roll_die(quantity, sides, drop = False):
    array_raw = []
    for i in range(quantity):
        roll = random.randint(1, sides)
        array_raw.append(roll)
    if drop:
        array = list(array_raw)
        array.sort()
        del array[0]
        return array, array_raw
    return array_raw

def roll_char_stats():
    """For 6 stats: Roll 4d6, drop lowest"""
    quant = 4
    sides = 6
    stats = ""
    for i in range(1, 7):
        array, array_raw = roll_die(quant, sides, drop = True)
        stats += f"\nStat #{i} = {quant}x d{sides} = {array_raw}\
            \n--Total: {sum(array)}."
    return stats

def process_roll(message):
    reply = re.split(r'd', message)
    return reply

def parse_roll(message):
    error_msg = []
    #Split into groups, keeping trigger as index [0]
    roll_grps = message.split(" ")
    #Remove empty.
    if len(roll_grps) < 2:
        error_msg.append("No dice to roll")
    else:
        # Check if an argument in the roll is invalid.
        inv_grp = False
        current_grp = roll_grps[1]
        quant_side = re.split(r'd', current_grp, 1)
        if len(quant_side) == 2:
            quant = quant_side[0]
            if quant.isdigit():
                quant = int(quant_side[0])
                if quant > 100:
                    error_msg.append("Too many dice")
                    inv_grp = True
            else:
                error_msg.append("Number of dice must be numeric")
                inv_grp = True

            sides = quant_side[1]
            if sides.isdigit():
                sides = int(quant_side[1])
                if sides > 1000:
                    error_msg.append("Too many sides of the dice")
                    inv_grp = True
            else:
                error_msg.append("Number of sides must be numeric")
                inv_grp = True
        else:
            error_msg.append("I can only roll one set of dice at the moment")
            inv_grp = True

        if inv_grp:
            return f"Malformed Expression: {error_msg}."
        else:
            array = roll_die(quant, sides)
            return f"{quant}x d{sides} = {array}\n--Total: {sum(array)}."
