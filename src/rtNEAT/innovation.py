import enum

class InnovationType(enum.Enum):
    NEWNODE = 0
    NEWLINK = 1

class Innovation:
    def __init__(self,
                 node_in_id: int,
                 node_out_id: int,
                 innovation_type: InnovationType,
                 innovation_number1: int,
                 innovation_number2: int=0,
                 old_innovation_number: int = 0,
                 new_node_id: int=0,
                 new_weight: float=0.0,
                 recurrence: bool=False
                 ):
        
        self.innovation_type: InnovationType = innovation_type # Either NEWNODE or NEWLINK
        self.node_in: int = node_in_id # Two nodes specify where the innovation took place
        self.node_out: int = node_out_id
        self.innovation_number1: int = innovation_number1 # The number assigned to the innovation
        self.innovation_number2: int = innovation_number2 # If this is a new node innovation, then there are 2 innovations (links) added for the new node 
        self.weight: float = new_weight # If a link is added, this is its weight  
        
        self.new_node_id: int = new_node_id # If a new node was created, this is its node_id 
        self.old_innovation_number: int = old_innovation_number # If a new node was created, this is the innovnum of the gene's link it is being stuck inside 
        self.recurrence_flag: bool = recurrence