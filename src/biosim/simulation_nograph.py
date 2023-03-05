"""
BioSim class. Top level class of the simulation
"""

__author__ = 'Hongpeng Zhang and Sujan Devkota'
__email__ = 'hongpeng.zhang@nmbu.no and sujan.devkota@nmbu.no'

import random
import numpy as np
from biosim import Cell, Animal, Graphics
from biosim import Map


class BioSim:
    """
    Top-level interface to BioSim package.
    """
    geography_dict = {'W': 'Water', 'L': 'Lowland', 'H': 'Highland', 'D': 'Desert'}

    def __init__(self, island_map, ini_pop, seed,
                 vis_years=1, ymax_animals=None, cmax_animals=None, hist_specs=None,
                 img_years=None, img_dir=None, img_base=None, img_fmt='png',
                 log_file=None):

        """
        Parameters
        ----------
        island_map : str
            Multi-line string specifying island geography
        ini_pop : list
            List of dictionaries specifying initial population
        seed : int
            Integer used as random number seed
        vis_years : int
            Years between visualization updates (if 0, disable graphics)
        ymax_animals : int
            Number specifying y-axis limit for graph showing animal numbers
        cmax_animals : dict
            Color-scale limits for animal densities, see below
        hist_specs : dict
            Specifications for histograms, see below
        img_years : int
            Years between visualizations saved to files (default: `vis_years`)
        img_dir : str
            Path to directory for figures
        img_base : str
            Beginning of file name for figures
        img_fmt : str
            File type for figures, e.g. 'png' or 'pdf'
        log_file : str
            If given, write animal counts to this file

        Notes
        -----
        - If `ymax_animals` is None, the y-axis limit should be adjusted automatically.
        - If `cmax_animals` is None, sensible, fixed default values should be used.
        - `cmax_animals` is a dict mapping species names to numbers, e.g.,

          .. code:: python

             {'Herbivore': 50, 'Carnivore': 20}

        - `hist_specs` is a dictionary with one entry per property for which a histogram
          shall be shown. For each property, a dictionary providing the maximum value
          and the bin width must be given, e.g.,

          .. code:: python

             {'weight': {'max': 80, 'delta': 2},
              'fitness': {'max': 1.0, 'delta': 0.05}}

          Permitted properties are 'weight', 'age', 'fitness'.
        - If `img_dir` is None, no figures are written to file.
        - Filenames are formed as

          .. code:: python

             Path(img_dir) / f'{img_base}_{img_number:05d}.{img_fmt}'

          where `img_number` are consecutive image numbers starting from 0.

        - `img_dir` and `img_base` must either be both None or both strings.
        """
        # check if the map is legal
        row_lengths = [len(line) for line in island_map.split('\n')]
        if len(set(row_lengths)) > 1:
            raise ValueError('The Map must be a square or a Rectangle')
        else:
            map_array = np.array([list(line) for line in island_map.split('\n')])
            if any(map_array[0, :] != 'W') | any(map_array[-1, :] != 'W') | \
                    any(map_array[:, 0] != 'W') | any(map_array[:, -1] != 'W'):
                raise ValueError('The boundary of the map must be "H"')
        for letter in island_map.replace('\n', 'W'):
            if letter not in BioSim.geography_dict.keys():
                raise ValueError(f'"{letter}"  is not a proper landscape type'
                                 f', landscape type must be one of "W", "D", "H", "L"')

        # init the sim if map is legal
        self.island_map = island_map
        self.ini_pop = ini_pop
        self.seed = seed
        random.seed(seed)
        self._year = 0
        self._map_instance = Map.Map(self.island_map)   # make a map instance
        self._herbivores_num, self._carnivores_num = self.add_population(self.ini_pop)

        self._herbivores_agelist = []
        self._herbivores_weightlist = []
        self._carnivores_agelist = []
        self._carnivores_weightlist = []

        # arguments about ploting
        self.ymax_animals = ymax_animals
        self.cmax_animals = cmax_animals
        self.hist_specs = hist_specs
        self.img_dir = img_dir
        self.img_base = img_base
        self.img_years = img_years
        self.vis_years = vis_years
        self.img_fmt = img_fmt
        self._graphics = Graphics.Graphics(self.island_map, self.img_dir, self.img_base,
                                           self.img_fmt, self.hist_specs)

    def set_animal_parameters(self, species, params):
        """
        Set parameters for animal species.

        Parameters
        ----------
        species : str
            Name of species for which parameters shall be set.
        params : dict
            New parameter values

        Raises
        ------
        ValueError
            If invalid parameter values are passed.
        """
        if (species == 'Herbivore') | (species == 'Carnivore'):
            if species == 'Herbivore':
                Animal.Herbivores.update_para(params)
            if species == 'Carnivore':
                Animal.Carnivores.update_para(params)
        else:
            raise TypeError(f'"{species}" is not right, Species must be Herbivore or Carnivore')

    def set_landscape_parameters(self, landscape, params):
        """
        Set parameters for landscape type.

        Parameters
        ----------
        landscape : str
            Code letter for landscape
        params : dict
            New parameter values

        Raises
        ------
        ValueError
            If invalid parameter values are passed.
        """
        if (landscape == 'L') | (landscape == 'H'):
            Cell.Cell.update_cell_para(landscape, params)
        else:
            raise TypeError(f'"{landscape}" is not right, landscape must be "L" or "H"')

    def simulate(self, num_years):
        """
        Run simulation while visualizing the result.

        Parameters
        ----------
        num_years : int
            Number of years to simulate
        """
        if self.vis_years == 0:
            self.vis_years = 1
        if self.img_years is None:
            self.img_years = self.vis_years
        if self.img_years % self.vis_years != 0:
            raise ValueError('img_years must be multiple of vis_years')

        self._final_years = self._year + num_years
        # self._graphics.setup(self._final_years, self.img_years, self.cmax_animals)
        while self._year < self._final_years:
            # Map and Cells annual cycle
            animal_percell_year, carnivore_percell_year,\
                Herbivores_distribute, Carnivores_distribute,\
                h_fitness_list, h_age_list, h_weight_list,\
                c_fitness_list, c_age_list, c_weight_list = self._map_instance.annul_cycle()
            self._herbivores_num, self._carnivores_num = \
                len(animal_percell_year), len(carnivore_percell_year)

            self._herbivores_agelist = h_age_list
            self._herbivores_weightlist = h_weight_list
            self._carnivores_agelist = c_age_list
            self._carnivores_weightlist = c_weight_list

            # if self._year % self.vis_years == 0:
            #     self._graphics.update_year_counter(self._year)
            #     self._graphics.update_fauna_amount(
            #         self._year, len(animal_percell_year), len(carnivore_percell_year))
            #     self._graphics.update_herbivores_distribute(Herbivores_distribute)
            #     self._graphics.update_carnivores_distribute(Carnivores_distribute)
            #     self._graphics.update_fitness(self._year, h_fitness_list, c_fitness_list)
            #     self._graphics.update_age(self._year, h_age_list, c_age_list)
            #     self._graphics.update_weight(self._year, h_weight_list, c_weight_list)
            # if self._year % self.img_years == 0:
            #     self._graphics.save_graphics()
            self._year += 1

    def add_population(self, population):
        """
        Add a population to the island

        Parameters
        ----------
        population : List of dictionaries
            See BioSim Task Description, Sec 3.3.3 for details.
        """
        animal_num, carnivores_num = self._map_instance.add_fauna(population)
        if self._year != 0:
            self._herbivores_num += animal_num
            self._carnivores_num += carnivores_num

        return animal_num, carnivores_num

    @property
    def year(self):
        """Last year simulated."""
        return self._year

    @property
    def num_animals(self):
        """Total number of animals on island."""
        return self._herbivores_num + self._carnivores_num

    @property
    def num_animals_per_species(self):
        """Number of different species."""
        species_dict = {'Herbivore': self._herbivores_num, 'Carnivore': self._carnivores_num}

        return species_dict

    def make_movie(self):
        """Make movie after the simulation figures of each year saved"""
        self._graphics.make_movie()
