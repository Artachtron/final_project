from __future__ import annotations
    
 
from project.src.rtNEAT.genome import Genome
from project.src.rtNEAT.network import Network
from project.src.simulation.universal import EntityType

class Brain:
    def __init__(self,
                 brain_id: int = 0,
                 entity_type: str = EntityType.Animal.value):
                
        self.__id = brain_id 
        self.entity_type = entity_type
        self.genotype: Genome 
        self.phenotype: Network
                
      
    @classmethod              
    def genesis(cls, brain_id: int, entity_type: EntityType) -> Brain:
        NUM_ANIMAL_INPUTS = 96
        NUM_ANIMAL_OUTPUTS = 12
        
        match entity_type:
            case EntityType.Animal.value:
                n_inputs = NUM_ANIMAL_INPUTS
                n_outputs = NUM_ANIMAL_OUTPUTS
        
        brain = cls(brain_id=brain_id,
                    entity_type=entity_type)
        
        brain.genotype = Genome.genesis(genome_id=brain_id,
                                        n_inputs=n_inputs,
                                        n_outputs=n_outputs)
        
        brain.phenotype = Network.genesis(genome=brain.genotype)
        
        return brain
    
    @classmethod
    def reproduce(cls, brain_id: int,  parent1: Brain, parent2: Brain):
        brain = cls(brain_id=brain_id,
                    entity_type=parent1.entity_type)
        
        brain.genotype = Genome.reproduce(parent1=parent1.genotype,
                                          parent2=parent2.genotype)
        
        brain.phenotype = Network.genesis(genome=brain.phenotype)
        
        return brain
        
    @property
    def id(self):
        return self.__id
        
           
     