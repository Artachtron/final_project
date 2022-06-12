from __future__ import annotations
import math
from numpy.random import uniform
from innovation import InnovTable
from functools import partial
import enum
from typing import Dict

class NodeType(enum.Enum):
    BIAS = 0
    INPUT = 1
    OUTPUT = 2
    HIDDEN = 3  
    
def sigmoid(x):
    """ Sigmoid activation function, Logistic activation with a range of 0 to 1
    
    Args:
        x (float): input value
        
    Returns:
        float: output value
    """
    try:
        return (1.0 / (1.0 + math.exp(-x)))
    except OverflowError:
        return 0 if x < 0 else 1


def relu(x):
    """ ReLu activation function, Limits the lower range of the input to 0
    Args:
        x (float): input value
        
    Returns:
        float: output value
    """
    return max(0, x)
    
class ActivationFuncType(enum.Enum):
    SIGMOID = partial(sigmoid)
    RELU = partial(relu)

class AggregationFuncType(enum.Enum):
    SUM = sum

class BaseGene:
    def __init__(self,
                 gene_id: int,
                 mutation_number: int,
                 enable: bool,
                 freeze: bool,):
    
        self.id: int = gene_id
        self.frozen: bool = freeze
        self.enabled: bool = enable
        self.mutation_number: int = mutation_number
        
    def __lt__(self, other) -> bool:
        return self.id < other.id
       
    def transcript(self):
        raise NotImplementedError("Please Implement the transcription method")
        
    def mutation_distance(self, other_gene: BaseGene) -> float:
        return abs(self.mutation_number -
                    other_gene.mutation_number)
        
     
class LinkGene(BaseGene):
    def __init__(self,
                 in_node: int,
                 out_node: int,
                 weight: float = 0.0,
                 mutation_number: int = 0,
                 link_id: int = 0,
                 enable: bool = True,
                 freeze: bool = False,
                 ):
        
        link_id = link_id or InnovTable.get_link_number(increment=True)
        
        super(LinkGene, self).__init__(gene_id=link_id,
                                       mutation_number=mutation_number,
                                       enable=enable,
                                       freeze=freeze)
        
        self.in_node: int = in_node
        self.out_node: int = out_node
        self.weight: float = weight or uniform(-1,1)
        
        self.mutation_number: int = mutation_number
        
    def transcript(self) -> Dict:
        """ Return a dictionary containing the LinkGene's 
            information to synthesize a Link

        Returns:
            Dict: dictionary of LinkGene's information
        """        
        return {'link_id':self.id, 'weight':self.weight,
                'in_node':self.in_node, 'out_node':self.out_node,
                 'enabled':self.enabled}
        
    def mutate(self, reset_weight: bool, mutate_power: float) -> None:
        if self.frozen: return
        
        if reset_weight:
            self.weight = uniform(-1,1)
        else:
            self.weight += uniform(-1,1) * mutate_power
            
        self.mutation_number = self.weight

        
class NodeGene(BaseGene):
    def __init__(self,
                 node_id: int = 0,
                 mutation_number: int = 0,
                 node_type: NodeType = NodeType.HIDDEN,
                 bias: float = 0.0,
                 activation_function: ActivationFuncType=ActivationFuncType.SIGMOID,
                 aggregation_function: AggregationFuncType=AggregationFuncType.SUM,
                 enable: bool = True,
                 freeze: bool = False,):
        
        super(NodeGene, self).__init__(gene_id=node_id,
                                       mutation_number=mutation_number,
                                       enable=enable,
                                       freeze=freeze)

        
        self.id: int = node_id or InnovTable.get_node_number(increment=True)
                
        self.type: NodeType = node_type     # HIDDEN, INPUT, OUTPUT, BIAS
       
        self.bias: float = bias or uniform(-1,1)
        self.activation_function: ActivationFuncType = activation_function 
        self.aggregation_function: AggregationFuncType = aggregation_function
            
        #self.incoming: Dict[int, Link] = {}                          # A list of pointers to incoming weighted signals from other nodes
        #self.outgoing: Dict[int, Link] = {}                         #  A list of pointers to links carrying this node's signal

    def transcript(self) -> Dict:
        """ Return a dictionary containing the NodeGene's 
            information to synthesize a Node

        Returns:
            Dict: dictionary of NodeGene's information
        """        
        return {'node_id':self.id, 'node_type':self.type,
                'activation_function':self.activation_function,
                'aggregation_function':self.aggregation_function,
                'enabled':self.enabled}
        
    def distance(self, other_node: NodeGene) -> float:
        distance = abs(self.bias - other_node.bias)
        distance += int(self.activation_function != other_node.activation_function)
        distance += int(self.aggregation_function != other_node.aggregation_function)
        
        return distance
    
def reset_innovation_table():
    InnovTable.reset_innovation_table()

""" class Gene:
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
        
        self.innovation_number: int = innovation_number or InnovTable.get_innovation_number(increment=True)
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
                    recurrence= gene.link.is_recurrent) """
                    