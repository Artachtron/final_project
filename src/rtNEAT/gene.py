from node import Node
from link import Link

class Gene:
    def __init__(self,
                 weight: float,
                 in_node: Node,
                 out_node: Node,
                 recurrence: bool,
                 innovation_number: int,
                 mutation_number: int):
        
        self.link = Link(weight=weight,
                    in_node=in_node,
                    out_node=out_node,
                    recurrence=recurrence)
        
        self.innovation_number: int = innovation_number
        self.mutation_number: int = mutation_number # Used to see how much mutation has changed the link
        self.enable: bool = True # When this is off the Gene is disabled
        self.frozen: bool = False # When frozen, the linkweight cannot be mutated