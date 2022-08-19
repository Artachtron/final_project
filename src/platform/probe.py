from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Set

if TYPE_CHECKING:
    from simulation import SimState
    from entities import Entity

import json
from dataclasses import dataclass, field
from os.path import dirname, join, realpath
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


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
    cycle: Optional[int] = 0

    actions_count: Dict = field(default_factory=dict)

    brain_complexity: Dict = field(default_factory=dict)
    death_age: Dict = field(default_factory=dict)

    max_hidden: int = 0
    max_links: int = 0

    actions: Dict = field(default_factory=list)

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

        self.sum_links:int = 0
        self.sum_hidden:int = 0
        self.max_links:int = 0
        self.max_hidden:int = 0
        animals = self.sim_state.animals.values()
        for animal in animals:
            self.set_max_brain_complexity(entity=animal)
            self.update_count_actions(entity=animal)

        count: int = max(1, len(animals))
        self.avg_links = self.sum_links/count
        self.avg_hidden = self.sum_hidden/count

        self.update_brain_complexity()
        self.update_population()
        self.update_death_age()


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
        self.cycle = self.sim_state.cycle

    def update_count_actions(self, entity: Entity) -> None:
        cycle = self.cycle
        self.actions_count.setdefault(cycle, {})

        if hasattr(entity, 'action'):
            action = entity.action.action_type.value
            self.actions_count[cycle][action] = self.actions_count[cycle].get(action, 0) + 1
            self.actions.append((cycle, action))

    def update_population(self) -> None:
        cycle = self.cycle
        self.population.setdefault('animal', {})
        self.population['animal'][cycle] = self.sim_state.n_animals
        self.population.setdefault('tree', {})
        self.population['tree'][cycle] = self.sim_state.n_trees

    def set_max_brain_complexity(self, entity: Entity) -> None:
        mind = entity.brain.phenotype
        self.sum_links += mind.n_links
        self.sum_hidden += mind.n_hidden

        if mind.n_hidden > self.max_hidden:
            self.max_hidden = mind.n_hidden

        if mind.n_links > self.max_links:
            self.max_links = mind.n_links

    def update_brain_complexity(self) -> None:
        cycle = self.cycle

        self.brain_complexity.setdefault('nodes', {})
        self.brain_complexity.setdefault('links', {})
        self.brain_complexity['nodes'].setdefault('average', {})
        self.brain_complexity['nodes'].setdefault('maximum', {})
        self.brain_complexity['links'].setdefault('average', {})
        self.brain_complexity['links'].setdefault('maximum', {})
        self.brain_complexity['nodes']['maximum'][cycle] = self.max_hidden
        self.brain_complexity['links']['maximum'][cycle] = self.max_links
        self.brain_complexity['nodes']['average'][cycle] = self.avg_hidden
        self.brain_complexity['links']['average'][cycle] = self.avg_links

    def update_death_age(self) -> None:
        age_sum: int = 0
        count: int = 0
        max_death_age: int = 0

        cycle = self.cycle
        self.death_age.setdefault('average', {})
        self.death_age.setdefault('maximum', {})

        for entity in self.sim_state.removed_entities.values():
            if entity.__class__.__name__ == 'Animal':
                age_sum += entity.age
                count += 1
                if entity.age > max_death_age:
                    max_death_age = entity.age
        if count > 0:
            avg_death_age = age_sum / count
            self.death_age['average'][cycle] = avg_death_age
            self.death_age['maximum'][cycle] = max_death_age

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
            data.setdefault('cycles', []).append(self.cycle)
        if 'generations' in metrics:
            data.setdefault('generations', []).append(self.max_generation)
        if 'born_animals' in metrics:
            data.setdefault('born_animals', []).append(self.added_animals)

        with open(measure_file, "w+") as write_file:
            json.dump(existing_data, write_file, indent=4)

    def graph(self, **metrics) -> None:
        if 'population' in metrics:
            self.graph_population()
        if 'brain_complexity' in metrics:
            self.graph_brain_complexity()
        if 'actions_count' in metrics:
            self.graph_actions_count()
        if 'actions_overtime' in metrics:
            self.graph_actions_overtime()
        if 'death_age' in metrics:
            self.graph_death_age()

    def graph_population(self) -> None:
        plt.clf()
        data = self.population['animal']
        g = sns.lineplot(x=data.keys(), y=data.values())
        g.set_xlabel('Cycle')
        g.set_ylabel('Animal population')
        g.set_title('Population of animals over cycles')

        self.save_fig('population')


    def graph_brain_complexity(self) -> None:
        plt.clf()
        fig, axs = plt.subplots(nrows=2)
        data = self.brain_complexity
        g1 = sns.lineplot(x=data['nodes']['maximum'].keys(), y=data['nodes']['maximum'].values(), ax=axs[0])
        g2 = sns.lineplot(x=data['links']['maximum'].keys(), y=data['links']['maximum'].values(), ax=axs[1])
        sns.lineplot(x=data['nodes']['average'].keys(), y=data['nodes']['average'].values(), ax=axs[0])
        sns.lineplot(x=data['links']['average'].keys(), y=data['links']['average'].values(), ax=axs[1])
        fig.suptitle('Brain Complexity')
        plt.xlabel('Cycle')
        g1.set_ylabel('Nodes')
        g2.set_ylabel('Links')
        g1.legend(labels=['Maximum hidden nodes','Average hidden nodes'])
        g2.legend(labels=['Maximum links','Average links'])

        self.save_fig('brain_complexity')


    def graph_actions_count(self) -> None:
        plt.clf()
        data = {}
        for cycle in self.actions_count:
            for action in self.actions_count[cycle]:
                data[action] = data.get(action, 0) + self.actions_count[cycle][action]

        g = sns.barplot(x=list(data.keys()), y=list(data.values()), color='blue')
        g.bar_label(g.containers[0])
        g.set(yticklabels=[])
        g.set(ylabel=None)
        g.tick_params(left=False)
        g.set_xlabel('Actions')
        g.set_title('Count of each action')
        g.set_xticklabels(g.get_xticklabels(), rotation=45)

        self.save_fig('actions_count')


    def graph_actions_overtime(self) -> None:
        plt.clf()
 
        df = pd.DataFrame(data=self.actions,columns=['cycle','action'])
        g = sns.kdeplot(data=df,x='cycle',hue='action', multiple="fill", palette="bright")

        plt.title('Actions over time')
        plt.xlabel('Cycle')
        plt.ylabel('Action proportion(%)')
        self.save_fig('actions_overtime')


    def graph_death_age(self) -> None:
        plt.clf()
        data = self.death_age

        if data['maximum']:
            g1 = sns.lineplot(x=data['maximum'].keys(), y=data['maximum'].values())
        if data['average']:
            g2 = sns.lineplot(x=data['average'].keys(), y=data['average'].values())

        plt.legend(labels=['maximum age', 'average age'], title='Death age')
        plt.title('Age at death')
        plt.xlabel('Cycle')
        plt.ylabel('Age')
        self.save_fig('death_age')


    def save_fig(self, name: str) -> None:
        plt.savefig(f"graphs/{name}.png", bbox_inches = "tight")
        
    def print(self, all_keys: bool=False, **metrics) -> None:
        if 'cycles' in metrics or all_keys:
            print(f"SHUTDOWN after {self.cycle} cycles.")
        if 'generations' in metrics or all_keys:
            print(f"{self.max_generation} generations spawned.")
        if 'born_animals' in metrics or all_keys:
            print(f"{self.added_animals} animals were born.")
