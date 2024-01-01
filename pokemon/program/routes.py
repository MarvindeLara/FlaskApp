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
login_manager.login_view = 'login'  


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
# @login_required
def index():

    pokemon_data = None

    if request.method == 'POST' and 'pokemon_type' in request.form:
        pokemon_type = request.form.get('pokemon_type')

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

        pokemon = Pokemon.query.filter_by(id=pokemon_id).first()
        current_user.coins = current_user.coins - pokemon.coins
        db.session.commit()

        return redirect(url_for('pokemons'))
        #  POST-REDIRECT-GET pattern solves the resubmission issue on refresh page

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
