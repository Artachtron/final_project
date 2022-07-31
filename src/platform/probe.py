from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Set

if TYPE_CHECKING:
    from simulation import SimState
    from entities import Entity

import json
from dataclasses import dataclass
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

    max_generation: Optional[int] = 0
    last_cycle: Optional[int] = 0

    def __post_init__(self):
        self.init_animals = len(self.sim_state.animals)
        self.init_trees = len(self.sim_state.trees)

    def update(self):
        added_entities = self.sim_state.added_entities
        self.added_animals += len(added_entities["Animal"])
        self.added_trees += len(added_entities["Tree"])

        self.find_max_generation(entities=set(added_entities["Animal"].values()))

        self.last_cycle = self.sim_state.cycle

    @property
    def total_entities(self) -> int:
        return self.added_animals + self.total_trees

    def total_animals(self) -> int:
        return self.init_animals + self.added_animals

    def total_trees(self) -> int:
        return self.init_trees + self.added_trees

    def find_max_generation(self, entities: Set[Entity]):
        for entity in entities:
            if entity.generation > self.max_generation:
                self.max_generation = entity.generation

    def write(self, parameter: str, variation: str) -> None:
        measure_file = join(Probe.directory, "measurements.json")

        try:
            existing_data = json.load(open(measure_file))
        except FileNotFoundError:
            existing_data = {}

        variation = str(variation)
  
        existing_data.setdefault(parameter, {})
        existing_data[parameter].setdefault(variation, {})
        
        data = existing_data[parameter][variation]
        data.setdefault('cycles', []).append(self.last_cycle)
        data.setdefault('generations', []).append(self.max_generation)
        data.setdefault('born_animals', []).append(self.added_animals)
        with open(measure_file, "w+") as write_file:
            json.dump(existing_data, write_file, indent=4)
