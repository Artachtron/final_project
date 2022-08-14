import os
import subprocess
import sys
from os import listdir
from os.path import dirname, isfile, join, realpath
from pathlib import Path

directory = join(
            Path(
                dirname(
                    realpath(__file__))).parent.parent.parent.absolute(),
            "configuration/")

files = [f for f in listdir(directory) if isfile(join(directory, f))]
""" files_info = [f.split(".")[0] for f in files]
combinations = [tuple(f.split("_")[1:]) for f in files_info]

for param, comb in combinations:
    pass """
for n, f in enumerate(files):
    for i in range(0, 5):
        print(f"{n} file: {f} {i}")
        os.system(f"python -m src.platform.running.main --c {f}")
#subprocess.call([sys.executable, 'src/platform/running/main.py', '--c config_A_1.json'])
#subprocess.run("python -m src.platform.running.main --c config_A_1.json",env={"PATH": "H:/UoL/Semester 5/Code/final-project"})
