# PoGoQuizBot

PoGoQuizBot is a Discord bot that quizzes you about Pokemon Go things, like type matchups and move counts. To install it, you need

* [py-cord](https://github.com/Pycord-Development/pycord) or some other [discord.py](https://discordpy.readthedocs.io/en/stable/) fork that supports slash commands. I installed via `pip install git+https://github.com/Pycord-Development/pycord` so that I could get the most recent version.
* somewhere to run the code. You can run it from the command line. You can also follow the examples in the excellent [EncourageBot](https://www.freecodecamp.org/news/create-a-discord-bot-with-python/) tutorial from [freeCodeCamp](https://www.freecodecamp.org/) to see how to use [repl.it](https://replit.com/~) to run it continuously in the cloud, making use of [uptimerobot](https://uptimerobot.com) to monitor things. I'm using [pm2](https://pm2.keymetrics.io/)

Thanks go to

* PvPoke/EmpoleonDynamite for making PvPoke data available for free. See below.
* The phenomenal py-cord Discord community, who gave me lots of great advice on how to write a Discord bot.
* Xehrfelrose for ideas and help testing the bot.
* Ruah22 for advice about Discord bots.

## Move data
[PvPoke](https://pvpoke.com/) is an amazing resource, and it's all available as an open-source [github repo](https://github.com/pvpoke/pvpoke). PoGoQuizBot uses PvPoke's move data. Since PvPoke uses the MIT License, I've included a copy of that license below.


## MIT License, as it applies to the pvpoke code included in this repository.

MIT License

Copyright (c) 2019 pvpoke

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

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
