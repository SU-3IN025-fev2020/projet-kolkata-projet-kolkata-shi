# -*- coding: utf-8 -*-

# Nicolas, 2020-03-20

from __future__ import absolute_import, print_function, unicode_literals
from gameclass import Game, check_init_game_done
from spritebuilder import SpriteBuilder
from players import Player
from sprite import MovingSprite
from ontology import Ontology
from itertools import chain
import pygame
import glo

import random
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# ==================
import a_star


__author__ = "Shi YU, 28507587"
__email__ = "shi4yu2@gmail.com"


# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()



def init(_boardname=None):
    global player, game
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else 'kolkata_6_10'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5  # frames per second
    # game.mainiteration()
    game.mask.allow_overlaping_players = True
    # player = game.player


def init_map(game):
    """initialisation block"""
    # -------------------------------
    # Initialisation
    # -------------------------------
    nbLignes = game.spriteBuilder.rowsize
    nbColonnes = game.spriteBuilder.colsize
    # print("lignes: {}".format(nbLignes))
    # print("colonnes: {}".format(nbColonnes))

    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)

    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    # print("Init states: {}".format(initStates))

    # on localise tous les objets  ramassables (les restaurants)
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    # print("Goal states: {}".format(goalStates))
    nbRestaus = len(goalStates)

    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    # print("Wall states: {}".format(wallStates))

    # on liste toutes les positions permises
    allowedStates = [(x, y) for x in range(nbLignes) for y in range(nbColonnes) \
                     if (x, y) not in (wallStates + goalStates)]
    # print("AllowedStates", allowedStates)
    return nbLignes, nbColonnes, players, nbPlayers, initStates, goalStates, nbRestaus, wallStates, allowedStates


def restaurant_random_choice(nbPlayers, nbRestaus, posPlayers, goalStates):
    restau = [0] * nbPlayers
    # print("strategie aleatoire uniforme")
    for j in range(nbPlayers):
        c = random.randint(0, nbRestaus - 1)
        # print("joueur {} {} chosit resto {} {}".format(j, posPlayers[j], c, goalStates[c]))
        restau[j] = c
    return restau


def restaurant_tetu(nbPlayers, nbRestaus, posPlayers, goalStates):
    restau = [0] * nbPlayers
    # print("strategie tetu")
    for j in range(nbPlayers):
        c = j % nbRestaus
        # print("joueur {} {} chosit resto {} {}".format(j, posPlayers[j], c, goalStates[c]))
        restau[j] = c
    return restau


def restaurant_plusproche(nbPlayers, nbRestaus, posPlayers, goalStates):
    restau = [0] * nbPlayers
    # print("strategie le plus proche")
    for j in range(nbPlayers):
        distance_list = [a_star.manhattan(posPlayers[j], goalStates[i]) for i in range(nbRestaus)]
        c = distance_list.index(min(distance_list))  # minimal distance choice

        # print("joueur {} {} chosit resto {} {}".format(j, posPlayers[j], c, goalStates[c]))
        restau[j] = c
    return restau


def main():
    # for arg in sys.argv:
    iterations = 20  # default
    if len(sys.argv) >= 2:
        iterations = int(sys.argv[1])
    # print("Iterations: {}".format(iterations))

    init()

    # -------------------------------
    # Initialisation
    # -------------------------------
    nbLignes, nbColonnes, players, nbPlayers, \
    initStates, goalStates, nbRestaus, wallStates, allowedStates = init_map(game)

    # Generate the map for pathfinding algorithm
    mapGame = allowedStates + goalStates


    # -------------------------------
    # Placement aleatoire des joueurs, en évitant les obstacles
    # -------------------------------
    posPlayers = initStates

    for j in range(nbPlayers):
        x, y = random.choice(allowedStates)
        players[j].set_rowcol(x, y)
        # game.mainiteration()
        posPlayers[j] = (x, y)

    # -------------------------------
    # chaque joueur choisit un restaurant
    # -------------------------------
    chemin = {}

    # -------------------------------
    # gain
    # ------------------------------
    # Players's gain
    # gain is represented as a dict
    # each restaurant is associated with players that arrived at that restaurant
    # gain = {restaurant: players}
    success = [0]*nbPlayers
    gain = {}

    # -------------------------------
    # strategy
    # ------------------------------
    # Stratégie aléatoire uniforme =================================
    restau0 = restaurant_random_choice(nbPlayers, nbRestaus, posPlayers, goalStates)
    # Stratégie tétue (toujours le même restaurant) ================
    # player's choice =  player_number % nbRestaus
    restau1 = restaurant_tetu(nbPlayers, nbRestaus, posPlayers, goalStates)

    # Stratégie restaurant le plus proche================
    restau2 = restaurant_plusproche(nbPlayers, nbRestaus, posPlayers, goalStates)

    if len(sys.argv) >= 3:
        strategy = str(sys.argv[2])
    else:
        strategy = "01"

    # Competition

    if strategy == "02":
        # aléatoire uniforme vs. le plus proche
        strategy_competition = [0, 2]
        restau = restau0[:5] + restau2[5:]
    elif strategy == "12":
        # têtu vs. le plus proche
        strategy_competition = [1, 2]
        restau = restau1[:5] + restau2[5:]
    else:
        # aléatoire uniforme vs. têtu
        strategy_competition = [0, 1]
        restau = restau0[:5] + restau1[5:]

    # print("restau {}".format(restau))
    # -------------------------------
    # Find path with A* algorithm
    # -------------------------------
    for player, restaurant in enumerate(restau):
        chemin[player] = a_star.astar_search(posPlayers[player], goalStates[restaurant], mapGame)
        # And generate gain
        gain[restaurant] = set()

    # print("chemin: {}".format(chemin))
    # print("gain: {}".format(gain))


    # Remplissage des restaurants
    remplissage = {}
    for i in range(nbRestaus):
        remplissage["restaurant_"+str(i)] = [0]
    # remplissage["strategie"] = [strategy]

    # -------------------------------
    # Boucle principale de déplacements
    # -------------------------------
    for i in range(iterations):
        # print(" ==== iteration {} ====".format(i))
        for j in range(nbPlayers):  # on fait bouger chaque joueur séquentiellement
            row, col = posPlayers[j]
            # si on est à l'emplacement d'un restaurant, on s'arrête
            if (row, col) == goalStates[restau[j]]:
                success[j] = 1
                # o = players[j].ramasse(game.layers)
                # game.mainiteration()
                # print("Le joueur {} est au restaurant {}.".format(j, restau[j]))
                # Add player to gain when arrived
                gain[restau[j]].add(j)
                # goalStates.remove((row, col)) # on enlève ce goalState de la liste
                remplissage["restaurant_"+str(restau[j])] = [len(gain[restau[j]])]
                continue

            next_row = chemin[j][i][0]
            next_col = chemin[j][i][1]
            players[j].set_rowcol(next_row, next_col)

            # print("joueur {}: pos ({},{})".format(j, next_row, next_col))
            # game.mainiteration()

            col = next_col
            row = next_row
            posPlayers[j] = (row, col)
    pygame.quit()

    # ---------------------------------
    # Calcul du gain pour chaque joueur
    # ---------------------------------
    for i in gain:
        # if multiple player arrive the same restaurant
        if len(gain[i]) > 0:
            gain[i] = random.choice(list(gain[i]))
        # if a restaurant selected is empty
        else:
            gain[i] = None

    # print("gain_finale {}".format(gain))

    # Final gain
    final_gain = {}
    # final_gain["strategie"] = [strategy]

    for i in range(nbPlayers):
        if i < 5:
            final_gain["strategy_" + str(i)] = [strategy_competition[0]]
        else:
            final_gain["strategy_" + str(i)] = [strategy_competition[1]]

        final_gain["choix_"+str(i)] = [restau[i]]
        final_gain["success_"+str(i)] = [success[i]]
        final_gain["gain_"+str(i)] = [0]

        for restaurant, joueur in gain.items():
            if joueur == i and restaurant == final_gain["choix_"+str(i)][0]:
                final_gain["gain_"+str(i)] = [1]

    # print(final_gain)

    # print(remplissage)

    # ---------------------------------
    # Write results to file
    # ---------------------------------
    if len(sys.argv) >= 4:
        filename = Path(sys.argv[3]+".csv")
        filename_remplissage = Path(sys.argv[3]+"_remplissage.csv")
        # convert to result to DataFrame
        result = pd.DataFrame(final_gain)
        if filename.is_file():
            result.to_csv(filename, mode='a', header=False, sep="\t", index=False)
        else:
            result.to_csv(filename, header=True, sep="\t", index=False)

        result_remplissage = pd.DataFrame(remplissage)
        if filename_remplissage.is_file():
            result_remplissage.to_csv(filename_remplissage, mode='a', header=False, sep="\t", index=False)
        else:
            result_remplissage.to_csv(filename_remplissage, header=True, sep="\t", index=False)

    return

# Main ========================================================
if __name__ == '__main__':
    main()



