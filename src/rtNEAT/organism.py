from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from project.src.simulation.entities import Entity
    
from typing import Tuple
  
from genome import Genome
from network import Network

from project.src.simulation.simulation import SimulatedObject

from project.src.simulation.config import WorldTable


class Organism(SimulatedObject):
    def __init__(self,
                 position: Tuple[int, int] =(-1, -1),
                 organism_id: int = 0,
                 generation: int = 0):
        
        super(Organism, self).__init__(sim_body_id=organism_id,
                                       position=position)
        
        self.id = organism_id or WorldTable.get_organism_id
        self.genotype: Genome # The Organism's genotype 
        self.mind: Network
        self.body: Entity
                
        self.species: int = 0 # The Organism's Species 
        self.genaration: int = generation # Tells which generation this Organism is from
        
        self.genesis()
                
    def genesis(self) -> Organism:
        NUM_INPUTS = 96
        NUM_OUTPUTS = 12
        
        self.genotype = Genome.genesis( genome_id=self.id,
                                        n_inputs=NUM_INPUTS,
                                        n_outputs=NUM_OUTPUTS)
        
        self.mind = Network.genesis(self.genotype)
        

                   
     