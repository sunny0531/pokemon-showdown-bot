import requests

data = {
    "normal": {
        "fighting": 2.0,
        "normal": 1.0, "flying": 1.0, "poison": 1.0, "ground": 1.0, "rock": 1.0, "bug": 1.0, "steel": 1.0, "fire": 1.0,
        "water": 1.0,
        "grass": 1.0, "electric": 1.0, "psychic": 1.0, "ice": 1.0, "dragon": 1.0, "dark": 1.0, "fairy": 1.0, "ghost": 0
    },
    "fighting": {
        "flying": 2.0, "psychic": 2.0, "fairy": 2.0, "normal": 1.0, "fighting": 1.0, "poison": 1.0, "ground": 1.0,
        "ghost": 1.0,
        "steel": 1.0, "fire": 1.0, "water": 1.0, "grass": 1.0, "electric": 1.0, "ice": 1.0, "dragon": 1.0, "rock": 0.5,
        "bug": 0.5,
        "dark": 0.5
    },
    "flying": {
        "rock": 2.0, "electric": 2.0, "ice": 2.0, "normal": 1.0, "flying": 1.0, "poison": 1.0, "ghost": 1.0,
        "steel": 1.0, "fire": 1.0, "water": 1.0, "psychic": 1.0, "dragon": 1.0, "dark": 1.0, "fairy": 1.0,
        "fighting": 0.5, "bug": 0.5, "grass": 0.5,"ground":0
    },
    "poison": {
        "ground": 2.0, "psychic": 2.0, "normal": 1.0, "flying": 1.0, "rock": 1.0, "ghost": 1.0, "steel": 1.0,
        "fire": 1.0, "water": 1.0, "electric": 1.0, "ice": 1.0, "dragon": 1.0, "dark": 1.0, "fighting": 0.5,
        "poison": 0.5, "bug": 0.5, "grass": 0.5, "fairy": 0.5
    },
    "ground": {
        "water": 2.0, "grass": 2.0, "ice": 2.0, "normal": 1.0, "fighting": 1.0, "flying": 1.0, "ground": 1.0,
        "bug": 1.0, "ghost": 1.0, "steel": 1.0, "fire": 1.0, "psychic": 1.0, "dragon": 1.0, "dark": 1.0, "fairy": 1.0,
        "poison": 0.5, "rock": 0.5, "electric": 0.0
    },
    "rock": {
        "fighting": 2.0, "ground": 2.0, "steel": 2.0, "water": 2.0, "grass": 2.0, "rock": 1.0, "bug": 1.0, "ghost": 1.0,
        "electric": 1.0, "psychic": 1.0, "ice": 1.0, "dragon": 1.0, "dark": 1.0, "fairy": 1.0, "normal": 0.5,
        "flying": 0.5, "poison": 0.5, "fire": 0.5
    },
    "bug": {
        "flying": 2.0, "rock": 2.0, "fire": 2.0, "normal": 1.0, "poison": 1.0, "bug": 1.0, "ghost": 1.0, "steel": 1.0,
        "water": 1.0, "electric": 1.0, "psychic": 1.0, "ice": 1.0, "dragon": 1.0, "dark": 1.0, "fairy": 1.0,
        "fighting": 0.5, "ground": 0.5, "grass": 0.5
    },
    "ghost": {
        "ghost": 2.0, "dark": 2.0, "flying": 1.0, "ground": 1.0, "rock": 1.0, "steel": 1.0, "fire": 1.0, "water": 1.0,
        "grass": 1.0, "electric": 1.0, "psychic": 1.0, "ice": 1.0, "dragon": 1.0, "fairy": 1.0, "poison": 0.5,
        "bug": 0.5,
        "normal": 0.0, "fighting": 0.0
    },
    "steel": {
        "fighting": 2.0, "ground": 2.0, "fire": 2.0, "ghost": 1.0, "water": 1.0, "electric": 1.0, "dark": 1.0,
        "normal": 0.5, "flying": 0.5, "rock": 0.5, "bug": 0.5, "steel": 0.5, "grass": 0.5, "psychic": 0.5, "ice": 0.5,
        "dragon": 0.5, "fairy": 0.5, "poison": 0.0,
    },
    "fire": {
        "ground": 2.0, "rock": 2.0, "water": 2.0, "normal": 1.0, "fighting": 1.0, "flying": 1.0, "poison": 1.0,
        "ghost": 1.0, "electric": 1.0, "psychic": 1.0, "dragon": 1.0, "dark": 1.0, "bug": 0.5, "steel": 0.5,
        "fire": 0.5, "grass": 0.5, "ice": 0.5, "fairy": 0.5
    },
    "water": {
        "grass": 2.0, "electric": 2.0, "normal": 1.0, "fighting": 1.0, "flying": 1.0, "poison": 1.0, "ground": 1.0,
        "rock": 1.0, "bug": 1.0, "ghost": 1.0, "psychic": 1.0, "dragon": 1.0, "dark": 1.0, "fairy": 1.0, "steel": 0.5,
        "fire": 0.5, "water": 0.5, "ice": 0.5
    },
    "grass": {
        "flying": 2.0, "poison": 2.0, "bug": 2.0, "fire": 2.0, "ice": 2.0, "normal": 1.0, "fighting": 1.0, "rock": 1.0,
        "ghost": 1.0, "steel": 1.0, "psychic": 1.0, "dragon": 1.0, "dark": 1.0, "fairy": 1.0, "ground": 0.5,
        "water": 0.5, "grass": 0.5, "electric": 0.5
    },
    "electric": {
        "ground": 2.0, "normal": 1.0, "fighting": 1.0, "poison": 1.0, "rock": 1.0, "bug": 1.0, "ghost": 1.0,
        "fire": 1.0, "water": 1.0, "grass": 1.0, "psychic": 1.0, "ice": 1.0, "dragon": 1.0, "dark": 1.0, "fairy": 1.0,
        "flying": 0.5, "steel": 0.5, "electric": 0.5

    },
    "psychic": {
        "bug": 2.0, "ghost": 2.0, "dark": 2.0, "normal": 1.0, "flying": 1.0, "poison": 1.0, "ground": 1.0, "rock": 1.0,
        "steel": 1.0, "fire": 1.0, "water": 1.0, "grass": 1.0, "electric": 1.0, "ice": 1.0, "dragon": 1.0, "fairy": 1.0,"fighting": 0.5, "psychic": 0.5

    },
    "ice": {
        "fighting": 2.0, "rock": 2.0, "steel": 2.0, "fire": 2.0, "normal": 1.0, "flying": 1.0, "poison": 1.0,
        "ground": 1.0, "bug": 1.0, "ghost": 1.0, "water": 1.0, "grass": 1.0, "electric": 1.0, "psychic": 1.0,
        "dragon": 1.0, "dark": 1.0, "fairy": 1.0, "ice": 0.5
    },
    "dragon": {
        "ice": 2.0, "dragon": 2.0, "fairy": 2.0, "normal": 1.0, "fighting": 1.0, "flying": 1.0, "poison": 1.0,
        "ground": 1.0, "rock": 1.0, "bug": 1.0, "ghost": 1.0, "steel": 1.0, "psychic": 1.0, "dark": 1.0, "fire": 0.5,
        "water": 0.5, "grass": 0.5, "electric": 0.5

    },
    "dark": {
        "fighting": 2.0, "bug": 2.0, "fairy": 2.0, "normal": 1.0, "flying": 1.0, "poison": 1.0, "ground": 1.0,
        "rock": 1.0, "steel": 1.0, "fire": 1.0, "water": 1.0, "grass": 1.0, "electric": 1.0, "ice": 1.0, "dragon": 1.0,
        "ghost": 0.5, "dark": 0.5, "psychic": 0.0

    },
    "fairy": {
        "poison": 2.0, "steel": 2.0, "normal": 1.0, "flying": 1.0, "ground": 1.0, "rock": 1.0, "ghost": 1.0,
        "fire": 1.0, "water": 1.0, "grass": 1.0, "electric": 1.0, "psychic": 1.0, "ice": 1.0, "fairy": 1.0,
        "fighting": 0.5, "bug": 0.5, "dark": 0.5, "dragon": 0.0

    }

}


def power(move, target, STAB=1.5):
    type, power = move
    effective = 1
    stab = 1.0
    for i in target:
        effective = effective * data[i.lower()][type.lower()]
    if type in target:
        stab = STAB
    return effective * float(power) * stab


print(power(("rock", 1), ("flying", "fighting")))
