from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Set

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

    actions_count: Dict = None

    def __post_init__(self):
        self.init_animals = len(self.sim_state.animals)
        self.init_trees = len(self.sim_state.trees)

    def update(self):
        added_entities = self.sim_state.added_entities
        self.added_animals += len(added_entities["Animal"])
        self.added_trees += len(added_entities["Tree"])

        self.find_max_generation(entities=set(added_entities["Animal"].values()))

        self.last_cycle = self.sim_state.cycle

        entities = self.sim_state.entities.values()
        self.count_actions(entities=entities)

    @property
    def total_entities(self) -> int:
        return self.added_animals + self.total_trees

    @property
    def total_animals(self) -> int:
        return self.init_animals + self.added_animals

    @property
    def total_trees(self) -> int:
        return self.init_trees + self.added_trees

    def find_max_generation(self, entities: Set[Entity]):
        for entity in entities:
            if entity.generation > self.max_generation:
                self.max_generation = entity.generation

    def count_actions(self, entities: Set[Entity]):
        self.actions_count = dict()
        for entity in entities:
            if hasattr(entity, 'action'):
                action = entity.action.action_type.value
                self.actions_count[action] = self.actions_count.get(action, 0) + 1

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
        if metrics.get('cycles', None):
            data.setdefault('cycles', []).append(self.last_cycle)
        if metrics.get('generations', None):
            data.setdefault('generations', []).append(self.max_generation)
        if metrics.get('born_animals', None):
            data.setdefault('born_animals', []).append(self.added_animals)
        if metrics.get('actions_count', None):
           data.setdefault('actions_count', []).append(self.actions_count)


        with open(measure_file, "w+") as write_file:
            json.dump(existing_data, write_file, indent=4)
