try: import ursina
except ImportError: import subprocess, sys; subprocess.check_call([sys.executable, "-m", "pip", "install", "ursina"])
try:
    import pygame
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from random import *
from os import *
import math

pygame.mixer.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def changemusic(file):
    path = os.path.join(BASE_DIR, file)
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(-1)

def playsound(file):
    path = os.path.join(BASE_DIR, file)
    pygame.mixer.Sound(path).play()



app = Ursina()
# config things
changemusic("pokemusic.mp3")
window.show_fps = True

# Hide the default top-right UI
window.exit_button.visible = False  # removes the X button
window.cog_button.visible = False     # removes the settings gear
window.entity_counter.visible = False # removes the entity counter





# DIALOGUE

###########################################

# Dialogue text explicitly parented to camera.ui
dialogue_text = Text(
    text="",
    position=(0,-0.45),
    scale=1.6,
    origin=(0,0),
    background=True,
    parent=camera.ui  # must be parented to camera.ui
)

# Dialogue logic
dialogue_active = False
dialogue_text_full = ""
dialogue_index = 0

def dialogue(text, text_colour=color.white, speaker=""):
    global dialogue_active, dialogue_text_full, dialogue_index
    dialogue_active = True
    dialogue_index = 0
    dialogue_text_full = f"{speaker}: {text}"
    dialogue_text.text = ""
    dialogue_text.color = text_colour

def update_dialogue():
    global dialogue_index
    if not dialogue_active:
        return
    if dialogue_index < len(dialogue_text_full):
        dialogue_index += 1
        dialogue_text.text = dialogue_text_full[:dialogue_index]

def input_dialogue(key):
    global dialogue_active, dialogue_index
    if not dialogue_active:
        return
    if key == 'enter':
        if dialogue_index < len(dialogue_text_full):
            dialogue_index = len(dialogue_text_full)
            dialogue_text.text = dialogue_text_full
        else:
            dialogue_text.text = ""
            dialogue_active = False





def touches(a, b, distance):
    """
    Returns True if points a and b are within 'distance' of each other.
    a, b should be Vec3 or tuple (x, y, z)
    """
    # convert tuples to Vec3 if needed
    if not isinstance(a, Vec3):
        a = Vec3(*a)
    if not isinstance(b, Vec3):
        b = Vec3(*b)

    return (a - b).length() <= distance
####################################################



player = FirstPersonController()
player.position = (0,4,0)

Sky()

city = Entity(model="viridian_city", scale=0.5)
ground = Entity(model="cube", scale=(100,1,100), collider="box", color=color.clear)

spawnpoints = [(6,1,9),(6,1,0),(7,1,10),(13,1,15),(6,1,18), (7, 1, 5), (9, 1, 14)]

def randomSpawnpoint():
    return choice(spawnpoints)

# ---------------------
# POKEDEX
# ---------------------

pokedex = ["mew","onix","charizard","pikachu","bulbasaur","charmander","dragonite","venusaur", "squirtle"]
pokedex_complete = False

# ---------------------
# DATA
# ---------------------

spawnable_pokemon = ["onix","charizard","pikachu","bulbasaur","charmander","dragonite","venusaur", "squirtle"]

pokemon = []
caught_pokemon = []
pokeballs = []
shadow_balls = []

mewtwo_spawned = False

mewdialogue = False
mewspawnpoint = (-13, 1, -13)


# ---------------------
# SPAWN SPECIFIC POKEMON FUNCTION
# ---------------------
def spawn_specific_pokemon(name, coordinates):

    scale_map = {
        "mew":0.045,
        "charizard":0.03,
        "pikachu":0.5,
        "bulbasaur":0.02,
        "charmander":0.4,
        "dragonite":0.02,
        "venusaur":0.02,
        "onix":0.03,
        "mewtwo":3,
        "squirtle":0.05
    }

    sc = scale_map.get(name,1)

    pok = Entity(
        model=name,
        position=coordinates,
        scale=sc
    )

    pok.name = name
    pokemon.append(pok)

    return pok

# Now spawn Mew safely (after function is defined)
spawn_specific_pokemon('mew', mewspawnpoint)


def checkmewdialogue():
     global mewdialogue
     if touches(player.position, mewspawnpoint, 4.5) and not mewdialogue:
        dialogue('A Mew appeared!', speaker='Game')
        mewdialogue = True

# ---------------------
# SPAWN NORMAL POKEMON
# ---------------------

def teleport_player_back():
    if player.y < -4:
        player.position = (0, 4, 0)

def spawn_new_pokemon():

    used_positions = [p.position for p in pokemon]
    free_spawns = [Vec3(*s) for s in spawnpoints if Vec3(*s) not in used_positions]

    if not free_spawns:
        return

    pos = choice(free_spawns)
    randompokemon = choice(spawnable_pokemon)

    scale_map = {
        "mew":0.045,
        "charizard":0.03,
        "pikachu":0.5,
        "bulbasaur":0.02,
        "charmander":0.4,
        "dragonite":0.02,
        "venusaur":0.02,
        "squirtle":0.05
    }

    sc = scale_map.get(randompokemon,1)

    pok = Entity(model=randompokemon, position=pos, scale=sc)
    pok.name = randompokemon

    pokemon.append(pok)


def spawn_pokemon():
    for _ in spawnpoints:
        spawn_new_pokemon()

spawn_pokemon()



battlemusic_playing = False



# ---------------------
# SPAWN MEWTWO
# ---------------------

def spawn_mewtwo():

    global mewtwo_spawned, battlemusic_playing

    if mewtwo_spawned:
        return

    print("POKEDEX COMPLETE!")
    print("Mewtwo appeared!")
    changemusic("bossfight.mp3")
    battlemusic_playing = True
    boss = Entity(
        model="mewtwo",
        scale=3,
        position=(9,4,0)
    )

    boss.name = "mewtwo"
    boss.is_boss = True

    boss.hp = 4
    boss.catchable = False

    boss.angle = 0
    boss.attack_timer = 0

    pokemon.append(boss)
    dialogue("You've filled your Pokedex! Now it's time to challenge Mewtwo!", speaker="Profesor Oak")
    dialogue("How dare you challenge me....?", speaker="Mewtwo")
    mewtwo_spawned = True


# ---------------------
# CHECK POKEDEX
# ---------------------

def check_pokedex():

    global pokedex_complete

    if all(p in caught_pokemon for p in pokedex):
        pokedex_complete = True

    if pokedex_complete:
        spawn_mewtwo()


# ---------------------
# CATCH ANIMATION
# ---------------------

def catch_animation(ball, p):

    # Stop ball movement and lock
    ball.velocity = Vec3(0,0,0)
    ball.catching = True
    p.being_caught = True

    start_y = ball.y

    # -----------------------
    # Ball pops up then drops slightly
    # -----------------------
    ball.animate_y(start_y + 1, duration=0.35, curve=curve.out_quad)
    ball.animate_y(start_y + 0.85, duration=0.15, delay=0.35)

    # -----------------------
    # SHAKE SEQUENCE (left-right x3)
    # -----------------------
    shake_times = [0.5, 0.8, 1.1]  # delays for 3 shakes

    for i, delay_time in enumerate(shake_times):

        # left
        invoke(lambda b=ball: b.animate_rotation_z(-25, duration=0.08), delay=delay_time)
        # right
        invoke(lambda b=ball: b.animate_rotation_z(25, duration=0.08), delay=delay_time + 0.08)
        # center
        invoke(lambda b=ball: b.animate_rotation_z(0, duration=0.08), delay=delay_time + 0.16)

    # -----------------------
    # STAR EFFECT
    # -----------------------
    def stars():
        for _ in range(8):
            star = Entity(
                model="sphere",
                color=color.yellow,
                scale=0.1,
                position=ball.position
            )

            direction = Vec3(random()-0.5, random(), random()-0.5).normalized()
            star.animate_position(star.position + direction * 2, duration=0.5)
            star.animate_scale(0, duration=0.5)

            destroy(star, delay=0.5)

    invoke(stars, delay=1.6)  # after shakes

    # -----------------------
    # Finish catch
    # -----------------------
    def finish():
        caught_name = p.name

        if p in pokemon:
            pokemon.remove(p)
        if ball in pokeballs:
            pokeballs.remove(ball)

        destroy(p)
        destroy(ball)

        caught_pokemon.append(caught_name)

        print("You caught:", caught_name)
        print("Caught list:", caught_pokemon)
        playsound("catch.mp3")
        dialogue(caught_name + " was caught!", speaker="Game")
        check_pokedex()
        invoke(spawn_new_pokemon, delay=8)

    invoke(finish, delay=2.0)


# ---------------------
# THROW BALLS
# ---------------------
notmewtwocaught = True
def throw_masterball():

    if mewtwo_catch and notmewtwocaught:
        dialogue("Now it's time to catch Mewtwo with the Masterball", speaker="Professor Oak")
        spawn_pos = player.position + Vec3(0,1.5,0)

        ball = Entity(
            model="masterball",
            scale=0.45,
            position=spawn_pos
        )

        ball.velocity = camera.forward * 7
        pokeballs.append(ball)

def throw_pokeball():

    spawn_pos = player.position + Vec3(0,1.5,0)

    ball = Entity(
        model="pokeball",
        scale=0.1,
        position=spawn_pos
    )

    ball.velocity = camera.forward * 7
    pokeballs.append(ball)


# ---------------------
# SHADOW BALL
# ---------------------

def throw_shadow_ball(mewtwo):

    ball = Entity(
        model="sphere",
        color=color.black,
        scale=0.5,
        position=mewtwo.position + Vec3(0,2,0)
    )

    direction = (player.position - ball.position).normalized()
    ball.velocity = direction * 6

    shadow_balls.append(ball)


# ---------------------
# INPUT
# ---------------------


# POKEDEX




def show_pokedex():
    """Displays all Kanto Pokémon in a grid, toggleable, using local sprites."""

    if hasattr(show_pokedex, "panel") and show_pokedex.panel:
        destroy(show_pokedex.panel)
        show_pokedex.panel = None
        return

    show_pokedex.panel = Entity(parent=camera.ui)

    grid_size = 10
    spacing = 0.08
    start_x = -0.45
    start_y = 0.45
    dialogue("Here's your caught Pokemon!", speaker="Game")

    # Mapping names → numbers
    name_to_number = {
        "bulbasaur": 1, "ivysaur": 2, "venusaur": 3, "charmander": 4, "charmeleon": 5,
        "charizard": 6, "squirtle": 7, "wartortle": 8, "blastoise": 9, "caterpie": 10,
        "metapod": 11, "butterfree": 12, "weedle": 13, "kakuna": 14, "beedrill": 15,
        "pidgey": 16, "pidgeotto": 17, "pidgeot": 18, "rattata": 19, "raticate": 20,
        "spearow": 21, "fearow": 22, "ekans": 23, "arbok": 24, "pikachu": 25, "raichu": 26,
        "sandshrew": 27, "sandslash": 28, "nidoran-f": 29, "nidorina": 30, "nidoqueen": 31,
        "nidoran-m": 32, "nidorino": 33, "nidoking": 34, "clefairy": 35, "clefable": 36,
        "vulpix": 37, "ninetales": 38, "jigglypuff": 39, "wigglytuff": 40, "zubat": 41,
        "golbat": 42, "oddish": 43, "gloom": 44, "vileplume": 45, "paras": 46, "parasect": 47,
        "venonat": 48, "venomoth": 49, "diglett": 50, "dugtrio": 51, "meowth": 52, "persian": 53,
        "psyduck": 54, "golduck": 55, "mankey": 56, "primeape": 57, "growlithe": 58, "arcanine": 59,
        "poliwag": 60, "poliwhirl": 61, "poliwrath": 62, "abra": 63, "kadabra": 64, "alakazam": 65,
        "machop": 66, "machoke": 67, "machamp": 68, "bellsprout": 69, "weepinbell": 70, "victreebel": 71,
        "tentacool": 72, "tentacruel": 73, "geodude": 74, "graveler": 75, "golem": 76, "ponyta": 77,
        "rapidash": 78, "slowpoke": 79, "slowbro": 80, "magnemite": 81, "magneton": 82, "farfetchd": 83,
        "doduo": 84, "dodrio": 85, "seel": 86, "dewgong": 87, "grimer": 88, "muk": 89, "shellder": 90,
        "cloyster": 91, "gastly": 92, "haunter": 93, "gengar": 94, "onix": 95, "drowzee": 96, "hypno": 97,
        "krabby": 98, "kingler": 99, "voltorb": 100, "electrode": 101, "exeggcute": 102, "exeggutor": 103,
        "cubone": 104, "marowak": 105, "hitmonlee": 106, "hitmonchan": 107, "lickitung": 108, "koffing": 109,
        "weezing": 110, "rhyhorn": 111, "rhydon": 112, "chansey": 113, "tangela": 114, "kangaskhan": 115,
        "horsea": 116, "seadra": 117, "goldeen": 118, "seaking": 119, "staryu": 120, "starmie": 121,
        "mr-mime": 122, "scyther": 123, "jynx": 124, "electabuzz": 125, "magmar": 126, "pinsir": 127,
        "tauros": 128, "magikarp": 129, "gyarados": 130, "lapras": 131, "ditto": 132, "eevee": 133,
        "vaporeon": 134, "jolteon": 135, "flareon": 136, "porygon": 137, "omanyte": 138, "omastar": 139,
        "kabuto": 140, "kabutops": 141, "aerodactyl": 142, "snorlax": 143, "articuno": 144, "zapdos": 145,
        "moltres": 146, "dratini": 147, "dragonair": 148, "dragonite": 149, "mewtwo": 150, "mew": 151
    }

    for i, name in enumerate(caught_pokemon):
        number = name_to_number.get(name.lower(), 0)
        if number == 0:
            continue

        row = i // grid_size
        col = i % grid_size
        x = start_x + col * spacing
        y = start_y - row * spacing

        sprite = Entity(
            parent=show_pokedex.panel,
            model='quad',
            texture=f"{number}.png",  # local sprite
            scale=(0.06, 0.06),
            position=(x, y),
            color=color.white  # very important for proper alpha
        )




def check_if_mewtwo_in_pokedex():
    global notmewtwocaught
    if "mewtwo" in caught_pokemon:
        notmewtwocaught = False




def input(key):
    if key == "p":
        show_pokedex()
        return  # ignore other keys while panel open
    if hasattr(show_pokedex, "panel") and show_pokedex.panel:
        return

    if key == "q":
        throw_pokeball()
    if key == "e":
        throw_masterball()
    if key == "o":
        _exit(0)
    input_dialogue(key)
# ---------------------
# UPDATE LOOP
# ---------------------
mewtwo_catch = False

dialogue("Hello! Welcome to the world of Pokemon!", speaker="Professor Oak")

def update():
    update_dialogue()
    global mewtwo_catch, battlemusic_playing
    # -----------------
    # MOVE POKEBALLS
    # -----------------

    for ball in pokeballs[:]:

        ball.position += ball.velocity * time.dt

        for p in pokemon[:]:

            if distance(ball.position, p.position) < 1 and not getattr(p,"being_caught",False):

                # MEWTWO DAMAGE SYSTEM
                if hasattr(p,"is_boss"):

                    if not p.catchable:

                        p.hp -= 1
                        print("Mewtwo HP:",p.hp)

                        destroy(ball)
                        pokeballs.remove(ball)

                        if p.hp <= 0:
                            mewtwo_catch = True
                            p.catchable = True
                            print("Mewtwo is weak! Now catch it!")
                            if battlemusic_playing == True:
                                battlemusic_playing = False
                                changemusic("pokemusic.mp3")

                        break

                # NORMAL CATCH
                p.visible = False

                catch_animation(ball, p)

                # removed duplicate append to caught_pokemon

                print("You caught:", p.name)
                print("Caught list:", caught_pokemon)

                check_pokedex()

                invoke(spawn_new_pokemon, delay=8)

                break


    # -----------------
    # MOVE SHADOWBALLS
    # -----------------

    for ball in shadow_balls[:]:

        ball.position += ball.velocity * time.dt

        if distance(ball.position, player.position) < 1:

            print("Mewtwo hit you!")

            player.position = (0,4,0)

            destroy(ball)
            shadow_balls.remove(ball)


    # -----------------
    # MEWTWO FLYING IN CIRCLES
    # -----------------

    for p in pokemon:

        if hasattr(p,"is_boss") and mewtwo_catch == False:

            # circular flight
            p.angle += time.dt * 0.8

            radius = 9

            x = math.cos(p.angle) * radius
            z = math.sin(p.angle) * radius

            p.position = Vec3(x,4,z)

            # attack timer
            p.attack_timer += time.dt

            if p.attack_timer > 2:

                throw_shadow_ball(p)
                p.attack_timer = 0


    teleport_player_back()
    checkmewdialogue()
    check_if_mewtwo_in_pokedex()

app.run()
