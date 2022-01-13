#!/usr/bin/env python
import discord
# We're using py-cord https://docs.pycord.dev/en/master/index.html
import os, random, asyncio
from datetime import datetime

## SECURITY WARNING: if this file becomes public, we need a way to
## make this secret. Probably import the *RIGHT* discord in repl.it
## and follow the tutorial to run continuously in the cloud.
##

# TODO
# * when you ask for a quiz in the wrong channel, start the quiz in the right channel!
#
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


@bot.slash_command(guild_ids=GUILD_IDS,description="Help message for PoGoQuizBot")
async def pqhelp(ctx):
    help_message = f"""Welcome to the Pokemon Go Quiz Bot!
/qa rock
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
"""
    await ctx.respond(help_message)


CATEGORY_NAME = 'POGOQUIZ'
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
    # Check to see if it exists!
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
        txt = f'{ctx.author}, your quiz in {get_private_channel(ctx).mention}!\n(asking for future quizzes there will help reduce clutter in {ctx.channel.mention}).'
        await ctx.respond(txt)
        return

async def get_attackers_and_defenders(attacker, defender, num_questions, ctx):
    random_attacker, random_defender = False, False
    if attacker == 'random':
        random_attacker = True
    if defender == 'random':
        random_defender = True
    if attacker != 'random' and attacker not in efectiveness:
        await ctx.respond(f"Attacker type {attacker} unknown. \nI'm choosing rock because nothing beats that.\nPlease either use 'random' or one of {list(effectiveness.keys())}")

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
        if question_mode == 'attacker':
            mymsg = await msg.reply(f'damage is ??? when {attacker} is attacking against {defender}')
        else:
            mymsg = await msg.reply(f'damage is ??? when {defender} is defending against {attacker}')
        for i in ('double resisted','not very effective','neutral','super effective'):
            await mymsg.add_reaction(emoji=effectiveness_to_emoji[i])

        def check(reaction,user):
            """If you give a check function, it ignores all
            reactions that fail the check. So they can react a bunch
            of wrong things and you'll wait for the right one.
            """
            result = (user == guesser) and (str(reaction.emoji) == right_answer_emoji)
            return result

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=QUIZ_TIMEOUT, check=check)
        except asyncio.TimeoutError:
            await mymsg.channel.send('You timed out')
            break
        else:
            await mymsg.add_reaction(emoji='👍')
            
@bot.slash_command(guild_ids=GUILD_IDS,description="Attacker: normal, rock, random ...")
async def qa(ctx, attacker: str, num_questions:int=18,):
    await check_channel_and_redirect_user(ctx)
    channel = get_private_channel(ctx)
    
    # Set up lists of attackers and defenders
    if num_questions > len(effectiveness) or num_questions < 1:
        await ctx.respond(f'You asked for {num_questions} questions, but there are only {len(effectiveness)} types, so I want a number between 1 and {len(effectiveness)}. I will ask you {len(effectiveness)} questions')
        num_questions = len(effectiveness)

    if attacker == 'random':
        attackers = [random.choice(list(effectiveness.keys())) for i in num_questions]
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
    await channel.send('The quiz is over!')

@bot.slash_command(guild_ids=GUILD_IDS,description="Defender: normal, rock, random ...")
async def qd(ctx, defender: str, num_questions:int=18,):
    await check_channel_and_redirect_user(ctx)
    channel = get_private_channel(ctx)
    
    # Set up lists of attackers and defenders
    if num_questions > len(effectiveness) or num_questions < 1:
        await ctx.respond(f'You asked for {num_questions} questions, but there are only {len(effectiveness)} types, so I want a number between 1 and {len(effectiveness)}. I will ask you {len(effectiveness)} questions')
        num_questions = len(effectiveness)

    if defender == 'random':
        defenders = [random.choice(list(effectiveness.keys())) for i in num_questions]
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

@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))

from discord.ext import tasks
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
        time_in_existence = CHANNEL_ACTIVITY[c]['last'] - CHANNEL_ACTIVITY[c]['last']
        time_since_active = datetime.now() - CHANNEL_ACTIVITY[c]['last']
        if time_since_active.seconds > CHANNEL_TIMEOUT:
            print(f'Time to delete {c}')
            del CHANNEL_ACTIVITY[c]
            await c.delete()
cleanup_channels.start()

bot.run(TOKEN)
