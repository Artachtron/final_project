from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Set

if TYPE_CHECKING:
    from simulation import SimState
    from entities import Entity

from dataclasses import dataclass


@dataclass
class Metrics:
    sim_state: SimState

    total_animals: Optional[int] = 0
    total_trees: Optional[int] = 0

    max_generation: Optional[int] = 0
    last_cycle: Optional[int] = 0
    
    def __post_init__(self):
        self.total_animals = self.sim_state.n_entities

    def update(self):
        added_entities = self.sim_state.added_entities
        self.total_animals += len(added_entities["Animal"])
        self.total_trees += len(added_entities["Tree"])
        
        self.find_max_generation(entities=set(added_entities["Animal"].values()))
        
        self.last_cycle = self.sim_state.cycle
        
    @property
    def total_entities(self):
        return self.total_animals + self.total_trees

    def find_max_generation(self, entities: Set[Entity]):
        for entity in entities:
            if entity.generation > self.max_generation:
                self.max_generation = entity.generation
