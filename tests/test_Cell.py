from biosim.simulation import BioSim


def test_produce_fodder():
    geogr = "WWW\nWLW\nWWW"
    ini_pop = [
        {"loc": (2, 2),
         "pop": [{"species": "Herbivore", "age": 10, "weight": 10}]}]
    test = BioSim(geogr, ini_pop, None)
    loc = (1, 1)
    previous_fodder = test._map_instance.cells_array[loc].fodder
    test._map_instance.cells_array[loc].produce_fodder()
    afterwards_fodder = test._map_instance.cells_array[loc].fodder

    assert previous_fodder < afterwards_fodder


def test_herbivore_birth():
    geogr = "WWW\nWLW\nWWW"
    ini_pop = [
        {"loc": (2, 2),
         "pop": [{"species": "Herbivore", "age": 10, "weight": 200}]} for _ in range(20)]
    test = BioSim(geogr, ini_pop, None)
    loc = (1, 1)
    before_num_animals = len(test._map_instance.cells_array[loc].animal_list)
    test._map_instance.cells_array[loc].herbivore_birth()
    after_num_animals = len(test._map_instance.cells_array[loc].animal_list)

    assert before_num_animals < after_num_animals


def test_carnivore_birth():
    geogr = "WWW\nWLW\nWWW"
    ini_pop = [
        {"loc": (2, 2),
         "pop": [{"species": "Carnivore", "age": 10, "weight": 200}]} for _ in range(20)]
    test = BioSim(geogr, ini_pop, None)
    loc = (1, 1)
    before_num_animals = len(test._map_instance.cells_array[loc].Carnivores_list)
    test._map_instance.cells_array[loc].carnivore_birth()
    after_num_animals = len(test._map_instance.cells_array[loc].Carnivores_list)

    assert before_num_animals < after_num_animals


def test_grow_and_loose_weight_herbivore():
    geogr = "WWW\nWLW\nWWW"
    ini_pop = [
        {"loc": (2, 2),
         "pop": [{"species": "Herbivore", "age": 10, "weight": 200}]} for _ in range(20)]
    test = BioSim(geogr, ini_pop, None)
    loc = (1, 1)
    before_weight = []

    for animal in test._map_instance.cells_array[loc].animal_list:
        before_weight += [(animal.weight for animal in test._map_instance.cells_array[loc].
                          animal_list)]

    test._map_instance.cells_array[loc].grow_and_loose_weight_herbivore()
    after_weight = []
    for animal in test._map_instance.cells_array[loc].animal_list:
        after_weight += [(animal.weight for animal in test._map_instance.cells_array[loc].
                         animal_list)]

    assert before_weight != after_weight


def test_grow_and_loose_weight_carnivore():
    geogr = "WWW\nWLW\nWWW"
    ini_pop = [
        {"loc": (2, 2),
         "pop": [{"species": "Carnivore", "age": 10, "weight": 200}]} for _ in range(20)]
    test = BioSim(geogr, ini_pop, None)
    loc = (1, 1)
    before_weight = []

    for animal in test._map_instance.cells_array[loc].Carnivores_list:
        before_weight += [animal.weight for animal in test._map_instance.cells_array[loc].
                          Carnivores_list]

    test._map_instance.cells_array[loc].grow_and_loose_weight_carnivore()
    after_weight = []
    for animal in test._map_instance.cells_array[loc].Carnivores_list:
        after_weight += [animal.weight for animal in test._map_instance.cells_array[loc].
                         Carnivores_list]

    assert (sum(before_weight) > sum(after_weight))


def test_carnivore_death():
    geogr = "WWW\nWLW\nWWW"
    ini_pop = [
        {"loc": (2, 2),
         "pop": [{"species": "Carnivore", "age": 2, "weight": 5}]} for _ in range(20)]
    test = BioSim(geogr, ini_pop, None)
    loc = (1, 1)
    before_num_animals = len(test._map_instance.cells_array[loc].Carnivores_list)
    test._map_instance.cells_array[loc].carnivore_death()
    after_num_animals = len(test._map_instance.cells_array[loc].Carnivores_list)

    assert before_num_animals > after_num_animals


def test_herbivore_death():
    geogr = "WWW\nWLW\nWWW"
    ini_pop = [
        {"loc": (2, 2),
         "pop": [{"species": "Herbivore", "age": 2, "weight": 10}]} for _ in range(20)]
    test = BioSim(geogr, ini_pop, None)
    loc = (1, 1)
    before_num_animals = len(test._map_instance.cells_array[loc].animal_list)
    test._map_instance.cells_array[loc].herbivore_death()
    after_num_animals = len(test._map_instance.cells_array[loc].animal_list)

    assert before_num_animals > after_num_animals
