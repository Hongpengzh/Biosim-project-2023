"""
Test module for simulation
"""
from biosim.simulation import BioSim
from biosim import Animal, Cell
import pytest


class TestSimParams:
    """
    Test for Simulation Parameters
    """
    @pytest.fixture(autouse=True)
    def create_sim(self):
        """Create a plain_sim instance of BioSim for testing."""
        self.island_map = ("WWW\nWLW\nWWW")
        self.ini_pop = [{"loc": (2, 2), "pop": [{"species": "Herbivore", "age": 5, "weight": 20}
                                                for _ in range(5)]}]
        self.seed = 1
        self.plain_sim = BioSim(self.island_map, self.ini_pop, self.seed)

    @pytest.mark.parametrize('species, param_dict',
                             [('tiger', {'beta': 0, 'eta': 0}),
                              (0, {'mu': 0, 'gama': 0}),
                              ('Herbivore', ['mu', 0]),
                              ('Carnivore', ['mu', 0]),
                              ('Herbivore', {'beta': -1}),
                              ('Herbivore', {'X': 100}),
                              ('Carnivore', {'Y': 100})])
    def test_set_animal_parameters_illegal(self, species, param_dict):
        """Test the illegal input for set_animal_parameters"""
        with pytest.raises((TypeError, AttributeError, ValueError)):
            self.plain_sim.set_animal_parameters(species, param_dict)

    @pytest.mark.parametrize('species, param_dict',
                             [('Herbivore', {'beta': 0, 'eta': 0}),
                              ('Herbivore', {'omega': 100, 'xi': 200}),
                              ('Herbivore', {'mu': 0, 'gamma': 0}),
                              ('Herbivore', {'F': 20, 'w_half': 10})
                              ])
    def test_set_herbivore_parameters_legal(self, species, param_dict):
        """Test legal input of herbivores for set_animal_parameters"""
        self.plain_sim.set_animal_parameters(species, param_dict)
        herb_parameters = Animal.Herbivores.parameter
        herb_true = all([herb_parameters[key] == param_dict[key] for key in param_dict])
        assert herb_true

    @pytest.mark.parametrize('species, param_dict',
                             [('Carnivore', {'beta': 10, 'eta': 20}),
                              ('Carnivore', {'omega': 100, 'xi': 200}),
                              ('Carnivore', {'mu': 0, 'gamma': 0}),
                              ('Carnivore', {'F': 20, 'DeltaPhiMax': 10})
                              ])
    def test_set_carnivore_parameters_legal(self, species, param_dict):
        """Test legal input of carnivores for set_animal_parameters"""
        self.plain_sim.set_animal_parameters(species, param_dict)
        carn_parameters = Animal.Carnivores.parameter
        carn_true = all([carn_parameters[key] == param_dict[key] for key in param_dict])
        assert carn_true

    @pytest.mark.parametrize('landscape, params',
                             [('X', {'f_max': 700}),
                              ('H', 200),
                              ('H', {'F_max': 10}),
                              ('H', {'f_max': -1}),
                              ('L', {'F_max': 100}),
                              ])
    def test_set_landscape_parameters_illegal(self, landscape, params):
        """Test illegal input for set_landscape_parameters"""
        with pytest.raises((TypeError, KeyError, AttributeError, ValueError)):
            self.plain_sim.set_landscape_parameters(landscape, params)

    @pytest.mark.parametrize('landscape, params',
                             [('H', {'f_max': 100}),
                              ('H', {'f_max': 200}),
                              ])
    def test_set_H_landscape_parameters_legal(self, landscape, params):
        """Test legal input of high land for set_landscape_parameters"""
        self.plain_sim.set_landscape_parameters(landscape, params)
        H_parameters = Cell.Cell.ParamCell['f_max_H']
        assert H_parameters == params['f_max']

    @pytest.mark.parametrize('landscape, params',
                             [('L', {'f_max': 300}),
                              ('L', {'f_max': 400}),
                              ])
    def test_set_L_landscape_parameters_legal(self, landscape, params):
        """Test legal input of low land for set_landscape_parameters"""
        self.plain_sim.set_landscape_parameters(landscape, params)
        L_parameters = Cell.Cell.ParamCell['f_max_L']
        assert L_parameters == params['f_max']


class TestSimRes:
    """
    Test for Simulation Results
    """
    @pytest.fixture(autouse=True)
    def create_sim(self):
        """Create a sim instance of BioSim for testing."""
        self.island_map = ("WWW\nWLW\nWWW")
        ini_herbs = [{'loc': (2, 2),
                      'pop': [{'species': 'Herbivore',
                               'age': 5,
                               'weight': 20}
                              for _ in range(50)]}]
        self.ini_pop = ini_herbs
        self.seed = 100
        self.sim = BioSim(self.island_map, self.ini_pop, self.seed)

    @pytest.fixture(autouse=True)
    def test_simulation(self):
        """Simulate 1 year for other testing."""
        self.sim.simulate(1)

    def test_year(self, test_simulation):
        """Test the year method"""
        assert self.sim.year == 1

    def test_num_animals(self, test_simulation):
        """Test the num_animals method"""
        assert self.sim.num_animals <= len(self.ini_pop[0]['pop'])

    @pytest.mark.parametrize('population',
                             [[{'loc': (2, 2), 'pop': [{'species': 'Carnivore',
                                                        'age': 5, 'weight': 20}
                                for _ in range(20)]}],
                              [{'loc': (2, 2),
                                'pop': [{'species': 'Herbivore',
                                         'age': 3,
                                         'weight': 10}
                                        for _ in range(30)]}]
                              ])
    def test_add_population(self, population, test_simulation):
        """Test the add_population method"""
        num = self.sim.num_animals
        self.sim.add_population(population)
        assert self.sim.num_animals >= num

    def test_num_animals_per_species(self, test_simulation):
        """Test the num_animals_per_species method"""
        num_dict = self.sim.num_animals_per_species
        num_dict['Herbivore'] == self.sim._herbivores_num
        num_dict['Carnivore'] == self.sim._carnivores_num

        assert (self.sim.num_animals == (num_dict['Herbivore'] + num_dict['Carnivore'])) \
            & (num_dict['Herbivore'] == self.sim._herbivores_num) \
            & (num_dict['Carnivore'] == self.sim._carnivores_num)
