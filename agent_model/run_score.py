import csv
import os, sys
import numpy as np

from create_agent_data import *

def run_game():
    agents_0 = ['ex.h5','ex.h5']
    agents_1 = ['ex.h5','ex.h5']
    num_games = 10
    full_score = 25
    score_matrix = []
    percent_matrix = []
    for a0 in agents_0:
        scores_list = []
        percent_list = []
        for a1 in agents_1:
            scores = DataCreator(num_games, a0, a1).create_data()
            percents = [ s / full_score for s in scores]
            scores_list.append(scores)
            percent_list.append(percents)
        score_matrix.append(scores_list)
        percent_matrix.append(percents)

if __name__ == '__main__':
    run_game()
