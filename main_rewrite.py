import asyncio
import websockets
import requests
import json
import random


class Battle:
    def __init__(self, websocket, pokemon):
        self.websocket = websocket
        self.data = data

    def effective(self):
        print(self.data)


class Client:
    def __init__(self, username, password=None, address="sim.smogon.com:8000") -> None:
        self.username = username
        self.password = password
        self.address = "ws://{}/showdown/websocket".format(address)
        self.login_address = "https://play.pokemonshowdown.com/action.php"
        self.battles = []
        self.setup_finish = False

    async def connect(self):
        self.websocket = await websockets.connect(self.address)

    async def login(self, challstr):
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

    async def recive_message(self):
        message = await self.websocket.recv()
        if "error" in str(message):
            print(message)
        # print(message)
        return message

    async def parse(self, accept=True, challange=None, format_="gen8randombattle", ladder_max=0,challange_max=0):
        challanger = None
        current = 0
        login = False
        while True:
            message = await self.recive_message()
            splitted = str(message).split("|")
            battle_name = splitted[0].replace(">", "").replace("\n", "")
            if splitted[1] == "challstr":
                await self.login("|".join([splitted[2], splitted[3]]))
                login = True
            elif splitted[1] == "pm" and splitted[3] == " "+self.username and splitted[4].startswith("/challenge"):
                if accept:
                    challanger = await self.accept_challange(splitted, challanger)
            elif splitted[1] == "init" and splitted[2] == "battle\n" or splitted[1] == "updatesearch":
                # Join already exits batlle or new battle created by accept_challange
                ladder_max = ladder_max-1
                await self.add_battle(splitted)
            elif battle_name in self.battles and splitted[1] == "request":
                try:
                    await self.choose_move(json.loads(splitted[2]), battle_name)
                    await asyncio.sleep(0.5)
                except json.decoder.JSONDecodeError as e:
                    pass
            elif battle_name in self.battles and "win" in splitted:
                await self.send("{}|/savereplay".format(battle_name))
                if splitted[splitted.index("win")+1] == self.username:
                    print("Battle {} won".format(battle_name))
                else:
                    print("Battle {} lost".format(battle_name))
            elif splitted[1] == "queryresponse" and splitted[2] == "savereplay":

                obj = json.loads(str(message).replace(
                    "|queryresponse|savereplay|", ""))
                log = obj['log']
                identifier = obj['id']
                post_response = requests.post(
                    "https://play.pokemonshowdown.com/~~showdown/action.php?act=uploadreplay",
                    data={
                        "log": log,
                        "id": identifier
                    }
                )
                print(obj["log"].split("|")
                      [-1].replace("\n", "").split("'s rating:")[0])
                if obj["log"].split("|")[-1].replace("\n", "").split("'s rating:")[0] or "forfeit" in obj["log"] == self.username:
                    with open("win.txt", "a") as f:
                        f.write("https://replay.pokemonshowdown.com/" +
                                identifier+"\n")
                else:
                    with open("lost.txt", "a") as f:
                        f.write("https://replay.pokemonshowdown.com/" +
                                identifier+"\n")
                # await self.send("{}|/leave {}".format(identifier,identifier))
            if login == True:
                if current < ladder_max:
                    print("Waiting for {} match".format(format_))
                    await self.ladder(format_)
                    await asyncio.sleep(10)
                else:
                    pass
                    # await self.send("/cancelsearch")
                if challange!=None and current<challange_max:
                    await self.challange_user(challange,format_=format_)
                    challange_max=challange_max-1

    async def ladder(self, format_):
        await self.send("|/utm {}".format("null"))  # for now
        await self.send("|/search {}".format(format_))

    async def accept_challange(self, splitted, challanger):
        if splitted[1] == "pm" and splitted[3] == " "+self.username and splitted[4].startswith("/challenge"):
            challanger = splitted[2]
            print(splitted)
            try:
                mode = splitted[5]
            except IndexError:
                mode="unknow"
            print("Started a battle with {}, format is {}.".format(challanger, mode))
        if challanger != None:
            await self.send("|/accept {}".format(challanger))
            challanger = None
        return challanger

    async def add_battle(self, splitted):

        try:
            updatesearch = json.loads(splitted[2])
            # print(updatesearch)
        except json.decoder.JSONDecodeError as e:
            pass
        if splitted[1] == "init" and splitted[2] == "battle\n":
            self.battles.append(splitted[0].replace(">", "").replace("\n", ""))
        elif splitted[1] == "updatesearch" and updatesearch.get("games") != None and not self.setup_finish:
            self.setup_finish = True
            for games in updatesearch["games"].keys():
                # print(games)
                self.battles.append({games: {}})
                await self.send("|/join {}".format(games))

        async def send(self, message):
            await self.websocket.send(message)
        #print("Sent \"{}\"".format(message))

    async def choose_move(self, data, room):
        avalable_moves = []
        if data.get("wait") == True:
            await asyncio.sleep(1)
        elif data.get("teamPreview") == True:
            await self.send("{}|/team {}".format(room, "123456"))

        elif data.get("active") != None:
            for move in data["active"][0]["moves"]:
                if move.get("disabled") != True:
                    avalable_moves.append(move["id"])
            print(avalable_moves)
            selected_move = random.choice(avalable_moves)
            await self.send("{}|/choose move {}".format(room, selected_move))
            print("{} | Used {}".format(room,selected_move),"\n\n")
            #Battle(self.websocket,data).effective()
        elif data.get("side") != None:
            active = []
            for pokemon in data["side"]["pokemon"]:
                if not pokemon["condition"].startswith("0") and not pokemon["active"]:
                    active.append(pokemon)
            switched_pokemon = random.choice(active)
            await self.send("{}|/choose switch {}".format(room, switched_pokemon["ident"].split(": ")[1]))
            print("{} | Switched to {} with {}".format(room,
                                                       switched_pokemon["ident"].split(": ")[1], switched_pokemon["item"]))
        else:
            print("Possible error: {}".format(data))
        await asyncio.sleep(1)

    async def challange_user(self, user, format_="gen8randombattle"):
        await self.send("/utm null")
        await self.send("|/challenge {}, {}".format(user, format_))
