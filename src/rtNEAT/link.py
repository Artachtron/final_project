from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from node import Node

class Link:
    def __init__(self,
                 weight: float,
                 in_node: Node,
                 out_node: Node,
                 enabled: bool = True,
                 recurrence: bool=False):
        
        self.weight: float = weight # Weight of connection
        self.in_node: Node = in_node # Node inputting into the link
        self.out_node: Node = out_node # Node that the link affects
        self.is_recurrent: bool = recurrence
        self.enabled: bool = enabled
        self.added_weight: float = 0.0 # The amount of weight adjustment 
        self.time_delay: bool = False
        """ self.link_trait = 0
        self.trait_id = 1 """
        