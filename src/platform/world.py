from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grid import Grid

from typing import Final, Tuple

from .config import config
from .display import Display
from .simulation import Simulation

INITIAL_ANIMAL_POPULATION: Final[int] = 10
INITIAL_TREE_POPULATION: Final[int] = 2


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
        self.simulation = Simulation(sim_id=self.id,
                                     dimensions=self.dimensions)

        sim_state = self.simulation.init()

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
        grid, sim_state = self.simulation.update()

        if self.display_active:
            self.display.update(sim_state=sim_state)
            self.display.draw(grid=grid)

        if (sim_state.cycle == World.MAX_CYCLE or
            len(sim_state.entities) == 0):

            print(f"SHUTDOWN after {sim_state.cycle} cycles")
            self.shutdown()

    def shutdown(self) -> None:
        """Public method:
            Stop the running of the simulation
        """
        self.running = False

    def run(self) -> None:
        """Public method:
            Run the simulation until shutdown is called
        """
        self.running = True
        while self.running:
            self._update()
