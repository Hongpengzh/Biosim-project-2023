"""
Full island simulation with herbivores and carnivores
including movie creation.
"""

__author__ = 'Hans Ekkehard Plesser, NMBU'

import textwrap

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from biosim.simulation_logfile_nograph import BioSim

if __name__ == '__main__':

    geogr = """\
               WWWWWWWWWWWWWWWWWWWWW
               WHHHHHLLLLWWLLLLLLLWW
               WHHHHHLLLLWWLLLLLLLWW
               WHHHHHLLLLWWLLLLLLLWW
               WWHHLLLLLLLWWLLLLLLLW
               WWHHLLLLLLLWWLLLLLLLW
               WWWWWWWWHWWWWLLLLLLLW
               WHHHHHLLLLWWLLLLLLLWW
               WHHHHHHHHHWWLLLLLLWWW
               WHHHHHDDDDDLLLLLLLWWW
               WHHHHHDDDDDLLLLLLLWWW
               WHHHHHDDDDDLLLLLLLWWW
               WHHHHHDDDDDWWLLLLLWWW
               WHHHHDDDDDDLLLLWWWWWW
               WWHHHHDDDDDDLWWWWWWWW
               WWHHHHDDDDDLLLWWWWWWW
               WHHHHHDDDDDLLLLLLLWWW
               WHHHHDDDDDDLLLLWWWWWW
               WWHHHHDDDDDLLLWWWWWWW
               WWWHHHHLLLLLLLWWWWWWW
               WWWHHHHHHWWWWWWWWWWWW
               WWWWWWWWWWWWWWWWWWWWW"""
    geogr = textwrap.dedent(geogr)

    ini_herbs = [{'loc': (2, 7),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(200)]}]
    ini_carns = [{'loc': (2, 7),
                  'pop': [{'species': 'Carnivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(100)]}]

    dflist = []
    for seed in range(10, 20):
        sim = BioSim(geogr, ini_herbs + ini_carns, seed,
                     hist_specs={'fitness': {'max': 1.0, 'delta': 0.05},
                                 'age': {'max': 60.0, 'delta': 2},
                                 'weight': {'max': 60, 'delta': 2}},
                     cmax_animals={'Herbivore': 200, 'Carnivore': 50},
                     img_dir='results',
                     img_base='sample')
        sim.simulate(200)
        dflist.append(sim._df_log)
    df_all = pd.concat(dflist, axis=1)

    fig = plt.figure(figsize=(12, 6))
    plt.plot(df_all.index, df_all.iloc[:, 0], 'b', alpha=0.4, label='Herbivores')
    plt.plot(df_all.index, df_all.iloc[:, 1], 'r', alpha=0.4, label='Carnivores')
    for i in np.arange(2, 20, 2):
        plt.plot(df_all.index, df_all.iloc[:, i], 'b', alpha=0.4)
        plt.plot(df_all.index, df_all.iloc[:, i + 1], 'r', alpha=0.4)
    plt.legend(loc='upper left')
    plt.title('Simulation 200 years with Herbivores and Carnivores with different seeds')
    plt.xlabel('year')
    plt.ylabel('Num of Fauna')

    fig, axes = plt.subplots(2, 5, figsize=(15, 7))
    num = np.arange(0, 20, 2)
    for i, ax in enumerate(axes.flat):
        ax.plot(df_all.index, df_all.iloc[:, num[i]], 'b', alpha=0.4)
        ax.plot(df_all.index, df_all.iloc[:, num[i] + 1], 'r', alpha=0.4)
        ax.set_title(f'Seed {i + 10}')

