from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Set

from project.src.rtNEAT.genes import OutputType

if TYPE_CHECKING:
    from genome import Genome
    from genes import NodeGene, LinkGene

import numpy.typing as npt

from .phenes import Link, Node


class Network:
    """Class:
         Neural network, containing nodes and links

         Attributes:
            __id (int):                     Unique identifier
            _inputs (Dict[int, Node]):      Dictionary of input nodes
            _outputs: (Dict[int, Node]):    Dictionary of output nodes
            _hidden: (Dict[int, Node]):     Dictionary of hidden nodes
            _all_nodes: (Dict[int, Node]):  Dictionary of all nodes

            _links: (Dict[int, Link]):      Dictionary of all links

            activation_phase (int):         Current activation phase
            frozen (bool):                  Frozen state (can't modify weights)
            complete (bool):                Whether the network is fully connected
    """
    def __init__(self,
                 network_id: int = 0,
                 frozen: bool = False):
        """Constructor:
            Build a network

        Args:
            network_id (int, optional): Unique identifier. Defaults to 0.
            frozen (bool, optional):    Can not modify weight. Defaults to False.
        """

        self.__id: int = network_id                 # Unique identifier

        self._inputs: Dict[int, Node] = {}          # Dictionary of input nodes
        self._outputs: Dict[int, Node] = {}         # Dictionary of output nodes
        self._trigger_outputs: Dict[int, Node] = {} # outputs to decide which action
        self._value_outputs: Dict[int, Node] = {}   # outputs with actions' values
        self._hidden: Dict[int, Node] = {}          # Dictionary of hidden nodes
        self._all_nodes: Dict[int, Node] = {}       # Dictionary of all nodes

        self._links: Dict[int, Link] = {}           # Dictionary of all links

        self.activation_phase: int = 0              # Current activation phase
        self.frozen: bool = frozen                  # Frozen state (can't modify weights)
        self.complete: bool

    @property
    def id(self) -> int:
        """Property:
            Return the network's id

        Returns:
            int: network's id
        """
        return self.__id

    @classmethod
    def genesis(cls, genome: Genome) -> Network:
        """Constructor:
            Create a new network corresponding to the given genome

        Args:
            genome (Genome): genome containing the encoding for this network

        Returns:
            Network: created network
        """
        network = cls(network_id=genome.id)
        network.complete = genome.complete

        network._synthetize_nodes(node_genes=genome.node_genes)
        network._synthetize_links(link_genes=genome.link_genes)

        return network

    def _synthetize_nodes(self, node_genes: Dict[int, NodeGene]):
        """Private method:
            Decode the NodeGenes to synthesize Nodes, and
            sort the Nodes based on their positions in the network

        Args:
            node_genes (Dict[int, NodeGene]): dictionary containing the NodeGenes
        """
        nodes = dict()
        for key, node_gene in node_genes.items():
            nodes[key] = Node.synthesis(node_gene.transcript())

        self._sort_nodes(nodes)

    def _synthetize_links(self, link_genes: Dict[int, LinkGene]):
        """Private method:
            Decode the LinkGenes to synthesize Links,
            add them to the network, and
            connect the incoming Node to the outgoing Node.


        Args:
            link_genes (Dict[int, LinkGene]): dictionary containing the LinkGenes

        Raises:
            ValueError: Thrown if an output is an incoming Node in a Link
            ValueError: Thrown if a sensor is an outgoing Node in a Link

        """
        for key, link_gene in link_genes.items():
            link = Link.synthesis(link_gene.transcript())
            # Replace id  by the actual Node
            in_node = self._all_nodes[link_gene.in_node]
            out_node = self._all_nodes[link_gene.out_node]

            if in_node.is_output():
                raise ValueError(
                    f"{in_node} is an output it can not be an in node")

            if out_node.is_sensor():
                raise ValueError(
                    f"{out_node} is a sensor it can not be an out node")

            link.in_node = in_node
            link.out_node = out_node
            self._links[key] = link
            if link_gene.enabled:
                self._connect_link(link)

    def _connect_link(self, link: Link) -> None:
        """Private method:
            Add the link to the list of incoming links of
            the out node and outgoing link of the in node

        Args:
            link (Link): link to add
        """
        in_node = self._all_nodes[link.in_node.id]
        out_node = self._all_nodes[link.out_node.id]

        out_node.incoming[link.id] = link
        in_node.outgoing[link.id] = link

    def _sort_nodes(self, nodes: Dict[int, Node]) -> None:
        """Private method:
            Sort the Nodes by positions in the network,
            add them to their respective dictionary, and
            add themm all to the all_nodes dictionary

        Args:
            nodes (Dict[int, Node]): Dictionary of Nodes to sort
        """

        for key, node in nodes.items():
            # Check for nodes' type
            # and sort them accordingly
            # in their dictionary
            match node.type.name:
                case 'INPUT':
                    self._inputs[key] = node
                case 'OUTPUT':
                    self._outputs[key] = node
                    if node.output_type == OutputType.TRIGGER:
                        self._trigger_outputs[key] = node
                    else:
                        self._value_outputs[key] = node
                case 'HIDDEN':
                    self._hidden[key] = node

            # Keep track of all nodes
            self._all_nodes[key] = node

    def verify_post_genesis(self):
        """Public method:
            Verify if the complete network's structure is correct

        Raises:
            ValueError: Outputs must be connected to all inputs
            ValueError: Outputs incoming connections must be equal to set of inputs
            ValueError: Outputs must not have any outgoing connections
            ValueError: Inputs must be connected to all outputs
            ValueError: Inputs outgoing connections must be equal to set of outputs
            ValueError: Inputs must not have any incoming connections
        """
        # Outputs
        for node in self.get_outputs():

            if node.outgoing:
                raise ValueError(f"{node} has some outgoing connections")

            # Fully connected
            if self.complete:
                if len(node.incoming) != len(self.inputs):
                    raise ValueError(
                        f"{node} is connected to {len(node.incoming)}/{len(self.inputs)}")

                if {n.in_node.id for n in node.get_incoming()} != set(self.inputs.keys()):
                    raise ValueError(f"{node} is not connected to all inputs ")

        # Inputs
        for node in self.get_inputs():

            if node.incoming:
                raise ValueError(f"{node} has some incoming connections")

            # Fully connected
            if self.complete:
                if len(node.outgoing) != len(self.outputs):
                    raise ValueError(
                        f"{node} is connected to {len(node.outgoing)}/{len(self.outputs)}")

                if {n.out_node.id for n in node.get_outgoing()} != set(self.outputs.keys()):
                    raise ValueError(f"{node} is not connected to all outputs")



    def activate(self, input_values: npt.NDArray) -> Dict[int, float]:
        """Public method:
            Activate the whole network after recieving input values

        Args:
            input_values (np.array): input values

        Raises:
            ValueError: The number of input values given does not correspond to the network

        Returns:
            np.array: activated values coming out of outputs nodes
        """
        # Compare the size of input values given to the network's inputs
        if input_values.size != len(self._inputs):
            raise ValueError(f"""Input values {(input_values.size)} does not correspond
                             to number of input nodes {len(self._inputs)}""")

        # increment the activation_phase
        self.activation_phase += 1

        # store the input values in the input nodes
        self._activate_inputs(values=input_values)
        # travel through the network to calculate the output values
        output_values = self._activate_outputs()

        return output_values

    def _activate_inputs(self, values: npt.NDArray):
        """Private method:
            Store the input values in the input nodes

        Args:
            values (np.array): values to store in the input nodes
        """
        # Make sure inputs are in the right order
        inputs = list(self.inputs.values())

        for node, value in zip(inputs, values):
            if not node.is_sensor():
                raise ValueError("The node must be a sensor")
            node.activation_value = value
            node.activation_phase = self.activation_phase

    def _activate_outputs(self) -> Dict[int, float]:
        """Private method:
            Travel through the network calculating the
            activation values necessary for each output


        Raises:
            ValueError: The nodes in the outputs list
                        are not of the proper type

        Returns:
            Set: set of trigger outputs
        """
        output_values: Dict[int, float] = {}

        for node in self.get_outputs():
            if not node.is_output():
                raise ValueError("The node must be an output")

            output_value = node.get_activation(
                activation_phase=self.activation_phase)

            if node.output_type == OutputType.TRIGGER:
                output_values[node.id] = output_value

            node.activation_value = output_value

        return output_values

    @property
    def n_inputs(self) -> int:
        """Property:
            Return the number of input Nodes

        Returns:
            int: number of input Nodes
        """
        return len(self._inputs)

    @property
    def n_outputs(self) -> int:
        """Property:
            Return the number of output Nodes

        Returns:
            int: number of output Nodes
        """
        return len(self._outputs)

    @property
    def n_nodes(self) -> int:
        """Property:
            Return the number of Nodes

        Returns:
            int: number of Nodes
        """
        return len(self._all_nodes)

    @property
    def n_links(self) -> int:
        """Property:
            Return the number of Links

        Returns:
            int: number of Links
        """
        return len(self._links)

    @property
    def inputs(self) -> Dict[int, Node]:
        """Property:
            Return the dictionary of input Nodes

        Returns:
            Dict[int, Node]: dictionary of input Nodes
        """
        return self._inputs

    @property
    def outputs(self) -> Dict[int, Node]:
        """Property:
            Return the dictionary of output Nodes

        Returns:
            Dict[int, Node]: dictionary of output Nodes
        """
        return self._outputs

    @property
    def trigger_outputs(self) -> Dict[int, Node]:
        """Property:
            Return the dictionary of trigger output Nodes

        Returns:
            Dict[int, Node]: dictionary of trigger output Nodes
        """
        return self._trigger_outputs

    @property
    def value_outputs(self) -> Dict[int, Node]:
        """Property:
            Return the dictionary of value output Nodes

        Returns:
            Dict[int, Node]: dictionary of value output Nodes
        """
        return self._value_outputs

    @property
    def hidden(self) -> Dict[int, Node]:
        """Property:
            Return the dictionary of hidden Nodes

        Returns:
            Dict[int, Node]: dictionary of hidden Nodes
        """
        return self._hidden

    @property
    def all_nodes(self) -> Dict[int, Node]:
        """Property:
            Return the dictionary of Nodes

        Returns:
            Dict[int, Node]: dictionary of Nodes
        """
        return self._all_nodes

    @property
    def links(self) -> Dict[int, Link]:
        """Property:
            Return the dictionary of Links

        Returns:
            Dict[int, Node]: dictionary of Links
        """
        return self._links

    def get_inputs(self) -> Set[Node]:
        """Getter:
            Return only the Nodes values from the dictionary

        Returns:
            Set[Node]: Set of input Nodes
        """
        return set(self._inputs.values())

    def get_outputs(self) -> Set[Node]:
        """Return only the Nodes values from the dictionary

        Returns:
            Set[Node]: Set of output Nodes
        """
        return set(self._outputs.values())

    def get_hidden(self) -> Set[Node]:
        """Return only the Nodes values from the dictionary

        Returns:
            Set[Node]: Set of hidden Nodes
        """
        return set(self._hidden.values())

    def get_all_nodes(self) -> Set[Node]:
        """Return only the Nodes values from the dictionary

        Returns:
            Set[Node]: Set of all Nodes
        """
        return set(self._all_nodes.values())

    def get_links(self) -> Set[Link]:
        """Return only the Nodes values from the dictionary

        Returns:
            Set[Link]: Set of Links
        """
        return set(self._links.values())

def _get_node_activation(node: Node, activation_phase: int):
        return node, node.get_activation(activation_phase=activation_phase)
