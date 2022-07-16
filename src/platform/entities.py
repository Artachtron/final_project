from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grid import Grid, SubGrid
    from simulation import Environment
    from project.src.rtNEAT.network import Network

import enum
import inspect
from random import choice, random
from typing import Any, Dict, Final, Optional, Tuple

import numpy as np
import numpy.typing as npt
from project.src.rtNEAT.brain import Brain

from actions import *
from energies import Energy, EnergyType, Resource
from universal import EntityType, Position, SimulatedObject


class Direction(enum.Enum):
    """Enum:
        Cardinal direction
    """
    RIGHT   =   (1, 0)
    LEFT    =   (-1, 0)
    DOWN    =   (0, 1)
    UP      =   (0, -1)

class Entity(SimulatedObject):
    """Subclass of simulated object:
        Simulated object that interact with the world,
        and take decisions using a neural network

    Attributes:
        status (Status):                    # current status
        _energies_stock (Dict[str, int]):   # energy currently owned
        generation (int):                   # generation the entity was born in
        species (int):                      # species the entity is part of
        ancestors (Dict[int, Entity]):      # ancestors
        _age (int):                         # time since birth
        _max_age (int):                     # maximum longevity before dying
        _adult_size (int):                  # size to reach before becoming adult
        _is_adult (bool):                   # can reproduce only if adult
        _action_cost (int):                 # blue energy cost of each action
        brain (Brain):                      # brain containing genotype and mind
        mind (Network):                     # neural network

    Methods:
        on_birth:           event on birth
        on_death:           event on death
        has_enough_energy:  check if has at least certain amount of energy from given type
        update:             update entity


    """
    MAX_AGE_SIZE_COEFF: Final[int] = 5
    GROWTH_ENERGY_REQUIRED: Final[int] = 10
    CHILD_ENERGY_COST_DIVISOR: Final[int] = 2
    CHILD_GROWTH_ENERGY_REQUIRED: Final[int] = int(GROWTH_ENERGY_REQUIRED /
                                                   CHILD_ENERGY_COST_DIVISOR)
    INITIAL_SIZE: Final[int] = 20
    INITIAL_BLUE_ENERGY: Final[int] = 100
    INITIAL_RED_ENERGY: Final[int] = 100
    INITIAL_ACTION_COST: Final[int] = int(INITIAL_SIZE/20)

    def __init__(self,
                 position: Tuple[int, int],
                 entity_id: int = 0,
                 generation: int = 0,
                 adult_size: int = 0,
                 max_age: int = 0,
                 size: int = INITIAL_SIZE,
                 action_cost: int = INITIAL_ACTION_COST,
                 blue_energy: int = INITIAL_BLUE_ENERGY,
                 red_energy: int = INITIAL_RED_ENERGY,
                 appearance: str = "",
                 ):
        """Super constructor:
            Get the necessary information for an entity

        Args:
            position (Tuple[int, int]):     coordinates in the world
            entity_id (int, optional):      unique identifier. Defaults to 0.
            generation (int, optional):     generation the entity was born in. Defaults to 0.
            adult_size (int, optional):     minimum size to reach adulthood. Defaults to 0.
            max_age (int, optional):        maximum longevity. Defaults to 0.
            size (int, optional):           initialization size. Defaults to INITIAL_SIZE.
            action_cost (int, optional):    blue energy cost of each action. Defaults to INITIAL_ACTION_COST.
            action (Action):                action of this turn decided by brain
            blue_energy (int, optional):    amount of blue energy owned. Defaults to INITIAL_BLUE_ENERGY.
            red_energy (int, optional):     amount of red energy owned. Defaults to INITIAL_RED_ENERGY.
            appearance (str, optional):     path to sprite's image. Defaults to "".
        """

        appearance = "models/entities/" + appearance
        super().__init__(sim_obj_id=entity_id,
                         position=position,
                         size=size,
                         appearance=appearance)

        self.status: Status = Status.ALIVE                      # current status

        self._energies_stock: Dict[str, int] = {                # energy currently owned
            EnergyType.BLUE.value: blue_energy,
            EnergyType.RED.value: red_energy
            }

        self.generation: int = generation                       # generation the entity was born in
        self.species: int = 0                                   # species the entity is part of
        self.ancestors: Dict[int, Entity] = {}                  # ancestors
        self._age: int = 0                                      # time since birth
        self._max_age: int = (max_age or                        # maximum longevity before dying
                              (size *
                               Entity.MAX_AGE_SIZE_COEFF))

        self._adult_size: int = adult_size                      # size to reach before becoming adult
        self._is_adult: bool = False                            # can reproduce only if adult
        self._reached_adulthood()                               # check if the adult size was reached

        self._action_cost: int = action_cost                    # blue energy cost of each action
        self.action: Action                                     # action of this turn decided by brain

        self.brain: Brain                                       # brain containing genotype and mind
        self.mind: Network                                      # neural network

        if self.generation == 0:
            self._create_brain()

    def _create_brain(self):
        """Private method:
            Create a brain's genotype and its associated phenotype
        """

    def on_birth(self, parent1: Entity, parent2: Entity) -> None:
        """Public method:
            Event: on entity's birth,
            add parents and their ancestors to ancestors set,
            Transplant a brain by crossovering parent's ones.

        Args:
            parent1 (Entity): first parent
            parent2 (Entity): second parent
        """
        self.ancestors: Dict[int, Entity] = ({parent1.id: parent1, parent2.id: parent2}
                                            | parent1.ancestors
                                            | parent2.ancestors)

        brain = Brain.crossover(brain_id=self.id,
                                parent1=parent1.brain,
                                parent2=parent2.brain)

        self._transplant_brain(brain=brain)

    def _transplant_brain(self, brain: Brain) -> None:
        """Private method:
            Action: Replace the entity's brain with a new one,
            or simply give a new one

        Args:
            brain (Brain): brain to transplant
        """
        self.brain = brain
        self.mind = brain.phenotype

    def _decide_action(self, action: Action):
        """Private method:
            Decide which action to perform,
            set the action attribute to action

        Args:
            action (Action): action to set
        """
        self.action = action

        # Energy cost of action
        self._perform_action()

    @property
    def energies(self) -> Dict[str, int]:
        """Public property:

        Returns:
            Dict[str, int]:     dictionary summarising owned energies,
                                arranged by EnergyType
        """
        return self._energies_stock

    @property
    def blue_energy(self) -> int:
        """Public property:

        Returns:
            int: amount of blue energy owned
        """
        return self._energies_stock[EnergyType.BLUE.value]

    @property
    def red_energy(self) -> int:
        """Public property:

        Returns:
            int: amount of red energy owned
        """
        return self._energies_stock[EnergyType.RED.value]

    def _change_status(self, new_status: Status, *statuses: Status):
        """Private method:
            change the status of the entity
            if not dead

        Args:
            new_status (Status):    new status to apply
            *statuses (Status):     extra statuses to check for before applying new one
           """

        if (self.status not in [Status.DEAD, *statuses]):
            self.status = new_status

    def _increase_age(self, amount: int = 1) -> None:
        """Private method:
            Action: Increase age by a given amount

        Args:
            amount (int, optional): amount to increase age by. Defaults to 1.
        """
        self._age += amount

        # if new age above maximum age threshold,
        # the entity dies
        if self._age > self._max_age:
            self._die()

    def _decide_grow(self) -> None:
        """Pivate method:
            Decide on grow action
        """
        self._action_grow()

    def _action_grow(self) -> None:
        """Private method:
            Action: Increase size
        """
        action = GrowAction()

        self._decide_action(action=action)

        self._grow()

    def _grow(self) -> None:
        """Private method:
            Action: Grow the entity to bigger size,
                    consumming red energy
        """
        # Red energy cost depend on adulthood status,
        # cost less energy for a child
        if self._is_adult:
            energy_required = self._size * Entity.GROWTH_ENERGY_REQUIRED

        else:
            energy_required = self._size * Entity.CHILD_GROWTH_ENERGY_REQUIRED

        # Perfrom action if possible: if enough energy is available
        if self._can_perform_action(energy_type=EnergyType.RED,
                                    quantity=energy_required):
            # Increase size,
            # maximum age,
            # action cost
            self._size += 1
            self._max_age += 5
            self._action_cost += 1

        # Check if new size
        # changes adulthood status
        if not self._is_adult:
            self._reached_adulthood()

    def _reached_adulthood(self) -> None:
        """ Private method:
            Check if the entity reached maturity size and
            assign the result in the is_adult instance variable
        """
        self._is_adult = self._size >= self._adult_size

    def _gain_energy(self, energy_type: EnergyType, quantity: int) -> None:
        """Private method:
            Gain energy of specified type and adds it to energies stock

        Args:
            energy_type (EnergyType):   type of energy to gain
            quantity (int):             amount of energy to gain

        Raises:
            ValueError: amount should not be negative
        """
        # quantiy can't be negative
        if quantity < 0 :
            raise ValueError

        # Add the quantity
        self._energies_stock[energy_type.value] += quantity

    def _quantity_from_stock(self, energy_type: EnergyType, quantity: int) -> int:
        """Private method:
            Calculate the quantity that can be taken from the stock for a certain energy type,
            either the quantity asked or the energy left in the stock

        Args:
            energy_type (EnergyType):   type of energy to check in stock
            quantity (int):             initial quantity

        Raises:
            ValueError: quantity cannot be negative

        Returns:
            int: calculated quantity that can be taken
        """
        # quantiy can't be negative
        if quantity < 0 :
            raise ValueError

        energy_amount: int = self._energies_stock[energy_type.value]

        return min(quantity, energy_amount)

    def _loose_energy(self, energy_type: EnergyType, quantity: int) -> int:
        """Private method:
            Loose energy of specified type from energies stock,
            if quantity greater than stock set stock to 0

        Args:
            energy_type (EnergyType):   type of energy to loose
            quantity (int):             amount of energy to loose

        Raises:
            ValueError: quantity should not be negative

        Returns:
            int: quantity of energy that was effectively lost
        """

        quantity = self._quantity_from_stock(energy_type=energy_type,
                                             quantity=quantity)

        self._energies_stock[energy_type.value] -= quantity

        # dies if the entity run out of blue energy
        if self._energies_stock[EnergyType.BLUE.value] <= 0:
            self._die()

        # effective quantity lost
        return quantity

    def _perform_action(self) -> None:
        """Private method:
            Consume blue energy when performing an action
        """
        self._loose_energy(energy_type=EnergyType.BLUE,
                           quantity=self._action_cost)

    def has_enough_energy(self, energy_type: EnergyType, quantity: int) -> bool:
        """Public method:
            Check if has at least certain amount of energy from given type

        Args:
            energy_type (EnergyType):   type of energy to loose
            quantity (int):             amount of energy to loose

        Returns:
            bool: True the entity had enough energy
                  False if it does not
        """
        return self.energies[energy_type.value] >= quantity

    def _can_perform_action(self, energy_type: EnergyType, quantity: int) -> bool:
        """Private method:
            Check if the entity has enough energy to perform an action,
            use the energy if it's the case

        Args:
            energy_type (EnergyType):   type of energy to loose
            quantity (int):             amount of energy to loose

        Returns:
            bool: True the entity had enough energy
                  False if the action can't be performed
        """
        if can_perform:= self.has_enough_energy(energy_type=energy_type,
                                                quantity=quantity):

            self._loose_energy(energy_type=energy_type,
                               quantity=quantity)

        return can_perform

    def _decide_drop(self, out: int) -> None:
        """Pivate method:
            Decide on drop action

        Args:
            out (int): output chosen to trigger action
        """
        if out == 5:
            energy_type = EnergyType.BLUE

        else:
            energy_type = EnergyType.RED

        self._action_drop_energy(energy_type=energy_type,
                                    quantity=10,
                                    coordinates=self.position)

    def _action_drop_energy(self, energy_type: EnergyType, quantity: int, coordinates: Tuple[int, int]):
        """Private method:
            Action: Drop an amount energy of the specified type at a coordinate

        Args:
            energy_type (EnergyType):       type of energy to drop
            quantity (int):                 amount of energy to drop
            coordinates (Tuple[int, int]):  coordinates on which to drop
        """

        # Calculate the energy capable of being dropped
        quantity = self._quantity_from_stock(energy_type=energy_type,
                                                quantity=quantity)

        action = DropAction(coordinates=coordinates,
                            energy_type=energy_type,
                            quantity=quantity)

        self._decide_action(action=action)

    def on_drop_energy(self, energy_type: EnergyType, quantity: int):
        # Remove energy amount from stock
        self._loose_energy(energy_type=energy_type,
                            quantity=quantity)

    def _action_pick_up_resource(self, coordinates: Tuple[int, int]):
        """Private method:
            Action: Pick energy up at coordinates

        Args:
            coordinates (Tuple[int, int]):  coordinates to pick up energy from
        """
        action = PickupAction(coordinates=coordinates)

        self._decide_action(action=action)

    def on_pick_up_resource(self, resource: Resource):
        """Public method:
            Event: on pick up resource

        Args:
            resource (Resource): resource picked up
        """
        # If resource is an energy
        if type(resource).__base__.__name__ == 'Energy':
            self._gain_energy(energy_type=resource.type,
                              quantity=resource.quantity)

        # If resource is a seed
        elif resource.__class__.__name__ == "Seed" and isinstance(self, Animal):
            self._store_seed(seed=resource)

    def _die(self) -> None:
        """Private method:
            Action: Death of the entity
        """
        print(f"{self} died at age {self._age}")
        self.status = Status.DEAD


    def update(self, environment: Environment) -> None:
        """Public method:
            Update entity, by resetting status,
            increment age, and activate the mind

        Args:
            environment (Environment): environment on which the entity live
        """
        # Reset status
        self._change_status(new_status=Status.ALIVE)
        # Increase age by 1
        self._increase_age()

        # Activate mind and return the result
        self._activate_mind(environment=environment)


    def _activate_mind(self, environment: Environment) -> None:
        """Private method:
            Activate entity's brain
        """
        inputs = self._normalize_inputs(environment=environment)
        mind = self.brain.phenotype
        outputs = mind.activate(input_values=inputs)
        self._interpret_outputs(outputs=outputs)

    def _normalize_inputs(self, environment: Environment) -> npt.NDArray:
        """Private method:
            Regroup and normalize inputs to feed brain

        Returns:
            npt.NDArray: array of normalized inputs
        """
        return np.array([])

    def _interpret_outputs(self, outputs: Dict[int, float]):
        """Private method:
            Take the adequate decision based on output values

        Args:
            outputs (Dict[int, float]): dictionary of output nodes' activation values
        """

    def on_death(self) -> None:
        """Public method:
            Event: on death

        Args:
            environment (Environment): current environment
        """


class Animal(Entity):
    """Subclass of Entity:
        Animated entity

        Attributes:
            pocket (Optional[Seed]): pocket in which to store seed

        methods:
            on_death:           event: on animal death
            can_reproduce:      fulfill conditions for reproduction
            on_reproduction:    event when reproducing

    """
    """ INITIAL_BLUE_ENERGY: Final[int] = 10
    INITIAL_RED_ENERGY: Final[int] = 10 """

    REPRODUCTION_ENERGY_COST: Final[int] = 10
    PLANTING_COST: Final[int] = 10

    def __init__(self,
                 position: Tuple[int, int],
                 animal_id: int = 0,
                 generation: int = 0,
                 adult_size: int = 0,
                 max_age: int = 0,
                 size: int = 20,
                 action_cost: int = 1,
                 blue_energy: int = 10,
                 red_energy: int = 10,
                 ):

        super().__init__(position=position,
                         entity_id=animal_id,
                         generation=generation,
                         adult_size=adult_size,
                         max_age=max_age,
                         size=size,
                         action_cost=action_cost,
                         blue_energy=blue_energy,
                         red_energy=red_energy,
                         appearance="animal.png")

        self._pocket: Optional[Seed] = None # pocket in which to store seed

    def __repr__(self):
        return f'Animal {self.id}'

    def can_reproduce(self) -> bool:
        """Public method:
            Fulfill conditions for reproduction

        Returns:
            bool:   True if conditions are satisfied,
                    False if at least one condition is not fulfilled
        """
        return (self._is_adult and
                self.has_enough_energy(energy_type=EnergyType.RED,
                                       quantity=Animal.REPRODUCTION_ENERGY_COST * self._size))

    def on_reproduction(self) -> None:
        """Public method:
            Event: when reproducing
        """
        DIE_GIVING_BIRTH_PROB = 0.02
        if random() < DIE_GIVING_BIRTH_PROB:
            self.status = (Status.DEAD
                           if random() < DIE_GIVING_BIRTH_PROB
                           else Status.ALIVE)

        self._loose_energy(energy_type=EnergyType.RED,
                           quantity=Animal.REPRODUCTION_ENERGY_COST * self._size)

    def _create_brain(self) -> None:
        """Private method:
            Create an animal brain's genotype and its associated phenotype
        """
        NUM_ANIMAL_INPUTS = 96
        NUM_ANIMAL_OUTPUTS = 12

        self.brain = Brain.genesis(brain_id=self.id,
                                   n_inputs=NUM_ANIMAL_INPUTS,
                                   n_outputs=NUM_ANIMAL_OUTPUTS)

        self.mind = self.brain.phenotype
        self.mind.verify_complete_post_genesis()

    def _action_move(self, direction: Direction) -> None:
        """Private method:
            Action: Move the animal in the given direction

        Args:
            direction (Direction):  direction in which to move
        """
        next_pos = Position.add(position=self._position,
                                vect=direction.value)()

        action = MoveAction(coordinates=next_pos)

        self._decide_action(action=action)

    def on_move(self, new_position: Tuple[int, int]) -> None:
        """Public method:
            Event: Update animal's position to the given coordinates

        Args:
            new_position (Tuple[int, int]): coordinates to move on
        """
        # update self position
        self._update_position(new_position=new_position)

    def _update_position(self, new_position: Tuple[int, int]) -> None:
        """Private method:
            Update the position of the animal

        Args:
            new_position (Tuple[int, int]): position's updated value
        """
        self.position = new_position

    def _action_plant_tree(self) -> None:
        """Private method:
            Action: Plant a tree nearby, consume red energy
        """
        # Verifiy that enough enough energy is available
        if self._can_perform_action(energy_type=EnergyType.RED,
                                    quantity=Animal.PLANTING_COST):

            action = PlantTreeAction(coordinates=self.position,
                                     seed=self._pocket)

        else:
            action = IdleAction()

        self._decide_action(action=action)

    def on_plant_tree(self) -> None:
        """Public method:
            Event: on animal planting a tree
        """
        self._pocket = None

    def _store_seed(self, seed: Seed) -> None:
        """Private method:
            Action: Pick up a seed and store it"""

        # Only store a seed if the pocket is empty
        if not self._pocket:
            self._pocket = seed

        # Energy cost of action
        self._perform_action()

    def _action_recycle_seed(self) -> None:
        """Private method:
            Action: Destroy seed stored and drop energy content
        """
        # if pocket is empty nothing to recycle
        if self._pocket:
            tree = self._pocket.germinate()

            action = RecycleAction(coordinates=self.position,
                                tree=tree)
        else:
            action = IdleAction()

        self._decide_action(action=action)

    def on_recycle_seed(self) -> None:
        """Private method:
        Action: Destroy seed stored and drop energy content
        """
        # Empty pocket
        self._pocket = None

    def _action_reproduce(self) -> None:
        """Private method:
            Action: Get ready for reproduction
        """
        action = ReproduceAction()

        self._decide_action(action=action)

    def on_death(self) -> None:
        """Private method:
            Event: on animal death, release energy on cells around death position"""
        pass

    def _want_to_reproduce(self) -> None:
        """Private method:
            Set this animal's status to fertile
        """
        self._change_status(new_status=Status.FERTILE)

    def _action_paint(self, color: Tuple[int, int, int]) -> None:
        """Private method:
            Action: modify a cell color

        Args:
            color (Tuple[int, int, int]): color to change on cell

        """
        action = PaintAction(coordinates=self.position,
                             color=color)

        self._decide_action(action=action)

    def on_paint(self) -> None:
        """Public method:
            Event: on paint action
        """
        pass

    def _normalize_inputs(self, environment: Environment) -> npt.NDArray:
        """Private method:
            Normalize input values for brain activation

        Args:
            environment (Environment): environment of the animal

        Returns:
            np.array: array containing the normalized input values
        """
        #Inputs
        ## Internal properties
        age = self._age/self._max_age
        size = self._size/100
        blue_energy, red_energy = (energy/100000 for energy in self.energies.values())
        ## Perceptions
        entities = environment.find_if_entities_around(coordinates=self.position,
                                                       include_self=False)
        see_entities = list(map(int, entities))
        energies = environment.find_if_resources_around(coordinates=self.position,
                                                        include_self=True)
        see_energies = list(map(int, energies))

        colors = environment.get_colors_around(coordinates=self.position,
                                               radius=2)

        see_colors = (1 - colors.flatten()/255).tolist()

        return np.array([age, size, blue_energy, red_energy] + see_entities + see_energies + see_colors)

    def _decide_move(self, out: int, value: float) -> None:
        """Pivate method:
            Decide on move action

        Args:
            out (int):      output chosen to trigger action
            value (float):  output value
        """
        if out == 0:
            if value > 0:
                direction = Direction.UP
            else:
                direction = Direction.DOWN

        else:
            if value > 0:
                direction = Direction.LEFT
            else:
                direction = Direction.RIGHT

        self._action_move(direction=direction)

    def _decide_paint(self, outputs: Dict[int, float], keys: Tuple[int, ...]) -> None:
        """Pivate method:
            Decide on paint action

        Args:
            outputs (Dict[int, float]): output values
            keys (Tuple[int, ...]):     sorted output keys
        """
        color = (int(outputs[keys[2]]*255),
                 int(outputs[keys[3]]*255),
                 int(outputs[keys[4]]*255))

        self._action_paint(color=color)

    def _decide_recycle(self) -> None:
        """Pivate method:
            Decide on recycle action
        """
        self._action_recycle_seed()

    def _decide_plant_tree(self) -> None:
        """Pivate method:
            Decide on plant tree action
        """
        self._action_plant_tree()

    def _decide_reproduce(self) -> None:
        """Pivate method:
            Decide on reproduce action
        """
        self._action_reproduce()

    def _decide_pickup(self, coordinates: Tuple[int, int]) -> None:
        """Pivate method:
            Decide on pickup action
        """
        self._action_pick_up_resource(coordinates=coordinates)

    def _interpret_outputs(self, outputs: Dict[int, float]) -> None:
        """Private method:
            Use the output values from brain activation to decide which action to perform.

        Args:
            outputs (np.array):         array or outputs values from brain activation
        """
        # Get the most absolute active value of all the outputs
        most_active_output = max(outputs, key = lambda k : abs(outputs.get(k, 0.0)))
        value = outputs[most_active_output]

        sorted_output_keys = tuple(sorted(outputs.keys()))

        match out:= sorted_output_keys.index(most_active_output):
            ## Simple actions ##
            # Move action
            case key if key in range(0,2):
                self._decide_move(out=out,
                                  value=value)

            # Modify cell color
            case key if key in range(2,5):
                self._decide_paint(outputs=outputs,
                                   keys=sorted_output_keys)

            # Drop energy
            case key if key in range(5,7):
                self._decide_drop(out=out)

            # Pick up resource
            case 7:
                self._decide_pickup(coordinates=self.position)

            # Recycle seed
            case 8:
                self._decide_recycle()

            ## Complex actions ##
            # Plant tree
            case 9:
                self._decide_plant_tree()

            # Grow
            case 10:
                self._decide_grow()

            # Reproduction
            case 11:
                self._decide_reproduce()

class Tree(Entity):
    """Subclass of Entity:
        Immobile entity, producing energy

        Attributes:
            _production_type: Type of energy produced by the tree

        Methods:
            on_death:       event on tree death
            create_seed:    create a seed on current position
    """
    def __init__(self,
                 position: Tuple[int, int],
                 tree_id: int = 0,
                 generation: int = 0,
                 adult_size: int = 0,
                 max_age: int = 0,
                 size: int = 10,
                 action_cost: int = 1,
                 blue_energy: int = 10,
                 red_energy: int = 10,
                 production_type: Optional[EnergyType] = None,
                 ):
        """Constructor:
            Initialize a tree

        Args:
            position (Tuple[int, int]):                         coordinates in the world
            tree_id (int, optional):                            unique identifier. Defaults to 0.
            generation (int, optional):                         generation the tree was born in. Defaults to 0.
            adult_size (int, optional):                         minimum size to reach adulthood. Defaults to 0.
            max_age (int, optional):                            maximum longevity. Defaults to 0.
            size (int, optional):                               current size. Defaults to 10.
            action_cost (int, optional):                        blue energy cost of each action. Defaults to 1.
            blue_energy (int, optional):                        amount of blue energy owned. Defaults to 10.
            red_energy (int, optional):                         amount of red energy owned. Defaults to 10.
            production_type (Optional[EnergyType], optional):   type of energy produced. Defaults to None.
        """

        super().__init__(position=position,
                         entity_id=tree_id,
                         generation=generation,
                         adult_size=adult_size,
                         max_age=max_age,
                         size=size,
                         action_cost=action_cost,
                         blue_energy=blue_energy,
                         red_energy=red_energy,
                         appearance="plant.png")

        self._production_type: EnergyType = (production_type or         # Type of energy produced by the tree
                                             choice(list(EnergyType)))

    def __repr__(self) -> str:
        return f'Tree {self.id}: {self._production_type}'

    def _create_brain(self):
        """Private method:
            Create a tree brain's genotype and its associated phenotype
        """
        NUM_TREE_INPUTS = 88
        NUM_TREE_OUTPUTS = 7

        self.brain = Brain.genesis(brain_id=self.id,
                                   n_inputs=NUM_TREE_INPUTS,
                                   n_outputs=NUM_TREE_OUTPUTS)

        self.mind = self.brain.phenotype
        self.mind.verify_complete_post_genesis()

    def on_death(self) -> None:
        """Public method:
            Event: On tree death, create a seed on dead tree position"""
        pass

    def _encode_genetic_data(self, data: Dict) -> Dict:
        """Private method:
            Encode the genetic information necessary
            to spawn another tree

        Returns:
            Dict: dictionary containing the genetic information
        """

        original_dict: Dict[str, Any] = self.__dict__   # original dictionary with tree data
        genetic_data: Dict[str, Any] = {}               # new dictionary with formatted value
        args = inspect.getfullargspec(Tree)[0]          # list of parameters to create a tree
        # loop through original dictionary and
        # take desired values after reformatting
        for key, value in original_dict.items():
            final_key = key[1:]
            if final_key in args:
                genetic_data[final_key] = value

        # Work on the parameter that need some custom transformation
        genetic_data['tree_id'] = original_dict['_SimulatedObject__id']
        genetic_data['position'] = genetic_data['position']()
        genetic_data['blue_energy'] = original_dict['_energies_stock'][EnergyType.BLUE.value]
        genetic_data['red_energy'] = original_dict['_energies_stock'][EnergyType.RED.value]

        # Extra given data from environment
        for key, value in data.items():
            genetic_data[key] = value

        return genetic_data

    def create_seed(self, data: Dict) -> Seed:
        """Public method:
            Create a seed on current position,
            with tree's genetic information

        Args:
            data (Dict): genetic data to encode

        Returns:
            Seed: created Seed
        """
        genetic_data = self._encode_genetic_data(data=data)

        seed = Seed(seed_id=self.id,
                    position=self.position,
                    genetic_data=genetic_data)

        return seed

    def _action_produce_energy(self) -> None:
        """Private method:
            Action: Produce energy
        """
        action = ProduceEnergyAction(energy_type=self._production_type,
                                     coordinates=self.position)
        self._decide_action(action)

    def _decide_produce(self) -> None:
        """Pivate method:
            Decide on produce energy action
        """
        self._action_produce_energy()

    def on_produce_energy(self, count_trees_around: int) -> None:
        """Public method:
            Event: Produce energy
        """
        MINUMUM_AGE: Final[int] = 20
        if self._age < MINUMUM_AGE:
            pass

        self._gain_energy(energy_type=self._production_type,
                         quantity=int((5 * self._size) / 2**count_trees_around))

    def _decide_pickup(self, outputs: Dict[int,float], keys: Tuple[int, ...]) -> None:
        """Pivate method:
            Decide on pickup action

        Args:
            outputs (Dict[int, float]): output values
            keys (Tuple[int, ...]):     sorted output keys
        """
        outs = (outputs[keys[-2]],
                outputs[keys[-1]])
        # Obtain value between 0 and 2 from -1 to 1
        out_x, out_y = (int((abs(out)*3 - 0.0001)) for out in outs)

        self._action_pick_up_resource(coordinates=(out_x, out_y))

    def _normalize_inputs(self, environment: Environment) -> npt.NDArray:
        """Private method:
            Normalize input values for brain activation

        Args:
            environment (Environment): environment of the tree

        Returns:
            np.array: array containing the normalized input values
        """
        #Inputs
        ## Internal properties
        age = self._age/self._max_age
        size = self._size/100
        blue_energy, red_energy = (energy/100000 for energy in self.energies.values())
        ## Perceptions
        energies = environment.find_if_resources_around(coordinates=self.position,
                                                        include_self=True)
        see_energies = list(map(int, energies))

        colors = environment.get_colors_around(coordinates=self.position,
                                               radius=2)

        see_colors = (1 - colors.flatten()/255).tolist()

        return np.array([age, size, blue_energy, red_energy] + see_energies + see_colors)

    def _interpret_outputs(self, outputs: Dict[int, float]) -> None:
        """Private method:
            Use the output values from brain activation to decide which action to perform.

        Args:
            outputs (np.array):         array or outputs values from brain activation
            environment (Environment):  environment of the tree
        """

        TREE_TRIGGER_OUTPUTS: Final[int] = 5
        sorted_output_keys = sorted(outputs.keys())
        out_dict = {k: outputs[k] for k in sorted_output_keys[:TREE_TRIGGER_OUTPUTS]}
        # Get the most absolute active value of the trigger outputs
        most_active_output = max(out_dict, key = lambda k : abs(out_dict.get(k, 0.0)))
        #value = outputs[most_active_output]

        match out:= sorted_output_keys.index(most_active_output):
            ## Simple actions ##
            # Produce energy
            case 0:
                self._decide_produce()
            # Drop energy
            case key if key in range(1,3):
                self._decide_drop(out=out)

            # Pick up resource
            case 3:
                self._decide_pickup(outputs=outputs,
                                    keys=tuple(sorted_output_keys))
            #Grow
            case 4:
                self._decide_grow()
        print(f"keys: {out_dict.keys()}")
        print(f"sorted keys: {sorted_output_keys}")
        print(f"Most active: {most_active_output}")
        print(f"OUT: {out}")

class Seed(Resource):
    """Subclass of Resource:
        Container of a tree's genetic information

        Attributes:
            genetic_data: genetic information of a tree

        Methods:
            germinate:  Spawn a tree from genetic data
    """
    def __init__(self,
                 seed_id: int,
                 position: Tuple[int, int],
                 genetic_data: Dict):

        super(Seed, self).__init__(resource_id=seed_id,
                                   position=position,
                                   appearance="seed.png",
                                   quantity=1)

        self.genetic_data = genetic_data

    def __repr__(self):
        return f"Seed {self.id}"

    def germinate(self) -> Tree:
        """Public method:
            Spawn a tree from genetic data
            contained in this seed

        Returns:
            Tree: tree spawned
        """
        return Tree(**self.genetic_data)
