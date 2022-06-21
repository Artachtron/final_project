from __future__ import annotations
from abc import abstractmethod
import math
from numpy.random import uniform, random

from functools import partial
import enum

from project.src.rtNEAT.innovation import InnovTable
from project.src.rtNEAT.neat import Config
Config.configure()

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
                 enabled: bool,
                 frozen: bool,):
    
        self.__id: int = gene_id                        # unique (per genome) identifier corresponding to innovation number
        self.frozen: bool = frozen                      # if the gene can be mutated
        self.enabled: bool = enabled                    # if the phene will participate in the activation calculation
        self.mutation_number: int = mutation_number     # allow to calculate distance between two genes with the same innovation number
        
    @property
    def id(self):
        return self.__id
        
    def __lt__(self, other: BaseGene) -> bool:
        """Compare two instances of genes by id

        Args:
            other (BaseGene): the other gene with which to compare

        Returns:
            bool: if the current gene's id is less than the other
        """        
        return self.id < other.id
       
    @abstractmethod
    def transcript(self) -> Dict:
        """Send information about gene

        Raises:
            NotImplementedError: the method need to be implemented for each type of gene
        
        Returns: 
            Dict: dictionary with the information about the gene
        """        
        raise NotImplementedError("Please implement the transcription method")
    
    @abstractmethod
    def mutate(self) -> None:
        """Mutate the gene

        Raises:
            NotImplementedError: the method need to be implemented for each type of gene
        """        
        raise NotImplementedError("Please implement the mutate method")
    
    @abstractmethod
    def duplicate(self) -> BaseGene:
        """Create a copy of the gene

        Raises:
            NotImplementedError: the method need to be implemented for each type of gene
            
        Returns:
            BaseGene: Copy of the gene
        """        
        raise NotImplementedError("Please implement the duplicate method")
    
    @abstractmethod
    def is_allele(self, other_gene: BaseGene) -> bool:
        """Check if two genes are different versions of the same allele

        Args:
            other_gene (BaseGene): other gene to compare with
            
        Raises:
            NotImplementedError: the method need to be implemented for each type of gene
        
        Returns:
            bool: True if the two genes are the same allele
        """              
        raise NotImplementedError("Please implement the is allele method")
    
    @abstractmethod 
    def mutation_distance(self, other_gene: BaseGene) -> float:
        """Calculate the mutation distance between two genes

        Args:
            other_gene (BaseGene): other gene to compare with

        Returns:
            float: calculated distance
        """        
        return abs(self.mutation_number -
                    other_gene.mutation_number)
        
     
class LinkGene(BaseGene):
    def __init__(self,
                 in_node: int,
                 out_node: int,
                 weight: float = 0.0,
                 mutation_number: int = 0,
                 link_id: int = 0,
                 enabled: bool = True,
                 frozen: bool = False,
                 ):
        
        # If no id is given, check the next link number 
        link_id = link_id or InnovTable.get_link_number(increment=True)  
        
        super(LinkGene, self).__init__(gene_id=link_id,
                                       mutation_number=mutation_number,
                                       enabled=enabled,
                                       frozen=frozen)
        
        self.in_node: int = in_node                     # node sending the incoming signal
        self.out_node: int = out_node                   # node sending the outgoing signal
        self.weight: float = weight or uniform(-1,1)    # weight of the connection
                
    def transcript(self) -> Dict:
        """Return a dictionary containing the LinkGene's 
           information to synthesize a Link

        Returns:
            Dict: dictionary of LinkGene's information
        """        
        return {'link_id':self.id, 'weight':self.weight,
                'in_node':self.in_node, 'out_node':self.out_node,
                 'enabled':self.enabled}
        
    def mutate(self) -> None:
        """Mutate the LinkGene
        """       
        # if frozen can't be mutated 
        if self.frozen: return
        
        # link is being reset
        if random() < Config.new_link_prob:
            self.weight = uniform(-1,1)
        # value is being added to current weight
        else:
            self.weight += uniform(-1,1) * Config.weight_mutate_power
            
            # associate new weight to mutation number
            self.mutation_number = self.weight
        
        # disable the link
        if random() < Config.disable_prob:
            self.disabled = True
        # enable the link
        elif random() < Config.enable_prob:
            self.enabled = True      
        
    def duplicate(self) -> LinkGene:
        """Create a copy of this LinkGene

        Returns:
            LinkGene: copy of this LinkGene
        """        
        return LinkGene(link_id=self.id,
                        in_node=self.in_node,
                        out_node=self.out_node,
                        weight=self.weight,
                        enabled=self.enabled,
                        frozen=self.frozen)
        
    def is_allele(self, other_gene: LinkGene) -> bool:
        """Check if two LinkGenes are different versions of the same allele

        Args:
            other_gene (LinkGene): other gene to compare with

        Returns:
            bool: True if the two genes are the same allele
        """        
        return ((self.in_node == other_gene.in_node and
                self.out_node == other_gene.out_node) or 
                (self.out_node == other_gene.in_node and
                self.in_node == other_gene.out_node) or
                self.id == other_gene.id)

        
class NodeGene(BaseGene):
    def __init__(self,
                 node_id: int = 0,
                 mutation_number: int = 0,
                 node_type: NodeType = NodeType.HIDDEN,
                 bias: float = 0.0,
                 activation_function: ActivationFuncType=ActivationFuncType.SIGMOID,
                 aggregation_function: AggregationFuncType=AggregationFuncType.SUM,
                 enabled: bool = True,
                 frozen: bool = False,):
        
        node_id: int = node_id or InnovTable.get_node_number(increment=True)
        
        super(NodeGene, self).__init__(gene_id=node_id,
                                       mutation_number=mutation_number,
                                       enabled=enabled,
                                       frozen=frozen)
                
        self.type: NodeType = node_type                                         # HIDDEN, INPUT, OUTPUT, BIAS
       
        self.bias: float = 0 if self.is_sensor() else bias or uniform(-1,1)     # bias value to add to the activation value
         
        self.activation_function: ActivationFuncType = activation_function      # function to calculate activation
        self.aggregation_function: AggregationFuncType = aggregation_function   # function to aggregates incoming values
            
    def transcript(self) -> Dict:
        """ Return a dictionary containing the NodeGene's 
            information to synthesize a Node

        Returns:
            Dict: dictionary of NodeGene's information
        """        
        return {'node_id':self.id, 'node_type':self.type,
                'activation_function':self.activation_function,
                'aggregation_function':self.aggregation_function,
                'bias':self.bias, 'enabled':self.enabled}
        
    def mutate(self) -> None:
        """Mutate the LinkGene
        """       
        # if frozen can't be mutated 
        if self.frozen: return
        
        # modify bias value
        if (random() < Config.mutate_bias_prob and
            not self.is_sensor()):
            self.bias = uniform(-1,1)
            
        # disable the link
        if random() < Config.disable_prob:
            self.disabled = True
        # enable the link
        elif random() < Config.enable_prob:
            self.enabled = True
        
    def distance(self, other_node: NodeGene) -> float:
        """Calculate the distance between two NodeGenes based on their properties

        Args:
            other_node (NodeGene): other NodeGene to calculate the distance from

        Returns:
            float: distance calculated
        """   
        # compare parameters, distance bigger if values are different     
        distance: float = abs(self.bias - other_node.bias)
        distance += int(self.activation_function != other_node.activation_function)
        distance += int(self.aggregation_function != other_node.aggregation_function)
        distance += int(self.enabled != other_node.enabled)
        
        return distance
       
    def duplicate(self) -> NodeGene:
        """Create a copy of this NodeGene

        Returns:
            NodeGene: copy of this NodeGene
        """
        return NodeGene(node_id=self.id,
                        node_type=self.type,
                        enabled=self.enabled,
                        frozen=self.frozen)
        
    def is_allele(self, other_gene: NodeGene) -> bool:
        """Check if two NodeGenes are different versions of the same allele

        Args:
            other_gene (NodeGene): other gene to compare with

        Returns:
            bool: True if the two genes are the same allele
        """
        return (self.id == other_gene.id and
                self.type == other_gene.type or
                self.id == other_gene.id)
     
    def is_sensor(self) -> bool:
        """ determine if the node is a sensor (INPUT or BIAS)

        Returns:
            bool: node is a sensor
        """        
        return (self.type == NodeType.INPUT or 
                self.type == NodeType.BIAS)   
       
def reset_innovation_table():
    InnovTable.reset_innovation_table()

