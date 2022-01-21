#!/usr/bin/env python
import os, random, asyncio, json, math
from datetime import datetime
# We're using py-cord https://docs.pycord.dev/en/master/index.html
import discord
from discord.ext import tasks
from discord.ui import Button, View

## SECURITY WARNING: if this file becomes public, we need a way to
## make this secret. Probably import the *RIGHT* discord in repl.it
## and follow the tutorial to run continuously in the cloud.
##

# TODO
# * should tell users it's question N/M so they know.
#

# USEFUL LINKS
# * freecodecamp encouragebot
# * buttons: https://www.youtube.com/watch?v=kNUuYEWGOxA and apparently some exampels on discord.

"""
https://discordpy.readthedocs.io/en/latest/api.html#discord.Guild.create_text_channel
probably want to create a secret channel!
this should grow up a bit and become a Bot. And even use slash commands.
Also want to support something like !qt pps to quiz specific teams
pps is

A9 (ice fairy) with a fairy fast move and an ice and psychic charge move
sableye (dark ghost) with a ghost fast move and a dark and normal charge move
cofagrigus (ghost) with a ghost and a dark charge move

"""

from data import effectiveness, effectiveness_to_emoji, emoji_to_effectiveness, effectiveness_to_words
from SecretInfo import TOKEN, GUILD_IDS

bot = discord.Bot()

MOVES_FILE = 'external/pvpoke/src/data/gamemaster.json'
MOVES_FILE = 'gamemaster.json'
RANKINGS_FILES = { # Eh. We can just use the top overall rankings.
    'great':{
        'overall': 'rankings-1500.json',
        #'overall': 'external/pvpoke/src/data/rankings/gobattleleague/overall/rankings-1500.json',
        #'attackers': 'external/pvpoke/src/data/rankings/gobattleleague/attackers/rankings-1500.json',
        #'chargers': 'external/pvpoke/src/data/rankings/gobattleleague/chargers/rankings-1500.json',
        #'closers': 'external/pvpoke/src/data/rankings/gobattleleague/closers/rankings-1500.json',
        #'consistency': 'external/pvpoke/src/data/rankings/gobattleleague/consistency/rankings-1500.json',
        #'leads': 'external/pvpoke/src/data/rankings/gobattleleague/leads/rankings-1500.json',
        #'switches': 'external/pvpoke/src/data/rankings/gobattleleague/switches/rankings-1500.json',
        },
    'ultra':{
        'overall': 'rankings-2500.json',
        #'overall': 'external/pvpoke/src/data/rankings/gobattleleague/overall/rankings-2500.json',
        #'attackers': 'external/pvpoke/src/data/rankings/gobattleleague/attackers/rankings-2500.json',
        #'chargers': 'external/pvpoke/src/data/rankings/gobattleleague/chargers/rankings-2500.json',
        #'closers': 'external/pvpoke/src/data/rankings/gobattleleague/closers/rankings-2500.json',
        #'consistency': 'external/pvpoke/src/data/rankings/gobattleleague/consistency/rankings-2500.json',
        #'leads': 'external/pvpoke/src/data/rankings/gobattleleague/leads/rankings-2500.json',
        #'switches': 'external/pvpoke/src/data/rankings/gobattleleague/switches/rankings-2500.json',
        },
    'master':{
        'overall': 'rankings-10000.json',
        #'overall': 'external/pvpoke/src/data/rankings/gobattleleague/overall/rankings-10000.json',
        #'attackers': 'external/pvpoke/src/data/rankings/gobattleleague/attackers/rankings-10000.json',
        #'chargers': 'external/pvpoke/src/data/rankings/gobattleleague/chargers/rankings-10000.json',
        #'closers': 'external/pvpoke/src/data/rankings/gobattleleague/closers/rankings-10000.json',
        #'consistency': 'external/pvpoke/src/data/rankings/gobattleleague/consistency/rankings-10000.json',
        #'leads': 'external/pvpoke/src/data/rankings/gobattleleague/leads/rankings-10000.json',
        #'switches': 'external/pvpoke/src/data/rankings/gobattleleague/switches/rankings-10000.json',
        },
}
        
    
def get_moves():
    f = open(MOVES_FILE)
    mf = json.load(f)
    fastmoves = {i['moveId']:i for i in mf['moves'] if i['energyGain'] != 0}
    chargedmoves = {i['moveId']:i for i in mf['moves'] if i['energyGain'] == 0}
    return fastmoves, chargedmoves
def get_rankings():
    """Get rankings from json files

    make sure to sort the results by rank, best pokemon first
    """
    rankings = {}
    for league in RANKINGS_FILES:
        rankings[league] = {}
        for ranktype in RANKINGS_FILES[league]:
            fn = RANKINGS_FILES[league][ranktype]
            f = open(fn)
            r = json.load(f)
            r.sort(key=lambda x: x['rating'], reverse=True)
            rankings[league][ranktype] = r
    return rankings

FASTMOVES, CHARGEDMOVES = get_moves()
RANKINGS = get_rankings()

@bot.slash_command(guild_ids=GUILD_IDS,description="Help message for PoGoQuizBot")
async def pqhelp(ctx):
    embed = discord.Embed(title="PoGo Quiz Bot help",
                              description="Here's everything I can do. Please note that I borrowed all of the move and ranking data from PvPoke."
                              )
    embed.add_field(name="Type matchups",
                        value=f"""/qa rock
gives you a quiz about rock as an attacker against all other types.
/qa rock 2
gives you a quiz about rock as an attacker against two other types.
/qa random
gives you a quiz about a random type as an attacker against all other types.

/qd command do the same as qa, except that you specify the defender rather than the attacker.

This quiz uses emojis to represent type effectiveness. Here's what the emojis mean:
{effectiveness_to_emoji['double resisted']}: double resisted
{effectiveness_to_emoji['not very effective']}: not very effective
{effectiveness_to_emoji['neutral']}: neutral
{effectiveness_to_emoji['super effective']}: super effective

""",)
    embed.add_field(name="Move counts",
                        value=f"""/qm1 bastiodon
gives you a quiz about one specific pokemon's move counts. In this case, bastiodon. You can also tell it how many questions to ask you.
/qm
gives you a quiz about the top 100 pokemon from a given league, using PvPoke's overall rankings. You can tell it which league (great, ultra, master). You can also tell it how many questions to ask you.

I personally can't count past ten, and I didn't see any good emojis for 11+, so you just select "more" for anything that takes more than 10 moves.""",)
    await ctx.respond(embed=embed)


CATEGORY_NAME = 'POGOQUIZ'
CHANNELS_WE_DO_NOT_DELETE = ["about-quizbot",]
CHANNEL_TIMEOUT = 600 # in seconds
QUIZ_TIMEOUT = 15.0

CHANNEL_ACTIVITY = {}
def record_channel_activity(channel):
    """Record the fact that we have seen activity in a channel.

    This is so that another function can delete inactive channels. That
    function should only delete channels in CATEGORY_NAME. But, out of
    pure paranoia, we'll only record channels in that category anyway.
    """
    if str(channel.category) != CATEGORY_NAME:
        print(f'Oh trouble, {channel.category} != {CATEGORY_NAME}') #MGL: TODO: FIXME
    #category = discord.utils.get(ctx.guild.categories, name=CATEGORY_NAME)

    if channel not in CHANNEL_ACTIVITY:
        CHANNEL_ACTIVITY[channel] = {'created':datetime.now(),'last':datetime.now()}
    CHANNEL_ACTIVITY[channel]['last'] = datetime.now()

def get_private_channel_name(ctx):
    """
    No special characters, has to be all lowercase. Discord.py will make it all lowercase regardless.

    TODO: does this work for multiple servesr (guilds)? Make my own and check.
    """
    stripped_name = str(ctx.author)
    stripped_name = ''.join(i for i in stripped_name if i.isalnum())
    if not stripped_name:
        stripped_name = 'suchAFancyName'
    stripped_name = stripped_name.lower()
    return f'pogoquiz-{stripped_name}'
def get_private_channel(ctx):
    channel = discord.utils.get(ctx.guild.channels, name=get_private_channel_name(ctx))
    # can be None!
    return channel
def check_channel(ctx):
    return str(ctx.channel) == get_private_channel_name(ctx)

async def create_channel(ctx):
    channel_name = get_private_channel_name(ctx)
    # MGL: TODO: Check to see if it exists!
    #https://stackoverflow.com/questions/67695694/discord-py-is-there-anyways-to-add-members-to-a-private-channel-through-discor
    overwrites = { 
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False), # make private
        ctx.guild.me: discord.PermissionOverwrite(read_messages=True), # add bot to channel
        ctx.author: discord.PermissionOverwrite(read_messages=True), # add original questioner to channel
        }
    user = ctx.author.id
    category = discord.utils.get(ctx.guild.categories, name=CATEGORY_NAME)
    if category is None:
        category = await ctx.guild.create_category(CATEGORY_NAME,reason=f'Creating PoGo quiz category')
    channel = await ctx.guild.create_text_channel(channel_name,
                                                      overwrites=overwrites, reason=f"Creating PoGo quiz channel for user {ctx.author}",
                                                      category=category)

async def check_channel_and_redirect_user(ctx):
    # Maybe also ping in the channel.
    if not check_channel(ctx):
        if not discord.utils.get(ctx.guild.channels,name=get_private_channel_name(ctx)):
            await create_channel(ctx)
        txt = f'{ctx.author}, your quiz is in {get_private_channel(ctx).mention}!\n(asking for future quizzes there will help reduce clutter in {ctx.channel.mention}).'
        await ctx.respond(txt)
        return
    return


async def ask_type_questions(attackers, defenders, channel, question_mode, guesser):
    """Ask the questions.

    question_mode can be attacker or defender

    guesser is the person who is guessing. This listens to every single
    reaction anywhere, so we need to know which ones actually count.

    No exceptions defined here. Can raise asyncio.TimeoutError
    """
    msg = await channel.send("Here's your quiz")
    if question_mode not in ('attacker','defender'):
        question_mode = 'attacker'
    for pogotype in attackers + defenders:
        if pogotype not in effectiveness:
            await msg.reply(f'Sorry, I could not find one of the types you wanted: {pogotype}')
            return
    for (attacker, defender) in zip(attackers,defenders):
        record_channel_activity(channel)
        right_answer = effectiveness[attacker][defender]
        right_answer_emoji = effectiveness_to_emoji[effectiveness_to_words[right_answer]]

        view = View(timeout=QUIZ_TIMEOUT)
        for i in ('double resisted','not very effective','neutral','super effective'):
            emoji = effectiveness_to_emoji[i]
            if emoji == right_answer_emoji:
                async def button_callback(interaction):
                    #await interaction.message.reply('You got it!')
                    await interaction.message.add_reaction(emoji='👍')
                    view.stop()
            else:
                async def button_callback(interaction):
                    #await interaction.message.reply('No sir!')
                    pass
            button = Button(emoji=emoji)
            button.callback = button_callback
            view.add_item(button)
        if question_mode == 'attacker':
            mymsg = await msg.reply(f'damage is ??? when {attacker} is attacking against {defender}',view=view)
        else:
            mymsg = await msg.reply(f'damage is ??? when {defender} is defending against {attacker}',view=view)
        await view.wait()
    return
            
@bot.slash_command(guild_ids=GUILD_IDS,description="Attacker: normal, rock, random ...")
async def qa(ctx, attacker: str, num_questions:int=18,):
    await check_channel_and_redirect_user(ctx)
    channel = get_private_channel(ctx)
    
    # Set up lists of attackers and defenders
    if num_questions > len(effectiveness) or num_questions < 1:
        await ctx.respond(f'You asked for {num_questions} questions, but there are only {len(effectiveness)} types, so I want a number between 1 and {len(effectiveness)}. I will ask you {len(effectiveness)} questions')
        num_questions = len(effectiveness)

    if attacker == 'random':
        attackers = [random.choice(list(effectiveness.keys())) for i in range(num_questions)]
    else:
        attackers = [attacker]*num_questions
    defenders = list(effectiveness.keys())
    random.shuffle(defenders)
    defenders = defenders[:num_questions]

    # Ask N questions.
    try:
         await ask_type_questions(attackers, defenders, channel, question_mode='attacker', guesser=ctx.user)
    except asyncio.TimeoutError:
        await channel.send('You timed out') # Where to send this? Could use ctx to send to original channel.
    await channel.send(f'The quiz is over!')

@bot.slash_command(guild_ids=GUILD_IDS,description="Defender: normal, rock, random ...")
async def qd(ctx, defender: str, num_questions:int=18,):
    await check_channel_and_redirect_user(ctx)
    channel = get_private_channel(ctx)
    
    # Set up lists of attackers and defenders
    if num_questions > len(effectiveness) or num_questions < 1:
        await ctx.respond(f'You asked for {num_questions} questions, but there are only {len(effectiveness)} types, so I want a number between 1 and {len(effectiveness)}. I will ask you {len(effectiveness)} questions')
        num_questions = len(effectiveness)

    if defender == 'random':
        defenders = [random.choice(list(effectiveness.keys())) for i in range(num_questions)]
    else:
        defenders = [defender]*num_questions
    attackers = list(effectiveness.keys())
    random.shuffle(attackers)
    attackers = attackers[:num_questions]

    # Ask N questions.
    try:
        await ask_type_questions(attackers, defenders, channel, question_mode='defender', guesser=ctx.user)
    except asyncio.TimeoutError:
        await channel.send('You timed out') # Where to send this? Could use ctx to send to original channel.
    await channel.send('The quiz is over!')

count_emojis = {
    1:"1️⃣",
    2:"2️⃣",
    3:"3️⃣",
    4:"4️⃣",
    5:"5️⃣",
    6:"6️⃣",
    7:"7️⃣",
    8:"8️⃣",
    9:"9️⃣",
    10:"🔟",
#    11:"⓫",
#    12:"⓬",
#    13:"⓭",
#    14:"⓮",
#    15:"⓯",
    'more':"🔼",
    }

async def ask_moves_questions(num_questions, mons, channel, guesser):
    # I can't decide if this looks better wtih emoji or text labels.
    # Since I can use text labels, I could definitely go all the way
    # up to 20 or whatever for low-energy moves.
    msg = await channel.send("Here is your quiz")
    for question_number in range(num_questions):
        record_channel_activity(channel)
        mon = random.choice(mons)
        if False: # random
            fast_move = random.choice(mon['moves']['fastMoves'])['moveId']
            charged_move = random.choice(mon['moves']['chargedMoves'])['moveId']
        else:
            # moveset lists fast move cm1, cm2.
            fast_move = mon['moveset'][0] 
            charged_move = random.choice(mon['moveset'][1:])
        fast_move_name = FASTMOVES[fast_move]['name']
        charged_move_name = CHARGEDMOVES[charged_move]['name']
        right_answer_full = CHARGEDMOVES[charged_move]['energy'] / FASTMOVES[fast_move]['energyGain']
        right_answer = int(math.ceil(right_answer_full))
        if right_answer > 10:
            right_answer = 'more'
        right_answer_emoji = count_emojis[right_answer]

        if 0:
            class MyView(View):
                def __init__(self):#,ctx):
                    super().__init__(timeout=QUIZ_TIMEOUT)

                for i in (1,2,3,4,5,6,7,8,9,10,'more'):
                    print("Doing",i)
                    emoji = count_emojis[i]
                    if emoji == right_answer_emoji:
                        @discord.ui.button(label=i)
                        async def button_callback(self,button,interaction):
                            button.style = discord.ButtonStyle.green
                            self.stop()
                    else:
                        @discord.ui.button(label=i)
                        async def button_callback(self,button,interaction):
                            button.style = discord.ButtonStyle.red
            view = MyView()
               
        if 1:
            view = View(timeout=QUIZ_TIMEOUT)
            for i in (1,2,3,4,5,6,7,8,9,10,'more'):
                emoji = count_emojis[i]
                button = Button(label=i)
                if emoji == right_answer_emoji:
                    async def button_callback(interaction):
                        button.style = discord.ButtonStyle.green
                        await interaction.message.add_reaction(emoji='👍')
                        if right_answer == 'more':
                            await interaction.message.reply(f"Yeah, it's {right_answer_full:g}")
                        view.stop()
                else:
                    def get_button_callback():
                        async def button_callback(interaction,button=button):
                            button.style = discord.ButtonStyle.red
                            print(f"I think {interaction.user} clicked the button with the wrong answer")
                            print(f'The button has label {button.label}')
                            button.label = 'FROGS'
                            pass
                        return button_callback
                    button_callback = get_button_callback()
                #button = Button(emoji=emoji)
                button.callback = button_callback
                view.add_item(button)

        mymsg = await msg.reply(f"How many {fast_move_name}s does it take {mon['speciesName']} to get to one {charged_move_name}?",
                                    view=view)
        await view.wait()
        
@bot.slash_command(guild_ids=GUILD_IDS, description="Move counts for top 100 pokemon")
#async def qm(ctx, league:str='great', ranktype:str='overall', num_questions:int=5):
async def qm(ctx, league:str='great', num_questions:int=5):
    await check_channel_and_redirect_user(ctx)
    channel = get_private_channel(ctx)
    ranktype='overall'
    
    if num_questions < 1:
        await ctx.respond(f"You asked for {num_questions} questions, but I'm giving you 1 instead")
        num_questions = 1
    if league not in RANKINGS:
        await ctx.respond("League must be one of " + ','.join(RANKINGS.keys()))
        return
    if ranktype not in RANKINGS[league]:
        await ctx.respond("Ranking type must be one of " + ",".join(RANKINGS[league].keys()))
        return
    try:
        mons = RANKINGS[league][ranktype][:100]
        await ask_moves_questions(num_questions, mons, channel, guesser=ctx.user)
    except asyncio.TimeoutError:
        await channel.send('You timed out') # Where to send this? Could use ctx to send to original channel.
    await channel.send('The quiz is over!')

@bot.slash_command(guild_ids=GUILD_IDS, description="Move counts for single pokemon")
async def qm1(ctx, pokemon:str, num_questions:int=5):
    await check_channel_and_redirect_user(ctx)
    channel = get_private_channel(ctx)

    if num_questions < 1:
        await ctx.respond(f"You asked for {num_questions} questions, but I'm giving you 1 instead")
        num_questions = 1
    found_it = False
    for league in ('great','ultra','master'):
        for mon in RANKINGS[league]['overall']:
            if pokemon in (mon['speciesId'],mon['speciesName']):
                pokemon = mon
                found_it = True
                break
        if found_it:
            break
    else:
        await ctx.respond(f"Could not find {pokemon} in the rankings. Did you use all lowercase letters?")
        print(list(RANKINGS['great']['overall'].keys())[:5])
        return
    
    try:
        await ask_moves_questions(num_questions, [pokemon], channel, guesser=ctx.user)
    except asyncio.TimeoutError:
        await channel.send('You timed out') # Where to send this? Could use ctx to send to original channel.
    await channel.send('The quiz is over!')

    
    
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user} and are looking for GUILDS {GUILD_IDS}<")

@tasks.loop(seconds=5.0)
async def cleanup_channels():
    """Delete old channels.

    Channels get deleted if they're inactive for longer than
    CHANNEL_TIMEOUT seconds. We could also delete them after a fixed
    period of time regardless.

    We carefully check to make sure the category matches CATEGORY_NAME
    before actually deleting.
    """
    # Lots of example code uses a while not bot.is_closed loop. I
    # don't think we need that.
    our_categories = []

    for guild in bot.guilds:
        category = discord.utils.get(guild.categories, name=CATEGORY_NAME)
        our_categories.append(category)
        if category is not None:
            channels = category.channels
            for c in channels:
                if c not in CHANNEL_ACTIVITY:
                    print(f'Oh, I found a channel {c} that was not properly recorded. Fixing.')
                    record_channel_activity(c)
                    
    
    channels = list(CHANNEL_ACTIVITY.keys())
    for c in channels:
        if c.category not in our_categories:
            print(f'Skipping deletion of {c} because {c.category} is unrecognized')
            continue
        if str(c) in CHANNELS_WE_DO_NOT_DELETE:
            #print(f'Skipping deletion of {c} because it is in our list of channels not to delete')
            continue
        time_in_existence = CHANNEL_ACTIVITY[c]['last'] - CHANNEL_ACTIVITY[c]['last']
        time_since_active = datetime.now() - CHANNEL_ACTIVITY[c]['last']
        if time_since_active.seconds > CHANNEL_TIMEOUT:
            print(f'Time to delete {c}')
            del CHANNEL_ACTIVITY[c]
            await c.delete()
cleanup_channels.start()

bot.run(TOKEN)
