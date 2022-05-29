from node import Node

class Link:
    def __init__(self,
                 weight: float,
                 in_node: Node,
                 out_node: Node,
                 reccurence: bool):
        
        self.weight: float = weight # Weight of connection
        self.in_node: Node = in_node # Node inputting into the link
        self.out_node: Node = out_node # Node that the link affects
        self.is_recurrent: bool = reccurence
        self.added_weight = 0 # The amount of weight adjustment 
        self.time_delay: bool = False
        """ self.link_trait = 0
        self.trait_id = 1 """
        