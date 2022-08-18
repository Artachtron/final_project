from __future__ import annotations

from typing import Any, Dict

from .genome import Genome
from .network import Network


class Brain:
    def __init__(self,
                 brain_id: int = 0):

        self.__id = brain_id
        self.genotype: Genome
        self.phenotype: Network


    @classmethod
    def genesis(cls, brain_id: int, genome_data: Dict[str, Any]) -> Brain:
        """Class method:
            Create a brain with genotype and phenotype for the given entity type

        Args:
            brain_id (int):                 id of the entity
            genome_data (Dict[str, Any]):   contain the brain's genome information

        Returns:
            Brain: created brain
        """

        brain = cls(brain_id=brain_id)

        # Create the genome
        brain.genotype = Genome.genesis(genome_id=brain_id,
                                        genome_data=genome_data)

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

        genome.crossover_mutate()

        brain.genotype = genome

        brain.phenotype = Network.genesis(genome=brain.genotype)

        return brain

    @property
    def id(self):
        return self.__id


