from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from ..probe import Probe

import json
from dataclasses import dataclass
from os.path import dirname, join, realpath
from pathlib import Path
from statistics import mean

import pandas as pd

from ..probe import Probe


def parameters_tuning():
    directory = join(
            Path(
                dirname(
                    realpath(__file__))).parent.parent.parent.absolute(),
            "measurements/")
    measure_file = join(directory, 'measurements.json')
    data = json.load(open(measure_file))

    best_params = {}
    
    cycle_coeff = 1
    generation_coeff = 3
    birth_coeff = 2

    for param in data:

        variations = {}
        for var in data[param]:
            params = {}
            columns = list(data[param][var].keys())
            for col, metric in zip(columns, data[param][var]):
                data[param][var][metric] = mean(data[param][var][metric])

                params[col] = (data[param][var][metric])

            variations[var] = params
        # print(variations)
        df = pd.DataFrame(data=variations).T
        for col in columns:
            df[f'rank_{col}'] = df[col].rank(ascending=True)

        df['rank_total'] = df['rank_cycles']*cycle_coeff + df['rank_generations']*generation_coeff + df['rank_born_animals']*birth_coeff
        df.sort_values(by=['rank_total'], inplace=True, ascending=False)
        print(param)
        print(df)
        best_params[param] = df.iloc[0].name
    
    for best in best_params:
        print(f"{best}: {best_params[best]}")
        
@dataclass 
class Evaluator: 
    probe: Probe
    
    def evaluate(self):
        print(self.evaluate_trade())
        print(self.evaluate_replant())

    def evaluate_trade(self) -> Tuple[int, int]:
        trade_count: int = 0
        max_trade_count: int = 0
        entities = self.probe.all_entities.values()
        for entity in entities:
            for partner in entity.trade_partners:
                if entity.id in entities[partner].trade_partners:
                    trade_value = entity.trade_partners[partner]
                    trade_count += trade_value
                    if trade_value > max_trade_count:
                        max_trade_count = trade_value

        return trade_count, max_trade_count
    
    def evaluate_replant(self) -> Tuple[int,int]:
        sum_replant: int = 0
        max_replant: int = 0
        for replant_times in self.probe.replant.values():
            sum_replant += replant_times
            if replant_times > max_replant:
                max_replant = replant_times
        
        avg_replant = sum_replant/len(self.probe.replant)
        return avg_replant, max_replant
            
        

        
""" animal_sparsity = [1, 2, 3, 4, 5]

initial_size = [5, 10, 20, 50, 100]
initial_action_cost = [0, 1, 2, 3, 4, 5]
max_age_size_coeff = [1, 5, 10, 100]
growth_energy_required = [1, 5, 10, 100]
child_energy_cost_divisor = [1, 2, 5, 10]

init_adult_size = [1, 5, 10, 100]
init_blue_energy = [100, 1000, 10000, 100000]
init_red_energy = [100, 1000, 10000, 100000]
reproduction_cost = [1, 2, 3]
planting_cost = [1, 5, 10]

animal_sparsity = 3
initial_size = 5
initial_action_cost = 0
max_age_size_coeff = 10
growth_energy_required = 5
child_energy_cost_divisor = 10
init_adult_size = 5
animal_init_blue_energy = 1000
animal_red_energy  = 10000
reproduction_cost = 1
planting_cost = 10
tree_init_blue_energy = 1000
tree_init_red_energy = 1000 """


if __name__ == '__main__':
    main()
