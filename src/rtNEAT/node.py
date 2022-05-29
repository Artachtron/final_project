import numpy as np
import enum


from pytest import param

class NodeType(enum.Enum):
    NEURON = 0
    SENSOR = 1
    
class FuncType(enum.Enum):
    SIGMOID = 0
    
class NodePlace(enum.Enum):
    HIDDEN = 0
    INPUT = 1
    OUTPUT = 2
    BIAS = 3

class Node:
    def __init__(self,
                  node_type: NodeType,
                  node_id: int,
                  node_place: NodePlace = NodePlace.HIDDEN.value,
                  ):
        self.active_flag: bool = False # To make sure outputs are active
        self.activesum: float = 0.0 # The incoming activity before being processed
        self.activation: float = 0.0 # The total activation entering the Node
        self.output: float = 0.0 # Output of the Node- the value in the Node
        self.last_activation: float = 0.0 # Holds the previous step's activation for recurrency
        self.last_activation2: float = 0.0 # Holds the activation BEFORE the prevous step's
        self._type: NodeType = node_type # NEURON or SENSOR
        self.activation_count: int = 0 # Keeps track of which activation the node is currently in
        self.id: int = node_id
        self.ftype:FuncType = FuncType.SIGMOID
        """ self.trait: Trait = 0 # Points to a trait of parameters
        self.trait_id: int = 1 # Identify the trait derived by this node """
        self.gen_node_label: NodePlace = node_place # Used for genetic marking of nodes
        self.dup: Node = 0 # Used for Genome duplication
        self.analogue: Node = 0 # Used for Gene decoding
        self.frozen: bool = False # When frozen, cannot be mutated (meaning its trait pointer is fixed)
        self.override: bool = False # The Node cannot compute its own output- something is overriding it
        self.override_value: float = 0.0 # Contains the activation value that will override this node's activation

        
        @property
        def type(self):
            return self._type
        
        @type.setter
        def type(self, new_type):
            self._type = new_type
            
        def get_analogue(self) -> Node:
            """Returns the gene that created the node

            Returns:
                Node: gene
            """            
            return self.analogue
        
        def override_output(self, new_output: float) -> None:
            """Force an output value on the node

            Args:
                new_output (float): value to override the output
            """            
            self.override_value = new_output
            self.override = True
            
        def overridden(self) -> None:
            """Tell whether node has been overridden
            """        
            return self.override
        
        def activate_override(self) -> None:
            """Set activation to the override value and turn off override
            """ 
            self.activation = self.override_value
            self.override = False
                
        def sensor_load(self, value: float) -> bool:
            """Add an incoming connection a node

            Args:
                value (float): _description_

            Returns:
                bool: _description_
            """            
            if self.type == NodeType.SENSOR:
                #Time delay memory
                self.last_activation2 = self.last_activation
                self.last_activation = self.activation

                self.activation_count+=1  #Puts sensor into next time-step
                self.activation=value
                return True
            else:
                return False
            
        def add_incoming(self, feednode: Node, weight: float, recur: bool) -> None:          
            new_link: Link = Link(weight, feednode, self, recur)
            incoming += new_link
            feednode.outgoing += new_link
                
        
        def add_incoming(self, feednode: Node, weight: float) -> None:          
            new_link: Link = Link(weight, feednode, self, False)
            incoming += new_link
            feednode.outgoing += new_link
            
        def get_active_out(self) -> float:
            """Return activation currently in node, if it has been activated

            Returns:
                float: activation currently in node
            """            
            if self.activation_count > 0:
                return self.activation
            else:
                return 0.0
            
        # Return activation currently in node from PREVIOUS (time-delayed) time step,
        # if there is one
        def get_active_out_td() -> float:
            if (self.activation_count>1):
                return self.last_activation
            else:
                return 0.0
        
        # This recursively flushes everything leading into and including this Node, including recurrencies    
        def flush_back(self) -> None:            
            # A sensor should not flush black
            if self.type != NodeType.SENSOR:
                if self.activation_count > 0:
                    self.flush()
                    
            # Flush back recursively
            for curlink in incoming:
                # Flush the link itself (For future learning parameters possibility
                if curlink.in_node.activation_count > 0:
                    curlink.in_node.flushback()
            
            else:
                # Flush the sensor
                self.flush()
                
        def flush(self):
            self.activation_count = 0
            self.activation = 0
            self.last_activation = 0
            self.last_activation2 = 0
            
    # This recursively checks everything leading into and including this NNode, 
    # including recurrencies
    # Useful for debugging
    def flushback_check(self, seen_list: np.array):
        innodes = np.array([], dtype=Link)
                
        if self.type == NodeType.SENSOR:
            if self.activation_count > 0:
                print(f"ALERT: {self} has activation count {self.activation_count}")
            if self.activation > 0:
                print(f"ALERT: {self} has activation {self.activation}")
            if self.last_activation > 0:
                print(f"ALERT: {self} has last activation {self.last_activation}")
            if self.last_activation2 > 0:
                print(f"ALERT: {self} has last activation2 {self.last_activation2}")
                
            for curlink in innodes:
                location = np.where(seen_list==curlink.in_node)
                if location == seen_list.size:
                    seen_list.append(curlink.in_node)
                    curlink.in_node.flushback_check(seen_list)
                    
        else:
            # Flush chek the SENSOR
            if self.type == NodeType.SENSOR:
                if self.activation_count > 0:
                    print(f"ALERT: {self} has activation count {self.activation_count}")
                if self.activation > 0:
                    print(f"ALERT: {self} has activation {self.activation}")
                if self.last_activation > 0:
                    print(f"ALERT: {self} has last activation {self.last_activation}")
                if self.last_activation2 > 0:
                    print(f"ALERT: {self} has last activation2 {self.last_activation2}")