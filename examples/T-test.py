import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
import numpy as np
import textwrap

from biosim.simulation_nograph import BioSim

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

    ini_herbspop = pd.DataFrame([{'species': 'Herbivore',
                                  'age': 5,
                                  'weight': 20}
                                 for _ in range(200)])

    ini_carnspop = pd.DataFrame([{'species': 'Carnivore',
                                  'age': 5,
                                  'weight': 20}
                                 for _ in range(50)])

    mu, simga = 20, 4
    np.random.seed(seed=1)
    ini_herbspop['weight'] = np.random.normal(20, 4, 200)
    ini_carnspop['weight'] = np.random.normal(20, 4, 50)

    ini_herbs = [{'loc': (2, 7),
                  'pop': ini_herbspop.to_dict('records')}]
    ini_carns = [{'loc': (2, 7),
                  'pop': ini_carnspop.to_dict('records')}]

    sim = BioSim(geogr, ini_herbs + ini_carns, seed=1)
    sim.simulate(300)

    h_agelist = sim._herbivores_agelist
    h_weightlist = sim._herbivores_weightlist
    c_agelist = sim._carnivores_agelist
    c_weightlist = sim._carnivores_weightlist

    df_h = pd.DataFrame({'h_age': h_agelist, 'h_weight': h_weightlist})
    df_c = pd.DataFrame({'c_age': c_agelist, 'c_weight': c_weightlist})
    df_age5_h = df_h[df_h['h_age'] == 5]
    df_age5_c = df_c[df_c['c_age'] == 5]


    print(f'The init population of herbivores and carnivores, '
          f'have normal weight distribution with mu={mu}, sigma={simga}.')
    print('After 300 years simulation')
    print('*'*100)
    print('One sample T-test on herbivores and carnivores weight')
    p_value_h = stats.ttest_1samp(df_age5_h['h_weight'], 20)[1]
    p_value_c = stats.ttest_1samp(df_age5_c['c_weight'], 20)[1]
    p_value_h_norm = stats.normaltest(df_age5_h['h_weight'])[1]
    p_value_c_norm = stats.normaltest(df_age5_c['c_weight'])[1]
    print(f'The p_value of T-test herbivores weight is {p_value_h}')
    print(f'The p_value of T-test carnivores weight is {p_value_c}')
    print(f'The p_value of normal distribution herbivores weight is {p_value_h_norm}')
    print(f'The p_value of normal distribution carnivores weight is {p_value_c_norm}')