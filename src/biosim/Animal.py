"""
The Animal class with Herbivores and Carnivores as subclasses of Animal.
"""


__author__ = 'Hongpeng Zhang and Sujan Devkota'
__email__ = 'hongpeng.zhang@nmbu.no and sujan.devkota@nmbu.no'

import numpy as np
import random
import numba


class Animal:
    """The animal class with Herbivores and carnivores."""
    parameter = {}

    def __init__(self, age=0, weight=None):
        """

        Parameters
        ----------
        age: int
        weight: float or int
        """
        self.age = age
        self.weight = weight
        self.moved = False

    @staticmethod
    @numba.jit
    def fitness_formula(plus_minus, x, x_half, phi_x):
        """
        Method to return the formula to be used in fitness calculation

        Parameters
        ----------
        plus_minus: 1 or -1
        x: int or float
            age or weight
        x_half: int or float
            a_half or w_half
        phi_x: int or float
            phi_age or phi_weight

        Returns
        -------
        Formula to be used in fitness calculation
        """
        formula = 1 / (1 + np.power(np.e, plus_minus * phi_x * (x - x_half)))
        return formula

    @classmethod
    def fitness_calculation(cls, age, weight, parameter):
        """
        Method to calculate the fitness of the animals

        Parameters
        ----------
        age: int
        weight: int or float
        parameter: dictionary

        Returns
        -------
        The fitness of the specific animal.
        """
        fitness = cls.fitness_formula(1, age, parameter['a_half'], parameter['phi_age']) \
            * cls.fitness_formula(-1, weight, parameter['w_half'], parameter['phi_weight'])
        return fitness

    @property
    def fitness(self):
        """
        Method to return fitness of the animal. This is a property method so each time the weight
        or age changes, the fitness is updated.

        Returns
        -------
        Fitness of the animals
        """
        if self.weight <= 0:
            return 0
        else:
            return self.fitness_calculation(self.age, self.weight, self.parameter)

    @classmethod
    def set_params(cls, params):
        """
        Method to set the parameter of the specific class.

        Parameters
        ----------
        params: dictionary

        """
        cls.parameter.update(params)

    @classmethod
    def update_para(cls, params):
        """
        Method to check for unknown parameters and raises value error if the parameters are not in
            animal parameters.

        Parameters
        ----------
        params: dictionary
            new params

        """
        for key in params.keys():
            if key not in cls.parameter.keys():
                raise ValueError(f'"{key}" is not a parameter for animals ')
            else:
                cls.parameter[key] = params[key]

        for value in params.values():
            if value < 0:
                raise ValueError(f'"{value}" < 0 , the parameter for animals must be larger than 0')

    def procreate(self, N):
        """Method to calculate if the animal has given birth. If the animal has given birth,
        it creates an instance of the class (object ) of Herbivore or the carnivore as baby animal.

        Formula
        -------
        The weight of the baby is calculated random log normal distribution with w_birth and
        sigma_birth from following formula:

        Parameters
        ----------
        N: N is the number of Herbivores in the cell at the start of the breeding season

        Returns
        -------
        Tuple
            Boolean value of animal has given birth or not and baby animal object
        """
        log_mu = np.log(self.parameter['w_birth'] ** 2 / (
                self.parameter['w_birth'] ** 2 + self.parameter['sigma_birth'] ** 2) ** 0.5)
        log_sigma = np.log(1 + self.parameter['sigma_birth'] ** 2 / self.parameter['w_birth']
                           ** 2) ** 0.5

        prob = min(1, self.parameter['gamma'] * self.fitness * N)
        if (self.weight >= (self.parameter['w_birth'] + self.parameter['sigma_birth']) *
            self.parameter['zeta']) \
                & (self.age > 1) & (random.choices([False, True], [1 - prob, prob])[0]):
            baby_weight = random.lognormvariate(log_mu, log_sigma)
            if self.weight - self.parameter['xi'] * baby_weight >= 0:
                self.weight -= self.parameter['xi'] * baby_weight
                baby_animal = self.__class__(0, baby_weight)
                return True, baby_animal
            else:
                return False,
        else:
            return False,

    def growth_per_year(self):
        """ Method to increase the age by 1 each year """

        self.age += 1

    def weight_loss_per_year(self):
        """
        Method to lose weight each year by the formula:
        weight * eta

        """
        self.weight -= (self.weight * self.parameter['eta'])

        if self.weight < 0:
            self.weight = 0

    def die(self):
        """
        Method to decide if the animal die with certainty if weight is 0 and with a probability

        ..math::
            probability = omega * (1 - fitness)

        Returns
        -------
        True if animal dies and False if animals do not die.
        """
        if self.weight == 0:
            return True
        else:
            prob = self.parameter['omega'] * (1 - self.fitness)
            return random.choices([False, True], [1 - prob, prob])[0]

    def migrate(self, neighbors):
        """
        Method to determine if the animal migrates. The animals migrate with probability
        mu * fitness
        Animals migrate to four adjacent cells at random with equal probability.

        Parameters
        ----------
        neighbors
            list of cells where animals can migrate

        Returns
        -------
        True if animals migrate otherwise false.
        """
        self_fitness = self.fitness
        prob = self_fitness * self.parameter['mu']
        if random.choices([False, True], [1 - prob, prob])[0]:
            if random.choices([False, True], [1 - prob, prob])[0]:
                if len(neighbors) == 4:
                    return random.choices(neighbors)[0]
                if len(neighbors) == 3:
                    return random.choices(neighbors + [False])[0]
                if len(neighbors) == 2:
                    return random.choices(neighbors + [False, False])[0]
                if len(neighbors) == 1:
                    return random.choices(neighbors + [False, False, False])[0]
                if len(neighbors) == 0:
                    return False


class Herbivores(Animal):
    """ Herbivore animals eats fodder and can reside in the Lowland, Highland and Desert
            although Dessert does not have any fodder """

    parameter = {'w_birth': 8.0, 'sigma_birth': 1.5, 'beta': 0.9, 'eta': 0.05,
                 'a_half': 40.0, 'phi_age': 0.6, 'w_half': 10.0, 'phi_weight': 0.1,
                 'mu': 0.25, 'gamma': 0.2, 'zeta': 3.5, 'xi': 1.2, 'omega': 0.4,
                 'F': 10.0}

    def eat(self):
        """ Method to increase the weight of the herbivore after the animal eats. The weight of the
                herbivore animal increases by beta * amount F of fodder """

        self.weight += (self.parameter['beta'] * self.parameter['F'])

    def __init(self, age=0, weight=None):
        super().__init__(age, weight)


class Carnivores(Animal):
    """ Carnivore animals hunts and eats Herbivores. Carnivores can reside in Desert, Lowland
            and Highland """

    parameter = {'w_birth': 6.0, 'sigma_birth': 1.0, 'beta': 0.75, 'eta': 0.125,
                 'a_half': 40.0, 'phi_age': 0.3, 'w_half': 4.0, 'phi_weight': 0.4,
                 'mu': 0.4, 'gamma': 0.8, 'zeta': 3.5, 'xi': 1.1, 'omega': 0.8,
                 'F': 50.0, 'DeltaPhiMax': 10.0}

    def __init__(self, age=0, weight=None):
        super().__init__(age, weight)

    def hunt(self, animal_list):
        """ Method to determine the list of the herbivore animals that can be hunted. Carnivore
            animal hunts herbivores in the order of the least fitness.

       Parameters
       ----------
       animal_list : list
        Herbivore list in the cell in weight ascending order

       Returns
       -------
        list of herbivore animals that can be hunted.
        """
        hunt_list = []
        fit = self.fitness
        for animal in animal_list:
            prob = 1
            animal_fitness = animal.fitness
            if fit <= animal_fitness:
                prob = 0
            elif 0 < fit - animal_fitness < self.parameter['DeltaPhiMax']:
                prob = (fit - animal_fitness) / self.parameter['DeltaPhiMax']
            if random.choices([False, True], [1 - prob, prob])[0]:
                hunt_list.append(animal)

        return hunt_list

    def eat(self, animal_list):
        """
        Method to get the list of herbivore animals that are eaten by carnivore animals. The weight
            of the carnivore animal increases by beta * amount F. The carnivore will continue to
            kill herbivore until it has eaten amount F or has tried to kill all herbivore in a cell.
            The carnivore will kill herbivore with probability:
            0 if fitness of carnivore <= fitness of herbivore
            (carnivore fitness - herbivore fitness)/ delta phi max if carnivore fitness - herbivore
            fitness < delta phi max
            1 otherwise

        Parameters
        ----------
        animal_list: list
            Herbivore animal list in a cell

        Returns
        -------
        List of Herbivore animals that are eaten
        """

        hunt_list = self.hunt(animal_list)
        hunt_weight_list = [animal.weight for animal in hunt_list]
        cum_weight_list = np.cumsum(hunt_weight_list)
        if len(cum_weight_list) < 2:
            eaten_animal_list = hunt_list
            self.weight += self.parameter['beta'] * sum(cum_weight_list)
        elif self.parameter['F'] > cum_weight_list[-2]:
            eaten_animal_list = hunt_list
            self.weight += self.parameter['beta'] * cum_weight_list[-1]
        else:
            stop_eat_index = np.searchsorted(cum_weight_list, self.parameter['F'], side='left')
            eaten_animal_list = hunt_list[:stop_eat_index + 1]
            self.weight += self.parameter['beta'] * cum_weight_list[stop_eat_index]

        return eaten_animal_list
