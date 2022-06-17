from __future__ import annotations
    
 
from project.src.rtNEAT.genome import Genome
from project.src.rtNEAT.network import Network
from project.src.simulation.universal import EntityType

class Organism:
    def __init__(self,
                 organism_id: int = 0,
                 generation: int = 0,
                 entity_type: str = EntityType.Animal.value):
                
        self.__id = organism_id 
        self.entity_type = entity_type
        self.genotype: Genome 
        self.mind: Network
                
        self.species: int = 0
        self.genaration: int = generation
        
        self.genesis()
                    
    def genesis(self) -> Organism:
        NUM_ANIMAL_INPUTS = 96
        NUM_ANIMAL_OUTPUTS = 12
        
        match self.entity_type:
            case EntityType.Animal.value:
                n_inputs = NUM_ANIMAL_INPUTS
                n_outputs = NUM_ANIMAL_OUTPUTS
        
        self.genotype = Genome.genesis( genome_id=self.id,
                                        n_inputs=n_inputs,
                                        n_outputs=n_outputs)
        
        self.mind = Network.genesis(self.genotype)
        
    @property
    def id(self):
        return self.__id
        
           
     