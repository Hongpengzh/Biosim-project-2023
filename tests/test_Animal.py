from biosim.Animal import Herbivores, Carnivores
import pytest


@pytest.mark.parametrize("age, weight",
                         [[1, 40],
                          [2, 50],
                          [20, 50]])
def test_fitness_after_weight_loss(age, weight):
    """
    test the fitness after change in weight for both herbivore and carnivore
    """
    herbivore_animal = Herbivores(age, weight)
    before_fitness_h = herbivore_animal.fitness
    herbivore_animal.weight_loss_per_year()
    assert before_fitness_h > herbivore_animal.fitness

    carnivore_animal = Carnivores(age, weight)
    before_fitness_c = carnivore_animal.fitness
    carnivore_animal.weight_loss_per_year()
    assert before_fitness_c > carnivore_animal.fitness


@pytest.mark.parametrize("age, weight",
                         [[1, 40],
                          [2, 50],
                          [20, 50]])
def test_fitness_after_age_increase(age, weight):
    """
    test the fitness after change in age for herbivore and carnivore
    """
    animal = Herbivores(age, weight)
    before_fitness = animal.fitness
    animal.growth_per_year()
    assert before_fitness > animal.fitness

    carnivore_animal = Carnivores(age, weight)
    before_fitness_c = carnivore_animal.fitness
    carnivore_animal.growth_per_year()
    assert before_fitness_c > carnivore_animal.fitness


@pytest.mark.parametrize("age, weight, num_species",
                         [[1, 40, 150],
                          [2, 50, 200],
                          [20, 50, 80]])
def test_fitness_after_procreate(age, weight, num_species):
    """
    test the fitness after animal has given birth for both herbivore and carnivore
    """
    animal_h = Herbivores(age, weight)
    before_fitness_h = animal_h.fitness

    if animal_h.procreate(num_species)[0]:
        after_fitness_h = animal_h.fitness
        assert before_fitness_h > after_fitness_h

    animal_c = Carnivores(age, weight)
    before_fitness_c = animal_c.fitness

    if animal_c.procreate(num_species)[0]:
        after_fitness_c = animal_c.fitness
        assert before_fitness_c > after_fitness_c


@pytest.mark.parametrize("age, weight",
                         [[1, 40],
                          [2, 50],
                          [20, 50]])
def test_fitness_after_eat_herbivore(age, weight):
    """
    test the fitness after animal eats
    """
    animal_h = Herbivores(age, weight)
    before_fitness_h = animal_h.fitness
    animal_h.eat()
    assert before_fitness_h < animal_h.fitness


@pytest.mark.parametrize("age, weight, num_species",
                         [[1, 50, 150],
                          [1, 24, 200],
                          [20, 20, 80]])
def test_procreate(age, weight, num_species):
    """
    Test that there is no birth if the age is less than 1 and the weight of the animal is less than
    (w_birth + sigma_birth)* zeta

    """
    animal_h = Herbivores(age, weight)
    assert not animal_h.procreate(num_species)[0]

    animal_c = Carnivores(age, weight)
    assert not animal_c.procreate(num_species)[0]


@pytest.mark.parametrize("age, weight",
                         [[1, 40],
                          [2, 50],
                          [20, 50]])
def test_growup1year(age, weight):
    """
    test if animals are aging every year or not
    """
    animal = Herbivores(age, weight)
    before_age = animal.age
    animal.growth_per_year()
    assert animal.age == before_age + 1


@pytest.mark.parametrize("age, weight, num_species",
                         [[1, 30, 150],
                          [2, 50, 200],
                          [20, 50, 80]])
def test_weightloss1year(age, weight, num_species):
    """
    test if animals are loosing weight each year and animals are loosing weight after giving birth
    """
    animal = Herbivores(age, weight)
    before_weight = animal.weight
    animal.weight_loss_per_year()
    assert before_weight > animal.weight

    if animal.procreate(num_species)[0]:
        after_weight = animal.weight
        assert before_weight > after_weight


@pytest.mark.parametrize("age, weight",
                         [[1, 40],
                          [2, 50],
                          [20, 50]])
def test_eat(age, weight):
    """
    test if the animals are loosing weight after eating

    """
    animal = Herbivores(age, weight)
    before_weight = animal.weight
    animal.eat()
    assert animal.weight > before_weight


@pytest.mark.parametrize("age, weight",
                         [[1, 0],
                          [2, 0],
                          [20, 0]])
def test_die(age, weight):
    """
  Test if the animals die with certainty if weight is 0 and with probability omega * ( 1 - fitness)
    """

    animal_h = Herbivores(age, weight)
    assert animal_h.die() is True

    animal_c = Carnivores(age, weight)
    assert animal_c.die() is True


@pytest.mark.parametrize("age, weight",
                         [[1, 2],
                          [2, 5],
                          [1, 1]])
def test_die_probability(age, weight):
    """
    Testing the probability of animal to die by setting omega = 0 so, probability to die is 0 as
    probability is omega * (1- fitness) and setting omega = 10 so probability is high and animal
    dies.
    Parameters
    ----------
    age
    weight

    Returns
    -------

    """
    # setting omega = 0, so, probability to die is 0 so should return False
    animal_h1 = Herbivores(age, weight)
    animal_h1.set_params({'omega': 0})
    assert animal_h1.die() is False

    # setting omega = 10 and testing for low age and weight so probability is close to 1, should
    # return True
    animal_h2 = Herbivores(age, weight)
    animal_h2.set_params({'omega': 10})
    assert animal_h2.die() is True
