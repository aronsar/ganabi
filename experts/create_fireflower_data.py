# this script creates data using python 2 and rainbow agents

# here we add the repo's root directory to the path variable; everything
# is imported relative to that to avoid problems
from os.path import dirname, abspath, join
ganabi_path = dirname(dirname(abspath(__file__)))
hanabi_env_path = join(ganabi_path, "hanabi_env")
import sys
sys.path.insert(0, ganabi_path)
sys.path.insert(0, hanabi_env_path)
import rl_env

import subprocess
# from subprocess import call
import argparse
import os
import pandas as pd
import numpy as np
import pickle

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--agent_name',
                        default='fireflower')

    parser.add_argument('--num_players',
                        type=int, default=2)

    parser.add_argument('--num_games',
                        type=int, default=10)

    parser.add_argument('--datapath')

    args = parser.parse_args()
    return args


# TODO: For future work, we can have the target agent and other agents to be different types
def create_csv_from_scala(numGames, numPlayers):
        subprocess.run("export JAVA_HOME=/data1/shared/fireflowerenv/jre1.8.0_221", shell=True)
        subprocess.run("export PATH=$JAVA_HOME/bin:$PATH", shell=True)
        
        args = ["/data1/shared/fireflowerenv/sbt/bin/sbt", "run " + str(numGames) + " " + str(numPlayers)]
        
        dir_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(os.path.join(dir_path, 'fireflower_model'))
        process = subprocess.Popen(args, universal_newlines=True)
        process.communicate() # solves issue where Popen hangs


def create_data_filenames(args):    
    # Config csv & pkl file path
    agent_data_filename = args.agent_name + "_" + str(args.num_players) + "_" + str(args.num_games)
    
    csv_filename = agent_data_filename + ".csv"
    pkl_filename = agent_data_filename + ".pkl"

    return csv_filename, pkl_filename


def get_action(action_type, color, rank, obs):
    '''
    Return action used for hanabi
    '''
    action = {}
    action['action_type'] = action_type
    print(action_type, color, rank)
    if (action_type == 'DISCARD'):
        match_indices = []
        for i, card in enumerate(obs):
            if card['color'] == color and card['rank'] == rank:
                match_indices.append(i)

        assert(len(match_indices) > 0)
        action['card_index'] = match_indices[0]
    elif (action_type == 'PLAY'):
        match_indices = []
        for i, card in enumerate(obs):
            if card['color'] == color and card['rank'] == rank:
                match_indices.append(i)

        assert(len(match_indices) > 0)
        action['card_index'] = match_indices[0]
    elif (action_type == 'REVEAL_COLOR'):
        assert(color != 'X')
        action['color'] = color
        action['target_offset'] = 1
    elif (action_type == 'REVEAL_RANK'):
        assert(rank >=0 and rank <=4)
        action['rank'] = rank 
        action['target_offset'] = 1
    else:
        raise("Unknow Action")

    return action

def create_pkl_data(args, csv_data):
    config={'colors': 5,
            'ranks': 5,
            'players': 2 ,
            'hand_size': 5,
            'max_information_tokens': 8,
            'max_life_tokens': 3,
            'seed': -1,
            'observation_type': 1, # FIXME: NEEDS CONFIRMATION
            'random_start_player': False}

    # Create the Hanabi Environment with the defined configuration.
    env = rl_env.HanabiEnv(config)
    raw_data = []
    for game_num in range(args.num_games):
        print("############## GAME "+ str(game_num) + " ###############")
        raw_data.append([[], []])
        game_done = False

        game_filter = csv_data.iloc[:, 0] == game_num
        game_data = csv_data[game_filter]
        deck_size = game_data.iloc[0, 1]
        action_type = np.array(game_data.iloc[:, 2]).tolist()
        action_card_color = np.array(game_data.iloc[:, 3]).tolist()
        action_card_rank = np.array(game_data.iloc[:, 4]).tolist()
        deck = np.array(game_data.iloc[0, 5:]).tolist()
        
        # Initialize the game with @deck. The arg is None by default.
        obs = env.reset(deck)

        game_step = -1
        while not game_done:
            for agent_id in range(args.num_players):
                game_step += 1
                print("--------------{}----------------".format(game_step))
                # FIXME: Make obs dict usage clearer

                # Retrieve current player's hand used to get action
                # Done in a very hack way for now that will only support 2 player game
                observer_agent_id = (game_step + 1) % 2
                agent_hand = obs['player_observations'][observer_agent_id]['observed_hands'][1]

                # Retrieve Action
                action = get_action(action_type[game_step], action_card_color[game_step], action_card_rank[game_step], agent_hand)

                # Construct one-hot action vector
                action_idx = obs['player_observations'][agent_id]['legal_moves_as_int'][obs['player_observations'][agent_id]['legal_moves'].index(action)]
                one_hot_action_vector = [0]*20 # FIXME: hard coded action length
                one_hot_action_vector[action_idx] = 1

                raw_data[game_num][0].append(obs['player_observations'][agent_id]['vectorized'])
                raw_data[game_num][1].append(one_hot_action_vector)

                # Step Through
                obs, reward, game_done, info = env.step(action)

                # Check Game status
                if game_done:
                    break

    return raw_data

def act_based_pipeline(args):
    # Sort Params
    #seed = 1 
    #csv_filename, pkl_filename, jar_filename = create_data_filenames(args) 
    csv_filename, pkl_filename = create_data_filenames(args)

    # Create csv on Disk by using Java code
    create_csv_from_scala(args.num_games, args.num_players)

    # Read csv
    csv_data = pd.read_csv(csv_filename, header=None)

    # Convert csv to pkl
    pkl_data = create_pkl_data(args, csv_data)

    # Save pkl on Disk
    pickle.dump(pkl_data, open(pkl_filename, "wb"))

    # Remove csv on Disk
    remove_csv = True
    if (remove_csv):
        os.remove(csv_filename)

def main(args):      
    act_based_pipeline(args)
        
if __name__ == '__main__':
    print("Create Fireflower Data")
    args = parse()
    main(args)
