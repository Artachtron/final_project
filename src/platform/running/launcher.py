import os
from os import listdir
from os.path import dirname, isfile, join, realpath
from pathlib import Path

directory = join(
            Path(
                dirname(
                    realpath(__file__))).parent.parent.parent.absolute(),
            "configuration/")

files = [f for f in listdir(directory) if isfile(join(directory, f))]
files = [f.split(".")[0] for f in files]
combinations = [tuple(f.split("_")[1:]) for f in files]

for param, comb in combinations:
    print(param)
#os.system("python -m src.platform.running.main --c config_1.json")
