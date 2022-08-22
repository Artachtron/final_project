from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grid import Grid

import pickle
import sys
from typing import Final, Tuple

from .display import Display
from .probe import Probe
from .running.config import config
from .simulation import SimState, Simulation

INITIAL_ANIMAL_POPULATION: Final[int] = 10
INITIAL_TREE_POPULATION: Final[int] = 2
# sys.setrecursionlimit(100000)

class World:
    """Class:
        Simulated world,
        containing a simulation and a visual display

        Attributes:
            __id (int):                     unique identifier
            dimensions (Tuple[int, int]):   dimensions of the simulation
            block_size (int):               blocks' cell's size
            sim_speed(int):                 speed of the simulation
            display_active (bool):          display should be visible
            running (bool):                 is currently running
            simulation (Simulation):        computation of the world
            display (Display):              visual representation of simulation

        Methods:
            init:       Initialize the world
            shutdown:   Shutdown the simulation
            run:        run the simulation until shutdown is called
    """
    GRID_HEIGHT: Final[int] = config['Simulation']['grid_height']
    GRID_WIDTH: Final[int] = config['Simulation']['grid_width']
    BLOCK_SIZE: Final[int] = config['Simulation']['block_size']
    MAX_CYCLE = config['Simulation']['max_cycle']

    SIMULATION_SPEED: Final[int] = config['Simulation']['simulation_speed']

    def __init__(self,
                 world_id: int,
                 dimensions: Tuple[int, int] = (GRID_HEIGHT,
                                                GRID_WIDTH),
                 block_size: int = BLOCK_SIZE,
                 sim_speed: int = SIMULATION_SPEED,
                 display_active: bool = False):

        self.__id: int = world_id
        self.dimensions: Tuple[int, int] = dimensions
        self.block_size: int = block_size
        self.sim_speed: int = sim_speed
        self.display_active: bool = display_active
        self.running: bool = False

        self.simulation: Simulation
        self.display: Display
        self.metrics: Probe

    @property
    def id(self) -> int:
        """Property:
            Return the world's id

        Returns:
            int: world's id
        """
        return self.__id

    def init(self, show_grid: bool=False) -> None:
        """Public method:
            Initialize the world,
            create a simulation and a display (if requested)

        Args:
            show_grid (bool, optional): Show grid's lines. Defaults to False.
        """
        self.simulation: Simulation
        sim_state: SimState
        self.metrics: Probe

        try:
            if not config.loaded_simulation:
                raise FileNotFoundError
            self.simulation = pickle.load(open('simulations/' + config.loaded_simulation, "rb"))
            sim_state = self.simulation.state
            self.simulation.load_innovations()

            World.MAX_CYCLE += sim_state.cycle
            self.display_active: bool = False
            """ phase = sim_state.cycle//1000 + 1
            config.set_difficulty_range(phase=phase) """

        except FileNotFoundError:
            if config.loaded_simulation:
                print(f"the file {config.loaded_simulation} does not exist")
            self.simulation = Simulation(sim_id=self.id,
                                         dimensions=self.dimensions)
            sim_state = self.simulation.init()


        self.metrics = Probe(sim_state=sim_state)

        if self.display_active:
            self.display = Display(display_id=self.id,
                                   dimensions=self.dimensions,
                                   block_size=self.block_size,
                                   sim_speed=self.sim_speed,
                                   show_grid=show_grid)

            self.display.init(sim_state=sim_state)


    def _update(self) -> None:
        """Private method:
            Update the world,
            by updating simulation and
            display and draw display
        """
        grid: Grid
        sim_state: SimState

        grid, sim_state = self.simulation.update()
        self.metrics.update()

        if self.display_active:
            self.display.update(sim_state=sim_state)
            self.display.draw(grid=grid)

        self.set_difficulty(sim_state=sim_state)

        if sim_state.cycle%500 == 0:
            self.save_simulation()
            
        if (sim_state.cycle == World.MAX_CYCLE or
            len(sim_state.entities) == 0):
            self.shutdown()

    def save_simulation(self):
        self.metrics.print(all_keys=True)
        self.graph_metrics()
        self.simulation.save()
        pickle.dump(self.simulation, open('simulations/simulation2', "wb"))

    def set_difficulty(self, sim_state) -> None:
        difficulty: float = ((sim_state.n_animals  - config['Simulation']['difficulty_pop_threshold'])
                             /config['Simulation']['difficulty_pop_factor']) + 1
        diff: float = config.set_difficulty(difficulty)

        print(f"{sim_state.cycle}: {sim_state.n_animals} {diff:.2f}")

        difficulty_factor = sim_state.cycle//config['Simulation']['diffulty_cycles_step']
        config.set_difficulty_factor(difficulty_factor * config['Simulation']['diffulty_factor_increment'])

    def shutdown(self) -> None:
        """Public method:
            Stop the running of the simulation
        """
        self.metrics.print(all_keys=True)
        # self.write_metrics()
        self.running = False

    def run(self) -> None:
        """Public method:
            Run the simulation until shutdown is called
        """
        self.running = True
        while self.running:
            self._update()

    def write_metrics(self) -> None:
        metrics = {'cycles': True,
                   'generations': True,
                   'born_animals': True,
                   }

        self.metrics.write(parameter=config['Run']['parameter'],
                           variation=config['Run']['value'],
                           **metrics)

    def graph_metrics(self) -> None:
        metrics = {'population':True,
                   'brain_complexity':True,
                   'actions_count':True,
                   'actions_overtime':True,
                   'death_age': True}

        self.metrics.graph(**metrics)
