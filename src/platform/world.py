from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grid import Grid

import pickle
from typing import Final, Tuple

from .display import Display
from .probe import Probe
from .running.analyze import Evaluator
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
                 display_active: bool = False,
                 probe: bool = False):

        self.__id: int = world_id
        self.dimensions: Tuple[int, int] = dimensions
        self.block_size: int = block_size
        self.sim_speed: int = sim_speed
        self.display_active: bool = display_active
        self.probe_active: bool = probe
        self.running: bool = False

        self.simulation: Simulation
        self.display: Display
        self.probe: Probe
        

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
        self.probe: Probe

        try:
            if not config.loaded_simulation:
                raise FileNotFoundError
            
            self.simulation = pickle.load(open('simulations/' + config.loaded_simulation, "rb"))
            sim_state = self.simulation.state
            self.simulation.load_innovations()

            World.MAX_CYCLE += sim_state.cycle
            # self.display_active: bool = False
            """ phase = sim_state.cycle//1000 + 1
            config.set_difficulty_range(phase=phase) """

        except FileNotFoundError:
            if config.loaded_simulation:
                print(f"the file {config.loaded_simulation} does not exist")
            self.simulation = Simulation(sim_id=self.id,
                                         dimensions=self.dimensions)
            sim_state = self.simulation.init()

        if self.probe_active:
            self.probe = Probe(sim_state=sim_state)

        if self.display_active:
            self.display = Display(display_id=self.id,
                                   dimensions=self.dimensions,
                                   block_size=self.block_size,
                                   sim_speed=self.sim_speed,
                                   show_grid=show_grid)

            self.display.init()
            self.display.init_from_sim(sim_state=sim_state)


    def _update(self) -> None:
        """Private method:
            Update the world,
            by updating simulation and
            display and draw display
        """
        grid: Grid
        sim_state: SimState

        grid, sim_state = self.simulation.update()
        config.set_cycle(sim_state.cycle)
        if self.probe_active:
            self.probe.update(cells=grid.color_grid.array)

        if self.display_active:
            self.display.update(sim_state=sim_state)
            self.display.draw(cells=grid.color_grid.array)

        self.set_difficulty(sim_state=sim_state)

        """ if sim_state.cycle%1000 == 0:
            self.save_simulation() """
            
        if (sim_state.cycle == World.MAX_CYCLE or
            len(sim_state.entities) == 0):
            self.shutdown()

    def save_metrics(self, sim_name: str="sim"):
            self.probe.print(all_keys=True)
            self.graph_metrics()
            self.probe.pickle_frames(sim_name=sim_name)
            
    def evaluate_results(self):
        evaluator = Evaluator(probe=self.probe)
        evaluator.evaluate()
            
    def save_simulation(self):
        sim_name = 'sim'
        
        if self.probe_active:
            self.save_metrics(sim_name=sim_name)
            self.evaluate_results()
            
        self.simulation.save()
        pickle.dump(self.simulation, open(f'simulations/{sim_name}', "wb"))
        

    def set_difficulty(self, sim_state) -> None:
        if sim_state.cycle > config['Simulation']['difficulty_cycle_factor_threshold']:
            difficulty_factor: float = ((sim_state.n_animals  - config['Simulation']['difficulty_pop_threshold'])
                                        /config['Simulation']['difficulty_pop_factor']) + 1
            
            config.set_difficulty_factor(difficulty_factor * config['Simulation']['difficulty_pop_coefficient'])
        
        difficulty = ((sim_state.cycle//config['Simulation']['diffulty_cycles_step'])
                     * config['Simulation']['diffulty_factor_coefficient']) + 1
             
        diff: float = config.set_difficulty(difficulty)

        print(f"{sim_state.cycle}: {sim_state.n_animals} {diff:.2f}")

    def shutdown(self) -> None:
        """Public method:
            Stop the running of the simulation
        """
        """ if self.probe:
            self.save_metrics() """
            
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

        self.probe.write(parameter=config['Run']['parameter'],
                           variation=config['Run']['value'],
                           **metrics)

    def graph_metrics(self) -> None:
        metrics = {'population':True,
                   'brain_complexity':True,
                   'actions_count':True,
                   'actions_overtime':True,
                   'death_age':True,
                   'energy_gain':True}

        self.probe.graph(**metrics)
