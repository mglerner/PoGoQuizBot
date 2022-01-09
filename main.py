#!/usr/bin/env python
import discord
# We're using py-cord https://docs.pycord.dev/en/master/index.html
import os, random, asyncio

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

"""


# effectiveness[attacker][defender]
# key: normal damage is a 1. super effective is a 2. not very effective is a 0.5. immune is a 0.
# The damage multiplioers are 1.6, 1, 0.62 and 0.39
effectiveness_to_words = {1:'normal',2:'super effective',0.5:'not very effective',0:'resisted'}
effectiveness = {
    'normal': {
        'normal':1.0, 'fire':1.0, 'water':1.0, 'electric':1.0, 'grass':1.0, 'ice':1.0, 'fighting':1.0, 'poison':1.0, 'ground':1.0, 
        'flying':1.0, 'psychic':1.0, 'bug':1.0, 'rock':0.5, 'ghost':0.0, 'dragon':1.0, 'dark':1.0, 'steel':0.5, 'fairy':1.0, 
    },
    'fire': {
        'normal':1.0, 'fire':0.5, 'water':0.5, 'electric':1.0, 'grass':2.0, 'ice':2.0, 'fighting':1.0, 'poison':1.0, 'ground':1.0, 
        'flying':1.0, 'psychic':1.0, 'bug':2.0, 'rock':0.5, 'ghost':1.0, 'dragon':0.5, 'dark':1.0, 'steel':2.0, 'fairy':1.0, 
    },
    'water': {
        'normal':1.0, 'fire':2.0, 'water':0.5, 'electric':1.0, 'grass':0.5, 'ice':1.0, 'fighting':1.0, 'poison':1.0, 'ground':2.0, 
        'flying':1.0, 'psychic':1.0, 'bug':1.0, 'rock':2.0, 'ghost':1.0, 'dragon':0.5, 'dark':1.0, 'steel':1.0, 'fairy':1.0, 
    },
    'electric': {
        'normal':1.0, 'fire':1.0, 'water':2.0, 'electric':0.5, 'grass':0.5, 'ice':1.0, 'fighting':1.0, 'poison':1.0, 'ground':0.0, 
        'flying':2.0, 'psychic':1.0, 'bug':1.0, 'rock':1.0, 'ghost':1.0, 'dragon':0.5, 'dark':1.0, 'steel':1.0, 'fairy':1.0, 
    },
    'grass': {
        'normal':1.0, 'fire':0.5, 'water':2.0, 'electric':1.0, 'grass':0.5, 'ice':1.0, 'fighting':1.0, 'poison':0.5, 'ground':2.0, 
        'flying':0.5, 'psychic':1.0, 'bug':0.5, 'rock':2.0, 'ghost':1.0, 'dragon':0.5, 'dark':1.0, 'steel':0.5, 'fairy':1.0, 
    },
    'ice': {
        'normal':1.0, 'fire':0.5, 'water':0.5, 'electric':1.0, 'grass':2.0, 'ice':0.5, 'fighting':1.0, 'poison':1.0, 'ground':2.0, 
        'flying':2.0, 'psychic':1.0, 'bug':1.0, 'rock':1.0, 'ghost':1.0, 'dragon':2.0, 'dark':1.0, 'steel':0.5, 'fairy':1.0, 
    },
    'fighting': {
        'normal':2.0, 'fire':1.0, 'water':1.0, 'electric':1.0, 'grass':1.0, 'ice':2.0, 'fighting':1.0, 'poison':0.5, 'ground':1.0, 
        'flying':0.5, 'psychic':0.5, 'bug':0.5, 'rock':2.0, 'ghost':0.0, 'dragon':1.0, 'dark':2.0, 'steel':2.0, 'fairy':0.5, 
    },
    'poison': {
        'normal':1.0, 'fire':1.0, 'water':1.0, 'electric':1.0, 'grass':2.0, 'ice':1.0, 'fighting':1.0, 'poison':0.5, 'ground':0.5, 
        'flying':1.0, 'psychic':1.0, 'bug':1.0, 'rock':0.5, 'ghost':0.5, 'dragon':1.0, 'dark':1.0, 'steel':0.0, 'fairy':2.0, 
    },
    'ground': {
        'normal':1.0, 'fire':2.0, 'water':1.0, 'electric':2.0, 'grass':0.5, 'ice':1.0, 'fighting':1.0, 'poison':2.0, 'ground':1.0, 
        'flying':0.0, 'psychic':1.0, 'bug':0.5, 'rock':2.0, 'ghost':1.0, 'dragon':1.0, 'dark':1.0, 'steel':2.0, 'fairy':1.0, 
    },
    'flying': {
        'normal':1.0, 'fire':1.0, 'water':1.0, 'electric':0.5, 'grass':2.0, 'ice':1.0, 'fighting':2.0, 'poison':1.0, 'ground':1.0, 
        'flying':1.0, 'psychic':1.0, 'bug':2.0, 'rock':0.5, 'ghost':1.0, 'dragon':1.0, 'dark':1.0, 'steel':0.5, 'fairy':1.0, 
    },
    'psychic': {
        'normal':1.0, 'fire':1.0, 'water':1.0, 'electric':1.0, 'grass':1.0, 'ice':1.0, 'fighting':2.0, 'poison':2.0, 'ground':1.0, 
        'flying':1.0, 'psychic':0.5, 'bug':1.0, 'rock':1.0, 'ghost':1.0, 'dragon':1.0, 'dark':0.0, 'steel':0.5, 'fairy':1.0, 
    },
    'bug': {
        'normal':1.0, 'fire':0.5, 'water':1.0, 'electric':1.0, 'grass':2.0, 'ice':1.0, 'fighting':0.5, 'poison':0.5, 'ground':1.0, 
        'flying':0.5, 'psychic':2.0, 'bug':1.0, 'rock':1.0, 'ghost':0.5, 'dragon':1.0, 'dark':2.0, 'steel':0.5, 'fairy':0.5, 
    },
    'rock': {
        'normal':1.0, 'fire':2.0, 'water':1.0, 'electric':1.0, 'grass':1.0, 'ice':2.0, 'fighting':0.5, 'poison':1.0, 'ground':0.5, 
        'flying':2.0, 'psychic':1.0, 'bug':2.0, 'rock':1.0, 'ghost':1.0, 'dragon':1.0, 'dark':1.0, 'steel':0.5, 'fairy':1.0, 
    },
    'ghost': {
        'normal':0.0, 'fire':1.0, 'water':1.0, 'electric':1.0, 'grass':1.0, 'ice':1.0, 'fighting':1.0, 'poison':1.0, 'ground':1.0, 
        'flying':1.0, 'psychic':2.0, 'bug':1.0, 'rock':1.0, 'ghost':2.0, 'dragon':1.0, 'dark':0.5, 'steel':1.0, 'fairy':1.0, 
    },
    'dragon': {
        'normal':1.0, 'fire':1.0, 'water':1.0, 'electric':1.0, 'grass':1.0, 'ice':1.0, 'fighting':1.0, 'poison':1.0, 'ground':1.0, 
        'flying':1.0, 'psychic':1.0, 'bug':1.0, 'rock':1.0, 'ghost':1.0, 'dragon':2.0, 'dark':1.0, 'steel':0.5, 'fairy':0.0, 
    },
    'dark': {
        'normal':1.0, 'fire':1.0, 'water':1.0, 'electric':1.0, 'grass':1.0, 'ice':1.0, 'fighting':0.5, 'poison':1.0, 'ground':1.0, 
        'flying':1.0, 'psychic':2.0, 'bug':1.0, 'rock':1.0, 'ghost':2.0, 'dragon':1.0, 'dark':0.5, 'steel':1.0, 'fairy':0.5, 
    },
    'steel': {
        'normal':1.0, 'fire':0.5, 'water':0.5, 'electric':0.5, 'grass':1.0, 'ice':2.0, 'fighting':1.0, 'poison':1.0, 'ground':1.0, 
        'flying':1.0, 'psychic':1.0, 'bug':1.0, 'rock':2.0, 'ghost':1.0, 'dragon':1.0, 'dark':1.0, 'steel':0.5, 'fairy':2.0, 
    },
    'fairy': {
        'normal':1.0, 'fire':0.5, 'water':1.0, 'electric':1.0, 'grass':1.0, 'ice':1.0, 'fighting':2.0, 'poison':0.5, 'ground':1.0, 
        'flying':1.0, 'psychic':1.0, 'bug':1.0, 'rock':1.0, 'ghost':1.0, 'dragon':2.0, 'dark':2.0, 'steel':0.5, 'fairy':1.0, 
    },
    }

effectiveness_to_emoji = {
    'immune':'🚫',
    'not very effective':'😐',
    'normal':'🆗',
    'super effective':'💥',
    }
emoji_to_effectiveness = {}
for (k,v) in effectiveness_to_emoji.items():
    emoji_to_effectiveness[v] = k

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
{effectiveness_to_emoji['immune']}: immune
{effectiveness_to_emoji['not very effective']}: not very effective
{effectiveness_to_emoji['normal']}: normal
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
                for i in ('immune','not very effective','normal','super effective'):
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
client.run(TOKEN)
