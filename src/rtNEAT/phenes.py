from __future__ import annotations

from abc import ABC, abstractclassmethod, abstractmethod
from functools import partial
from typing import Dict, Optional, Set, ValuesView

from .genes import ActivationFuncType, AggregationFuncType, NodeType, sigmoid


class BasePhene(ABC):
    """Abstract class:
        Contains the phenes' common attributes and methods

    Attributes:
        __id (int):     Unique identifier
        enabled (bool): Can output its activation value

    Abstract class methods:
        synthesis: Create a phene from gene information
    """
    __slots__ = '__id', 'name', 'enabled'
    def __init__(self,
                 phene_id: int,
                 name: Optional[str] = None,
                 enabled: bool = True):
        """Super constructor:
            Get the necessary information for a gene

        Args:
            phene_id (int):             unique identifier
            enabled (bool, optional):   can transmit activation value. Defaults to True.
        """

        self.__id: int = phene_id       # unique identifier
        self.name: Optional[str] = name # unique name
        self.enabled: bool = enabled    # does not output any value if false

    @property
    def id(self):
        return self.__id

    def __eq__(self, other) -> bool:
        return self.id == other.id

    def __hash__(self):
        return hash(self.__id)

    @abstractclassmethod
    def synthesis(cls, kwargs):
        """Abstract class method:
            Create a phene from gene information

        Args:
            kwargs : phenes' information
        """


class Link(BasePhene):
    """BasePhene sublcass:
        Link created from LinkGene's information,
        a Link connects two Nodes together

    Attributes:
        weight (float):     weight of the connection
        in_node (Node):     incoming Node
        out_node (Node):    outgoing Node

    class method:
        synthesis: create a link from LinkGene's information
    """
    __slots__ = 'weight', 'in_node', 'out_node'
    def __init__(self,
                link_id: int,
                weight: float,
                in_node: Node,
                out_node: Node,
                name: Optional[str] = None,
                enabled: bool = True,
                ):
        """Constructor:
            Initialize a Link

        Args:
            link_id (int):              unique identifier
            weight (float):             weight of the connection
            in_node (Node):             incoming Node
            out_node (Node):            outgoing Node
            enabled (bool, optional):   can transmit activation value. Defaults to True.
        """

        super().__init__(phene_id=link_id,
                         name=name,
                         enabled=enabled)

        self.weight: float = weight     # Weight of the connection
        self.in_node: Node = in_node    # Node inputting into the link
        self.out_node: Node = out_node  # Node that the link affects

    def __repr__(self):
        return f"{self.id}: {self.in_node} -> {self.out_node}"

    @classmethod
    def synthesis(cls, kwargs) -> Link:
        """Constructor:
            Synthesize a Link from a LinkGene
            and return it

        Args:
            kwargs (Dict): contains the information to synthesize a Link

        Returns:
            Link: create Link
        """
        return Link(**kwargs)

class Node(BasePhene):
    """BasePhene sublcass:
        Node created from NodeGene's information

    Attributes:
        activation_phase (int):                         current activation phase based on network
        activation_value (float):                       output value after activation
        node_type (NodeType):                           position in the network
        bias (float):                                   incoming bias' value
        activation_function (ActivationFuncType):       calculate activation form incoming signals
        aggregation_function (AggregationFuncType):     aggregate input signals' value
        incoming (Dict[int, Link]):                     incoming Links
        outgoing (Dict[int, Link]):                     outgoing Links

    method:
        get_incoming:   returns the set of incoming Links
        get_outgoing:   returns the set of outgoing Links
        is_sensor:      Check if the Node is a sensor (INPUT or BIAS)
        is_output:      Check if the Node is an OUTPUT
        get_activation: Browse the list of incoming Links and calculate the activation value

    class method:
        synthesis: synthesize a Node from a NodeGene
    """
    __slots__ = ('activation_phase', 'activation_value', 'activation_function',
                'aggregation_function', 'incoming', 'outgoing', 'type','bias',
                'associated_values', 'output_type')
    
    def __init__(self,
                  node_id: int,
                  activation_function = None,
                  aggregation_function = None,
                  name: Optional[str] = None,
                  node_type: NodeType = NodeType.HIDDEN,
                  bias: float = 1.0,
                  enabled: bool = True,
                  associated_values: Optional[Set[int]] = None,
                  output_type: Optional[str] = None
                  ):
        """Constructor:
            Initialize a Node

        Args:
            node_id (int):                                          unique identifier
            node_type (NodeType, optional):                         position in the network. Defaults to NodeType.HIDDEN.
            activation_function (ActivationFuncType, optional):     calculate activation form incoming signals. Defaults to ActivationFuncType.SIGMOID.
            aggregation_function (AggregationFuncType, optional):   aggregate input signals' value. Defaults to AggregationFuncType.SUM.
            bias (float, optional):                                 incoming bias' value. Defaults to 1.0.
            enabled (bool, optional):                               can transmit activation value. Defaults to True.
        """

        super().__init__(phene_id=node_id,
                         name=name,
                         enabled=enabled)

        self.activation_phase: int = 0              # Current activation phase
        self.activation_value: float = 0.0          # The total output value
        self.type: NodeType = node_type             # HIDDEN, INPUT, OUTPUT
        self.bias: float = bias                     # Bias value

        self.activation_function: ActivationFuncType = partial(sigmoid)
        self.aggregation_function: AggregationFuncType = sum

        self.incoming: Dict[int, Link] = {}          # Dictionary of incoming links
        self.outgoing: Dict[int, Link] = {}          # Dictionary of outgoing links

        self.associated_values: Optional[Set[int]] = associated_values  # Associated values for trigger outputs
        self.output_type: Optional[str] = output_type                   # Type of output

    def __repr__(self):
        if self.name:
            return f"{self.name} {self.id}"
        return f"{self.type} {self.id}"

    def get_incoming(self)  -> ValuesView:
        """Public method:
            Return only the Links values from
            the incoming dictionary

        Returns:
            Set[Link]: set of incoming links
        """
        return self.incoming.values()

    def get_outgoing(self)  ->  ValuesView:
        """Public method:
            Return only the Links values from
            the outgoing dictionary

        Returns:
            Set[Link]: set of outgoing links
        """
        return self.outgoing.values()

    @classmethod
    def synthesis(cls, kwargs) -> Node:
        """Constructor:
            Synthesize a Node from a NodeGene
            and return it

        Returns:
            Node: the created Node
        """
        return Node(**kwargs)

    def is_sensor(self) -> bool:
        """Public method:
            Check if the node is a sensor (INPUT or BIAS)

        Returns:
            bool: Node is a sensor
        """
        return (self.type == NodeType.INPUT or
                self.type == NodeType.BIAS)

    def is_output(self) -> bool:
        """Public method:
            Check if the node is an OUTPUT

        Returns:
            bool: Node is an output
        """
        return self.type == NodeType.OUTPUT

    
    def get_activation(self, activation_phase: int) -> float:
        """Public method:
            Browse the list of incoming Links and calculate the activation value

        Args:
            activation_phase (int): current activation phase of the network

        Returns:
            float: the output value of the node after activation
        """
        # If the output was already calculated during the current phase,
        # or the node is an input: then just return the value
        if self.activation_phase != activation_phase and not self.is_sensor():
            # set the activation phase to the current one,
            # since the value is now already calculated
            self.activation_phase = activation_phase

            values = self.bias
            # Loop through the list of incoming links and
            # calculate the sum of its incoming activation

            for link in self.get_incoming():
                # Only take the value of activated links
                if link.enabled:
                    # Recurrence call to calculate all the
                    # necessary incoming activation values
                    values += link.in_node.get_activation(activation_phase=activation_phase) * link.weight
            
            self.activation_value = self.activation_function(values)
            
        return self.activation_value
