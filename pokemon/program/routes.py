import json

import flask
from flask import render_template, request, flash, url_for, redirect, session
from flask_login import LoginManager, login_required, login_user, UserMixin, logout_user, current_user
from sqlalchemy import text

from program import app, db
import requests
import random
from pprint import pp

from program.data.models.badges import Badge
from program.data.models.my_pokemons import MyPokemon
from program.data.models.players import Player
from program.data.models.pokemons import Pokemon

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # same name as login function

# @app.route('/', methods=['GET', 'POST'])
# @app.route('/index', methods=['GET', 'POST'])
# # @login_required
# def index():
#     # cache this VERY IMPORTANT
#
#     pokemon_data = None
#     if request.method == 'POST' and 'pokemon_type' in request.form:
#         pokemon_type = request.form.get('pokemon_type')
#         r = requests.get('https://pokeapi.co/api/v2/type/' + pokemon_type.lower())
#         pokemon_data = r.json()
#         pokemon_data = pokemon_data['pokemon']
#     else:
#         r = requests.get('https://pokeapi.co/api/v2/pokemon?limit=100000&offset=0')
#         pokemon_data = r.json()
#         pokemon_data = pokemon_data['results']
#
#     all_pokemon = []
#     row_pokemon = {0: None, 1: None, 2: None, 3: None, 4: None}
#
#     # random.shuffle(pokemon_data)
#
#     for i in pokemon_data:
#         if request.method == 'POST' and 'pokemon_type' in request.form:
#             pokemon_id = i['pokemon']['url'].split('/')[-2]
#         else:
#             pokemon_id = i['url'].split('/')[-2]
#         r = requests.get('https://pokeapi.co/api/v2/pokemon/' + pokemon_id)
#         pokemon = r.json()
#
#         if not pokemon["sprites"]["other"]["official-artwork"]["front_shiny"]:
#             continue
#
#         # name = pokemon["species"]["name"][0].upper() + pokemon["species"]["name"][1:]
#         # types = [pokemon_type["type"]["name"][0].upper() + pokemon_type["type"]["name"][1:]
#         #          for pokemon_type in pokemon["types"]]
#         # types = ", ".join(types)
#         # abilities = [pokemon_type["ability"]["name"][0].upper() + pokemon_type["ability"]["name"][1:]
#         #              for pokemon_type in pokemon["abilities"]]
#         # abilities = ", ".join(abilities)
#         # img_url = pokemon["sprites"]["other"]["official-artwork"]["front_shiny"]
#         # coins = random.randint(50, 500)
#         # db_pokemon = Pokemon(name=name, types=types, abilities=abilities, img_url=img_url, coins=coins)
#         # db.session.add(db_pokemon)
#         # db.session.commit()
#         # db.session.close()
#
#         if not row_pokemon[0]:
#             row_pokemon[0] = pokemon
#         elif not row_pokemon[1]:
#             row_pokemon[1] = pokemon
#         elif not row_pokemon[2]:
#             row_pokemon[2] = pokemon
#         elif not row_pokemon[3]:
#             row_pokemon[3] = pokemon
#         else:
#             row_pokemon[4] = pokemon
#             all_pokemon.append(row_pokemon)
#             row_pokemon = {0: None, 1: None, 2: None, 3: None, 4: None}
#
#     if row_pokemon[0]:  # for last incomplete row
#         all_pokemon.append(row_pokemon)
#
#     return render_template('index.html', all_pokemon=all_pokemon)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
# @login_required
def index():
    # cache this VERY IMPORTANT (user is cached in current_user, pokemons are cached in database and global variable
    # __pokemons)

    pokemon_data = None

    if request.method == 'POST' and 'pokemon_type' in request.form:
        pokemon_type = request.form.get('pokemon_type')
        # r = requests.get('https://pokeapi.co/api/v2/type/' + pokemon_type.lower())
        # pokemon_data = r.json()
        # pokemon_data = pokemon_data['pokemon']

        if not current_user.is_authenticated:
            pokemon_data = Pokemon.query.filter(Pokemon.types.contains(pokemon_type)).all()
        else:
            statement = text("""
            SELECT pokemons.id, pokemons.name, pokemons.types, pokemons.abilities, pokemons.img_url, pokemons.coins
            FROM pokemons
            WHERE pokemons.id NOT IN (
                SELECT my_pokemons.pokemon_id
                FROM my_pokemons
                WHERE my_pokemons.player_id = :id
            ) AND pokemons.types LIKE '%'||:type||'%'
            ORDER BY pokemons.id ASC;
            """)
            pokemon_data = list(db.session.execute(statement, {'id': current_user.id, 'type': pokemon_type}))
    else:
        # r = requests.get('https://pokeapi.co/api/v2/pokemon?limit=100000&offset=0')
        # pokemon_data = r.json()
        # pokemon_data = pokemon_data['results']

        if not current_user.is_authenticated:
            pokemon_data = Pokemon.query.order_by(Pokemon.id).all()
        else:
            statement = text("""
            SELECT pokemons.id, pokemons.name, pokemons.types, pokemons.abilities, pokemons.img_url, pokemons.coins
            FROM pokemons
            WHERE pokemons.id NOT IN (
                SELECT my_pokemons.pokemon_id
                FROM my_pokemons
                WHERE my_pokemons.player_id = :id
            )
            ORDER BY pokemons.id ASC;
            """)
            pokemon_data = list(db.session.execute(statement, {'id': current_user.id}))

        # TODO: load badges data OK, spent OK and earned coins OK, arena
        # file_names = [
        #     "01_Boulder_Badge.png",
        #     "02_Cascade_Badge.png",
        #     "03_Thunder_Badge.png",
        #     "04_Rainbow_Badge.png",
        #     "05_Soul_Badge.png",
        #     "06_Marsh_Badge.png",
        #     "07_Volcano_Badge.png",
        #     "08_Earth_Badge.png",
        #     "09_Zephyr_Badge.png",
        #     "10_Hive_Badge.png",
        #     "11_Plain_Badge.png",
        #     "12_Fog_Badge.png",
        #     "13_Storm_Badge.png",
        #     "14_Mineral_Badge.png",
        #     "15_Glacier_Badge.png",
        #     "16_Rising_Badge.png",
        #     "17_Stone_Badge.png",
        #     "18_Knuckle_Badge.png",
        #     "19_Dynamo_Badge.png",
        #     "20_Heat_Badge.png",
        #     "21_Balance_Badge.png",
        #     "22_Feather_Badge.png",
        #     "23_Mind_Badge.png",
        #     "24_Rain_Badge.png",
        #     "25_Coal_Badge.png",
        #     "26_Forest_Badge.png",
        #     "27_Cobble_Badge.png",
        #     "28_Fen_Badge.png",
        #     "29_Relic_Badge.png",
        #     "30_Mine_Badge.png",
        #     "31_Icicle_Badge.png",
        #     "32_Beacon_Badge.png",
        #     "33_Trio_Badge.png",
        #     "34_Basic_Badge.png",
        #     "35_Insect_Badge.png",
        #     "36_Bolt_Badge.png",
        #     "37_Quake_Badge.png",
        #     "38_Jet_Badge.png",
        #     "39_Freeze_Badge.png",
        #     "40_Legend_Badge.png",
        #     "41_Toxic_Badge.png",
        #     "42_Wave_Badge.png",
        #     "43_Cliff_Badge.png",
        #     "44_Rumble_Badge.png",
        #     "45_Plant_Badge.png",
        #     "46_Voltage_Badge.png",
        #     "47_Fairy_Badge.png",
        #     "48_Psychic_Badge.png",
        #     "49_Iceberg_Badge.png",
        #     "50_Grass_Badge.png",
        #     "51_Water_Badge.png",
        #     "52_Fire_Badge.png",
        #     "53_Fighting_Badge.png",
        #     "54_Ghost_Badge.png",
        #     "55_GalarFairy_Badge.png",
        #     "56_Rock_Badge.png",
        #     "57_Ice_Badge.png",
        #     "58_Dark_Badge.png",
        #     "59_Dragon_Badge.png",
        #     "60_Cortondo_Badge.png",
        #     "61_Artazon_Badge.png",
        #     "62_Levincia_Badge.png",
        #     "63_Cascarrafa_Badge.png",
        #     "64_Medali_Badge.png",
        #     "65_Montenevera_Badge.png",
        #     "66_Alfornada_Badge.png",
        #     "67_Glaseado_Badge.png",
        #     "68_Segin_Badge.png",
        #     "69_Schedar_Badge.png",
        #     "70_Navi_Badge.png",
        #     "71_Ruchbah_Badge.png",
        #     "72_Caph_Badge.png",
        #     "73_South_Province_Badge.png",
        #     "74_West_Province_Badge.png",
        #     "75_East_Province_Badge.png",
        #     "76_Asado_Desert_Badge.png",
        #     "77_Casseroya_Lake_Badge.png",
        #     "78_Coral-Eye_Badge.png",
        #     "79_Sea_Ruby_Badge.png",
        #     "80_Spike_Shell_Badge.png",
        #     "81_Jade_Star_Badge.png",
        #     "82_Tranquility_Badge.png",
        #     "83_Freedom_Badge.png",
        #     "84_Patience_Badge.png",
        #     "85_Harmony_Badge.png",
        #     "86_Pride_Badge.png",
        # ]
        #
        # descriptions = [
        #     "It is a simple gray octagon.",
        #     "It is in the shape of a light blue raindrop.",
        #     "It is in the shape of an eight-pointed gold star with an orange octagon in the center.",
        #     "It is shaped like a flower, showing grass, with rainbow colored petals.",
        #     "It is in the shape of a fuchsia heart.",
        #     "It is two concentric golden circles.",
        #     "It is red and shaped like a flame with a small pink diamond in the center.",
        #     "It is shaped like a plant, most likely a Sakaki tree, which is where Giovanni's Japanese name comes from.",
        #     "It is shaped like a pair of wings. The Badge is named after the Greek god of the west wind.",
        #     "It is shaped like a ladybug viewed from above.",
        #     "It is a plain diamond. This Badge is not obtainable until after the player talks to Whitney a second time.",
        #     "It is shaped like a wispy ghost.",
        #     "It is shaped like a fist.",
        #     "It is a steel-colored octagon.",
        #     "It is a hexagon with a snowflake design.",
        #     "It is shaped like a dragon's face.",
        #     "It is shaped like a rectangle with two of its corners more emphasized than the others.",
        #     "It is shaped like a boxing glove.",
        #     "It is shaped like a coiled wire.",
        #     "It is shaped like a wisp of fire.",
        #     "It is shaped like two circles, counterbalancing each other or a barbell.",
        #     "It is shaped like feathers on a bird's wing.",
        #     "It is shaped like a heart, with two sides closing in, possibly in reference to how Tate and Liza are twins.",
        #     "It is shaped like three raindrops arranged in a triangle.",
        #     "It is shaped like a boulder and a Poké Ball combined. It also resembles Roark's hard hat, or possibly a treasure chest.",
        #     "It is shaped like three trees of a forest, with the trunks whited out.",
        #     "It is reminiscent of bricks or a tatami mat.",
        #     "It is shaped like a lake with gray reeds around it or a wave seen from the front, a reference to the type of wetland called a fen. It also resembles Crasher Wake's Mask.",
        #     "It is similar in appearance to a Will-o'-the-wisp or a ghostly aura. It also resembles Fantina's hair.",
        #     "It is shaped like three stones and three pickaxes combined.",
        #     "It is shaped like an iceberg or two icy mountains.",
        #     "It is shaped like a lighthouse.",
        #     "It is shaped like a bow tie, similar to those worn by the Striaton Gym Leaders. It may also bear a resemblance to an opened pea pod, which contains two large peas; one green and one blue, with a smaller red pea at the center.",
        #     "It is shaped like a purple spine of a book.",
        #     "It is shaped like a green heart divided into three parts or the wings and body of an insect.",
        #     "It is shaped like a lightning bolt or a Pikachu or Emolga tail, with an orange crown sticking out of the tip.",
        #     "It is shaped like a vertical piece of earth, the top half of which has cracked and slid out of place, resembling the result of an earthquake, or as two tectonic plates interacting.",
        #     "It is shaped like a stylized feather, with a soaring bird at the bottom.",
        #     "It is shaped like three white icicles.",
        #     "It is shaped like a dragon's head with the snout pointing downwards, a medieval mace, or a dragon's wing when stretched out.",
        #     "It is shaped like a smoke signal with four small purple circles lining up to a poison mark.",
        #     "It is shaped like a raindrop with waves in it.",
        #     "It is shaped like a cliff or a rock climbing wall.",
        #     "It is shaped like two fists clashing against each other.",
        #     "It is shaped like a leaf, with the veins forming the shape of a plant.",
        #     "It is shaped like a shield with bolts shooting out of it.",
        #     "It is shaped like a vitrail with motifs of fairy or butterfly.",
        #     "It is shaped like a crystal ball emanating smoke.",
        #     "It is shaped like a snowflake with an iceberg in the center.",
        #     "It is a design shaped like a stylized leaf of spinach or a leaf floating in the wind.",
        #     "It is a design shaped like three water droplets in the shape of a Tomoe or a splash.",
        #     "It is a design shaped like a flame.",
        #     "It is a design shaped like a fist with a trail indicating a punching motion.",
        #     "It is a design shaped like a will-o'-the-wisp.",
        #     "It is a design shaped like a stylized fairy or butterfly.",
        #     "It is a design shaped like a boulder with cracks in it.",
        #     "It is a design shaped like an ice cube.",
        #     "It is a design shaped like a demonic face with horns and a wide, toothy grin.",
        #     "It is a design shaped like a dragon's face and neck when viewed from the side.",
        #     "It is a round badge with the icon for the Bug type on it.",
        #     "It is a round badge with the icon for the Grass type on it.",
        #     "It is a round badge with the icon for the Electric type on it.",
        #     "It is a round badge with the icon for the Water type on it.",
        #     "It is a round badge with the icon for the Normal type on it.",
        #     "It is a round badge with the icon for the Ghost type on it.",
        #     "It is a round badge with the icon for the Psychic type on it.",
        #     "It is a round badge with the icon for the Ice type on it.",
        #     "It is a round badge with the icon for the Dark type overlaid on top of Team Star's logo.",
        #     "It is a round badge with the icon for the Fire type overlaid on top of Team Star's logo.",
        #     "It is a round badge with the icon for the Poison type overlaid on top of Team Star's logo.",
        #     "It is a round badge with the icon for the Fairy type overlaid on top of Team Star's logo.",
        #     "It is a round badge with the icon for the Fighting type overlaid on top of Team Star's logo.",
        #     "It is a round badge with the icon for the Rock type on it.",
        #     "It is a round badge with the icon for the Flying type on it.",
        #     "It is a round badge with the icon for the Steel type on it.",
        #     "It is a round badge with the icon for the Ground type on it.",
        #     "It is a round badge with the icon for the Dragon type on it.",
        #     "It is shaped like a tellins shell with a small gemstone on it. Its Japanese name refers to Nitidotellina nitidula (桜貝 sakuragai), a species of tellins.",
        #     "It is shaped like a giant clam shell with a small gemstone on it. Its Japanese name refers to the maxima clam (白波貝 shiranamigai).",
        #     "It is shaped like a triumphant star turban with a small gemstone on it. Its Japanese name refers to the triumphant star turban (輪宝貝 rinbōgai).",
        #     "It is shaped like a purple snail shell with a small gemstone on it. Its Japanese name refers to the elongate janthina (瑠璃貝 rurigai), a species of sea snails.",
        #     "The green hexagon and gold, leaf-like emblem reference Erika's Grass-type specialty.",
        #     "Resembles a feather, similar to Skyla's Badge in the core series, the Jet Badge.",
        #     "Resembles a tatami door, something seen in Petalburg Gym.",
        #     "It is shaped like a stylized snowflake, referencing Pryce's Ice-type specialty.",
        #     "It is shaped like a tall volcano or mountain, in reference to the mountainous Poni Island where Hapu comes from.",
        # ]
        #
        # for i in range(0, 86):
        #     name = file_names[i][3: -4].replace('_', ' ')
        #     file_name = '/static/img/' + file_names[i]
        #     description = descriptions[i]
        #     coins = 100 + (i * 200)
        #
        #     db.session.expire_on_commit = False
        #     badge = Badge(name=name, file_name=file_name, description=description, coins=coins)
        #     db.session.add(badge)
        #     db.session.commit()

    all_pokemon = []
    row_pokemon = {0: None, 1: None, 2: None, 3: None, 4: None}

    random.shuffle(pokemon_data)

    for pokemon in pokemon_data:
        # if request.method == 'POST' and 'pokemon_type' in request.form:
        #     pokemon_id = i['pokemon']['url'].split('/')[-2]
        # else:
        #     pokemon_id = i['url'].split('/')[-2]
        # r = requests.get('https://pokeapi.co/api/v2/pokemon/' + pokemon_id)
        # pokemon = r.json()
        #
        # if not pokemon["sprites"]["other"]["official-artwork"]["front_shiny"]:
        #     continue

        # name = pokemon["species"]["name"][0].upper() + pokemon["species"]["name"][1:]
        # types = [pokemon_type["type"]["name"][0].upper() + pokemon_type["type"]["name"][1:]
        #          for pokemon_type in pokemon["types"]]
        # types = ", ".join(types)
        # abilities = [pokemon_type["ability"]["name"][0].upper() + pokemon_type["ability"]["name"][1:]
        #              for pokemon_type in pokemon["abilities"]]
        # abilities = ", ".join(abilities)
        # img_url = pokemon["sprites"]["other"]["official-artwork"]["front_shiny"]
        # coins = random.randint(50, 500)
        # db_pokemon = Pokemon(name=name, types=types, abilities=abilities, img_url=img_url, coins=coins)
        # db.session.add(db_pokemon)
        # db.session.commit()
        # db.session.close()

        html_pokemon = {}
        html_pokemon['id'] = pokemon.id
        html_pokemon['name'] = pokemon.name
        html_pokemon['types'] = pokemon.types
        html_pokemon['abilities'] = '<br>'.join(pokemon.abilities.split(', '))
        html_pokemon['img_url'] = pokemon.img_url
        html_pokemon['coins'] = pokemon.coins
        pokemon = html_pokemon

        if not row_pokemon[0]:
            row_pokemon[0] = pokemon
        elif not row_pokemon[1]:
            row_pokemon[1] = pokemon
        elif not row_pokemon[2]:
            row_pokemon[2] = pokemon
        elif not row_pokemon[3]:
            row_pokemon[3] = pokemon
        else:
            row_pokemon[4] = pokemon
            all_pokemon.append(row_pokemon)
            row_pokemon = {0: None, 1: None, 2: None, 3: None, 4: None}

    if row_pokemon[0]:  # for last incomplete row
        all_pokemon.append(row_pokemon)

    return render_template('index.html', all_pokemon=all_pokemon)


@app.route('/account/pokemons', methods=['GET', 'POST'])
@login_required
def pokemons():
    # cache this VERY IMPORTANT (user is cached in current_user, pokemons are cached in database and global variable
    # __pokemons)

    pokemon_data = None
    pokemon_id = None
    player_id = current_user.id
    if request.method == 'POST' and 'pokemon_id' in request.form:
        pokemon_id = request.form.get('pokemon_id')

        pokemon = Pokemon.query.filter_by(id=pokemon_id).first()
        if current_user.coins < pokemon.coins:
            flash('Insufficient coins, please reload.')
            return redirect(url_for('pokemons'))

        db.session.expire_on_commit = False
        my_pokemon = MyPokemon(player_id=player_id, pokemon_id=pokemon_id)
        db.session.add(my_pokemon)
        db.session.commit()
        # db.session.close()

        pokemon = Pokemon.query.filter_by(id=pokemon_id).first()
        # player = Player.query.filter_by(id=player_id).first() can use current_user
        current_user.coins = current_user.coins - pokemon.coins
        db.session.commit()

        # print(pokemon_id)
        return redirect(url_for('pokemons'))
        #  POST-REDIRECT-GET pattern solves the resubmission issue on refresh page

    # pokemon_data = MyPokemon.query.filter_by(player_id=player_id).order_by(MyPokemon.created_date).all()

    statement = text("""
    SELECT pokemons.id, pokemons.name, pokemons.types, pokemons.abilities, pokemons.img_url, pokemons.coins
    FROM my_pokemons
    JOIN pokemons
    ON my_pokemons.pokemon_id = pokemons.id
    WHERE my_pokemons.player_id = :id
    ORDER BY my_pokemons.created_date DESC;
    """)
    pokemon_data = db.session.execute(statement, {'id': player_id})

    all_pokemon = []
    row_pokemon = {0: None, 1: None, 2: None, 3: None, 4: None}

    # random.shuffle(pokemon_data)

    for pokemon in pokemon_data:
        html_pokemon = {}
        html_pokemon['id'] = pokemon.id
        html_pokemon['name'] = pokemon.name
        html_pokemon['types'] = pokemon.types
        html_pokemon['abilities'] = '<br>'.join(pokemon.abilities.split(', '))
        html_pokemon['img_url'] = pokemon.img_url
        html_pokemon['coins'] = pokemon.coins
        pokemon = html_pokemon

        if not row_pokemon[0]:
            row_pokemon[0] = pokemon
        elif not row_pokemon[1]:
            row_pokemon[1] = pokemon
        elif not row_pokemon[2]:
            row_pokemon[2] = pokemon
        elif not row_pokemon[3]:
            row_pokemon[3] = pokemon
        else:
            row_pokemon[4] = pokemon
            all_pokemon.append(row_pokemon)
            row_pokemon = {0: None, 1: None, 2: None, 3: None, 4: None}

    if row_pokemon[0]:  # for last incomplete row
        all_pokemon.append(row_pokemon)

    return render_template('pokemons.html', all_pokemon=all_pokemon)


@app.route('/account/badges')
@login_required
def badges():
    # cache this VERY IMPORTANT (user is cached in current_user, pokemons are cached in database and global variable
    # __pokemons)

    badge_data = Badge.query.order_by(Badge.created_date.asc()).all()

    # statement = text("""
    # SELECT pokemons.id, pokemons.name, pokemons.types, pokemons.abilities, pokemons.img_url, pokemons.coins
    # FROM my_pokemons
    # JOIN pokemons
    # ON my_pokemons.pokemon_id = pokemons.id
    # WHERE my_pokemons.player_id = :id
    # ORDER BY my_pokemons.created_date DESC;
    # """)
    # pokemon_data = db.session.execute(statement, {'id': player_id})

    all_badge = []
    row_badge = {0: None, 1: None, 2: None, 3: None, 4: None}

    # random.shuffle(pokemon_data)

    for badge in badge_data:
        html_badge = {}
        html_badge['id'] = badge.id
        html_badge['name'] = badge.name
        html_badge['file_name'] = badge.file_name

        description = badge.description.split(' ')
        format_description = []
        line = ''
        for i in range(len(description)):
            line = line + ' ' + description[i]
            if len(line) > 25:
                format_description.append(line[1:].replace(' ', '&nbsp;'))
                line = ''
            elif len(line) <= 25 and i == len(description) - 1:
                format_description.append(line[1:].replace(' ', '&nbsp;'))

        html_badge['description'] = '<br>'.join(format_description)
        html_badge['coins'] = badge.coins
        badge = html_badge

        if not row_badge[0]:
            row_badge[0] = badge
        elif not row_badge[1]:
            row_badge[1] = badge
        elif not row_badge[2]:
            row_badge[2] = badge
        elif not row_badge[3]:
            row_badge[3] = badge
        else:
            row_badge[4] = badge
            all_badge.append(row_badge)
            row_badge = {0: None, 1: None, 2: None, 3: None, 4: None}

    if row_badge[0]:  # for last incomplete row
        all_badge.append(row_badge)

    return render_template('badges.html', all_badge=all_badge)


@app.route('/arena/result')
def arena_result():

    opponent = session['result']['opponent']
    player = session['result']['player']
    result = session['result']['result']

    return render_template('arena_result.html', all_opponents=None, all_pokemon=None, opponent=opponent, player=player,
                           result=result)


@app.route('/arena', methods=['GET', 'POST'])
@login_required
def arena():
    # cache this VERY IMPORTANT (user is cached in current_user, pokemons are cached in database and global variable
    # __pokemons)

    pokemon_data = None
    opponent = None
    player_id = current_user.id

    statement = text("""
                SELECT pokemons.id, pokemons.name, pokemons.types, pokemons.abilities, pokemons.img_url, pokemons.coins
                FROM my_pokemons
                JOIN pokemons
                ON my_pokemons.pokemon_id = pokemons.id
                WHERE my_pokemons.player_id = :id
                ORDER BY my_pokemons.created_date DESC;
                """)
    pokemon_data = list(db.session.execute(statement, {'id': player_id}))
    if len(pokemon_data) == 0:
        flash('You have not caught a pokemon. Go to home page.')
        return render_template('arena.html', all_opponents=None, all_pokemon=None, opponent=None, player=None, result=None)
    pokemon_data = None

    if request.method == 'POST' and 'opponent_id' in request.form and 'player_id' in request.form \
            and 'play' in request.form:
        opponent_id = request.form.get('opponent_id')
        player_id = request.form.get('player_id')
        opponent_attack_1 = request.form.get('opponent_attack_1')
        opponent_attack_2 = request.form.get('opponent_attack_2')
        opponent_attack_3 = request.form.get('opponent_attack_3')
        player_attack_1 = request.form.get('player_attack_1')
        player_attack_2 = request.form.get('player_attack_2')
        player_attack_3 = request.form.get('player_attack_3')
        player_damage_1 = int(request.form.get('player_damage_1'))
        player_damage_2 = int(request.form.get('player_damage_2'))
        player_damage_3 = int(request.form.get('player_damage_3'))

        decision = random.randint(0,1)
        total = player_damage_1 + player_damage_2 + player_damage_3
        if decision == 0:
            #  player WINS
            while True:
                opponent_damage_1 = random.randint(1, total - 1)
                opponent_damage_2 = random.randint(1, total - 1 - opponent_damage_1)
                opponent_damage_3 = random.randint(1, total - 1 - opponent_damage_1 - opponent_damage_2)
                if opponent_damage_1 + opponent_damage_2 + opponent_damage_3 < total:
                    break
        elif decision == 1:
            #  opponent WINS
            while True:
                new_total = total * 2
                opponent_damage_1 = random.randint(1, new_total)
                opponent_damage_2 = random.randint(1, new_total)
                opponent_damage_3 = random.randint(1, new_total)
                if opponent_damage_1 + opponent_damage_2 + opponent_damage_3 > total:
                    break

        opponent = Pokemon.query.filter_by(id=opponent_id).first()
        html_pokemon = {}
        html_pokemon['id'] = opponent.id
        html_pokemon['name'] = opponent.name
        html_pokemon['types'] = opponent.types
        attacks = []
        attacks.append(opponent_attack_1)
        attacks.append(opponent_attack_2)
        attacks.append(opponent_attack_3)
        html_pokemon['attacks'] = attacks
        damages = []
        damages.append(opponent_damage_1)
        damages.append(opponent_damage_2)
        damages.append(opponent_damage_3)
        html_pokemon['damages'] = damages
        html_pokemon['abilities'] = '<br>'.join(opponent.abilities.split(', '))
        html_pokemon['img_url'] = opponent.img_url
        html_pokemon['coins'] = opponent.coins
        opponent = html_pokemon

        player = Pokemon.query.filter_by(id=player_id).first()
        html_pokemon = {}
        html_pokemon['id'] = player.id
        html_pokemon['name'] = player.name
        html_pokemon['types'] = player.types
        attacks = []
        attacks.append(player_attack_1)
        attacks.append(player_attack_2)
        attacks.append(player_attack_3)
        html_pokemon['attacks'] = attacks
        damages = []
        damages.append(player_damage_1)
        damages.append(player_damage_2)
        damages.append(player_damage_3)
        html_pokemon['damages'] = damages
        html_pokemon['abilities'] = '<br>'.join(player.abilities.split(', '))
        html_pokemon['img_url'] = player.img_url
        html_pokemon['coins'] = player.coins
        player = html_pokemon

        result = decision
        pp ('DECISION: ' + str(result))

        #  update earned coins here
        logged_in_player = Player.query.filter_by(id=current_user.id).first()
        total = player_damage_1 + player_damage_2 + player_damage_3

        if decision == 0:
            current_user.earned = current_user.earned + opponent_damage_1 + opponent_damage_2 + opponent_damage_3
            db.session.commit()
        else:
            if logged_in_player.earned < total:
                current_user.coins = current_user.coins - total
                db.session.commit()
            else:
                current_user.earned = current_user.earned - total
                db.session.commit()

        session['result'] = {}
        session['result']['opponent'] = opponent
        session['result']['player'] = player
        session['result']['result'] = result
        return redirect(url_for('arena_result'))

        # return render_template('arena_result.html', all_opponents=None, all_pokemon=None, opponent=opponent, player=player,
        #                        result=result)

    if request.method == 'POST' and 'opponent_id' in request.form and 'player_id' in request.form:
        opponent_id = request.form.get('opponent_id')
        player_id = request.form.get('player_id')

        opponent = Pokemon.query.filter_by(id=opponent_id).first()
        html_pokemon = {}
        html_pokemon['id'] = opponent.id
        html_pokemon['name'] = opponent.name
        html_pokemon['types'] = opponent.types
        abilities = opponent.abilities.split(', ')
        attacks = []
        attacks.append(random.choice(abilities))
        attacks.append(random.choice(abilities))
        attacks.append(random.choice(abilities))
        html_pokemon['abilities'] = '<br>'.join(opponent.abilities.split(', '))
        html_pokemon['attacks'] = attacks
        html_pokemon['img_url'] = opponent.img_url
        html_pokemon['coins'] = opponent.coins
        opponent = html_pokemon

        player = Pokemon.query.filter_by(id=player_id).first()
        html_pokemon = {}
        html_pokemon['id'] = player.id
        html_pokemon['name'] = player.name
        html_pokemon['types'] = player.types
        html_pokemon['abilities'] = '<br>'.join(player.abilities.split(', '))
        html_pokemon['img_url'] = player.img_url
        html_pokemon['coins'] = player.coins
        player = html_pokemon

        return render_template('arena.html', all_opponents=None, all_pokemon=None, opponent=opponent, player=player, result=None)

    if request.method == 'POST' and 'opponent_id' in request.form:
        opponent_id = request.form.get('opponent_id')

        # pokemon = Pokemon.query.filter_by(id=pokemon_id).first()
        # if current_user.coins < pokemon.coins:
        #     flash('Insufficient coins, please reload.')
        #     return redirect(url_for('pokemons'))
        #
        # db.session.expire_on_commit = False
        # my_pokemon = MyPokemon(player_id=player_id, pokemon_id=pokemon_id)
        # db.session.add(my_pokemon)
        # db.session.commit()
        # db.session.close()

        opponent = Pokemon.query.filter_by(id=opponent_id).first()
        html_pokemon = {}
        html_pokemon['id'] = opponent.id
        html_pokemon['name'] = opponent.name
        html_pokemon['types'] = opponent.types
        html_pokemon['abilities'] = '<br>'.join(opponent.abilities.split(', '))
        html_pokemon['img_url'] = opponent.img_url
        html_pokemon['coins'] = opponent.coins
        opponent = html_pokemon
        # # player = Player.query.filter_by(id=player_id).first() can use current_user
        # current_user.coins = current_user.coins - pokemon.coins
        # db.session.commit()

        # print(pokemon_id)
        # return redirect(url_for('pokemons'))

        statement = text("""
            SELECT pokemons.id, pokemons.name, pokemons.types, pokemons.abilities, pokemons.img_url, pokemons.coins
            FROM my_pokemons
            JOIN pokemons
            ON my_pokemons.pokemon_id = pokemons.id
            WHERE my_pokemons.player_id = :id
            ORDER BY my_pokemons.created_date DESC;
            """)
        pokemon_data = db.session.execute(statement, {'id': player_id})

        all_pokemon = []
        row_pokemon = {0: None, 1: None, 2: None, 3: None, 4: None}

        # random.shuffle(pokemon_data)

        for pokemon in pokemon_data:
            html_pokemon = {}
            html_pokemon['id'] = pokemon.id
            html_pokemon['name'] = pokemon.name
            html_pokemon['types'] = pokemon.types
            html_pokemon['abilities'] = '<br>'.join(pokemon.abilities.split(', '))
            html_pokemon['img_url'] = pokemon.img_url
            html_pokemon['coins'] = pokemon.coins
            pokemon = html_pokemon

            if not row_pokemon[0]:
                row_pokemon[0] = pokemon
            elif not row_pokemon[1]:
                row_pokemon[1] = pokemon
            elif not row_pokemon[2]:
                row_pokemon[2] = pokemon
            elif not row_pokemon[3]:
                row_pokemon[3] = pokemon
            else:
                row_pokemon[4] = pokemon
                all_pokemon.append(row_pokemon)
                row_pokemon = {0: None, 1: None, 2: None, 3: None, 4: None}

        if row_pokemon[0]:  # for last incomplete row
            all_pokemon.append(row_pokemon)

        return render_template('arena.html', all_opponents=None, all_pokemon=all_pokemon, opponent=opponent, player=None, result=None)
        #  POST-REDIRECT-GET pattern solves the resubmission issue on refresh page
    #
    # # pokemon_data = MyPokemon.query.filter_by(player_id=player_id).order_by(MyPokemon.created_date).all()
    #
    offset = random.randint(1, 1159)
    statement = text("""
        SELECT * FROM pokemons ORDER BY pokemons.id LIMIT 100 OFFSET :offset;
    """)
    pokemon_data = list(db.session.execute(statement, {'offset': offset}))

    all_opponents = []
    row_pokemon = {0: None, 1: None, 2: None, 3: None, 4: None}

    random.shuffle(pokemon_data)
    pokemon_data = pokemon_data[69:89]

    for pokemon in pokemon_data:
        html_pokemon = {}
        html_pokemon['id'] = pokemon.id
        html_pokemon['name'] = pokemon.name
        html_pokemon['types'] = pokemon.types
        html_pokemon['abilities'] = '<br>'.join(pokemon.abilities.split(', '))
        html_pokemon['img_url'] = pokemon.img_url
        html_pokemon['coins'] = pokemon.coins
        pokemon = html_pokemon

        if not row_pokemon[0]:
            row_pokemon[0] = pokemon
        elif not row_pokemon[1]:
            row_pokemon[1] = pokemon
        elif not row_pokemon[2]:
            row_pokemon[2] = pokemon
        elif not row_pokemon[3]:
            row_pokemon[3] = pokemon
        else:
            row_pokemon[4] = pokemon
            all_opponents.append(row_pokemon)
            row_pokemon = {0: None, 1: None, 2: None, 3: None, 4: None}

    if row_pokemon[0]:  # for last incomplete row
        all_opponents.append(row_pokemon)

    return render_template('arena.html', all_opponents=all_opponents, all_pokemon=None, opponent=None, player=None, result=None)


# /api/pokemon/<type>
# /api/pokemon/<type>?min_coins=100&max_coins=1000
@app.route('/api/pokemon_type/<type>')
@login_required
def api_pokemon_type(type: str):
    min_coins = request.args.get('min_coins')
    max_coins = request.args.get('max_coins')

    pokemons = {}
    if type and min_coins is None and max_coins is None:
        type = type[0].upper() + type[1:]
        result = Pokemon.query.filter(Pokemon.types.contains(type)).all()

        for r in result:
            pokemons[r.id] = {}
            pokemons[r.id]['name'] = r.name
            pokemons[r.id]['types'] = r.types
            pokemons[r.id]['abilities'] = r.abilities
            pokemons[r.id]['image'] = r.img_url
            pokemons[r.id]['coins'] = r.coins

    elif type and min_coins is not None and max_coins is not None:
        type = type[0].upper() + type[1:]
        result = Pokemon.query.filter(Pokemon.types.contains(type), Pokemon.coins.between(int(min_coins), int(max_coins))).all()
        #  between is INCLUSIVE
        for r in result:
            pokemons[r.id] = {}
            pokemons[r.id]['name'] = r.name
            pokemons[r.id]['types'] = r.types
            pokemons[r.id]['abilities'] = r.abilities
            pokemons[r.id]['image'] = r.img_url
            pokemons[r.id]['coins'] = r.coins

    pokemons = json.dumps(pokemons, indent=8)
    return pokemons


# /api/pokemon/<ability>
# /api/pokemon/<ability>?min_coins=100&max_coins=1000
@app.route('/api/pokemon_ability/<ability>')
@login_required
def api_pokemon_ability(ability: str):
    min_coins = request.args.get('min_coins')
    max_coins = request.args.get('max_coins')

    pokemons = {}
    if ability and min_coins is None and max_coins is None:
        ability = ability[0].upper() + ability[1:]
        result = Pokemon.query.filter(Pokemon.abilities.contains(ability)).all()

        for r in result:
            pokemons[r.id] = {}
            pokemons[r.id]['name'] = r.name
            pokemons[r.id]['types'] = r.types
            pokemons[r.id]['abilities'] = r.abilities
            pokemons[r.id]['image'] = r.img_url
            pokemons[r.id]['coins'] = r.coins

    elif ability and min_coins is not None and max_coins is not None:
        ability = ability[0].upper() + ability[1:]
        result = Pokemon.query.filter(Pokemon.abilities.contains(ability), Pokemon.coins.between(int(min_coins), int(max_coins))).all()
        #  between is INCLUSIVE

        for r in result:
            pokemons[r.id] = {}
            pokemons[r.id]['name'] = r.name
            pokemons[r.id]['types'] = r.types
            pokemons[r.id]['abilities'] = r.abilities
            pokemons[r.id]['image'] = r.img_url
            pokemons[r.id]['coins'] = r.coins

    pokemons = json.dumps(pokemons, indent=8)
    return pokemons


# /api/pokemon/types
@app.route('/api/pokemon_type/types')
@login_required
def api_pokemon_types():
    result = Pokemon.query.all()
    all_types = []
    for r in result:
        types = r.types.split(', ')
        for type in types:
            all_types.append(type)

    all_types = list(set(all_types))
    types = {}
    i = 0
    for type in all_types:
        types[i] = type
        i = i + 1

    types = json.dumps(types, indent=8)
    return types


# /api/pokemon/abilities
@app.route('/api/pokemon_ability/abilities')
@login_required
def api_pokemon_abilities():
    result = Pokemon.query.all()
    all_abilities = []
    for r in result:
        abilities = r.abilities.split(', ')
        for ability in abilities:
            all_abilities.append(ability)

    all_abilities = list(set(all_abilities))
    abilities = {}
    i = 0
    for ability in all_abilities:
        abilities[i] = ability
        i = i + 1

    abilities = json.dumps(abilities, indent=8)
    return abilities


# /api/pokemon/?types=Grass,Poison
@app.route('/api/pokemon_type/')
@login_required
def api_pokemontype():
    types = request.args.get('types')

    pokemons = {}
    if types is not None:
        types = types.split(',')
        type0 = types[0][0].upper() + types[0][1:]
        type1 = types[1][0].upper() + types[1][1:]
        result = Pokemon.query.filter(Pokemon.types.contains(type0), Pokemon.types.contains(type1)).all()

        for r in result:
            pokemons[r.id] = {}
            pokemons[r.id]['name'] = r.name
            pokemons[r.id]['types'] = r.types
            pokemons[r.id]['abilities'] = r.abilities
            pokemons[r.id]['image'] = r.img_url
            pokemons[r.id]['coins'] = r.coins

    pokemons = json.dumps(pokemons, indent=8)
    return pokemons


# /api/pokemon/?limit=100000&offset=0
@app.route('/api/pokemon/')
@login_required
def api_pokemon():
    limit = request.args.get('limit')
    offset = request.args.get('offset')

    pokemons = {}
    if limit is not None and offset is not None:
        result = Pokemon.query.limit(int(limit)).offset(int(offset)).all()

        for r in result:
            pokemons[r.id] = {}
            pokemons[r.id]['name'] = r.name
            pokemons[r.id]['types'] = r.types
            pokemons[r.id]['abilities'] = r.abilities
            pokemons[r.id]['image'] = r.img_url
            pokemons[r.id]['coins'] = r.coins

    pokemons = json.dumps(pokemons, indent=8)
    return pokemons


# /api/pokemon/<name>
@app.route('/api/pokemon/<name>')
@login_required
def api_pokemon_name(name: str):
    if name:
        name = name[0].upper() + name[1:]
        result = Pokemon.query.filter_by(name=name).first()
        pokemon = {}
        pokemon[result.id] = {}
        pokemon[result.id]['name'] = result.name
        pokemon[result.id]['types'] = result.types
        pokemon[result.id]['abilities'] = result.abilities
        pokemon[result.id]['image'] = result.img_url
        pokemon[result.id]['coins'] = result.coins
        pokemon = json.dumps(pokemon, indent=8)
        return pokemon


@app.route('/apis', methods=['GET', 'POST'])
@login_required
def apis():
    if request.method == 'POST' and 'api_1' in request.form:
        api_1 = request.form.get('api_1')
        # < name > or ?limit = 100000 & offset = 0
        if '?' in api_1:
            api_1 = api_1[1:].split('&')
            limit = api_1[0].split('=')[1]
            offset = api_1[1].split('=')[1]
            if limit is not None and offset is not None:
                result = Pokemon.query.limit(int(limit)).offset(int(offset)).all()
                pokemons = {}
                for r in result:
                    pokemons[r.id] = {}
                    pokemons[r.id]['name'] = r.name
                    pokemons[r.id]['types'] = r.types
                    pokemons[r.id]['abilities'] = r.abilities
                    pokemons[r.id]['image'] = r.img_url
                    pokemons[r.id]['coins'] = r.coins

                pokemons = json.dumps(pokemons, indent=8)
                return render_template('apis.html', output_1=pokemons, output_2=None, output_3=None)
        else:
            name = api_1[0].upper() + api_1[1:]
            result = Pokemon.query.filter_by(name=name).first()
            pokemon = {}
            pokemon[result.id] = {}
            pokemon[result.id]['name'] = result.name
            pokemon[result.id]['types'] = result.types
            pokemon[result.id]['abilities'] = result.abilities
            pokemon[result.id]['image'] = result.img_url
            pokemon[result.id]['coins'] = result.coins
            pokemon = json.dumps(pokemon, indent=8)
            return render_template('apis.html', output_1=pokemon, output_2=None, output_3=None)

    if request.method == 'POST' and 'api_2' in request.form:
        api_2 = request.form.get('api_2')
        # types or <type> or ?types=Grass,Poison or <type>?min_coins=100&max_coins=1000
        if '?' in api_2:
            api_2 = api_2.split('?')
            if len(api_2) == 2 and api_2[0] == '':
                api_2 = api_2[1].split('=')
                types = api_2[1]

                pokemons = {}
                if types is not None:
                    types = types.split(',')
                    type0 = types[0][0].upper() + types[0][1:]
                    type1 = types[1][0].upper() + types[1][1:]
                    result = Pokemon.query.filter(Pokemon.types.contains(type0), Pokemon.types.contains(type1)).all()

                    for r in result:
                        pokemons[r.id] = {}
                        pokemons[r.id]['name'] = r.name
                        pokemons[r.id]['types'] = r.types
                        pokemons[r.id]['abilities'] = r.abilities
                        pokemons[r.id]['image'] = r.img_url
                        pokemons[r.id]['coins'] = r.coins

                pokemons = json.dumps(pokemons, indent=8)
                return render_template('apis.html', output_1=None, output_2=pokemons, output_3=None)
            elif len(api_2) == 2:
                type = api_2[0]
                api_2 = api_2[1].split('&')
                min_coins = api_2[0].split('=')[1]
                max_coins = api_2[1].split('=')[1]

                type = type[0].upper() + type[1:]
                result = Pokemon.query.filter(Pokemon.types.contains(type),
                                              Pokemon.coins.between(int(min_coins), int(max_coins))).all()
                #  between is INCLUSIVE
                pokemons = {}
                for r in result:
                    pokemons[r.id] = {}
                    pokemons[r.id]['name'] = r.name
                    pokemons[r.id]['types'] = r.types
                    pokemons[r.id]['abilities'] = r.abilities
                    pokemons[r.id]['image'] = r.img_url
                    pokemons[r.id]['coins'] = r.coins

                pokemons = json.dumps(pokemons, indent=8)
                return render_template('apis.html', output_1=None, output_2=pokemons, output_3=None)

        else:
            if api_2 == 'types':
                result = Pokemon.query.all()
                all_types = []
                for r in result:
                    types = r.types.split(', ')
                    for type in types:
                        all_types.append(type)

                all_types = list(set(all_types))
                types = {}
                i = 0
                for type in all_types:
                    types[i] = type
                    i = i + 1

                types = json.dumps(types, indent=8)
                return render_template('apis.html', output_1=None, output_2=types, output_3=None)
            else:
                type = api_2[0].upper() + api_2[1:]
                result = Pokemon.query.filter(Pokemon.types.contains(type)).all()
                pokemons = {}
                for r in result:
                    pokemons[r.id] = {}
                    pokemons[r.id]['name'] = r.name
                    pokemons[r.id]['types'] = r.types
                    pokemons[r.id]['abilities'] = r.abilities
                    pokemons[r.id]['image'] = r.img_url
                    pokemons[r.id]['coins'] = r.coins
                pokemons = json.dumps(pokemons, indent=8)
                return render_template('apis.html', output_1=None, output_2=pokemons, output_3=None)

    if request.method == 'POST' and 'api_3' in request.form:
        api_3 = request.form.get('api_3')
        # abilities or <ability> or <ability>?min_coins=100&max_coins=1000
        if '?' in api_3:
            api_3 = api_3.split('?')
            if len(api_3) == 2:
                ability = api_3[0]
                api_3 = api_3[1].split('&')
                min_coins = api_3[0].split('=')[1]
                max_coins = api_3[1].split('=')[1]

                ability = ability[0].upper() + ability[1:]
                result = Pokemon.query.filter(Pokemon.abilities.contains(ability), Pokemon.coins.between(int(min_coins), int(max_coins))).all()
                #  between is INCLUSIVE
                pokemons = {}
                for r in result:
                    pokemons[r.id] = {}
                    pokemons[r.id]['name'] = r.name
                    pokemons[r.id]['types'] = r.types
                    pokemons[r.id]['abilities'] = r.abilities
                    pokemons[r.id]['image'] = r.img_url
                    pokemons[r.id]['coins'] = r.coins

                pokemons = json.dumps(pokemons, indent=8)
                return render_template('apis.html', output_1=None, output_2=None, output_3=pokemons)
        else:
            if api_3 == 'abilities':
                result = Pokemon.query.all()
                all_abilities = []
                for r in result:
                    abilities = r.abilities.split(', ')
                    for ability in abilities:
                        all_abilities.append(ability)

                all_abilities = list(set(all_abilities))
                abilities = {}
                i = 0
                for ability in all_abilities:
                    abilities[i] = ability
                    i = i + 1

                abilities = json.dumps(abilities, indent=8)
                return render_template('apis.html', output_1=None, output_2=None, output_3=abilities)
            else:
                ability = api_3[0].upper() + api_3[1:]
                result = Pokemon.query.filter(Pokemon.abilities.contains(ability)).all()
                pokemons = {}
                for r in result:
                    pokemons[r.id] = {}
                    pokemons[r.id]['name'] = r.name
                    pokemons[r.id]['types'] = r.types
                    pokemons[r.id]['abilities'] = r.abilities
                    pokemons[r.id]['image'] = r.img_url
                    pokemons[r.id]['coins'] = r.coins
                pokemons = json.dumps(pokemons, indent=8)
                return render_template('apis.html', output_1=None, output_2=None, output_3=pokemons)

    return render_template('apis.html', output_1=None, output_2=None, output_3=None)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and 'email' in request.form and 'hashed_password' in request.form \
            and 'full_name' in request.form and 'coins' in request.form:
        email = request.form.get('email')
        hashed_password = request.form.get('hashed_password')
        full_name = request.form.get('full_name')
        coins = request.form.get('coins')

        db.session.expire_on_commit = False
        player = Player(full_name=full_name, email=email, hashed_password=hashed_password, coins=coins)
        db.session.add(player)
        db.session.commit()
        # db.session.close()

        flash('Player created.')

        player = Player.query.filter_by(email=email).first()
        if player:
            if player.hashed_password == request.form.get('hashed_password'):
                login_user(player, remember=True)
                return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'email' in request.form and 'hashed_password' in request.form:
        player = Player.query.filter_by(email=request.form.get('email')).first()
        if player:
            if player.hashed_password == request.form.get('hashed_password'):
                login_user(player, remember=True)
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password.')
        else:
            flash('Invalid email or password.')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@login_manager.user_loader
def load_player(id):
    return Player.query.get(int(id))


if __name__ == '__main__':
    pass  # this is where we can call creation of db and importing mock data
