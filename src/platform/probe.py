from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from simulation import SimState
    from entities import Entity

import json
import pickle
from collections import namedtuple
from dataclasses import dataclass, field
from os.path import dirname, join, realpath
from pathlib import Path

import matplotlib.pyplot as plt
import numpy.typing as npt
import pandas as pd
import seaborn as sns

Entity = namedtuple("Entity",["id","type","size", "position"])
Energy = namedtuple("Energy",["id","type","size", "position"])

@dataclass
class Frame:
    entities: List[Entity]
    energies: List[Energy]
    cells: npt.NDArray

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
    total_actions_count: Dict = field(default_factory=dict)

    brain_complexity: Dict = field(default_factory=dict)
    death_age: Dict = field(default_factory=dict)
    energy_gain: Dict = field(default_factory=dict)

    max_hidden: int = 0
    max_links: int = 0

    actions: Dict = field(default_factory=list)
    
    frames: List[Frame] = field(default_factory=list)
    
    all_animals: Dict = field(default_factory=dict)
    all_trees: Dict = field(default_factory=dict)
    
    replant: Dict =  field(default_factory=dict)
    colors: Dict =  field(default_factory=dict)
    colors_cycle: Dict =  field(default_factory=dict)

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
    
    @property
    def all_entities(self) -> Dict:
        return self.all_animals | self.all_trees

    def update(self, cells) -> None:
        self.save_frame(cells=cells)
        
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
        self.update_on_death()
        
        # self.register_entities()

    def save_frame(self, cells):
        state = self.sim_state
        entities = [Entity(entity.id, entity.__class__.__name__, entity.size, entity.position) for entity in state.get_entities()]
        energies = [Energy(energy.id, energy.__class__.__name__, energy.size, energy.position) for energy in state.get_resources()]

        self.frames.append(Frame(entities=entities,
                                 energies=energies,
                                 cells=cells))
        
    def pickle_frames(self, sim_name:str = "sim"):
        pickle.dump(self.frames, open(f'simulations/frames/{sim_name}_frames', "wb"))

    def register_entities(self):
        for key, entity in self.sim_state.removed_entities.items():
            if entity.__class__.__name__ == 'Animal':
                self.all_animals[key] = entity
            elif entity.__class__.__name__ == 'Tree':
                self.all_trees[key] = entity

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

        if hasattr(entity, 'actions'):
            for action in entity.actions:
                action_type = action.action_type.value
                if action_type == 'paint':
                    self.update_colors(action)
                self.actions_count[cycle][action_type] = self.actions_count[cycle].get(action_type, 0) + 1
                self.actions.append((cycle, action_type))
                self.total_actions_count[action_type] = self.total_actions_count.get(action_type, 0) + 1

    def update_colors(self, action):
        color = action.color
        cycle = self.cycle
        self.colors_cycle.setdefault(cycle, {})
        self.colors[color] = self.colors.get(color, 0) + 1
        self.colors_cycle[color] = self.colors.get(color, 0) + 1
        
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

    def update_on_death(self) -> None:
        age_sum: int = 0
        energy_gain_sum: int = 0
        count: int = 0
        max_death_age: int = 0
        max_energy_gain: int = 0

        cycle = self.cycle
        self.death_age.setdefault('average', {})
        self.death_age.setdefault('maximum', {})
        self.energy_gain.setdefault('average', {})
        self.energy_gain.setdefault('maximum', {})

        for entity in self.sim_state.removed_entities.values():
            if entity.__class__.__name__ == 'Animal':
                age_sum += entity.age
                energy_gain_sum += entity.gained_energy
                count += 1
                if entity.age > max_death_age:
                    max_death_age = entity.age
                if entity.gained_energy > max_energy_gain:
                    max_energy_gain = entity.gained_energy
                    
            elif entity.__class__.__name__ == 'Tree':
                self.replant[entity.id] = entity.planted_times       
            
        if count > 0:
            avg_death_age = age_sum / count
            self.death_age['average'][cycle] = avg_death_age
            self.death_age['maximum'][cycle] = max_death_age
            avg_energy_gain = energy_gain_sum / count
            self.energy_gain['average'][cycle] = avg_energy_gain
            self.energy_gain['maximum'][cycle] = max_energy_gain

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
        if 'energy_gain' in metrics:
            self.graph_energy_gain()

    def graph_population(self) -> None:
        plt.clf()
        data = self.population['animal']
        sns.lineplot(x=data.keys(), y=data.values())
        data = self.population['tree']
        g = sns.lineplot(x=data.keys(), y=data.values())
        g.set_xlabel('Cycle')
        g.set_ylabel('Population')
        g.set_title('Population over cycles')
        plt.legend(labels=['Animals', 'Trees'])

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
        data = self.total_actions_count

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
        sns.move_legend(g, title='Actions', loc='center left', bbox_to_anchor=(1, 0.5))
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
        
    def graph_energy_gain(self) -> None:
        plt.clf()
        data = self.energy_gain

        if data['maximum']:
            g1 = sns.lineplot(x=data['maximum'].keys(), y=data['maximum'].values())
        if data['average']:
            g2 = sns.lineplot(x=data['average'].keys(), y=data['average'].values())

        plt.legend(labels=['maximum energy', 'average energy'], title='Energy gained')
        plt.title('Energy gained through lifetime')
        plt.xlabel('Cycle')
        plt.ylabel('Energy gained')
        self.save_fig('energy_gain')


    def save_fig(self, name: str) -> None:
        plt.savefig(f"graphs/{name}.png", bbox_inches = "tight")
        
    def print(self, all_keys: bool=False, **metrics) -> None:
        if 'cycles' in metrics or all_keys:
            print(f"SHUTDOWN after {self.cycle} cycles.")
        if 'generations' in metrics or all_keys:
            print(f"{self.max_generation} generations spawned.")
        if 'born_animals' in metrics or all_keys:
            print(f"{self.added_animals} animals were born.")
        if 'actions_count' in metrics or all_keys:
            print(self.total_actions_count)    
        
    def print_actions_count(self):
        data = {}
        for cycle in self.actions_count:
            for action in self.actions_count[cycle]:
                data[action] = data.get(action, 0) + self.actions_count[cycle][action]
        
        print(data)
    
    @staticmethod
    def graph_from_file(file_path: str):
        file_path = "H:\\UoL\\Semester 5\\Code\\project\\measurements\\measurements.json"
        data = json.load(open(file_path, encoding="utf-8"))

        metrics = set()

        frame = []
        for param in list(data.keys())[:1]:
            
            fig, axs = plt.subplots(nrows=3, figsize=(5,10), sharex=True, constrained_layout=True)
            fig.suptitle(param, fontsize=16)
            for var in data[param]:
                for metric in data[param][var]:
                    metrics.add(metric)
                    values = data[param][var][metric]
                    for val in values:
                        frame.append((param, var, metric, val))
                        
            df = pd.DataFrame(data=frame, columns=['parameter', 'variation', 'metrics', 'value'])           
            frame = []  
            for i, metric in enumerate(metrics):
                df_m = df[df['metrics'] == metric]   
                g = sns.boxplot(data=df_m, x='variation', y='value', ax=axs[i])
                g.set_title(metric)
                g.set_xlabel('')
            plt.xlabel("variation")
