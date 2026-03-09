from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from random import *
from os import *
import math

app = Ursina()


# DIALOGUE

###########################################

# -------------------------
# POKEMON STYLE DIALOGUE
# -------------------------


# -------------------------
# POKEMON STYLE DIALOGUE
# -------------------------

# -------------------------
# SIMPLE POKEMON DIALOGUE
# -------------------------

dialogue_active = False
dialogue_text_full = ""
dialogue_index = 0

dialogue_text = Text(
    text="",
    position=(0,-0.45),
    scale=1.6,
    origin=(0,0),
    background=True
)


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

    if key == "enter":

        if dialogue_index < len(dialogue_text_full):
            dialogue_index = len(dialogue_text_full)
            dialogue_text.text = dialogue_text_full
        else:
            dialogue_text.text = ""
            dialogue_active = False





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

pokedex = ["mew","onix","charizard","pikachu","bulbasaur","charmander","dragonite","venusaur"]
pokedex_complete = False

# ---------------------
# DATA
# ---------------------

spawnable_pokemon = ["mew","onix","charizard","pikachu","bulbasaur","charmander","dragonite","venusaur"]

pokemon = []
caught_pokemon = []
pokeballs = []
shadow_balls = []

mewtwo_spawned = False


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
        "venusaur":0.02
    }

    sc = scale_map.get(randompokemon,1)

    pok = Entity(model=randompokemon, position=pos, scale=sc)
    pok.name = randompokemon

    pokemon.append(pok)


def spawn_pokemon():
    for _ in spawnpoints:
        spawn_new_pokemon()

spawn_pokemon()
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
        "mewtwo":3
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

# ---------------------
# SPAWN MEWTWO
# ---------------------

def spawn_mewtwo():

    global mewtwo_spawned

    if mewtwo_spawned:
        return

    print("POKEDEX COMPLETE!")
    print("Mewtwo appeared!")

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
# PLAYER SAFETY
# ---------------------

def catch_animation(ball, p):

    # stop physics
    ball.velocity = Vec3(0,0,0)

    # lock objects so collision can't trigger again
    ball.catching = True
    p.being_caught = True

    # lift ball
    ball.animate_y(ball.y + 1, duration=0.4, curve=curve.out_quad)

    # shake animation
    def shake():

        ball.animate_rotation_z(20, duration=0.08)
        ball.animate_rotation_z(-20, duration=0.08, delay=0.08)
        ball.animate_rotation_z(0, duration=0.08, delay=0.16)

    invoke(shake, delay=0.5)
    invoke(shake, delay=1.0)
    invoke(shake, delay=1.5)

    # stars
    def stars():

        for i in range(8):

            star = Entity(
                model="sphere",
                color=color.yellow,
                scale=0.1,
                position=ball.position
            )

            star.animate_position(
                star.position + Vec3(
                    random()-0.5,
                    random(),
                    random()-0.5
                ).normalized()*2,
                duration=0.5
            )

            star.animate_scale(0, duration=0.5)

            destroy(star, delay=0.5)

    # finish catch
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

        check_pokedex()

        invoke(spawn_new_pokemon, delay=8)

    invoke(stars, delay=2)
    invoke(finish, delay=2.3)



def throw_masterball():

    if mewtwo_catch:
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

    if True:
        
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

def input(key):

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
    global mewtwo_catch
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

                        break

                # NORMAL CATCH
                caught_name = p.name

                catch_animation(ball, p)

                caught_pokemon.append(caught_name)

                print("You caught:", caught_name)
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


app.run()
