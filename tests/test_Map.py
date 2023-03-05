"""
Test module for Map
"""
from biosim.Map import Map
from biosim import Cell
import pytest


class TestMapRes:
    """
    Test Results of method in Map
    """
    @pytest.fixture(autouse=True)
    def creat_map(self):
        """Creat a map instance for other test"""
        self.island_map = ("WWWW\nWLDW\nWHHW\nWWWW")
        self.plain_map = Map(self.island_map)

    @pytest.mark.parametrize('population',
                             [[{'loc': (2, 2),
                                'pop': [{'species': 'Carnivore', 'age': 5,
                                                    'weight': 20} for _ in range(20)]}],
                              [{'loc': (2, 2),
                                'pop': [{'species': 'Herbivore',
                                         'age': 3,
                                         'weight': 10}
                                        for _ in range(30)]}]
                              ])
    def test_add_fauna(self, population):
        """Test the add_fauna method."""
        animal_num, Carnivores_num = self.plain_map.add_fauna(population)

        assert (animal_num + Carnivores_num) == len(population[0]['pop'])

    @pytest.fixture()
    def test_ini_population(self):
        """Set an ini polulation for other test."""
        ini_herbs = [{'loc': (2, 2),
                      'pop': [{'species': 'Herbivore',
                               'age': 5,
                               'weight': 20}
                              for _ in range(50)]}]
        ini_carns = [{'loc': (2, 2),
                      'pop': [{'species': 'Carnivore',
                               'age': 5,
                               'weight': 20}
                              for _ in range(20)]}]
        population = ini_herbs + ini_carns
        self.plain_map.add_fauna(population)

    def test_produce(self, test_ini_population):
        """Test produce method"""
        num_H_land = len(self.plain_map.island_map_array[self.plain_map.island_map_array == 'H'])
        num_L_land = len(self.plain_map.island_map_array[self.plain_map.island_map_array == 'L'])
        fodder_gain = Cell.Cell.ParamCell['f_max_L'] * num_L_land + \
            Cell.Cell.ParamCell['f_max_H'] * num_H_land
        fodder_last_year = 0
        for cell in self.plain_map.cells_array[(self.plain_map.island_map_array == 'L')
                                               | (self.plain_map.island_map_array == 'H')]:
            fodder_last_year += cell.fodder
        self.plain_map.produce()
        fodder_next_year = 0
        for cell in self.plain_map.cells_array[(self.plain_map.island_map_array == 'L')
                                               | (self.plain_map.island_map_array == 'H')]:
            fodder_next_year += cell.fodder

        assert (fodder_last_year + fodder_gain) == fodder_next_year

    def test_givebirth(self, test_ini_population):
        """Test givebirth method"""
        animal_num_before = 0
        carnivore_num_before = 0
        for cell in self.plain_map.cells_array[self.plain_map.island_map_array != 'W']:
            animal_num_before += len(cell.animal_list)
            carnivore_num_before += len(cell.Carnivores_list)
        self.plain_map.givebirth()
        animal_num_after = 0
        carnivore_num_after = 0
        for cell in self.plain_map.cells_array[self.plain_map.island_map_array != 'W']:
            animal_num_after += len(cell.animal_list)
            carnivore_num_after += len(cell.Carnivores_list)

        assert (animal_num_before <= animal_num_after) \
               & (carnivore_num_before <= carnivore_num_after)

    def test_feed(self, test_ini_population):
        """Test feed method"""
        carnivore_weight_before = []
        for cell in self.plain_map.cells_array[self.plain_map.island_map_array != 'W']:
            carnivore_weight_before += [animal.weight for animal in cell.Carnivores_list]
        self.plain_map.feed()
        carnivore_weight_after = []
        for cell in self.plain_map.cells_array[self.plain_map.island_map_array != 'W']:
            carnivore_weight_after += [animal.weight for animal in cell.Carnivores_list]

        assert (sum(carnivore_weight_after) > sum(carnivore_weight_before))

    def test_move_permit(self, test_ini_population):
        """Test move_permit method"""
        self.plain_map.move_permit()
        false_list_h = []
        false_list_c = []
        for cell in self.plain_map.cells_array[self.plain_map.island_map_array != 'W']:
            false_list_h += [animal.moved for animal in cell.animal_list]
            false_list_c += [animal.moved for animal in cell.Carnivores_list]

        assert (~all(false_list_h)) & (~all(false_list_c))

    def test_grow_loss(self, test_ini_population):
        """Test the grow_loss method"""
        h_age_before = []
        c_age_before = []
        h_weight_before = []
        c_weight_before = []
        for cell in self.plain_map.cells_array[self.plain_map.island_map_array != 'W']:
            h_age_before += [animal.age for animal in cell.animal_list]
            c_age_before += [animal.age for animal in cell.Carnivores_list]
            h_weight_before += [animal.weight for animal in cell.animal_list]
            c_weight_before += [animal.weight for animal in cell.Carnivores_list]

        self.plain_map.grow_loss()

        h_age_after = []
        c_age_after = []
        h_weight_after = []
        c_weight_after = []
        for cell in self.plain_map.cells_array[self.plain_map.island_map_array != 'W']:
            h_age_after += [animal.age for animal in cell.animal_list]
            c_age_after += [animal.age for animal in cell.Carnivores_list]
            h_weight_after += [animal.weight for animal in cell.animal_list]
            c_weight_after += [animal.weight for animal in cell.Carnivores_list]

        assert (sum(h_age_before) <= sum(h_age_after)) & (sum(c_age_before) <= sum(c_age_after)) \
               & (sum(h_weight_before) >= sum(h_weight_after)) \
               & (sum(c_weight_before) >= sum(c_weight_after))

    def test_reset_fodder(self):
        """Test reset_fodder method"""
        self.plain_map.reset_fodder()
        non_zero_cell = [cell for cell in
                         self.plain_map.cells_array[self.plain_map.island_map_array != 'W']
                         if cell.fodder != 0]

        assert len(non_zero_cell) == 0

    def test_die(self):
        """Test die method"""
        h_die_before = []
        c_die_before = []
        for cell in self.plain_map.cells_array[self.plain_map.island_map_array != 'W']:
            h_die_before += cell.animal_list
            c_die_before += cell.Carnivores_list
        self.plain_map.die()
        h_die_after = []
        c_die_after = []
        for cell in self.plain_map.cells_array[self.plain_map.island_map_array != 'W']:
            h_die_after += cell.animal_list
            c_die_after += cell.Carnivores_list

        assert (h_die_before >= h_die_after) & (c_die_before >= c_die_after)

    def test_annul_cycle(self, test_ini_population):
        """Test annul_cycle method"""
        h_cycle_before = []
        c_cycle_before = []
        for cell in self.plain_map.cells_array[self.plain_map.island_map_array != 'W']:
            h_cycle_before += cell.animal_list
            c_cycle_before += cell.Carnivores_list

        self.plain_map.annul_cycle()

        h_cycle_after = []
        c_cycle_after = []
        for cell in self.plain_map.cells_array[self.plain_map.island_map_array != 'W']:
            h_cycle_after += cell.animal_list
            c_cycle_after += cell.Carnivores_list

        assert (h_cycle_before != h_cycle_after) & (c_cycle_before != c_cycle_after)
