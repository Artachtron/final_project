from __future__ import annotations
from node import Node
from link import Link
from numpy.random import uniform
from innovation import InnovTable

class Gene:
    def __init__(self,
                 in_node: Node,
                 out_node: Node,
                 innovation_number: int=None,
                 weight: float=None,
                 mutation_number: int=0,
                 recurrence: bool=False):
        
        weight = weight or uniform(-1,1)
              
        self.link = Link(   weight=weight,
                            in_node=in_node,
                            out_node=out_node,
                            recurrence=recurrence)
        
        self.innovation_number: int = innovation_number or InnovTable.get_innovation_number()
        self.mutation_number: int = mutation_number # Used to see how much mutation has changed the link
        self.enabled: bool = True # When this is off the Gene is disabled
        self.frozen: bool = False # When frozen, the linkweight cannot be mutated
     
    @classmethod   
    def constructor_from_gene(cls, gene: Gene, in_node: Node, out_node: Node):
        return Gene(weight=gene.link.weight,
                    in_node=in_node,
                    out_node=out_node,
                    innovation_number=gene.innovation_number,
                    mutation_number=gene.mutation_number,
                    recurrence= gene.link.is_recurrent)
                    