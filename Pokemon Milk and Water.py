from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from random import *
from os import *

app = Ursina()

player = FirstPersonController()
player.position = (0,4,0)

Sky() #create sky
#create the city and ground
city = Entity(model="viridian_city", scale=0.5)
ground = Entity(model="cube", scale=(100, 1, 100), collider="box", color=color.clear)
spawnpoints = [(6,1,9),(6,1,0),(7,1,10),(13,1,15),(6,1,18)]

def randomSpawnpoint():
    return choice(spawnpoints)


spawnable_pokemon = ["mewtwo", "mew", "onix", "charizard", "pikachu", "bulbasaur", "charmander", "dragonite"]
pokemon = []
caught_pokemon = []
pokeballs = []


def spawn_new_pokemon():
    # find free spawnpoints
    used_positions = [p.position for p in pokemon]
    free_spawns = [Vec3(*s) for s in spawnpoints if Vec3(*s) not in used_positions]

    if not free_spawns:
        return  # no free spawnpoint

    pos = choice(free_spawns)

    randompokemon = choice(spawnable_pokemon)
    if randompokemon == 'wailmer':
        sc = 0.02
    elif randompokemon == 'mew':
        sc = 0.045
    elif randompokemon == 'mewtwo':
        sc = 3
    elif randompokemon == 'charizard':
        sc = 0.03
    elif randompokemon == 'pikachu':
        sc = 0.5
    elif randompokemon == 'bulbasaur':
        sc = 0.02
    elif randompokemon == 'charmander':
        sc = 0.2
    elif randompokemon == 'dragonite':
        sc = 0.02
    else:
        sc = 1

    pok = Entity(model=randompokemon, position=pos, scale=sc)
    pok.name = randompokemon

    pokemon.append(pok)


def spawn_pokemon():
    for _ in spawnpoints:
        spawn_new_pokemon()
spawn_pokemon()


def teleport_player_back():
    if player.y < -2:
        player.position = (0,4,0)


def throw_pokeball():
    spawn_pos = player.position + Vec3(0,1.5,0)

    ball = Entity(
        model="pokeball",
        scale=0.2,
        position=spawn_pos
    )

    ball.velocity = camera.forward * 7
    pokeballs.append(ball)

def throw_masterball():
    spawn_pos = player.position + Vec3(0,1.5,0)

    ball = Entity(
        model="masterball",
        scale=1,
        position=spawn_pos
    )

    ball.velocity = camera.forward * 7
    pokeballs.append(ball)


def input(key):
    if key == "q":
        throw_pokeball()

    if key == "e":
        throw_masterball()

    if key == "o":
        _exit(0)


def update():

    for ball in pokeballs[:]:
        ball.position += ball.velocity * time.dt

        for p in pokemon[:]:

            if distance(ball.position, p.position) < 1:

                caught_name = p.name   # SAVE NAME FIRST

                destroy(ball)
                destroy(p)

                pokeballs.remove(ball)
                pokemon.remove(p)

                caught_pokemon.append(caught_name)

                print("You caught:", caught_name)
                print("Caught list:", caught_pokemon)

                invoke(spawn_new_pokemon, delay=8)

                break

    teleport_player_back()


app.run()
