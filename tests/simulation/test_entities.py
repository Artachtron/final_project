
import pytest
from project.src.platform.actions import *
from project.src.platform.energies import BlueEnergy, EnergyType, RedEnergy
from project.src.platform.entities import (Animal, Direction, Entity, Seed,
                                           Status, Tree)
from project.src.platform.grid import Grid
from project.src.platform.running.config import config
from project.src.platform.simulation import Environment
from project.src.rtNEAT.brain import Brain
from project.src.rtNEAT.genome import Genome
from project.src.rtNEAT.network import Network


class TestEntity:
    def test_create_entity(self):
        entity = Entity(position=(20,20))

        assert type(entity) == Entity

    def test_entity_fields(self):
        entity = Entity(position=(20,10),
                        entity_id=3,
                        adult_size=15,
                        max_age=100,
                        size=13,
                        action_cost=1,
                        blue_energy=12,
                        red_energy=27)

        assert {'_position', '_adult_size', '_age',
                '_max_age', '_size', '_action_cost', '_is_adult',
                '_energies_stock'}.issubset(vars(entity))

        assert entity.id == 3
        assert entity.position == (20,10)
        assert entity._adult_size == 15
        assert entity._max_age == 100
        assert entity.age == 0
        assert entity._size == 13
        assert entity._action_cost == 1
        assert entity._energies_stock == {'blue energy': 12, 'red energy': 27}
        assert entity._is_adult == False

    class TestEntityMethods:
        @pytest.fixture(autouse=True)
        def setup(self):
            self.entity = Entity(position=(20,10),
                                entity_id=3,
                                adult_size=15,
                                max_age=100,
                                size=13,
                                action_cost=1,
                                blue_energy=1000,
                                red_energy=2000)

            yield

            self.entity = None

        def test_increase_age(self):
            self.entity._is_adult = True
            assert self.entity.age == 0
            self.entity._increase_age()
            assert self.entity.age == 1

        def test_grow(self):
            assert self.entity._size == 13
            self.entity._grow()
            assert self.entity._size == 14

        def test_reached_adulthood(self):
            for _ in range(10):
                if self.entity._size < self.entity._adult_size:
                    assert not self.entity._is_adult
                else:
                    assert self.entity._is_adult

                self.entity._grow()

            assert self.entity._is_adult

        def test_gain_energy(self):
            #Initial values
            assert self.entity.blue_energy == 1000
            assert self.entity.red_energy == 2000

            # Add Blue energy
            self.entity._gain_energy(energy_type=EnergyType.BLUE,
                                     quantity=3)
            assert self.entity.blue_energy == 1003
            assert self.entity.red_energy == 2000

            # Add Red energy
            self.entity._gain_energy(energy_type=EnergyType.RED,
                                     quantity=23)
            assert self.entity.blue_energy == 1003
            assert self.entity.red_energy == 2023

             # ValueError if negative
            with pytest.raises(ValueError):
                self.entity._gain_energy(energy_type=EnergyType.BLUE,
                                         quantity=-5)

        def test_loose_energy(self):
            #Initial values
            assert self.entity.blue_energy == 1000
            assert self.entity.red_energy == 2000

            # Add Blue energy
            quantity = self.entity._loose_energy(energy_type=EnergyType.BLUE,
                                                 quantity=3)
            assert self.entity.blue_energy == 997
            assert self.entity.red_energy == 2000
            assert quantity == 3

            # Add Red energy
            quantity =self.entity._loose_energy(energy_type=EnergyType.RED,
                                                quantity=23)
            assert self.entity.blue_energy == 997
            assert self.entity.red_energy == 2000 - 23
            assert quantity == 23

            # Energy stock should be 0 if loose more than pocessed
            quantity = self.entity._loose_energy(energy_type=EnergyType.RED,
                                                 quantity=2300)
            assert self.entity.blue_energy == 997
            assert self.entity.red_energy == 0
            assert quantity == 2000 - 23

             # ValueError if negative
            with pytest.raises(ValueError):
                self.entity._gain_energy(energy_type=EnergyType.BLUE,
                                         quantity=-5)

        def test_perform_action(self):
            #Initial values
            assert self.entity.blue_energy == 1000
            assert self.entity.red_energy == 2000

            self.entity._perform_action()
            assert self.entity.blue_energy == 1000 - self.entity._action_cost

        def test_can_perform_action(self):
            # Initial values
            assert self.entity.blue_energy == 1000
            assert self.entity.red_energy == 2000

            #Can perform action
            can = self.entity._can_perform_action(energy_type=EnergyType.RED,
                                                  quantity=2)
            assert can == True
            assert self.entity.red_energy == 1998

            # Cannot perform action
            can = self.entity._can_perform_action(energy_type=EnergyType.RED,
                                                    quantity=3000)
            assert can == False
            assert self.entity.red_energy == 1998

        def test_change_status(self):
            assert self.entity.status == Status.ALIVE
            # change to fertile
            self.entity._change_status(new_status=Status.FERTILE)
            assert self.entity.status == Status.FERTILE
            # can't change because of extra condition
            self.entity._change_status(Status.ALIVE,
                                       Status.FERTILE)
            assert self.entity.status == Status.FERTILE
            # dead
            self.entity._change_status(new_status=Status.DEAD)
            assert self.entity.status == Status.DEAD
            # stay dead
            self.entity._change_status(new_status=Status.ALIVE)
            assert self.entity.status == Status.DEAD

        class TestEntityGridMethods:
            @pytest.fixture(autouse=True)
            def setup(self):
                self.env = Environment(env_id=0)
                self.env.init()
                self.grid = self.env.grid
                self.entity_grid = self.grid.entity_grid

                self.entity = self.env.spawn_animal(coordinates=(0,0))
                yield

            def test_drop_energy(self):
                assert self.entity._loose_energy(energy_type=EnergyType.BLUE,
                                                 quantity=5)
                assert self.entity.energies == {"blue energy": 5, "red energy": 10}
                assert self.entity.blue_energy == 5
                self.entity._action_cost = 0

                # Drop blue energy
                blue_cell = (1,1)
                assert self.grid.resource_grid.get_cell_value(coordinates=blue_cell) == None
                self.entity._action_drop_energy(energy_type=EnergyType.BLUE,
                                                quantity=1,
                                                coordinates=blue_cell)
                self.env._event_on_action(entity=self.entity)
                assert self.entity.energies == {"blue energy": 4, "red energy": 10}
                assert self.entity.blue_energy == 4
                blue_energy = self.grid.resource_grid.get_cell_value(coordinates=blue_cell)
                assert blue_energy != None
                assert type(blue_energy).__name__ == 'BlueEnergy'
                assert blue_energy.quantity == 1

                # Drop red energy
                red_cell = (3,2)
                assert self.grid.resource_grid.get_cell_value(coordinates=red_cell) == None
                assert self.entity.red_energy == 10
                self.entity._action_drop_energy(energy_type=EnergyType.RED,
                                                quantity=3,
                                                coordinates=red_cell)
                self.env._event_on_action(entity=self.entity)

                assert self.entity.energies == {"blue energy": 4, "red energy": 7}
                assert self.entity.red_energy == 7
                red_energy = self.grid.resource_grid.get_cell_value(coordinates=red_cell)
                assert red_energy != None
                assert type(red_energy).__name__ == 'RedEnergy'
                assert red_energy.quantity == 3

                # Drop energy on occupied cell
                self.entity._action_drop_energy(energy_type=EnergyType.BLUE,
                                                quantity=1,
                                                coordinates=red_cell)
                self.env._event_on_action(entity=self.entity)
                assert self.entity.energies == {"blue energy": 4, "red energy": 7}
                assert self.entity.blue_energy == 4
                red_energy2 = self.grid.resource_grid.get_cell_value(coordinates=red_cell)
                assert red_energy2 != None
                assert type(red_energy2).__name__ == 'RedEnergy'
                assert red_energy.quantity == 3

                # Drop too much energy
                red_cell2 = (3,3)
                assert self.grid.resource_grid.get_cell_value(coordinates=red_cell2) == None
                assert self.entity.red_energy == 7
                self.entity._action_drop_energy(energy_type=EnergyType.RED,
                                                quantity=10,
                                                coordinates=red_cell2)
                self.env._event_on_action(entity=self.entity)
                assert self.entity.energies == {"blue energy": 4, "red energy": 0}
                assert self.entity.red_energy == 0
                red_energy2 = self.grid.resource_grid.get_cell_value(coordinates=red_cell2)
                assert red_energy2.quantity == 7




class TestTree:
    def test_create_tree(self):
        tree = Tree(position=(20,20))

        assert type(tree) == Tree
        assert tree.__class__.__base__ == Entity

    def test_tree_fields(self):
        tree = Tree(position=(20,10),
                        tree_id=3,
                        adult_size=15,
                        max_age=100,
                        size=13,
                        action_cost=1,
                        blue_energy=12,
                        red_energy=27,
                        production_type=EnergyType.BLUE)

        assert {'_position', '_adult_size', '_age',
                '_max_age', '_size', '_action_cost', '_is_adult',
                '_energies_stock', '_production_type'}.issubset(vars(tree))

        assert tree.id == 3
        assert tree.position == (20,10)
        assert tree._adult_size == 15
        assert tree._max_age == 100
        assert tree.age == 0
        assert tree._size == 13
        assert tree._action_cost == 1
        assert tree._energies_stock == {'blue energy': 12, 'red energy': 27}
        assert tree._is_adult == False
        assert tree._production_type == EnergyType.BLUE

    class TestTreeMethods:
        @pytest.fixture(autouse=True)
        def setup(self):
            self.env = Environment(env_id=0)
            self.env.init()

            self.tree1 = self.env.spawn_tree(coordinates=(19,10))


            self.tree2 = self.env.spawn_tree(coordinates=(19,11))


            self.grid = self.env.grid
            self.grid.entity_grid._set_cell_value(coordinates=self.tree1.position,
                                                 value=self.tree1)

            yield

            self.tree = None


        def test_on_death(self):
            position = self.tree1.position
            assert self.grid.entity_grid.get_cell_value(coordinates=position)
            assert not self.grid.resource_grid.get_cell_value(coordinates=position)
            assert self.tree1.status.name == Status.ALIVE.name
            self.tree1._die()
            assert self.tree1.status.name == Status.DEAD.name
            #self.tree1.on_death()
            self.env._on_tree_death(tree=self.tree1)
            seed = self.grid.resource_grid.get_cell_value(coordinates=position)
            assert seed
            assert seed.__class__.__name__ == 'Seed'



        def test_energy_production(self):
            # Red energy
            tree = self.env.spawn_tree(production_type=EnergyType.RED,
                                        coordinates=(0,0),
                                        size=1,
                                        red_energy=5,
                                        blue_energy=5)

            tree._decide_produce()
            self.env._event_on_action(entity=tree)
            action = tree.action
            assert action.action_type.name == ActionType.PRODUCE_ENERGY.name
            assert action.energy_type == EnergyType.RED

            # Blue energy
            tree2 = self.env.spawn_tree(production_type=EnergyType.BLUE,
                                        coordinates=(2,2),
                                        size=1,
                                        blue_energy=5,
                                        red_energy=5,
                                        action_cost=0)

            tree2._decide_produce()
            self.env._event_on_action(entity=tree2)
            action = tree2.action
            assert action.action_type.name == ActionType.PRODUCE_ENERGY.name
            assert action.energy_type == EnergyType.BLUE


class TestAnimal:
    def test_create_animal(self):
        animal = Animal(position=(20,20))

        assert type(animal) == Animal
        assert animal.__class__.__base__ == Entity

    def test_animal_fields(self):
        animal = Animal(position=(20,10),
                        animal_id=3,
                        adult_size=15,
                        max_age=100,
                        size=13,
                        action_cost=1,
                        blue_energy=12,
                        red_energy=27)

        assert {'_position', '_adult_size', '_age', 'brain', 'mind',
                '_max_age', '_size', '_action_cost', '_is_adult',
                '_energies_stock', '_pocket'}.issubset(vars(animal))

        assert animal.id == 3
        assert animal.position == (20,10)
        assert animal._adult_size == 15
        assert animal._max_age == 100
        assert animal.age == 0
        assert animal._size == 13
        assert animal._action_cost == 1
        assert animal._energies_stock == {'blue energy': 12, 'red energy': 27}
        assert animal._is_adult == False
        assert animal._pocket == None

        # brain
        brain = animal.brain
        gen = brain.genotype
        net = brain.phenotype

        assert brain.id == animal.id
        assert net.id == animal.id
        assert gen.id == animal.id

        assert len(net.inputs) == 96
        assert len(net.outputs) == 15

    class TestAnimalMethods:
        @pytest.fixture(autouse=True)
        def setup(self):

            """ self.entity_grid = SubGrid(dimensions=(20,20),
                                    data_type=Entity,
                                    initial_value=None) """

            self.env = Environment(env_id=0)
            self.env.init()

            self.animal = self.env.spawn_animal(coordinates=(3,3))


            self.grid: Grid = self.env.grid

            self.entity_grid = self.grid.entity_grid

            yield

            del self.animal
            del self.grid


        def test_move(self):
            animal = self.animal

            # Down
            assert self.entity_grid.get_cell_value(coordinates=(3,4)) == None
            animal._action_move(Direction.DOWN)
            action = animal.action
            assert action.action_type.name == ActionType.MOVE.name
            assert action.coordinates == (3,4)

            # Up
            animal._action_move(Direction.UP)

            action = animal.action
            assert action.action_type.name == ActionType.MOVE.name
            assert action.coordinates == (3,2)

            # Left
            animal._action_move(Direction.LEFT)

            action = animal.action
            assert action.action_type.name == ActionType.MOVE.name
            assert action.coordinates == (2,3)

            # Right
            animal._action_move(Direction.RIGHT)

            action = animal.action
            assert action.action_type.name == ActionType.MOVE.name
            assert action.coordinates == (4,3)

        def test_grow(self):
            self.animal = Animal(size=1,
                                 position=(0,0),
                                 blue_energy=5,
                                 red_energy=10,)

            self.animal._is_adult = True
            assert self.animal.energies == {"blue energy": 5, "red energy": 10}
            assert self.animal.red_energy == 10
            assert self.animal.size == 1
            assert self.animal._max_age == self.animal.size*5
            assert self.animal._action_cost == 1

            # Grow
            self.animal._grow()
            assert self.animal.red_energy == 0
            assert self.animal.size == 2
            assert self.animal._max_age == 10
            assert self.animal._action_cost == 2

        def test_age(self):
            self.animal._max_age = 5
            assert self.animal.age == 0
            self.animal._increase_age()

            # +1
            assert self.animal.age == 1

            # +5
            self.animal._increase_age(amount=4)
            assert self.animal.age == 5

            # Above max age
            assert self.animal.status.name != Status.DEAD.name
            self.animal._increase_age()
            assert self.animal.status.name == Status.DEAD.name

        def test_run_out_of_energy(self):
            assert self.animal.status.name != Status.DEAD.name
            self.animal._loose_energy(energy_type=EnergyType.BLUE,
                                      quantity=500)
            assert self.animal.status.name == Status.DEAD.name

        def test_reached_adulthood(self):
            self.animal = Animal(position=(1,1),
                                 size=1,
                                 adult_size=2,
                                 red_energy=100)
            assert not self.animal._is_adult
            assert self.animal.size == 1
            assert self.animal.red_energy == 100
            self.animal._grow()
            red_energy = 100 - (self.animal.size-1) * Entity.CHILD_GROWTH_ENERGY_REQUIRED
            assert self.animal.red_energy == red_energy
            assert self.animal.size == 2
            assert self.animal._is_adult
            self.animal._grow()
            assert self.animal.red_energy == red_energy - (self.animal.size-1) * Entity.GROWTH_ENERGY_REQUIRED
            assert self.animal.size == 3
            assert self.animal._is_adult

        def test_plant_tree(self):
            animal = self.env.spawn_animal(coordinates=(5,5))
            assert animal.red_energy == 10
            animal._action_plant_tree()
            assert animal.red_energy == 0
            assert animal.action.action_type.name == ActionType.PLANT_TREE.name
            # No free cells

            # env2 = Environment(env_id=2)
            # animal2 = env2.create_animal(coordinates=(0,0))
            # animal2._plant_tree(environment=env2)
            # assert len(env2.grid.entity_grid._find_coordinates_with_class(position=(0,0),
            #                                                           target_class=Tree)) == 0

        def test_pick_up_resource(self):
            position = (1,1)
            energy = self.env.create_energy(coordinates=position,
                                            quantity=10,
                                            energy_type=EnergyType.RED)

            assert self.grid.resource_grid.get_cell_value(position)

            blue_stock = self.animal.blue_energy
            red_stock = self.animal.red_energy
            self.animal._action_pick_up_resource(coordinates=position)

            assert self.animal.blue_energy <= blue_stock
            action = self.animal.action
            assert action.action_type.name == ActionType.PICKUP.name

        def test_pick_up_seed(self):
            tree = self.env.spawn_tree(coordinates=(3,2))
            seed = self.env._create_seed_from_tree(tree)

            position = seed.position

            self.grid.resource_grid._set_cell_value(coordinates=position,
                                                    value=seed)

            animal = self.env.spawn_animal(coordinates=(4,2))

            animal._action_pick_up_resource(coordinates=position)

            assert animal.action.action_type.name == ActionType.PICKUP.name

        def test_recycle_seed(self):
            tree = self.env.spawn_tree(coordinates=(3,2),
                                        blue_energy=5,
                                        red_energy=7)
            seed = self.env._create_seed_from_tree(tree)

            animal = self.env.spawn_animal(coordinates=(3,4))

            animal._pocket = seed
            assert animal._pocket
            animal._action_recycle_seed()

            assert animal.action.action_type.name == ActionType.RECYCLE.name

        def test_replant_seed(self):
            self.animal._action_plant_tree()

            assert self.animal.action.action_type.name == ActionType.PLANT_TREE.name


        def test_decompose(self):
            resource_grid = self.grid.resource_grid
            position = self.animal.position
            self.grid.place_entity(value=self.animal)
            assert not resource_grid._find_coordinates_baseclass(coordinates=position,
                                                                    base_class=BlueEnergy)
            assert not resource_grid._find_coordinates_baseclass(coordinates=position,
                                                                    base_class=RedEnergy)


            self.env.decompose_entity(entity=self.animal)
            assert resource_grid._find_coordinates_baseclass(coordinates=position,
                                                                base_class=BlueEnergy)
            assert resource_grid._find_coordinates_baseclass(coordinates=position,
                                                                base_class=RedEnergy)

        def test_die(self):
            resource_grid = self.grid.resource_grid
            position = self.animal.position
            self.grid.place_entity(value=self.animal)

            assert self.animal.status.name == Status.ALIVE.name
            self.animal._die()
            assert self.animal.status.name == Status.DEAD.name

            assert not resource_grid._find_coordinates_baseclass(coordinates=position,
                                                                    base_class=BlueEnergy)
            assert not resource_grid._find_coordinates_baseclass(coordinates=position,
                                                                    base_class=RedEnergy)
            assert self.grid.entity_grid.get_cell_value(coordinates=position)
            self.env._on_animal_status(animal=self.animal)
            assert resource_grid._find_coordinates_baseclass(coordinates=position,
                                                             base_class=BlueEnergy)
            assert resource_grid._find_coordinates_baseclass(coordinates=position,
                                                             base_class=RedEnergy)
            assert not self.grid.entity_grid.get_cell_value(coordinates=position)

        def test_modify_cell_color(self):
            new_color = (177,125,234)

            self.animal._action_paint(color=new_color)
            action = self.animal.action
            assert action.action_type.name == ActionType.PAINT.name
            assert action.color == new_color

        def test_want_to_reproduce(self):
            assert self.animal.status.name == Status.ALIVE.name
            self.animal._want_to_reproduce()
            assert self.animal.status.name == Status.FERTILE.name

        def test_action_cost(self):
            animal = self.env.spawn_animal(coordinates=(4,4),
                                           blue_energy=100,
                                           red_energy=100,
                                           size=1,
                                           adult_size=2)

            animal._action_cost = 1
            assert animal.blue_energy == 100
            assert animal.red_energy == 100

            # Move
            animal._action_move(direction=Direction.UP)
            assert animal.blue_energy == 99
            assert animal.red_energy == 100

            # Paint cell
            animal._action_paint(color=(125,12,32))
            assert animal.blue_energy == 98
            assert animal.red_energy == 100

            # Drop energy
            animal._action_drop_energy(energy_type=EnergyType.RED,
                                       quantity=10,
                                       coordinates=animal.position)
            assert animal.blue_energy == 97
            assert animal.red_energy == 100

            # Pickup energy
            animal._action_pick_up_resource(coordinates=animal.position)
            assert animal.blue_energy == 96
            assert animal.red_energy == 100

            # Recycle
            animal._action_recycle_seed()
            assert animal.blue_energy == 95
            assert animal.red_energy == 100

            # Recycle
            animal._action_plant_tree()
            assert animal.blue_energy == 94
            assert animal.red_energy == 90

            # Grow child
            animal._action_grow()
            assert animal.blue_energy == 93
            assert animal.red_energy == 85

            # Grow adult
            animal._action_grow()
            assert animal.blue_energy == 91
            assert animal.red_energy == 65

            # Reproduce
            animal._action_reproduce()
            assert animal.blue_energy == 88
            assert animal.red_energy == 65
            animal.on_reproduction()
            assert animal.blue_energy == 88
            assert animal.red_energy == 35


        class TestAnimalMind:
            @pytest.fixture(autouse=True)
            def setup(self):
                self.env = Environment(env_id=0)
                self.env.init()
                self.animal = self.env.spawn_animal(coordinates=(5,5),
                                                     blue_energy=157,
                                                     red_energy=122,
                                                     max_age=24,
                                                     size=37)

                self.animal._increase_age(amount=12)


            def test_normalize_inputs(self):
                # Empty grid
                inputs = self.animal._normalize_inputs(environment=self.env)

                assert len(inputs) == 96
                assert inputs[0] == 0.5
                assert inputs[1] == 37/100
                assert round(inputs[2],5) == 157/10000
                assert round(inputs[3],5) == 122/10000
                assert sum(inputs[4:12]) == 0
                assert sum(inputs[12:21]) == 0
                assert sum(inputs[21:]) == 75*0

                # Non-empty grid
                self.env.spawn_tree(coordinates=(5,6))
                self.env.create_energy(energy_type=EnergyType.BLUE,
                                       quantity=15,
                                       coordinates=(6,5))
                self.env.create_energy(energy_type=EnergyType.BLUE,
                                       quantity=15,
                                       coordinates=(4,5))
                self.env.create_energy(energy_type=EnergyType.BLUE,
                                       quantity=15,
                                       coordinates=(5,4))

                inputs = self.animal._normalize_inputs(environment=self.env)


                assert sum(inputs[4:12]) == 1
                assert sum(inputs[12:21]) == 3
                assert sum(inputs[21:]) == 75*0


            def test_activate_mind(self):
                
                for _ in range(100):
                    self.animal._activate_mind(environment=self.env)


            def test_transplant_brain(self):
                gen_data = {'n_inputs':96,
                            'n_outputs':15,
                            'n_actions':0,
                            'actions':{}}
                brain = Brain.genesis(brain_id=0,
                                      genome_data=gen_data)

                self.animal._transplant_brain(brain=brain)

                assert self.animal.brain == brain

            def test_born(self):
                anim1 = self.env.spawn_animal(coordinates=(5,7))
                anim2 = self.env.spawn_animal(coordinates=(5,6))

                self.animal.brain = None
                self.animal.on_birth(parent1=anim1,
                                     parent2=anim2)

                assert self.animal.brain
                assert self.animal.brain.id == self.animal.id
                
            def test_child(self):
                anim1 = self.env.spawn_animal(coordinates=(5,7),
                                              size=5,
                                              red_energy=1000)
                anim2 = self.env.spawn_animal(coordinates=(5,6),
                                              size=5,
                                              red_energy=1000)
                
                assert anim1.can_reproduce()
                assert anim2.can_reproduce()
                
                child = self.env._reproduce_entities(parent1=anim1,
                                                     parent2=anim2)
                
                mind = child.brain.phenotype
                assert mind.n_inputs == config['Simulation']['Animal']['num_input']
                assert mind.n_outputs == config['Simulation']['Animal']['num_output']
                child._activate_mind(environment=self.env)

            def test_many_hidden_nodes(self):  
                for i in range(10):
                    animal = self.env.spawn_animal(coordinates=(0+i,0+i))
                    if animal:
                        genome_data = {"complete": True,
                                        "n_inputs": Animal.NUM_INPUTS,
                                        "n_outputs": Animal.NUM_OUTPUTS,
                                        "n_actions": Animal.NUM_ACTIONS,
                                        "n_values": Animal.NUM_VALUES,
                                        "actions":{
                                            "move": [0,1],
                                            "drop": [2],
                                            "paint": [3,4,5],
                                            "pickup": [],
                                            "recycle": [],
                                            "plant tree": [],
                                            "grow": [],
                                            "reproduce": []
                                        }}
                        
                        genome = Genome.genesis(genome_id=2,
                                                genome_data=genome_data)
                        
                        for _ in range(100):
                            genome._mutate_add_node()
                            for _ in range(10):
                                genome._mutate_add_link()
                                
                            
                        network = Network.genesis(genome=genome)
                        
                        assert len(network.hidden) == 100
                    
                        animal._activate_mind(environment=self.env)
