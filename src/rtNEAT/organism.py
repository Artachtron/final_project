from __future__ import annotations
from genome import Genome
from network import Network

class Organism:
    def __init__(self,
                 genome: Genome,
                 generation: int):
        self.genome: Genome = genome # The Organism's genotype 
        self.network: Network = genome.phenotype
        self.species: int = 0 # The Organism's Species 
        self.genaration: int = generation # Tells which generation this Organism is from
 
    def update_phenotype(self) -> Organism:
        self.network = self.genome.genesis(network_id=self.genome.id)