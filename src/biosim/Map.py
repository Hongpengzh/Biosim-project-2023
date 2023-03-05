"""
The Map class
"""

__author__ = 'Hongpeng Zhang and Sujan Devkota'
__email__ = 'hongpeng.zhang@nmbu.no and sujan.devkota@nmbu.no'

import numpy as np
from biosim import Cell, Animal


class Map:
    """
    Class for the whole island map.
    """
    geography_dict = {'W': 'Water', 'L': 'Lowland', 'H': 'Highland', 'D': 'Desert'}

    def __init__(self, island_map):
        """

        Parameters
        ----------
        island_map: str
            Multi-line string specifying island geography

        Notes
        -----
        - island_map should be a rectangle or a square, and the border should be water e.g.,
        """
        self.island_map = island_map
        self.cells_array = self.init_cells_array()

    @property
    def island_map_array(self):
        """
        Turn island_map into a numpy array

        Returns
        -------
        Numpy array
            A 2d numpy array with a letter in each position, representing the geography information
            for the cell in the same position.
        """
        return np.array([list(line) for line in self.island_map.split('\n')])

    def init_cells_array(self):
        """
        Init the numpy array with the cell instances,
        each cell instance has the geography information in the island_map_array.

        Returns
        -------
        Numpy array
            A 2d numpy array with cell instances.
        """
        cells_array = np.empty(self.island_map_array.shape, dtype=object)
        for geo in Map.geography_dict.keys():
            n_geo = len(cells_array[self.island_map_array == geo])
            cells_array[self.island_map_array == geo] = [Cell.Cell(geography=geo) for _ in
                                                         range(n_geo)]

        return cells_array

    def add_fauna(self, population):
        """
        Add Herbivores and Carnivores into the map.

        Parameters
        ----------
        population:
            List of dictionaries specifying initial population.

        Notes
        -----
        - population should be in a list of dictionary, contain loc and pop information  e.g.,

          .. code:: python

             ini_herbs = [{'loc': (2, 2),
              'pop': [{'species': 'Herbivore',
                       'age': 5,
                       'weight': 20}
                      for _ in range(50)]}]

        Returns
        -------
        Tuple
            The total amount of Herbivores and the total amount of Carnivores added into the map.
        """
        if len(population) == 0:
            return 0, 0
        else:
            for dict in population:
                loc = (dict['loc'][0] - 1, dict['loc'][1] - 1)
                animal_num = 0
                Carnivores_num = 0
                animal_list = []
                Carnivores_list = []
                for fauna_dict in dict['pop']:
                    if fauna_dict['species'] == 'Herbivore':
                        animal_list.append(Animal.Herbivores(fauna_dict['age'],
                                                             fauna_dict['weight']))
                        animal_num += 1
                    if fauna_dict['species'] == 'Carnivore':
                        Carnivores_list.append(Animal.Carnivores(fauna_dict['age'],
                                                                 fauna_dict['weight']))
                        Carnivores_num += 1
                self.cells_array[loc].animal_list += animal_list
                self.cells_array[loc].Carnivores_list += Carnivores_list

            return animal_num, Carnivores_num

    def annul_cycle(self):
        """
        Do the annual cycle on the map step by step in the right order.

        Returns
        -------
        Tuple
            the total amount, the distributing numpy arrays, the fitness, age, weight
            of herbivores and carnivores after the annual cycle
        """
        animal_percell_year = []
        carnivore_percell_year = []

        self.produce()
        self.givebirth()
        self.feed()
        self.move_permit()  # give all the animals the right to move before annul migrate start
        self.migrate()
        self.grow_loss()
        self.reset_fodder()
        self.die()

        def array_colormap(cellarray):
            """
            Get the distributing numpy arrays of herbivores and carnivores
            from the cells numpy array to make colormaps.

            Parameters
            ----------
            cellarray: numpy array
                The numpy array of cells

            Returns
            -------
            Tuple
                The distributing numpy arrays of herbivores and carnivores
            """
            Herbivores_array = np.zeros(cellarray.shape)
            Carnivores_array = np.zeros(cellarray.shape)
            for [i, j], cell in np.ndenumerate(cellarray):
                Herbivores_array[i, j] = len(cell.animal_list)
                Carnivores_array[i, j] = len(cell.Carnivores_list)

            return Herbivores_array, Carnivores_array

        cells_array = self.cells_array

        Herbivores_distribute, Carnivores_distribute = array_colormap(cells_array)

        for cell in cells_array[self.island_map_array != 'W']:
            animal_percell_year += cell.animal_list
            carnivore_percell_year += cell.Carnivores_list

        h_fitness_list = []
        h_age_list = []
        h_weight_list = []

        for animal in animal_percell_year:
            h_fitness_list.append(animal.fitness)
            h_age_list.append(animal.age)
            h_weight_list.append(animal.weight)

        c_fitness_list = []
        c_age_list = []
        c_weight_list = []

        for animal in carnivore_percell_year:
            c_fitness_list.append(animal.fitness)
            c_age_list.append(animal.age)
            c_weight_list.append(animal.weight)

        return animal_percell_year, carnivore_percell_year, \
            Herbivores_distribute, Carnivores_distribute, \
            h_fitness_list, h_age_list, h_weight_list, \
            c_fitness_list, c_age_list, c_weight_list

    def produce(self):
        """Produce fodder on Low land and High land cells in the map."""
        for cell in self.cells_array[(self.island_map_array == 'L')
                                     | (self.island_map_array == 'H')]:
            cell.produce_fodder()

    def givebirth(self):
        """Let herbivores and carnivores in the map procreate."""
        for cell in self.cells_array[self.island_map_array != 'W']:
            cell.herbivore_birth()
            cell.carnivore_birth()

    def feed(self):
        """Let herbivores and carnivores in the map feed themselves."""
        for cell in self.cells_array[self.island_map_array != 'W']:
            cell.feed_animals()
            cell.feed_carnivores()

    def move_permit(self):
        """Give herbivores and carnivores in the map permission to move."""
        for cell in self.cells_array[self.island_map_array != 'W']:
            for animal in cell.animal_list:
                animal.moved = False
            for animal in cell.Carnivores_list:
                animal.moved = False

    def migrate(self):
        """Let herbivores and carnivores in the map migrate to accessible places. """
        for [i, j], cell in np.ndenumerate(self.cells_array):
            if cell.geography != 'W':
                neighbors = self.get_neighbors(i, j)
                cell.animal_migration(neighbors)

    def get_neighbors(self, i, j):
        """
        Get the accessible cells list for fauna on the cell with the location i, j in the map.

        Parameters
        ----------
        i: int
            The row location of the cell
        j: int
            The column location of the cell

        Returns
        -------
        list
            The accessible cells list
        """
        island_shape = self.island_map_array.shape
        map_shape = (island_shape[0] - 1, island_shape[1] - 1)
        cells_array = self.cells_array
        neighbors = []
        if i > 0:
            if cells_array[i - 1, j].geography != 'W':
                neighbors.append(cells_array[i - 1, j])
        if i < map_shape[0]:
            if cells_array[i + 1, j].geography != 'W':
                neighbors.append(cells_array[i + 1, j])
        if j > 0:
            if cells_array[i, j - 1].geography != 'W':
                neighbors.append(cells_array[i, j - 1])
        if j < map_shape[1]:
            if cells_array[i, j + 1].geography != 'W':
                neighbors.append(cells_array[i, j + 1])

        return neighbors

    def grow_loss(self):
        """Let herbivores and carnivores in the map loss weight."""
        for cell in self.cells_array[self.island_map_array != 'W']:
            cell.grow_and_loose_weight_herbivore()
            cell.grow_and_loose_weight_carnivore()

    def reset_fodder(self):
        """Reset the fodder amount after herbivores and carnivores feed themselves in the map"""
        for cell in self.cells_array[self.island_map_array != 'W']:
            cell.fodder = 0

    def die(self):
        """Let herbivores and carnivores in the map die."""
        for cell in self.cells_array[self.island_map_array != 'W']:
            cell.herbivore_death()
            cell.carnivore_death()
