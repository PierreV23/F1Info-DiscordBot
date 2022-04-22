__author__ = "PierreV23 https://github.com/PierreV23"
__copyright__ = "Copyright (C) 2022 Pièrre (A.P.) V"
__license__ = "GNU General Public License v3.0"
__author__forked__ = "" # NOTE: Put your version of `__author__` in here.


from disnake.ext import commands
import datetime as dt
import json_rw
import time
import ergastwrapper


global F1YEAR
global F1ROUND
F1YEAR = 2022
F1ROUND = 1



def get_current_weekend():
    global F1ROUND
    weekend = ergastwrapper.get_weekend(F1YEAR, F1ROUND)
    while True:
        print(weekend.Race.datetime.timestamp() - time.time() + 3*60*60, weekend.circuit.name)
        if weekend.Race.datetime.timestamp() - time.time() + 3*60*60 > 0: # TODO: Less hours?
            break
        else:
            F1ROUND += 1
            weekend = ergastwrapper.get_weekend(F1YEAR, F1ROUND)
    return weekend


def initialize_commands(self): # NOTE: This exists so i can collapse all commands in my IDE.
    @self.command(name="debug-setround")
    async def setf1round(ctx: commands.Context):
        if ctx.author.id == 174134334628823041:
            _temp = ctx.message.content.split()
            if len(_temp) != 2:
                ctx.channel.send("bruh")
            else:
                global F1ROUND
                try:
                    F1ROUND = int(_temp[1])
                except:
                    ctx.channel.send("bruh v2")
    
    
    @self.command(name="getround", aliases=['round'])
    async def getf1round(ctx: commands.Context):
        await ctx.channel.send(F1ROUND)
    

    @self.command(
        name = "next-session",
        aliases = [
            'next',
            'fp', 'fp1', 'fp2', 'fp3',
            'q', 'q1', 'q2', 'q3',
            'sprint', 'race'
        ]
    )
    async def get_session(ctx: commands.Context):
        cmd = ctx.invoked_with.lower()
        if cmd == "fp": cmd = "fp1"

        try:
            wknd = get_current_weekend()
            if "next" in cmd:
                global F1ROUND
                filtered = list(filter(lambda sess: (sess.datetime.timestamp() - time.time() >= 0), wknd.sessions))
                ######################################################################################################### NOTE: I was bored
                while bool(filtered) == False:                                                                          # NOTE: I was bored
                    F1ROUND += 1                                                                                        # NOTE: I was bored
                    wknd = get_current_weekend()                                                                    	# NOTE: I was bored
                    filtered = list(filter(lambda sess: (sess.datetime.timestamp() - time.time() >= 0), wknd.sessions)) # NOTE: I was bored
                ######################################################################################################### NOTE: I was bored TODO: Delete this childy behaviour.
                session = min(filtered, key = lambda sess: sess.datetime.timestamp())
                F1ROUND -= 1 # .
            else:
                session = wknd.get_session(ergastwrapper.SessionType(cmd))
            
            unix = int(session.datetime.timestamp())
            circuit = session.circuit
            # await ctx.channel.send(f"**{circuit.name},  {circuit.locality},  {circuit.country}**\n> `{session.name} happens on `<t:{unix}:F>\n> `{session.name} starts `<t:{unix}:R>")
            delta: dt.timedelta = session.datetime - dt.datetime.now(tz = dt.timezone.utc)
            _days = delta.days
            if _days < 0:
                started = True
                delta = abs(delta)
            else:
                started = False
            
            days = delta.days

            rest = delta.seconds

            hours = rest // (60 * 60)
            rest -= hours * 60 * 60
            minutes = rest // 60
            rest -= minutes * 60
            seconds = rest

            text_days = f"**`{days}`**` days"
            text_hours = f"**`{hours}`**` hours"
            text_minutes = f"**`{minutes}`**` minutes"
            
            if started:
                text_seconds = f"**`{seconds}`**` seconds ago"
                text_starts_in = f"`{session.name} started `{text_days}, `{text_hours}, `{text_minutes} and `{text_seconds}`"
            else:
                text_seconds = f"**`{seconds}`**` seconds"
                text_starts_in = f"`{session.name} starts in `{text_days}, `{text_hours}, `{text_minutes} and `{text_seconds}`"            
            

            
            await ctx.channel.send(f"**{circuit.name},  {circuit.locality},  {circuit.country}**\n> `{session.name} happens on `<t:{unix}:F>\n> {text_starts_in}")
        except Exception as e:
            ergastwrapper.cache.reset_cache()
            print("Exception occured when trying to send session timings.", e)
            await ctx.channel.send(f"Something went wrong, try again later.")
    
    
    @self.command("raw_timestamps")
    async def raw_timestamps(ctx):
        wknd = get_current_weekend()
        sessions = {name:wknd.get_session(ergastwrapper.SessionType(name)) for name in ["fp1", "fp2", "fp3", "q", "q1", "q2", "q3", "sprint", "race"]}
        raw = ""
        for sesname, sesobj in sessions.items():
            if sesobj:
                raw += f"{sesname}: '{int(sesobj.datetime.timestamp())}'\n"
        
        await ctx.channel.send(raw)
    

    @self.command("schedule", aliases = ["weekend", "timing", "timings"])
    async def schedule(ctx):
        wknd = get_current_weekend()
        sessions = {name:wknd.get_session(ergastwrapper.SessionType(name)) for name in ["fp1", "fp2", "fp3", "q", "q1", "q2", "q3", "sprint", "race"]}
        circuit = sessions["fp1"].circuit
        if wknd.is_sprint_weekend():
            txt = f"""
            **{circuit.name},  {circuit.locality},  {circuit.country}**
            > **fp1**: <t:{int(sessions['fp1'].datetime.timestamp())}:F>
            > **q**: <t:{int(sessions['q'].datetime.timestamp())}:F>
            > **fp2**: <t:{int(sessions['fp2'].datetime.timestamp())}:F>
            > **sprint**: <t:{int(sessions['sprint'].datetime.timestamp())}:F>
            > **race**: <t:{int(sessions['race'].datetime.timestamp())}:F>
            """
        else:
            txt = f"""
            **{circuit.name},  {circuit.locality},  {circuit.country}**
            > **fp1**: <t:{int(sessions['fp1'].datetime.timestamp())}:F>
            > **fp2**: <t:{int(sessions['fp2'].datetime.timestamp())}:F>
            > **fp3**: <t:{int(sessions['fp3'].datetime.timestamp())}:F>
            > **q**: <t:{int(sessions['q'].datetime.timestamp())}:F>
            > **sprint**: <t:{int(sessions['sprint'].datetime.timestamp())}:F>
            > **race**: <t:{int(sessions['race'].datetime.timestamp())}:F>
            """
        await ctx.channel.send(txt)
            
        

    @self.command(name='creator', aliases=['owner', 'maker', 'bot', 'github'])
    async def send_creator(ctx: commands.Context):
        text = f"\n**Author**: `{__author__}`\n**Copyright**: `{__copyright__}`\n**License**: `{__license__}`" + (f"\n**Author of fork**: `{__author__forked__}`" if __author__forked__ else "")
        await ctx.channel.send(text)
    

    @self.command(name='prefix')
    async def set_prefix(ctx: commands.Context):
        if ctx.author.guild_permissions.administrator:
            ctx.channel.send(f"Sorry, our bot doesnt have a database yet, and thus cant have custom prefixes.")
            '''
            prefix = get_server_prefix(ctx.guild.id)
            _temp = ctx.message.content.split(' ')
            if len(_temp) != 2:
                await ctx.channel.send(f"Something went wrong changing the prefix. The command should be formatted like: `{prefix}prefix %insert_new_prefix%`")
            else:
                newprefix = _temp[1]
                set_server_prefix(ctx.guild.id, newprefix)
                await ctx.channel.send(f"Prefix changed from `{prefix}` to `{newprefix}`")
            '''



class F1Info(commands.Bot):
    def __init__(self, *args, **kwargs):
        commands.Bot.__init__(self, *args, **kwargs)
        initialize_commands(self)        


    async def on_ready(self):
        print(f"The bot is ready! - {dt.datetime.now()}")
    

    async def on_message(self, ctx):
        await self.process_commands(ctx)
        # print(ctx.content) # debug purposes 🙄
        #if ctx.content == f'<@{}>' # TODO: get bot id
        #await ctx.author.dm_channel.channel. # TODO: fix this shit
        # TODO: Make it so a message containing just a tag of the bot sends a dm to the guy pinging the bot, incase people forget prefixes....


# global SERVER_PREFIXES
# SERVER_PREFIXES: dict[int, str] = json_rw.get_json('server_prefixes.json')
default_prefix = '-'


# @@@ NOTE: Disabled for the time being, will have to be replaced by a database @@@ (TODO)
'''
def get_server_prefix(id: int or str): 
    return SERVER_PREFIXES.get(str(id), default_prefix)


def set_server_prefix(id: int or str, prefix: str):
    global SERVER_PREFIXES
    SERVER_PREFIXES[str(id)] = prefix
    json_rw.set_json('server_prefixes.json', SERVER_PREFIXES)


def get_prefix(_, message):
    id = message.guild.id
    return get_server_prefix(id)
'''



# bot = F1Info(command_prefix = get_prefix, case_insensitive=True) TODO: Look above
bot = F1Info(command_prefix = default_prefix, case_insensitive=True)


#BOT_TOKEN = open("token.txt", 'r').readlines()[0].strip()

import os
BOT_TOKEN = os.environ.get('TOKEN')
if BOT_TOKEN == None:
    raise Exception("Token was None")


bot.run(BOT_TOKEN)

