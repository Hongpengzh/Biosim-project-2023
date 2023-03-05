"""
The Animal class with Herbivores and Carnivores as subclasses of Animal.
"""

__author__ = 'Hongpeng Zhang and Sujan Devkota'
__email__ = 'hongpeng.zhang@nmbu.no and sujan.devkota@nmbu.no'

import random


class Cell:
    """
    Class Cell for one landscape type where animals reside.
    """
    ParamCell = {'f_max_L': 800, 'f_max_H': 300}

    @classmethod
    def update_cell_para(cls, landscape, params):
        """
        Method to update parameters in the cell. Raises value error if values are negative

        Parameters
        ----------
        landscape: str
        params: dictionary

        """
        if list(params.values())[0] < 0:
            raise ValueError('the parameter for landscape must be larger than 0')
        else:
            if landscape == 'L':
                cls.ParamCell['f_max_L'] = params['f_max']
            if landscape == 'H':
                cls.ParamCell['f_max_H'] = params['f_max']

    def __init__(self, geography, fodder=0, animal_list=None, Carnivores_list=None):
        """
        Constructor for class Cell.

        Parameters
        ----------
        geography: str
            Water, Lowland, Highland or Desert
        fodder: int
        animal_list: list
            Herbivore list
        Carnivores_list: list
            Carnivore list

        Notes
        -----
        - Geography or landscape types are Lowland, Highland, Desert and water.

          .. code:: python

             geography_dict = {'W': 'Water', 'L': 'Lowland', 'H': 'Highland', 'D': 'Desert'}

        """
        self.fodder = fodder
        self.geography = geography
        self.animal_list = animal_list if animal_list is not None else []
        self.Carnivores_list = Carnivores_list if Carnivores_list is not None else []

    def produce_fodder(self):
        """
        Method to add fodder to the geography type. There is no fodder in desert and water.

        """
        if (self.geography == 'W') | (self.geography == 'D'):
            self.fodder += 0
        elif self.geography == 'L':
            self.fodder += Cell.ParamCell['f_max_L']
        else:
            self.fodder += Cell.ParamCell['f_max_H']

    def herbivore_birth(self):
        """
        Method that checks if herbivore animal has given birth and updates the herbivore animal list

        Returns
        -------
        List
            Baby herbivore animal list
        """
        baby_animal_list = []
        for animal in self.animal_list:
            baby = animal.procreate(len(self.animal_list))
            if baby[0]:
                baby_animal_list.append(baby[1])
        self.animal_list += baby_animal_list

        return baby_animal_list

    def carnivore_birth(self):
        """
        Method that checks if carnivore animal has given birth and updates the carnivore animal list

        Returns
        -------
        List
            Baby herbivore animal list
        """
        baby_animal_list = []
        for animal in self.Carnivores_list:
            baby = animal.procreate(len(self.Carnivores_list))
            if baby[0]:
                baby_animal_list.append(baby[1])
        self.Carnivores_list += baby_animal_list

        return baby_animal_list

    def feed_animals(self):
        """
        Method to feed herbivore animals in the random order and stop when the fodder is not enough

        """
        random.shuffle(self.animal_list)
        for animal in self.animal_list:
            if self.fodder >= animal.parameter['F']:
                animal.eat()
                self.fodder -= animal.parameter['F']
            else:
                break

    def feed_carnivores(self):
        """
        Method to feed carnivores.

        """
        if len(self.Carnivores_list) > 0:
            carnivore_hunting_order_list = sorted({animal: animal.weight for animal in
                                                   self.Carnivores_list}.items(),
                                                  key=lambda x: x[1], reverse=True)
            self.Carnivores_list = [item[0] for item in carnivore_hunting_order_list]
            for animal in self.Carnivores_list:
                # Herbivores hunted in weight descending order
                herbivore_hunted_order_list = sorted({animal: animal.weight for animal in
                                                      self.animal_list}.items(), key=lambda x: x[1])
                self.animal_list = [item[0] for item in herbivore_hunted_order_list]
                eaten_herbivores = animal.eat(self.animal_list)

                if len(eaten_herbivores) > 0:
                    for herbivores in eaten_herbivores:
                        self.animal_list.remove(herbivores)
        else:
            pass

    def grow_and_loose_weight_herbivore(self):
        """
        Method to increase the age of the herbivore animal each year and decrease the weight of the
            herbivore animal in a cell.

        """
        for animal in self.animal_list:
            animal.growth_per_year()
            animal.weight_loss_per_year()

    def grow_and_loose_weight_carnivore(self):
        """
        Method to increase the age of the carnivore animal each year and decrease the weight of the
            carnivore animal in a cell.

        """
        for animal in self.Carnivores_list:
            animal.growth_per_year()
            animal.weight_loss_per_year()

    def herbivore_death(self):
        """
        Method to check if the herbivore animal wants to die. If the animal dies, it removes the
            animal from the herbivore list.

        Returns
        -------
        List
            The list of died herbivore animals

        """
        died_animal_list = []
        for animal in self.animal_list:
            if animal.die():
                died_animal_list.append(animal)
        if len(died_animal_list) > 0:
            for animal in died_animal_list:
                self.animal_list.remove(animal)

        return died_animal_list

    def carnivore_death(self):
        """
        Method to check if the carnivore animal wants to die. If the animal dies, it removes the
            animal from the carnivore list.

        Returns
        -------
        List
           The list of died carnivore animals

        """
        died_carnivores_list = []
        for animal in self.Carnivores_list:
            if animal.die():
                died_carnivores_list.append(animal)
        if len(died_carnivores_list) > 0:
            for animal in died_carnivores_list:
                self.Carnivores_list.remove(animal)

        return died_carnivores_list

    def animal_migration(self, neighbors):
        """
        Method to check if the animal wants to migrate. If the animal wants to stay, then the method
            updates the animal in the stay list for both herbivores and carnivores in a particular
            cell. If the animal wants to move then it appends the list of the destination cell.

        Parameters
        ----------
        neighbors: list

        """
        stay_animal_list = []
        stay_carnivores_list = []
        for animal in self.animal_list:
            if animal.moved:
                stay_animal_list.append(animal)
            else:
                destination = animal.migrate(neighbors)
                if destination:
                    animal.moved = True
                    destination.animal_list.append(animal)
                else:
                    stay_animal_list.append(animal)
        self.animal_list = stay_animal_list

        for animal in self.Carnivores_list:
            if animal.moved:
                stay_carnivores_list.append(animal)
            else:
                destination = animal.migrate(neighbors)
                if destination:
                    animal.moved = True
                    destination.Carnivores_list.append(animal)
                else:
                    stay_carnivores_list.append(animal)
        self.Carnivores_list = stay_carnivores_list
