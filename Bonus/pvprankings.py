#!/usr/bin/env python

import pandas as pd, numpy as np
import math, json, re
from IPython.display import display, Markdown, Latex, HTML


MOVES_FILE = 'gamemaster.json'
def get_moves():
    f = open(MOVES_FILE)
    mf = json.load(f)
    fastmoves = {i['moveId']:i for i in mf['moves'] if i['energyGain'] != 0}
    chargedmoves = {i['moveId']:i for i in mf['moves'] if i['energyGain'] == 0}
    return fastmoves, chargedmoves
def get_pokemon():
    f = open(MOVES_FILE)
    mf = json.load(f)
    # This gives you a list of pokemon dictionaries. I actually just want to look things up by name
    pokemon = {mon['speciesName']:mon for mon in mf['pokemon']}
    return pokemon

pokemon = get_pokemon()
# Kind of surprised this isn't in PvPoke
evolutions = ( ['Spheal', 'Sealeo','Walrein'],
        ['Bulbasaur', 'Ivysaur', 'Venusaur'],
        ['Mudkip','Marshtomp','Swampert'],
        ['Hoppip','Skiploom','Jumpluff'],
        ['Deoxys'],
        ['Seel','Dewgong'],
        ['Sandshrew','Sandslash'],
        ['Cottonee','Whimsicott'],
        ['Registeel'],
        ['Azurill','Marill','Azumarill'],
        )


# I definitely stole this table from https://gamepress.gg/pokemongo/cp-multiplier
def get_cpm(level):
    d = {
        1:	0.094,
        1.5: 0.1351374318,
        2: 0.16639787,
        2.5: 0.192650919,
        3: 0.21573247,
        3.5: 0.2365726613,
        4: 0.25572005,
        4.5: 0.2735303812,
        5: 0.29024988,
        5.5: 0.3060573775,
        6: 0.3210876,
        6.5: 0.3354450362,
        7: 0.34921268,
        7.5: 0.3624577511,
        8: 0.3752356,
        8.5: 0.387592416,
        9: 0.39956728,
        9.5: 0.4111935514,
        10: 0.4225,
        10.5: 0.4329264091,
        11: 0.44310755,
        11.5: 0.4530599591,
        12: 0.4627984,
        12.5: 0.472336093,
        13: 0.48168495,
        13.5: 0.4908558003,
        14: 0.49985844,
        14.5: 0.508701765,
        15: 0.51739395,
        15.5: 0.5259425113,
        16: 0.5343543,
        16.5: 0.5426357375,
        17: 0.5507927,
        17.5: 0.5588305862,
        18: 0.5667545,
        18.5: 0.5745691333,
        19: 0.5822789,
        19.5: 0.5898879072,
        20: 0.5974,
        20.5: 0.6048236651,
        21: 0.6121573,
        21.5: 0.6194041216,
        22: 0.6265671,
        22.5: 0.6336491432,
        23: 0.64065295,
        23.5: 0.6475809666,
        24: 0.65443563,
        24.5: 0.6612192524,
        25: 0.667934,
        25.5: 0.6745818959,
        26: 0.6811649,
        26.5: 0.6876849038,
        27: 0.69414365,
        27.5: 0.70054287,
        28: 0.7068842,
        28.5: 0.7131691091,
        29: 0.7193991,
        29.5: 0.7255756136,
        30: 0.7317,
        30.5: 0.7347410093,
        31: 0.7377695,
        31.5: 0.7407855938,
        32: 0.74378943,
        32.5: 0.7467812109,
        33: 0.74976104,
        33.5: 0.7527290867,
        34: 0.7556855,
        34.5: 0.7586303683,
        35: 0.76156384,
        35.5: 0.7644860647,
        36: 0.76739717,
        36.5: 0.7702972656,
        37: 0.7731865,
        37.5: 0.7760649616,
        38: 0.77893275,
        38.5: 0.7817900548,
        39: 0.784637,
        39.5: 0.7874736075,
        40: 0.7903,
        40.5: 0.792803968,
        41: 0.79530001,
        41.5: 0.797800015,
        42: 0.8003,
        42.5: 0.802799995,
        43: 0.8053,
        43.5: 0.8078,
        44: 0.81029999,
        44.5: 0.812799985,
        45: 0.81529999,
        45.5: 0.81779999,
        46: 0.82029999,
        46.5: 0.82279999,
        47: 0.82529999,
        47.5: 0.82779999,
        48: 0.83029999,
        48.5: 0.83279999,
        49: 0.83529999,
        49.5: 0.83779999,
        50: 0.84029999,
        50.5: 0.84279999,
        51: 0.84529999,        
        }
    return d[level]

def ivs_to_stats(my_a, my_d, my_s, my_level,*,mon, max_level=40,max_cp=1500.99, 
                 ):
    """convert ivs to stat. what a mess.

    my_a, my_d, my_s are the stats of the pokemon you're looking at. my_level is its level.

    max_level is the max level you want to consider. 40 for normal, 41 for best buddy, 50 for XL, 51 for XL BB.
    max_cp should be the max cp for your league + 0.99. E.g. 1500.99 for great.

    This function has some errors for mons that go above the max cp right when you evolve them.
    """

    bs = pokemon[mon]['baseStats']
    base_attack, base_defense, base_stamina = bs['atk'],bs['def'],bs['hp']
    attack = base_attack + my_a
    defense = my_d + base_defense
    stamina = my_s + base_stamina
    level = my_level#10
    cp = 10
    level_attack, level_defense, level_stamina, stat_prod = 0,0,0,0
    stats = (level, cp, level_attack, level_defense, level_stamina, stat_prod)
    while level <= max_level:
        cpm = get_cpm(level)
        cp = (attack * defense**0.5 * stamina**0.5 * cpm**2) / 10
        level_attack = attack * cpm
        level_defense = defense * cpm
        level_stamina = stamina * cpm
        if cp <= max_cp:
            stat_prod = math.floor(level_attack*level_defense*math.floor(level_stamina))
            #stat_prod = math.floor(level_attack*level_defense*level_stamina)
            stats = level, cp, level_attack, level_defense, level_stamina, stat_prod
        level = level + 0.5
    level, cp, level_attack, level_defense, level_stamina, stat_prod  = stats
    #print(f'{level_attack}, {level_defense}, {level_stamina}, {level_attack*level_defense*level_stamina}')
    return stats
    #print(f'level {level} cp {cp:.0f} attack {level_attack:.1f} defense {level_defense:.1f} stamina {level_stamina:.0f}')
    
    
def mons_to_consider(df,mon):
    if '(' in mon:
        if 'Shadow' in mon:
            raise Exception('No code for shadows yet')
        form_pattern = re.compile('(.*) \((.*)\)') # "Deoxys (Defense)"
        form = form_pattern.search(mon).group(2)
        mon = form_pattern.search(mon).group(1)
    else:
        form = None
        form = 'Normal'
    if form == 'Alolan':
        form = 'Alola'
    evolution_line = [i for i in evolutions if mon in i]
    if not len(evolution_line) == 1:
        raise Exception(f'Could not find evolution line for {mon}. got {evolution_line}')
    else:
        evolution_line = evolution_line[0]
    result = df[df.Name.isin(evolution_line)]
    if form is not None:
        # Sometimes, if there isn't an alola form or whatever, the normal form gets Form set to NaN.
        # If that happens, we won't get any results, so check explicitly for isna and use those.
        _result = result[result.Form == form]
        if not len(_result):
            _result = result[pd.isna(result.Form)]
        resut = _result
            
    return result

#'':{'attack':,'defense':,'hp':},
RS_INFO = {
    'Jumpluff':{'Great':
                    {
                    'Top 12 amazing stat product':{'attack':0,'defense':157.31,'hp':0,'onlytop':12},
                    'Slight attack, high def':{'attack':97.6,'defense':156.3,'hp':0},
                    'Slight attack, balanced bulk':{'attack':97.6,'defense':150,'hp':151},
                    }
                },
    'Walrein':{
        'article':'https://gamepress.gg/pokemongo/walrein-pvp-iv-deep-dive#topic-372706',
        'videos':('https://www.youtube.com/watch?v=yJUjtPAPkEM',),
        'Great':
        {
            'GOD TIER':{'attack':114.46,'defense':114.75,'hp':148},
        'All Attack Breakpoints':{'attack':114.45,'defense':113,'hp':148},
        'Azumarill Attack, Rank 1 Umbreon Def':{'attack':113.77,'defense':114.75,'hp':148},
        'Azumarill Attack':{'attack':113.77,'defense':113,'hp':148},
        'Waterfall, Pidgeot + Talonflame slayer':{'attack':114.62,'defense':113,'hp':148},
        'Waterfall, Pidgeot only, may bring down to 112.13 Atk':{'attack':113.16,'defense':113,'hp':148},
        },
        'Ultra':
        {
            'Best of the best':{'attack':147.45,'defense':145.3,'hp':197},
            'Mirror masters':{'attack':147,'defense':145.3,'hp':197},
            '>147.75 and still ties most 0-0 mirrors':{'attack':147.76,'defense':143.89,'hp':197},
            },
        'Master':
        {
            'Obviously the best':{'attack':15,'defense':15,'hp':15},
            'Still hits the breakpoints':{'attack':15,'defense':14,'hp':13},
            'Read the article to see about these!':{'attack':13,'defense':12,'hp':12},
        },
    },
    'Deoxys (Defense)':{
        'article':'https://gamepress.gg/pokemongo/deoxys-defense-pvp-iv-deep-dive-analysis',
        'videos':('https://www.youtube.com/watch?v=p-UrAQDrvTQ',),
        'Great':
        {
            'Best you can get are here, but watch the actual video':{'attack':100.78,'defense':221,'hp':98},
            },
        'Ultra':
        {
            'BB umbreon':{'attack':132.81,'defense':284,'hp':122},
            'Registeel and TF':{'attack':131.9,'defense':0,'hp':126},
            }
        },
    'Venusaur':{
        'article':'https://gamepress.gg/pokemongo/venusaur-pvp-iv-deep-dive',
        'Great':
        {
            'Froslass Slayer + OK Def':{'attack':122.5,'defense':117.88,'hp':122},
            'Froslass Slayer + Big Def':{'attack':122.5,'defense':121.13,'hp':122},
            'Big Bulk':{'attack':0,'defense':121.13,'hp':123},
            },
            'Ultra':
            {
            'Galar Stunfisk Slayer':{'attack':159.2,'defense':157.25,'hp':152},                
            'Huge Defense':{'attack':0,'defense':160.82,'hp':156},                
            'As good as Rank 1 Bulk':{'attack':0,'defense':158.05,'hp':156},
                },
        },
    'Dewgong':{
        'article':'https://gamepress.gg/pokemongo/dewgong-pvp-iv-deep-dive',
        'videos':('https://www.youtube.com/watch?v=u_eDH5HNg1M',),
        'extrainfo':'If you have to choose, favor higher def over higher hp. For GBL, may be best to favor atk breakpoint or high stat product.',
        'Great':
        {
            'Max Def Umbreon, Dewgong, most Mew, weather boosted trev atk, very OK bulk':{'attack':102.89,'defense':131.7,'hp':0},
            'Rank 1 umbreon atk, balanced bulk':{'attack':101.79,'defense':136.81,'hp':150},
            'rank 1 umbreon atk, rank 1 dewgong dominating def':{'attack':101.79,'defense':138.28,'hp':150},
            },
        },
    'Sandslash':{
        'article':'https://gamepress.gg/pokemongo/alolan-sandslash-pvp-iv-deep-dive',
        'videos':('https://www.youtube.com/watch?v=o3e84ZurZ0o',),
        'extrainfo':'Breakpoints are less important here, you really want some bulk.',
        'Great':
        {
            'RS says this':{'attack':121,'defense':120,'hp':0},
            },
        },
    'Sandslash (Alolan)':{
        'article':'https://gamepress.gg/pokemongo/alolan-sandslash-pvp-iv-deep-dive',
        'videos':('https://www.youtube.com/watch?v=o3e84ZurZ0o',),
        'extrainfo':'Breakpoints are less important here, you really want some bulk (top 100ish). Ashrew wants to be at least 12/13/13 and probably at least 12/15/15.',
        'Great':
        {
            'High Attack':{'attack':115.31,'defense':128.92,'hp':119},
            'Super High Attack (egg hatch)':{'attack':118.24,'defense':127.59,'hp':118},
            },
        'Ultra':
        {
            '149.14 atk 173.07 def':{'attack':149.14,'defense':173.07,'hp':0},
            '154.26 atk 168 def':{'attack':154.26,'defense':168,'hp':0},
            }
        },
    'Whimsicott':{
        'article':'https://gamepress.gg/pokemongo/whimsicott-pvp-iv-deep-dive',
        'videos':('https://www.youtube.com/watch?v=kJUjufO4YXA',),
        'extrainfo':'Article is quite detailed.',
        'Great':
        {
            'Moderate attack weight':{'attack':121.26,'defense':132.25,'hp':0},
            'Slight attack weight':{'attack':119.47,'defense':132.25,'hp':0},
            'Alolan Ninetails Slayer':{'attack':121.87,'defense':132.25,'hp':0},
            'Lickitung Slayer (no brain, just charmm)':{'attack':122.81,'defense':132.25,'hp':0},
            },
        },
    'Swampert':{
        'article':'',
        'videos':('',),
        'extrainfo':'No good deep dive',
        'Great':
        {
            'Def':{'attack':0,'defense':110,'hp':0},
            'Atk':{'attack':121.6,'defense':108,'hp':0},
            },
        },
    'Registeel':{
        'article':'https://gamepress.gg/pokemongo/registeel-pvp-iv-deep-dive#topic-379686',
        'videos':('https://www.youtube.com/watch?v=C66Ud9me-tg','https://www.youtube.com/watch?v=W_ZOJPz7LV4'),
        'extrainfo':'Oof. Raid IVs.',
        'Great':
        {
            'Raid Only 186.7 Def 127 HP':{'attack':0,'defense':186.7,'hp':127},
            '190.09 Def 129 HP (trade only)':{'attack':0,'defense':190.09,'hp':129},
            '191.97 Def 129 HP (trade only)':{'attack':0,'defense':191.97,'hp':129},
            },
        'Ultra':
        {
            'Raid Only 240.5 Def 165 HP':{'attack':0,'defense':240.5,'hp':165},
            '244.4 Def 167 HP':{'attack':0,'defense':244.4,'hp':167},
            }
        },
    'Azumarill':{
        'article':'https://gamepress.gg/pokemongo/azumarill-pvp-iv-deep-dive',
        'videos':('https://www.youtube.com/watch?v=iYaqdQG0Ic8',),
        'extrainfo':'Old non-XL article: https://gamepress.gg/pokemongo/azumarill-great-league-pvp-iv-deep-dive .. you can make up or lower def/hp at a 1:2 ratio, so 134.7 def is fixed by a94 hp, 190 hp is fixed by 136.7 def.',
        'Great':
        {
            'Medicham 1-1 consistency, 1-2 potential with play rough':{'attack':0,'defense':137.64,'hp':0},
            'Hits the min':{'attack':0,'defense':135.78,'hp':192},
            'General Def/HP Azu':{'attack':0,'defense':132.8,'hp':187},
            'Slight Atk Weight Azu':{'attack':92,'defense':132.8,'hp':187},
            },
            }
}


def display_full_report(df):
    for mon in RS_INFO:
        display_rs_info(df,mon)

def display_rs_info(df,mon):
    """
    """
    if mon not in RS_INFO:
        raise Exception(f"Sorry, I don't know what Ryan Swag says about {mon}.")
        
    df = mons_to_consider(df,mon)
    mon_stats = {
        'Great':get_max_stats(df,mon,max_level=51,max_cp=1500.99),
        'Great cheap':get_max_stats(df,mon,max_level=41,max_cp=1500.99),
        'Ultra':get_max_stats(df,mon,max_level=51,max_cp=2500.99),
        'Ultra cheap':get_max_stats(df,mon,max_level=41,max_cp=2500.99),
        }
    # Maybe rename this.
    def get_mons(attack,defense,hp,mine,*,level_max=99):    
        these = mine[mine.attack >= attack]
        these = these[these.defense >= defense]
        these = these[these.stamina >= hp]
        these = these[these.level <= level_max]
        these = these.sort_values('statprod',ascending=False)
        return these.sort_values('statprod',ascending=False)
        
    display(Markdown(f'# {mon}s you have, according to the Swag Man'))
    if 'article' in RS_INFO[mon]:
        display(Markdown(f'Check out the article [here]({RS_INFO[mon]["article"]})!'))
    if 'videos' in RS_INFO[mon]:
        txt = 'Check out the videos: ' + ' '.join(f'[here]({video})' for video in RS_INFO[mon]['videos']) + '!'
        display(Markdown(txt))
    if 'extrainfo' in RS_INFO[mon]:
        display(Markdown(f'Extra Tips: {RS_INFO[mon]["extrainfo"]}'))
    
    for league in ('Great','Ultra'):
        display(Markdown(f'## {league} League'))
        if league not in RS_INFO[mon]:
            continue
        for k in RS_INFO[mon][league]:
            display(Markdown(f'### {k}'))
            attack, defense, hp = [RS_INFO[mon][league][k][i] for i in ('attack','defense','hp')]
            if 'onlytop' in RS_INFO[mon][league][k]:
                onlytop = RS_INFO[mon][league][k]['onlytop']
                display(HTML(f'<p style="color:red">NOTE! Ryan says you only want the top {onlytop} mons in this category. This code does only checks IVs and stat products, so you want to double-check his actual article before evolving something!</p>'))
            display(get_mons(attack, defense, hp, mon_stats[league]))
                    
        
def get_max_stats(df, mon, max_level, max_cp):
    # Great League, allowing XL, allowing best buddy
    d = {'CP':[],'max CP':[],'level':[],'attack':[],'defense':[],'stamina':[],'a':[],'d':[],'s':[],'statprod':[]}
    for row in df.iterrows():
        i,s = row
        orig_cp, my_a, my_d, my_s, my_level = s.CP, s['Atk IV'], s['Def IV'], s['Sta IV'], s['Level Min']
        level, cp, attack, defense, stamina, stat_prod = ivs_to_stats(my_a, my_d, my_s,my_level = my_level,
                                                                          max_level=max_level,max_cp=max_cp,mon=mon)
        #print('orig_cp',orig_cp,'my_a',my_a)
        d['CP'].append(orig_cp)
        d['max CP'].append(int(np.floor(cp)))
        d['level'].append(level)
        d['attack'].append(attack)
        d['defense'].append(defense)
        d['stamina'].append(int(np.floor(stamina)))
        d['a'].append(my_a)
        d['d'].append(my_d)
        d['s'].append(my_s)
        d['statprod'].append(stat_prod)
    mine = pd.DataFrame.from_dict(d)
    return mine
