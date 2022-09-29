#!/usr/bin/env python

# TODO
# * Make it so that for shadows, you also see the purified IVs
# * Add rankings. 
# * Some PVP IV Deep Dives, like Medicham, use the "top N" pokemon in addition to stats cutoffs. We should do that or a stat product cutoff.
# * Figure out if we're actually calculating things correctly, since we disagree very slightly with pvpivs.com

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
EVOLUTIONS = ( ['Spheal', 'Sealeo','Walrein'],
        ['Bulbasaur', 'Ivysaur', 'Venusaur'],
        ['Mudkip','Marshtomp','Swampert'],
        ['Hoppip','Skiploom','Jumpluff'],
        ['Deoxys (Defense)'],
        ['Seel','Dewgong'],
        ['Sandshrew','Sandslash'],
        ['Cottonee','Whimsicott'],
        ['Registeel'],
        ['Azurill','Marill','Azumarill'],
        ['Dewpider','Araquanid'],
        ['Geodude','Graveler','Golem'],
        ['Cubone','Marowak'],
        ['Zigzagoon (Galarian)','Linoone (Galarian)','Obstagoon'],
        ['Zigzagoon (Galarian)','Linoone (Galarian)'],
        ['Meditite','Medicham'],
        ['Dunsparce'],
        ['Stunfisk (Galarian)'],
        ['Lickitung'],#,'Lickilicky'],
        ['Mareanie','Toxapex'],
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
    """Get a list of mons to consider from a df

    We had to split this into two functions because you get weirdo mons
    like Obstagoon where the base forms are Galarian, but the final form
    isn't. We probably could combine it into one function with "or" but
    it's easier this way.
    """
    #evolution_line = [i for i in EVOLUTIONS if mon in i]
    evolution_line = [i for i in EVOLUTIONS if mon in i[-1]]
    if not len(evolution_line) == 1:
        raise Exception(f'Could not find evolution line for {mon}. got {evolution_line}')
    else:
        evolution_line = evolution_line[0]


    all_results = [_mons_to_consider(df,mon) for mon in evolution_line]
#    print(evolution_line)
#    print(all_results[0])
#    print(all_results[1])
#    print(all_results[2])
    result = pd.concat(all_results)
    return result

def _mons_to_consider(df,mon):
    """Helper function for `mons_to_consider` that just does a single mon, not a whole evolution line.
    """
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
    elif form == 'Galarian':
        # This is to remind us that it's actually listed as galarian for zig and lin
        form = 'Galarian'
    #evolution_line = [i for i in EVOLUTIONS if mon in i]
    #if not len(evolution_line) == 1:
    #    raise Exception(f'Could not find evolution line for {mon}. got {evolution_line}')
    #else:
    #    evolution_line = evolution_line[0]
    #result = df[df.Name.isin(evolution_line)]
    result = df[df.Name == mon]
#    print(f"Looking for {mon} of form {form} I see {result}")
    if form is not None:
        # Sometimes, if there isn't an alola form or whatever, the normal form gets Form set to NaN.
        # If that happens, we won't get any results, so check explicitly for isna and use those.
        _result = result[result.Form == form]
        if not len(_result):
            _result = result[pd.isna(result.Form)]
        result = _result
            
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
        'extrainfo':'For GL, the SwagMan wants the rank 67>77>22 (15/14/10 > 15/10/12 > 14/12/13) and then bulk 1 > 3 > 9 (10/15/13 > 10/10/15 > 11/13/12) then the mirror slayer rank 17 (13/11/15). For that first range, the 15/13/10 is my best so far. \n The 12/13/15 I have is the UL rank 1. But also my best GL mirror slayer. For UL I decide between that rank 1 and my rank 150 15/13/12 and rank 146 15/11/12 which hit the table breakpoints.',
        'Great':
        {
            'Best you can get are here, but watch the actual video':{'attack':101.95,'defense':221,'hp':98},
            'Lanturn 0-1 1-1 Spark 1-0 2-1 water gun, if lanturn is not super high def': {'attack':101.95,'defense':220.18,'hp':95,},
            'Includes SwagMan table plus more read the article yo':{'attack':100.78,'defense':220.18,'hp':95},
            'Mirror':{'attack':100.78,'defense':0,'hp':98},
            },
        'Ultra':
        {
            'BB umbreon':{'attack':132.81,'defense':284,'hp':122},
            'Registeel and TF (not BB)':{'attack':132.28,'defense':0,'hp':126},
            'Sme rando Umb, TF, Regi': {'attack':131.8,'defense':0,'hp':126},
            'Just atk breakpoint': {'attack':132.28,'defense':0,'hp':0},
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
            },
    'Araquanid':{
        'article':'',
        'videos':('https://www.youtube.com/watch?v=dQKFwYr9tQY',),
        'extrainfo':'In general, HP > def, Atk > b/c walrus.',
        'Great':
        {
            'Shadow Drapion attack':{'attack':99.02,'defense':0,'hp':0},
            'High end viggy atk':{'attack':99.2,'defense':0,'hp':0},
            'Best best walrus atk':{'attack':99.93,'defense':0,'hp':0},
            'DD D min':{'attack':0,'defense':163.77,'hp':0},
            'DD D max':{'attack':0,'defense':165.21,'hp':0},
            'HP sable min':{'attack':0,'defense':0,'hp':134},
            'HP sable max':{'attack':0,'defense':0,'hp':136},
            'General':{'attack':99.2,'defense':165.2,'hp':134},
            },
            },
    'Golem (Alolan)':{
        'article':'',
        'videos':('',),
        'extrainfo':'',
        'Great':
        {
            'General':{'attack':124.79,'defense':0,'hp':0},
            'Min':{'attack':123.93,'defense':0,'hp':0},
            'Best':{'attack':126,'defense':118,'hp':0},
            },
            },
    'Marowak (Alolan)':{
        'article':'https://gamepress.gg/pokemongo/alolan-marowak-pvp-iv-deep-dive',
        'videos':('https://www.youtube.com/watch?v=jMwFqbkVlpU',),
        'extrainfo':'Right now, this is looking at everything, so you have to check for shadow explicitly. Go for mid range attack if hit the bulk.',
        'Great':
        {
            'Shadow AWak Min attack, very min defense':{'attack':110.5,'defense':141.49,'hp':0},
            'Shadow AWak Min attack high end':{'attack':111.85,'defense':141.49,'hp':0},
            'All':{'attack':0.,'defense':0,'hp':0},
            'Best':{'attack':126,'defense':118,'hp':0},
            },
            },
    'Linoone (Galarian)':{
        'article':'https://twitter.com/SwgTips/status/1558892455017185280',
        'videos':('',),
        'extrainfo':'Still bad right now.',
        'Great':
        {
            'Swamp/cash':{'attack':112.87,'defense':0,'hp':144},
            'Drap/A9 CMP':{'attack':114,'defense':0,'hp':144},
            'Diggers':{'attack':0.,'defense':110.11,'hp':144},
            'SwagAtk FS Awak':{'attack':0.,'defense':111.14,'hp':144},
            'Best':{'attack':114,'defense':111.14,'hp':144},
            },
            },
    'Obstagoon':{
        'article':'https://gamepress.gg/pokemongo/obstagoon-pvp-iv-deep-dive',
        'videos':('https://www.youtube.com/watch?v=XEygOnJDnlY',),
        'extrainfo':'You want three of each league, one with obstruct and one without, and one with high bulk. Also, this does not filter for galarian zig/lin; you have to do that yourself.\n For UL you really want 148+ attack, then 172 HP',
        'Great':
        {
            'Super Premium Atk ':{'attack':115.5,'defense':123.56,'hp':137},
            'Premium Atk (115.5 Atk slightly better, 123.56 Def 137 HP better)':{'attack':115,'defense':123.3,'hp':135},
            'Bulk focus':{'attack':0,'defense':126,'hp':137},
            'All':{'attack':0.,'defense':0,'hp':0},
            },
        'Ultra':
        {
            'Unicorn':{'attack':148,'defense':166.8,'hp':172},
            'Bare minimum':{'attack':148,'defense':0,'hp':172},
            'General Atk':{'attack':146.95,'defense':163.8,'hp':172},
            'General Atk+':{'attack':148,'defense':163.8,'hp':172},
            'Mirror Focus':{'attack':149.1,'defense':0,'hp':172},
            'Bulk Focus':{'attack':0,'defense':166.8,'hp':174},
            'All':{'attack':0.,'defense':0,'hp':0},
            },
            },
    'Medicham':{
        'article':'https://gamepress.gg/pokemongo/medicham-pvp-iv-deep-dive',
        'videos':('https://www.youtube.com/watch?v=-ihUhkBfdok',),
        'extrainfo':'',
        'Great':{
            'The Good (105.38 Atk, 138.6 Def, 140 HP)':{'attack':105.38,'defense':138.6,'hp':140},
            'Premium Cut':{'attack':105.87,'defense':138.64,'hp':140},
            'The few worthwhile best buddies':{'attack':105.38,'defense':140.3,'hp':142},
            'The Mirror Slayers (note: the drop in bulk may cause trouble in other matchups. Simply going for CMP may be better)':{'attack':108,'defense':137.64,'hp':0},
            }
        },
    'Dunsparce':{
        'article':'https://gamepress.gg/pokemongo/dunsparce-pvp-iv-deep-dive',
        'videos':('https://www.youtube.com/watch?v=ZiZEbDqMur0',),
        'extrainfo':'Cares ONLY about bulk, not about Atk at all',
        'Great':{
            'Basic Bulk':{'attack':0,'defense':110.63,'hp':185},
            'Premium Bulk':{'attack':0,'defense':111.14,'hp':186},
            #'Premium Bulk, bulk sort':{'attack':102.78,'defense':97.85,'hp':186,'sort':'bulk'},
            }
        },
    'Stunfisk (Galarian)':{
        'article':'https://gamepress.gg/pokemongo/galarian-stunfisk-pvp-iv-deep-dive',
        'videos':('https://www.youtube.com/watch?v=iUja0_EjGnc',),
        'extrainfo':'For UL, realy do want 15/15/14',
        'Great':{
            'High Bulk (124.75 def, 174 hp)':{'attack':99,'defense':124.75,'hp':174},
            'pure mirror slayer (101.79 atk, 127.34 def)':{'attack':101.79,'defense':127.34,'hp':0},
            'bulk mirror slayer (101.79 atk, 124.75/172)':{'attack':101.79,'defense':124.75,'hp':172,},
            'Minimum bulk (124.75 def 172 hp)':{'attack':99,'defense':124.75,'hp':172},
            }
        },
    'Lickitung':{
        'article':'https://gamepress.gg/pokemongo/lickitung-pvp-iv-deep-dive',
        'videos':('',),
        'extrainfo':'''General Good is minimum bulk for "good" lickitung.\nAtk focus: Potentiates Registeel and Shadow Walrein Breakpoints without giving up too much bulk, 126.2 Def, 126.58 Def, and 184 HP are notable stat checks, Priority Recommendation 126.2 Def=184 HP>185+ HP=126.58 Def\nBudget Boi: This budget list is for players who’ve already built a Lickitung and are wondering if they should build twice (or for players looking to save ~94 XL Candy), If you meet at least 125.1 Def and 181 HP, building a better Lickitung might not be worth it compared to other projects''',
        'Great':{
            'General Good (125.94 def, 183 hp)':{'attack':96.36,'defense':125.94,'hp':183},
            'Atk Focus (97.7 Atk, 125.94 def, 183 hp)':{'attack':97.7,'defense':125.94,'hp':183},
            'Budget Bois (97 Atk, 125.1 def, 181 hp)':{'attack':97,'defense':125.1,'hp':181},
            }
        },
    'Toxapex':{
        'article':'https://gamepress.gg/pokemongo/toxapex-pvp-iv-deep-dive',
        'videos':('',),
        'extrainfo':'''High Bulk:
        * For tie-breakers, generally HP > Def
        * If you fear Swampert, 227.82+ Def is important
        * If you hate Venusaur & Jumpluff, 91+ Atk is important

        Mirror Slayer
        * If you hate Venusaur & Jumpluff, 91+ Atk is important

        Lickitung Slayer
        * Rank 1 and 2 Best Buddy Lickitung require 94.13 Atk
''',
        'Great':{
            'High Bulk (226.73 Def, 118 HP)':{'attack':0,'defense':226.73,'hp':118},
            'Mirror Slayer/Big HP (219 Def, 121 HP)':{'attack':0,'defense':219,'hp':121},
            'Lickitung Slayer (93 Atk, 118 HP)':{'attack':93,'defense':0,'hp':118},
            }
        },
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
