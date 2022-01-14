One thought: just use discord.py (https://discordpy.readthedocs.io/en/stable/) with the menu system (https://github.com/Rapptz/discord-ext-menus)
Another thought: follow this tutorial (https://python.plainenglish.io/build-discord-quizbot-with-python-and-deploy-1-44dec1250a37)
Also, this appears to work: https://stackoverflow.com/questions/63837615/multiple-choice-reaction-python-discord-py
And maybe something like this: https://github.com/eibex/reaction-light


I added PvPoke as a subtree so that I could get the json file with all of the move data. I did that via this awesome command:


```
mkdir external
git subtree add --prefix external/pvpoke git@github.com:pvpoke/pvpoke.git master --squash
```

I can the update it via 
```
git subtree pull --prefix external/pvpoke git@github.com:pvpoke/pvpoke.git master --squash
```
