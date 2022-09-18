import websockets
import requests
import json
import asyncio
import random
import time
import re
import string


class Client:
    def __init__(self, username, password=None, address="sim.smogon.com:8000", accept_challange=True, challange=[],
                 format_="gen8randombattle",ladder_max=0) -> None:
        self.username = username
        self.password = password
        self.address = "ws://{}/showdown/websocket".format(address)
        self.login_address = "https://play.pokemonshowdown.com/action.php"
        self.accept = accept_challange
        self.challange = challange
        self.team = "null"
        self.setup = True
        self.format_ = format_
        self.ladder_max=ladder_max
        self.battle = Battle()
        self.events = {}
        self.register("challstr", self.login)
        self.register("pm", self.accept_challange)
        self.register("request", self.move)
        self.register("init", self.new_battle)
        self.register("updatesearch", self.update)
        self.register("raw", self.raw)
        self.register("\n", self.switch)
        self.register("player", self.player)

    async def raw(self, splitted):
        print("|".join(splitted))

    async def player(self, splitted):
        battle_name = splitted[0].replace(">", "").replace("\n", "")
        await self.switch(splitted)
        self.battle.add_player(battle_name, splitted)

    async def switch(self, splitted):
        battle_name = splitted[0].replace(">", "").replace("\n", "")
        for i in range(len(splitted)):
            if splitted[i] == "switch":
                self.battle.switch(battle_name, splitted[i + 1:])

    async def new_battle(self, splitted):
        battle_name = splitted[0].replace(">", "").replace("\n", "")
        self.battle.create(battle_name)
        await self.player(splitted)

    async def accept_challange(self, splitted):
        if splitted[3] == " " + self.username and splitted[4].startswith("/challenge"):
            if self.accept:
                challanger = splitted[2]
                try:
                    mode = splitted[5]
                except IndexError:
                    mode = "unknow"
                if challanger != None:
                    await self.send("|/accept {}".format(challanger))
                print("Started a battle with {}, format is {}.".format(challanger, mode))

    async def send(self, message):
        await self.websocket.send(message)
        await asyncio.sleep(0.6)

    async def update(self, splitted):
        try:
            updatesearch = json.loads(splitted[2])
            # print(updatesearch)
        except json.decoder.JSONDecodeError as e:
            pass
        if updatesearch.get("games") != None:
            for games in updatesearch["games"].keys():
                await self.send("|/join {}".format(games))

    async def move(self, splitted):
        battle_name = splitted[0].replace(">", "").replace("\n", "")
        try:
            await self.choose_move(json.loads(splitted[2]), battle_name)
        except json.decoder.JSONDecodeError as e:
            pass

    async def connect(self):
        self.websocket = await websockets.connect(self.address)

    async def login(self, splitted):
        challstr = "|".join([splitted[2], splitted[3]])
        if self.password != None:
            login = requests.post(
                self.login_address,
                data={
                    "act": "login",
                    "name": self.username,
                    "pass": self.password,
                    "challstr": challstr
                }
            )
        else:
            login = requests.get(
                self.login_address +
                "?act=getassertion&userid={}&challstr={}".format(
                    self.username, challstr),
            )
        if login.status_code == 200:
            if self.password != None:
                login_json = json.loads(login.text[1:])
                if not login_json['actionsuccess']:
                    raise Exception("Could not log-in")

                assertion = login_json.get('assertion')
            else:
                assertion = login.text
        print("Logging in as {}".format(self.username))
        await self.send("|/trn {},0,{}".format(self.username, assertion))
        self.setup = False

    async def recive_message(self):
        message = await self.websocket.recv()
        # print(message)
        return message

    def register(self, event: str, func):
        self.events[event] = func

    async def choose_move(self, data, room):

        avalable_moves = []
        if data.get("wait") == True:
            await asyncio.sleep(1)
        elif data.get("teamPreview") == True:
            await self.send("{}|/team {}".format(room, "123456"))

        elif data.get("active") != None:
            switch,result=self.battle.choose_move(room, data, self.username)
            if not switch:
                await self.send("{}|/choose move {}".format(room, result["move"]))
                print("{} | Used {}".format(room, result["move"]), "\n\n")
            else:
                active = []
                for pokemon in data["side"]["pokemon"]:
                    if not pokemon["condition"].startswith("0") and not pokemon["active"]:
                        active.append(pokemon)
                switched_pokemon = random.choice(active)
                await self.send("{}|/choose switch {}".format(room, switched_pokemon["ident"].split(": ")[1]))
                print("{} | Switched to {} with {}".format(room,
                                                           switched_pokemon["ident"].split(": ")[1],
                                                           switched_pokemon["item"]))
        elif data.get("side") != None:
            active = []
            for pokemon in data["side"]["pokemon"]:
                if not pokemon["condition"].startswith("0") and not pokemon["active"]:
                    active.append(pokemon)
            switched_pokemon = random.choice(active)
            await self.send("{}|/choose switch {}".format(room, switched_pokemon["ident"].split(": ")[1]))
            print("{} | Switched to {} with {}".format(room,
                                                       switched_pokemon["ident"].split(": ")[1],
                                                       switched_pokemon["item"]))
        else:
            print("Possible error: {}".format(data))

    async def start(self):
        while True:
            current=0
            message = await self.recive_message()
            splitted = str(message).split("|")
            battle_name = splitted[0].replace(">", "").replace("\n", "")
            if self.events.get(splitted[1]) != None:
                await self.events[splitted[1]](splitted)
            elif len(splitted[1].replace("\n", "")) > 0:
                print("Nothing register for event: {}".format(splitted[1]))
            if self.challange and not self.setup:
                for i in self.challange:
                    await self.send("/utm " + self.team)
                    await self.send("|/challenge {}, {}".format(i, self.format_))
                    self.challange.remove(i)
            if current<self.ladder_max and not self.setup:
                self.ladder_max=self.ladder_max-1
                await self.send("|/utm {}".format("null"))  # for now
                await self.send("|/search {}".format(self.format_))




class Battle:
    def __init__(self):
        self.battle = {}
        self.player = {}
        self.pokedex = requests.get("https://play.pokemonshowdown.com/data/pokedex.json").json()

    def create(self, battle):
        self.battle[battle] = {}
        self.player[battle] = {}

    def switch(self, battle, data):
        player_pokemon = data[0]
        id = player_pokemon.split(": ")[0]
        pokemon = player_pokemon.split(": ")[1]
        level = data[1].split(", ")[1]
        player = re.search("p(\d)([abcd])", id).group(1)
        id = re.search("p(\d)([abcd])", id).group(2)
        try:
            self.battle[battle][player][id] = {"name": pokemon, "level": level.replace("L", "")}
        except KeyError:
            self.battle[battle][player] = {id: {"name": pokemon, "level": level.replace("L", "")}}

    def add_player(self, battle, data):
        for i in range(len(data)):
            if data[i] == "player":
                id = data[i + 1].replace("p", "")
                name = data[i + 2]
                self.player[battle][name] = id

    def choose_move(self, battle, data, me):
        switch=False
        avalable_moves = []
        best_move={
            "damage":0,
            "move":"",
            "target":""
        }
        for move in data["active"][0]["moves"]:
            if move.get("disabled") != True:
                avalable_moves.append(move["move"])
        attacker = None
        for i in data["side"]["pokemon"]:
            if i["active"]:
                attacker = i
                print(attacker)
        for ii in self.player[battle]:
            if ii != me:
                for iii in self.battle[battle][self.player[battle][ii]]:
                    for move in avalable_moves:
                        opposite = self.battle[battle][self.player[battle][ii]][iii]
                        print(self.pokedex[opposite])
                        ability=""
                        for abilitys in self.data[attacker["details"].split(", ")[0].lower().replace(" ","").translate(str.maketrans('', '', string.punctuation))]["abilities"].values():
                            if abilitys.lower().replace(" ","")==attacker["baseAbility"]:
                                ability=abilitys
                        damage = requests.post("https://calc-api.herokuapp.com/calc-api", json={
                            "attacker": {
                                "species": attacker["details"].split(", ")[0].lower().replace(" ","").translate(str.maketrans('', '', string.punctuation)),
                                "ability": ability,
                                "item": attacker["item"],
                                "level": attacker["details"].split(", ")[1].replace("L", "")
                            },
                            "defender": {
                                "species": opposite["name"].lower().replace(" ","").translate(str.maketrans('', '', string.punctuation)),
                                "ability": random.choice(list(self.data[opposite["name"].lower().replace(" ","").translate(str.maketrans('', '', string.punctuation))]["abilities"].values())),
                                "level": opposite["level"],
                                "item": "leftover",
                            },
                            "move":move
                        })
                        damage=damage.json()
                        try:
                            if best_move["damage"]<max(damage["damage"]):
                                best_move={
                                    "damage":max(damage["damage"]),
                                    "target":opposite["name"],
                                    "move":move
                                }
                                print(damage["name"],damage["damage"])
                                if best_move["damage"]<55:
                                    switch=True
                                elif best_move["damage"]<100:
                                    if random.randint(0,1)==0:
                                        switch=True
                        except KeyError:
                            if best_move["move"]=="":
                                best_move["move"]=random.choice(avalable_moves)
        print(best_move)
        return (switch,best_move)

