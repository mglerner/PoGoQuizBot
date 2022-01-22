#!/usr/bin/env python

"""
This is where I put working code that I no longer use, but that might be useful in the future.
"""
async def ask_moves_questions(num_questions, channel, guesser):
    msg = await channel.send("Here is your quiz")
    for question_number in range(num_questions):
        record_channel_activity(channel)
        # Could think about excluding moves with archetype 'Low Quality'
        fast_move = FASTMOVES[random.choice(list(FASTMOVES.keys()))]
        charge_move = CHARGEMOVES[random.choice(list(CHARGEMOVES.keys()))]
        mymsg = await msg.reply(f'How many {fast_move["moveId"]}s does it take to get to one {charge_move["moveId"]}?')
        for i in (1,2,3,4,5,6,7,8,9,10,'more'):
            await mymsg.add_reaction(emoji=count_emojis[i])
        right_answer = charge_move['energy']/fast_move['energyGain']
        right_answer = int(math.ceil(right_answer))
        right_answer_emoji = count_emojis[right_answer]
        if right_answer > 10:
            right_answer = 10
        def check(reaction,user):
            result = (user == guesser) and (str(reaction.emoji) == right_answer_emoji)
            return result
        try:
            reaction, user = await bot.wait_for('reaction_add',timeout=QUIZ_TIMEOUT, check=check)
        except asyncio.TimeoutError:
            await mymsg.channel.send('You timed out')
            break
        else:
            await mymsg.add_reaction(emoji='👍')    

@bot.slash_command(guild_ids=GUILD_IDS, description="Prototype move quiz")
async def qm(ctx, num_questions:int=5):
    await check_channel_and_redirect_user(ctx)
    channel = get_private_channel(ctx)
    
    # Set up lists of attackers and defenders
    if num_questions < 1:
        await ctx.response(f"You asked for {num_questions} questions, but I'm giving you 1 instead")
        num_questions = 1
    try:
        await ask_moves_questions(num_questions, channel, guesser=ctx.user)
    except asyncio.TimeoutError:
        await channel.send('You timed out') # Where to send this? Could use ctx to send to original channel.
    await channel.send('The quiz is over!')



#
# This would be nice, but I didn't see an easy way
# to make a bunch of different function definitions. Making up the funciton names each time?
class QuestionView(View):
    @discord.ui.button(label="Right answer")
    async def right_button_callback(self, button, interaction):
        button.label="You got it!"
        button.style = discord.ButtonStyle.green
        await interaction.response.edit_message(view=self) # have to do this or else the button doesn't actually update.
        self.stop()

    @discord.ui.button(label="Wrong answer")
    async def wrong_button_callback(self, button, interaction):
        button.label="Nope"
        button.style = discord.ButtonStyle.red
        button.disabled = True
        await interaction.response.edit_message(view=self) # have to do this or else the button doesn't actually update.

    
