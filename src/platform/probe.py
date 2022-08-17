from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Set

if TYPE_CHECKING:
    from simulation import SimState
    from entities import Entity

import json
from dataclasses import dataclass, field
from os.path import dirname, join, realpath
from pathlib import Path


@dataclass
class Probe:
    directory = join(
            Path(
                dirname(
                    realpath(__file__))).parent.parent.absolute(),
            "measurements/")

    sim_state: SimState

    added_animals: Optional[int] = 0
    init_animals: Optional[int] = 0
    added_trees: Optional[int] = 0
    init_trees: Optional[int] = 0
    population: Dict = field(default_factory=dict)

    max_generation: Optional[int] = 0
    last_cycle: Optional[int] = 0

    actions_count: Dict = field(default_factory=dict)

    brain_complexity: Dict = field(default_factory=dict)

    max_hidden: int = 0
    max_links: int = 0

    def __post_init__(self):
        self.init_animals = len(self.sim_state.animals)
        self.init_trees = len(self.sim_state.trees)

    @property
    def total_entities(self) -> int:
        return self.total_animals + self.total_trees

    @property
    def total_animals(self) -> int:
        return self.init_animals + self.added_animals

    @property
    def total_trees(self) -> int:
        return self.init_trees + self.added_trees

    def update(self) -> None:
        self.set_added_entities()
        self.set_cycle()

        self.set_max_generation()

        for entity in self.sim_state.entities.values():
            self.set_max_brain_complexity(entity=entity)
            self.update_count_actions(entity=entity)

        self.update_brain_complexity()
        self.update_population()


    def set_added_entities(self) -> None:
        added_entities = self.sim_state.added_entities
        self.added_animals += len(added_entities["Animal"])
        self.added_trees += len(added_entities["Tree"])

    def set_max_generation(self) -> None:
        entities = set(self.sim_state.added_entities["Animal"].values())
        for entity in entities:
            if entity.generation > self.max_generation:
                self.max_generation = entity.generation

    def set_cycle(self) -> None:
        self.last_cycle = self.sim_state.cycle

    def update_count_actions(self, entity: Entity) -> None:
        cycle = self.last_cycle
        self.actions_count.setdefault(cycle, {})

        if hasattr(entity, 'action'):
            action = entity.action.action_type.value
            self.actions_count[cycle][action] = self.actions_count[cycle].get(action, 0) + 1

    def update_population(self) -> None:
        cycle = self.last_cycle
        self.population.setdefault('animal', {})
        self.population['animal'][cycle] = self.sim_state.n_animals
        self.population.setdefault('tree', {})
        self.population['tree'][cycle] = self.sim_state.n_trees

    def set_max_brain_complexity(self, entity: Entity) -> None:
        mind = entity.brain.phenotype

        if mind.n_hidden > self.max_hidden:
            self.max_hidden = mind.n_hidden

        if mind.n_nodes > self.max_links:
            self.max_links = mind.n_links

    def update_brain_complexity(self) -> None:
        cycle = self.last_cycle

        self.brain_complexity.setdefault('nodes', {})
        self.brain_complexity.setdefault('links', {})
        self.brain_complexity['nodes'][cycle] = self.max_hidden
        self.brain_complexity['links'][cycle] = self.max_links

    def write(self, parameter: str, variation: str, **metrics) -> None:
        measure_file = join(Probe.directory, "measurements.json")

        try:
            existing_data = json.load(open(measure_file))
        except FileNotFoundError:
            existing_data = {}

        variation = str(variation)

        existing_data.setdefault(parameter, {})
        existing_data[parameter].setdefault(variation, {})

        data = existing_data[parameter][variation]
        if 'cycles' in metrics:
            data.setdefault('cycles', []).append(self.last_cycle)
        if 'generations' in metrics:
            data.setdefault('generations', []).append(self.max_generation)
        if 'born_animals' in metrics:
            data.setdefault('born_animals', []).append(self.added_animals)

        """ if 'actions_count' in metrics:
           data.setdefault('actions_count', []).append(self.actions_count) """
           
    def graph(self, **metrics) -> None:
        if 'population' in metrics:
            self.graph_population()
        if 'brain_complexity' in metrics:
            self.graph_brain_complexity()
        if 'actions_count' in metrics:
            self.graph_actions_count()

        with open(measure_file, "w+") as write_file:
            json.dump(existing_data, write_file, indent=4)
