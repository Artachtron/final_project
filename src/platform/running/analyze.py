import json
from os.path import dirname, join, realpath
from pathlib import Path
from statistics import mean

import pandas as pd


def main():
    directory = join(
            Path(
                dirname(
                    realpath(__file__))).parent.parent.parent.absolute(),
            "measurements/")
    measure_file = join(directory, 'measurements.json')
    data = json.load(open(measure_file))

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
        print(df.head())

                
if __name__ == '__main__':
    main()
