__author__ = "PierreV23 https://github.com/PierreV23"
__copyright__ = "Copyright (C) 2022 Pièrre (A.P.) V"
__license__ = "GNU General Public License v3.0"
__author__forked__ = "" # NOTE: Put your version of `__author__` in here.


from disnake.ext import commands
import datetime
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
        if weekend.Race.datetime.timestamp() - time.time() > 3*60*60: # TODO: Less hours?
            break
        else:
            F1ROUND += 1
            weekend = ergastwrapper.get_weekend(F1YEAR, F1ROUND)
    return weekend


def initialize_commands(self): # NOTE: This exists so i can collapse all commands in my IDE.
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
                filtered = list(filter(lambda sess: (sess.datetime.timestamp() - time.time() >= 0), wknd.sessions))
                ######################################################################################################### NOTE: I was bored
                while bool(filtered) == False:                                                                          # NOTE: I was bored
                    global F1ROUND                                                                                      # NOTE: I was bored
                    F1ROUND += 1                                                                                        # NOTE: I was bored
                    wknd = get_current_weekend()                                                                    	# NOTE: I was bored
                    filtered = list(filter(lambda sess: (sess.datetime.timestamp() - time.time() >= 0), wknd.sessions)) # NOTE: I was bored
                ######################################################################################################### NOTE: I was bored
                session = min(filtered, key = lambda sess: sess.datetime.timestamp())
                global F1ROUND
                F1ROUND -= 1 # .
            else:
                session = wknd.get_session(ergastwrapper.SessionType(cmd))
            
            unix = int(session.datetime.timestamp())
            circuit = session.circuit
            await ctx.channel.send(f"**{circuit.name},  {circuit.locality},  {circuit.country}**\n> `{session.name} happens on `<t:{unix}:F>\n> `{session.name} starts `<t:{unix}:R>")
            # delta = session.datetime - dt.datetime.utcnow()
            # await ctx.channel.send(f"**{circuit.name},  {circuit.locality},  {circuit.country}**\n> `{session.name} happens on `<t:{unix}:F>\n> `{session.name} starts ``in {delta.hours} hours, {delta.minutes} minutes and {delta.seconds} seconds.`")
        except Exception as e:
            ergastwrapper.cache.reset_cache()
            print("Exception occured when trying to send session timings.", e)
            await ctx.channel.send(f"Something went wrong, try again later.")
    

    @self.command(name='creator', aliases=['owner', 'maker', 'bot', 'github'])
    async def send_creator(ctx: commands.Context):
        text = f"\n**Author**: `{__author__}`\n**Copyright**: `{__copyright__}`\n**License**: `{__license__}`" + (f"\n**Author of fork**: `{__author__forked__}`" if __author__forked__ else "")
        await ctx.channel.send(text)
    

    @self.command(name='prefix')
    async def set_prefix(ctx: commands.Context):
        if ctx.author.guild_permissions.administrator:
            prefix = get_server_prefix(ctx.guid.id)
            _temp = ctx.message.content.split(' ')
            newprefix = _temp[1]
            if len(_temp) < 2:
                await ctx.channel.send(f"Something went wrong changing the prefix. The command should be formatted like: `{prefix}prefix %insert_new_prefix%`")
            else:
                set_server_prefix(ctx.guild.id, newprefix)
                await ctx.channel.send(f"Prefix changed from `{prefix}` to `{newprefix}`")



class F1Info(commands.Bot):
    def __init__(self, *args, **kwargs):
        commands.Bot.__init__(self, *args, **kwargs)
        initialize_commands(self)        


    async def on_ready(self):
        print(f"The bot is ready! - {datetime.datetime.now()}")
    

    async def on_message(self, ctx):
        await self.process_commands(ctx)
        # print(ctx.content) # debug purposes 🙄
        #if ctx.content == f'<@{}>' # TODO: get bot id
        #await ctx.author.dm_channel.channel. # TODO: fix this shit
        # TODO: Make it so a message containing just a tag of the bot sends a dm to the guy pinging the bot, incase people forget prefixes....



SERVER_PREFIXES: dict[int, str] = json_rw.get_json('server_prefixes.json')
default_prefix = '-'


def get_server_prefix(id: int): 
    return SERVER_PREFIXES.get(id, default_prefix)


def set_server_prefix(id, prefix):
    global SERVER_PREFIXES
    SERVER_PREFIXES[id] = prefix
    json_rw.set_json('server_prefixes.json', SERVER_PREFIXES)


def get_prefix(_, message):
    id = message.guild.id
    return get_server_prefix(id)




bot = F1Info(command_prefix = get_prefix, case_insensitive=True)


BOT_TOKEN = open("token.txt", 'r').readlines()[0].strip()


bot.run(BOT_TOKEN)

