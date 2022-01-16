# PoGoQuizBot

PoGoQuizBot is a Discord bot that quizzes you about Pokemon Go things, like type matchups and move counts. To install it, you need

* [py-cord](https://github.com/Pycord-Development/pycord) or some other [discord.py](https://discordpy.readthedocs.io/en/stable/) fork that supports slash commands. I installed via `pip install git+https://github.com/Pycord-Development/pycord` so that I could get the most recent version.
* somewhere to run the code. You can run it from the command line. You can also follow the examples in the excellent [EncourageBot](https://www.freecodecamp.org/news/create-a-discord-bot-with-python/) tutorial from [freeCodeCamp](https://www.freecodecamp.org/) to see how to use [repl.it](https://replit.com/~) to run it continuously in the cloud, making use of [uptimerobot](https://uptimerobot.com) to monitor things. I'm using [pm2](https://pm2.keymetrics.io/)

Thanks go to

* The phenomenal py-cord Discord community, who gave me lots of great advice on how to write a Discord bot.
* Xehrfelrose for ideas and help testing the bot.
* Ruah22 for advice about Discord bots.
* PvPoke/EmpoleonDynamite for making PvPoke data available for free. See below.

## Move data
[PvPoke](https://pvpoke.com/) is an amazing resource, and it's all available as an open-source [github repo](https://github.com/pvpoke/pvpoke). PoGoQuizBot uses PvPoke's move data. Since PvPoke uses the MIT License, I've included a copy of that license below.


## MIT License

One thought: just use discord.py (https://discordpy.readthedocs.io/en/stable/) with the menu system (https://github.com/Rapptz/discord-ext-menus)
Another thought: follow this tutorial (https://python.plainenglish.io/build-discord-quizbot-with-python-and-deploy-1-44dec1250a37)
Also, this appears to work: https://stackoverflow.com/questions/63837615/multiple-choice-reaction-python-discord-py
And maybe something like this: https://github.com/eibex/reaction-light

## My own notes

I added PvPoke as a subtree so that I could get the json file with all of the move data. I did that via this awesome command:

```
mkdir external
git subtree add --prefix external/pvpoke git@github.com:pvpoke/pvpoke.git master --squash
```

I can the update it via 
```
git subtree pull --prefix external/pvpoke git@github.com:pvpoke/pvpoke.git master --squash
```
