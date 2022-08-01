import asyncio
from statistics import mode
import websockets
import requests
import json


class Client:
    def __init__(self, username, password=None, address="sim.smogon.com:8000") -> None:
        self.username = username
        self.password = password
        self.address = "ws://{}/showdown/websocket".format(address)
        self.login_address = "https://play.pokemonshowdown.com/action.php"
        self.battles = []

    async def connect(self):
        self.websocket = await websockets.connect(self.address)

    async def login(self):
        challstr = await self.get_challstr()
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
        # print(message)
        return message

    async def get_challstr(self):
        while True:
            splitted = await self.__split()
            if splitted[1] == "challstr":
                return "|".join([splitted[2], splitted[3]])

    async def accept_challange(self, challanger):
        splitted = await self.__split()
        if splitted[1] == "pm" and splitted[3] == " "+self.username and splitted[4].startswith("/challenge"):
            challanger = splitted[2]
            mode = splitted[5]
            print("Started a battle with {}, format is {}.".format(challanger, mode))
        else:
            await self.add_battle(splitted)
        if challanger != None:
            await self.send("|/accept {}".format(challanger))
            challanger = None
        return challanger

    async def main_loop(self):
        print("Waiting for challange")
        challanger = None
        while True:
            challanger = await self.accept_challange(challanger)
            await self.add_battle()
            await self.battle()
            await asyncio.sleep(1)

    async def send(self, message):
        await self.websocket.send(message)
        #print("Sent \"{}\"".format(message))

    async def add_battle(self, splitted=None):

        # while True:
        if splitted == None:
            splitted = await self.__split()
        try:
            updatesearch = json.loads(splitted[2])
            print(updatesearch)
        except json.decoder.JSONDecodeError as e:
            pass
        if splitted[1] == "init" and splitted[2] == "battle\n":
            self.battles.append(splitted[0].replace(">", "").replace("\n", ""))
        elif splitted[1] == "updatesearch" and updatesearch.get("games") != None:
            for games in updatesearch["games"].keys():
                print(games)
                self.battles.append(games)
                await self.send("|/join {}".format(games))

    async def battle(self):
        for i in self.battles:
            await self.__battle(i)

    async def __battle(self, name):
        print("hi")
        pass

    async def __split(self):
        splitted = str(await self.recive_message()).split("|")
        return splitted


client = Client("my-testing-acct", "sunny0531!")
#client = Client("sunnyayyl0531ayyl")


async def main():
    global client
    await client.connect()
    await client.login()
    await client.main_loop()


loop = asyncio.get_event_loop()
res = loop.run_until_complete(main())
