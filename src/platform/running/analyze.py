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
        print(self.evaluate_colors())

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
    
    def evaluate_colors(self):
        colors = self.probe.colors
        count_color = len(colors)
        max_color = max(list(colors.values()))
      
        return count_color, max_color

if __name__ == '__main__':
    main()
