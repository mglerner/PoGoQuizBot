#!/usr/bin/env python
import discord
# We're using py-cord https://docs.pycord.dev/en/master/index.html
import os, random, asyncio
from datetime import datetime

## SECURITY WARNING: if this file becomes public, we need a way to
## make this secret. Probably import the *RIGHT* discord in repl.it
## and follow the tutorial to run continuously in the cloud.
##

## TODO:
## make it make a channel for you.

# Notes
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

"""I think I want channel permissions members

channe.created_at gives the creation time in UTC
"""

CHANNEL_ACTIVITY = {}
CHANNEL_TIMEOUT = 600 # in seconds

def record_channel_activity(ctx):
    if not check_channel(ctx):
        return
    c = str(ctx.channel)
    if c not in CHANNEL_ACTIVITY:
        CHANNEL_ACTIVITY[c] = {'created':ctx.channel.created_at,'last':ctx.channel.created_at,'channel':ctx.channel}
    CHANNEL_ACTIVITY[c]['last'] = datetime.now()

def get_private_channel_name(ctx):
    """
    No special characters, has to be all lowercase. Discord.py will make it all lowercase regardless.
    """
    stripped_name = str(ctx.author)
    stripped_name = ''.join(i for i in stripped_name if i.isalnum())
    if not stripped_name:
        stripped_name = 'suchAFancyName'
    stripped_name = stripped_name.lower()
    return f'pogoquiz-{stripped_name}'

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
    category_name = 'POGOQUIZ'
    category = discord.utils.get(ctx.guild.categories, name=category_name)
    if category is None:
        category = await ctx.guild.create_category(category_name,reason=f'Creating PoGo quiz category')
    channel = await ctx.guild.create_text_channel(channel_name,
                                                      overwrites=overwrites, reason=f"Creating PoGo quiz channel for user {ctx.author}",
                                                      category=category)

# Obviously qa and qd should be refactored. The main reason that they
# aren't is because of the `break` for the timeout in the middle of
# the while loop.
@bot.slash_command(guild_ids=GUILD_IDS,description="Attacker: normal, rock, random ...")
async def qa(ctx, attacker: str, num_questions:int=18,):
    if not check_channel(ctx):
        await ctx.respond(f'{ctx.author}, check #{get_private_channel_name(ctx)} for your quiz results!\n(The bot will only respond there, not in {ctx.channel}).')
        if not discord.utils.get(ctx.guild.channels,name=get_private_channel_name(ctx)):
            await create_channel(ctx)
        return
    if num_questions > len(effectiveness) or num_questions < 1:
        await ctx.respond(f'You asked for {num_questions} questions, but there are only {len(effectiveness)} types, so I want a number between 1 and {len(effectiveness)}. I will ask you {len(effectiveness)} questions')
        num_questions = len(effectiveness)
    random_attacker = False
    if attacker == 'random':
        random_attacker = True
    defenders = list(effectiveness.keys())
    random.shuffle(defenders)
    defenders = defenders[:num_questions]
    question_count = 0
    while question_count < num_questions:
        defender = defenders.pop()
        if random_attacker:
            attacker = random.choice(list(effectiveness.keys()))
        record_channel_activity(ctx)
        if attacker not in effectiveness or defender not in effectiveness:
            await ctx.respond(f'Sorry, I could not find one of the two types you wanted: {attacker} or {defender}')
            break

        right_answer = effectiveness[attacker][defender]
        right_answer_emoji = effectiveness_to_emoji[effectiveness_to_words[right_answer]]

        # OK, this is baffling to me. The first time through, it looks like you want orgmsg.
        # But then orgmsg never changes. So, on subsequent iterations, we want resp.
        # AND I DON'T KNOW HOW TO GET THAT! So, a really fragile check to see if it has the add_reaction method seems to work.
        resp = await ctx.respond(f'damage is ??? when {attacker} is attacking against {defender}')
        orgmsg = await ctx.interaction.original_message()
        if hasattr(resp,'add_reaction'):
            mymsg = resp
        else:
            mymsg = orgmsg
        for i in ('double resisted','not very effective','neutral','super effective'):
            await mymsg.add_reaction(emoji=effectiveness_to_emoji[i])
        def check(reaction,user):
            """If you give a check function, it ignores all
            reactions that fail the check. So they can react a bunch
            of wrong things and you'll wait for the right one.
            """
            result = (user == ctx.author and str(reaction.emoji) == right_answer_emoji)
            return result
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await ctx.channel.send('You timed out')
            break
        else:
            await mymsg.add_reaction(emoji='👍')
            question_count = question_count + 1
    await ctx.channel.send('The quiz is over!')

# Obviously qa and qd should be refactored. The main reason that they
# aren't is because of the `break` for the timeout in the middle of
# the while loop.
@bot.slash_command(guild_ids=GUILD_IDS,description="Defender: normal, rock, random ...")
async def qd(ctx, defender: str, num_questions:int=18,):
    if not check_channel(ctx):
        embed = discord.Embed()
        embed.description = f'{ctx.author}, check #{get_private_channel_name(ctx)} for your quiz results!\n(The bot will only respond there, not in #{ctx.channel}).'
        # TODO: FIXME: need to record an interaction with the channel at this point!
        # Otherwise, they can create the channel, never touch it, and it never gets deleted.
        # Maybe the loop should also find a way to loop over all channels in the POGO quiz category too?
        await ctx.respond(embed=embed)
        if not discord.utils.get(ctx.guild.channels,name=get_private_channel_name(ctx)):
            await create_channel(ctx)
        return
    if num_questions > len(effectiveness) or num_questions < 1:
        await ctx.respond(f'You asked for {num_questions} questions, but there are only {len(effectiveness)} types, so I want a number between 1 and {len(effectiveness)}. I will ask you {len(effectiveness)} questions')
        num_questions = len(effectiveness)
    random_defender = False
    if defender == 'random':
        random_defender = True
    attackers = list(effectiveness.keys())
    random.shuffle(attackers)
    attackers = attackers[:num_questions]
    question_count = 0
    while question_count < num_questions:
        attacker = attackers.pop()
        if random_defender:
            defender = random.choice(list(effectiveness.keys()))
        record_channel_activity(ctx)
        if attacker not in effectiveness or defender not in effectiveness:
            await ctx.respond(f'Sorry, I could not find one of the two types you wanted: {attacker} or {defender}')
            break

        right_answer = effectiveness[attacker][defender]
        right_answer_emoji = effectiveness_to_emoji[effectiveness_to_words[right_answer]]

        # OK, this is baffling to me. The first time through, it looks like you want orgmsg.
        # But then orgmsg never changes. So, on subsequent iterations, we want resp.
        # AND I DON'T KNOW HOW TO GET THAT! So, a really fragile check to see if it has the add_reaction method seems to work.
        resp = await ctx.respond(f'damage is ??? when {attacker} is attacking against {defender}')
        orgmsg = await ctx.interaction.original_message()
        if hasattr(resp,'add_reaction'):
            mymsg = resp
        else:
            mymsg = orgmsg
        for i in ('double resisted','not very effective','neutral','super effective'):
            await mymsg.add_reaction(emoji=effectiveness_to_emoji[i])
        def check(reaction,user):
            """If you give a check function, it ignores all
            reactions that fail the check. So they can react a bunch
            of wrong things and you'll wait for the right one.
            """
            result = (user == ctx.author and str(reaction.emoji) == right_answer_emoji)
            return result
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await ctx.channel.send('You timed out')
            break
        else:
            await mymsg.add_reaction(emoji='👍')
            question_count = question_count + 1
    await ctx.channel.send('The quiz is over!')

@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))

#async def my_background_task():
#    await bot.wait_until_ready()
#    print('frog')
#    while not bot.is_closed:
#        print('cow')
#        await asyncio.sleep(1) # task runs every 1 seconds
#bot.loop.create_task(my_background_task())
from discord.ext import tasks
@tasks.loop(seconds=5.0)
async def cleanup_channels():
    """Delete old channels.

    Channels get deleted if they're inactive for longer than
    CHANNEL_TIMEOUT seconds. We could also delete them after a fixed
    period of time regardless.
    """
    # Lots of example code uses a while not bot.is_closed loop. I
    # don't think we need that.
    channels = list(CHANNEL_ACTIVITY.keys())
    for c in channels:
        time_in_existence = CHANNEL_ACTIVITY[c]['last'] - CHANNEL_ACTIVITY[c]['last']
        time_since_active = datetime.now() - CHANNEL_ACTIVITY[c]['last']
        if time_since_active.seconds > CHANNEL_TIMEOUT:
            print(f'Time to delete {c}')
            await CHANNEL_ACTIVITY[c]['channel'].delete()
            del CHANNEL_ACTIVITY[c]
cleanup_channels.start()

bot.run(TOKEN)


if 0:

    client = discord.Client()

    @client.event
    async def on_ready():
        print("We have logged in as {0.user}".format(client))

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        if message.content.startswith('!hello'):
            await message.channel.send("Hello player farts!")
        elif message.content.startswith('!help'):
            await message.channel.send(f"""Welcome to the Pokemon Go type quiz bot.
    !q1 quizzes one explicit type matchup.
    !q1 rock ground
    tells you how effective rock is when attacking ground.
    !qa quizzes you about one type as an attacker
    !qa rock
    gives you a quiz about rock as an attacker against a random type.
    !qa rock 3
    gives you three quizzes about rock as an attacker against a random type.

    !qa steel
    gives you a quiz about steel as an defender against a random type.
    !qa steel 3
    gives you three quizzes about steel as an defender against a random type.

    You can also run quizzes against random types. For example
    !qa random 3
    gives you three quizzes about random types as attackers against random types

    This quiz uses emojis to represent type effectiveness. Here's what the emojis mean:
    {effectiveness_to_emoji['double resisted']}: double resisted
    {effectiveness_to_emoji['not very effective']}: not very effective
    {effectiveness_to_emoji['neutral']}: neutral
    {effectiveness_to_emoji['super effective']}: super effective
    """)
        elif message.content.startswith('!q1 '):
            parts = message.content.split()
            if len(parts) == 3:
                attacker, defender = parts[1], parts[2]
                e = effectiveness[attacker][defender]
                await message.channel.send(f'{attacker} is {effectiveness_to_words[e]} against {defender}')
            else:
                await message.channel.send("Sorry, I didn't understand that. Type !help for help.")
        elif message.content.startswith('!qa ') or message.content.startswith('!qd '):
            parts = message.content.split()
            random_attacker, random_defender = False, False
            if message.content.startswith('!qa'):
                attacking_or_defending = 'attacking'
            elif message.content.startswith('!qd'):
                attacking_or_defending = 'defending'
            else:
                await message.channel.send(f'Sorry, I did not understand the command {message.content}. Please type !help for help')
            num_questions = 1
            if len(parts) == 3:
                try:
                    num_questions = int(parts[2])
                    parts = parts[:2]
                except:
                    await message.channel.send(f"Sorry, I did not understand {parts[2]} as a number.")
            if len(parts) == 2 and num_questions >= 1:
                if attacking_or_defending == 'attacking':
                    attacker = parts[1]
                    if attacker == 'random':
                        random_attacker = True
                    defender = random.choice(list(effectiveness.keys())) # never gets used, but it's cool. it gets defined.
                else:
                    defender = parts[1]
                    if defender == 'random':
                        random_defender = True
                    attacker = random.choice(list(effectiveness.keys())) # never gets used, but it's cool. it gets defined.
                question_count = 0
                while question_count < num_questions:
                    if attacking_or_defending == 'attacking' or random_defender:
                        defender = random.choice(list(effectiveness.keys()))
                    if attacking_or_defending == 'defending' or random_attacker:
                        attacker = random.choice(list(effectiveness.keys()))
                    # This check needs to happen before the first lookup
                    if attacker not in effectiveness or defender not in effectiveness:
                        await message.channel.send(f'Sorry, I could not find one of the two types you wanted: {attacker} or {defender}')
                        break
                    right_answer = effectiveness[attacker][defender]
                    right_answer_emoji = effectiveness_to_emoji[effectiveness_to_words[right_answer]]

                    if attacking_or_defending == 'attacking':
                        mymsg = await message.channel.send(f'damage is ??? when {attacker} is attacking against {defender}')
                    else:
                        mymsg = await message.channel.send(f'damage is ??? when {defender} is defending against {attacker}')
                    for i in ('double resisted','not very effective','neutral','super effective'):
                        await mymsg.add_reaction(effectiveness_to_emoji[i])

                    def check(reaction,user):
                        """If you give a check function, it ignores all
                        reactions that fail the check. So they can react a bunch
                        of wrong things and you'll wait for the right one.
                        """
                        global num_wrong
                        result = (user == message.author and str(reaction.emoji) == right_answer_emoji)
                        return result

                    try:
                        reaction, user = await client.wait_for('reaction_add', timeout=10.0, check=check)
                    except asyncio.TimeoutError:
                        await message.channel.send('You timed out')
                        break
                    else:
                        await mymsg.add_reaction('👍')
                        question_count = question_count + 1
                await message.channel.send('The quiz is over!')

            else:
                await message.channel.send(f"Sorry, I think you told me to ask {num_questions} questions. Type !help for help.")
        elif message.content.startswith('!'):
            await message.channel.send("Sorry, I know you're typing a command, but I don't know what command. Type !help for help.")

    #@client.event
    #async def on_reaction_add(reaction, user):
    #    print(f'I got reaction {reaction} from user {user}')

    """
    Notes for ourselves:
    when someone gets it right or wrong, I would like to
    use msg.edit to change the text of it!
    """
    #client.run(TOKEN)
