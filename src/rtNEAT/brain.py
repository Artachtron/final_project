from __future__ import annotations
    
 
from project.src.rtNEAT.genome import Genome
from project.src.rtNEAT.network import Network

class Brain:
    def __init__(self,
                 brain_id: int = 0):
                
        self.__id = brain_id 
        self.genotype: Genome 
        self.phenotype: Network
                
      
    @classmethod              
    def genesis(cls, brain_id: int, n_inputs: int, n_outputs: int) -> Brain:  
        """Class method:
            Create a brain with genotype and phenotype for the given entity type

        Args:
            brain_id (int):     id of the entity
            n_inputs (int):     number of inputs of the brain
            n_outputs (int):    number of outputs of the brain

        Returns:
            Brain: created brain
        """        
     
        brain = cls(brain_id=brain_id)
        
        # Create the genome
        brain.genotype = Genome.genesis(genome_id=brain_id,
                                        n_inputs=n_inputs,
                                        n_outputs=n_outputs)
        
        # Create the phenotype from the genome
        brain.phenotype = Network.genesis(genome=brain.genotype)
        
        return brain
    
    @classmethod
    def crossover(cls, brain_id: int,  parent1: Brain, parent2: Brain) -> Brain:
        """Class method:
            Crossover two parents brain into a new brain,
            apply mutation to the new genome before creating its phenotype

        Args:
            brain_id (int):     baby's id
            parent1 (Brain):    first parent's brain
            parent2 (Brain):    second parent's brain

        Returns:
            Brain: baby's brain
        """        
        brain = cls(brain_id=brain_id)
        
        genome = Genome.crossover(genome_id=brain_id,
                                  parent1=parent1.genotype,
                                  parent2=parent2.genotype)
        
        genome.mutate()
        
        brain.genotype = genome
        
        brain.phenotype = Network.genesis(genome=brain.genotype)
        
        return brain
        
    @property
    def id(self):
        return self.__id
        
           
     