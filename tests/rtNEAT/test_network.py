import pytest, os, sys
from numpy.random import choice
import numpy as np

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'rtNEAT')))
from project.src.rtNEAT.network import Network
from project.src.rtNEAT.genes import NodeGene, LinkGene, NodeType, reset_innovation_table, sigmoid
from project.src.rtNEAT.genome import Genome
from project.src.rtNEAT.neat import Config
from project.src.rtNEAT.organism import Organism
from project.src.rtNEAT.innovation import InnovTable
from project.src.rtNEAT.phenes import Node, Link


class TestNetwork:
    def test_network_fields(self):
        network = Network()
        
        assert type(network) == Network
        assert {'_inputs', '_outputs','_hidden',
                '_all_nodes', 'activation_phase',
                'frozen'}.issubset(vars(network))
        
    class TestNetworkMethods:
        @pytest.fixture(autouse=True)
        def setup(self):
            reset_innovation_table()
            self.genome = Genome(genome_id=0, node_genes={}, link_genes={})
            self.network = Network(network_id=self.genome.id,
                                   inputs={},
                                   outputs={},
                                   all_nodes={})
                                   
            
            yield 
            
            self.genome._node_genes = {}
            self.genome._link_genes = {}
            self.network._links = {}
            self.genome = None
            self.network = None
                            
        def test_syntethize_nodes(self):
            node_genes = {}
            node_types = [None, NodeType.BIAS, NodeType.INPUT, 
                        NodeType.HIDDEN, NodeType.OUTPUT]
            
            for i, _ in enumerate(range(4),1):
                node_genes[i] = NodeGene(node_type=node_types[i])
             
            assert len(node_genes) == len(node_types)-1
            
            self.network._synthetize_nodes(node_genes=node_genes)
            
            for i, node in self.network._all_nodes.items():
                assert node.id == i
                assert node.__class__.__name__ == "Node"
                assert node.type == node_types[i]
            
            #Sorted                     
            for node in self.network.get_inputs():
                assert node.type == NodeType.INPUT
                
            for node in self.network.get_hidden():
                assert node.type == NodeType.HIDDEN    
            
            for node in self.network.get_outputs():
                assert node.type == NodeType.OUTPUT
                            
        def test_synthetize_links(self):
            for _ in range(50):
                self.genome.add_node(NodeGene(node_type=choice(list(NodeType))))
                
            for _ in range(10):
                in_node, out_node = choice(list(self.genome._node_genes.values()), 2)
                self.genome.add_link(LinkGene(in_node=in_node,
                                         out_node=out_node))
                
            self.network._synthetize_nodes(node_genes=self.genome._node_genes)
            self.network._synthetize_links(link_genes=self.genome._link_genes)
            
            assert len(self.network._links) == 10
            for link in self.network._links.values():
                assert link.__class__.__name__ == 'Link'
                
            # ALl link have been attributed to incoming and outgoing links
            assert sum([len(node.incoming) for node in self.network._all_nodes.values()]) == 10
            assert sum([len(node.outgoing) for node in self.network._all_nodes.values()]) == 10
            
            assert self.network.n_links == 10
            assert self.network.n_nodes == 50
            
        def test_network_genesis(self):
            for _ in range(100):
                self.genome.add_node(NodeGene(node_type=choice(list(NodeType))))
                
            for _ in range(1000):
                in_node, out_node = choice(list(self.genome._node_genes.values()), 2)
                self.genome.add_link(LinkGene(in_node=in_node,
                                         out_node=out_node))
                
            self.network = Network.genesis(self.genome)
            
            assert self.network.id == self.genome.id
            assert self.network.n_links == 1000
            assert self.network.n_nodes == 100
            assert self.network.n_inputs > 0
            assert self.network.n_outputs > 0
            
    class TestActivation:   
            
        def test_activate_callable_functions(self):
            values = [1,2,3,4,5]
            node = Node(node_id=1)
            node.aggregation_function.value(values) == sum(values)
            node.activation_function.value(node.aggregation_function.value(values)) == sigmoid(sum(values))
            
        def test_activate_complete_no_hidden_nodes(self):
            n_inputs, n_outputs = np.random.randint(3,10,2)
            genome = Genome.genesis(genome_id=10,
                                    n_inputs=n_inputs,
                                    n_outputs=n_outputs)
            dim = (n_inputs+1) * n_outputs
            weights = np.random.uniform(-1,1,dim)
            l_inputs = np.random.uniform(-1,1,n_inputs)
            new_weights = {}
                        
            genes = genome.get_link_genes()
            for link_gene in genes:
                link_gene.weight = weights[link_gene.id-1]
                new_weights[link_gene.id-1] = weights[link_gene.id-1]
                    
            mind = Network.genesis(genome=genome)
            
            for node in mind.get_all_nodes():
                assert node.activation_phase == 0
            
            outputs = mind.activate(input_values=l_inputs)
            
            link_count = 0
            for value, node in zip(l_inputs, mind.get_inputs()):
                assert node.activation_value == value
                assert node.activation_phase == 1
                for link in node.get_outgoing():
                    assert link.weight == weights[link.id-1]
                    link_count += 1
            
            for i, node in enumerate(mind.get_outputs()):
                assert node.activation_phase == 1
                for j, link in enumerate(node.get_incoming()):
                    assert link.weight == weights[link.id-1]
            
            # inputs = list(l_inputs)
            for key, output_value in outputs.items():
                output = mind.outputs[key]
                """ links_id = [link.id - 1 for link in output.get_incoming()]
                sorted_id = sorted(links_id)
                values = [value *  new_weights[sorted_id[i]] for i, value in enumerate(l_inputs)]
                values += [output.bias] """
                
                values = [link.in_node.activation_value * link.weight for link in output.get_incoming()]
                values += [output.bias]             
                assert round(output_value, 10) == round(sigmoid(sum(values)), 10)
                assert output.activation_value == output_value
                #assert output_value == sigmoid(sum(values))
                
        def test_activate_simple_networks(self):
            #   
            #   O
            #    \
            #     O ----O
            #    /
            #   O
            #
          
            for i in range(100):
                reset_innovation_table()
                weights = np.random.uniform(-1,1,3)
                input1 = NodeGene(node_type=NodeType.INPUT)
                input2 = NodeGene(node_type=NodeType.INPUT)
                hidden = NodeGene(node_type=NodeType.HIDDEN)
                output = NodeGene(node_type=NodeType.OUTPUT)
                
                link1 = LinkGene(in_node=input1.id,
                                out_node=hidden.id,
                                weight=weights[0])
                link2 = LinkGene(in_node=input2.id,
                                out_node=hidden.id,
                                weight=weights[1])
                link3 = LinkGene(in_node=hidden.id,
                                out_node=output.id,
                                weight=weights[2])
                
                nodes =  [input1, input2, hidden, output]
                nodes_dict = {node.id: node for node in nodes}
                links = [link1, link2, link3]
                links_dict = {link.id: link for link in links}
                
                
                genome = Genome(genome_id=i,
                                node_genes=nodes_dict,
                                link_genes=links_dict)
        
                mind = Network.genesis(genome=genome)
                
                inputs = np.random.uniform(-1,1,2)
                outputs = mind.activate(np.array(inputs))
                
                first_layer = sigmoid(sum([inputs[0]*weights[0],
                                            inputs[1]*weights[1],
                                            hidden.bias]))
                
                assert round(first_layer,10) == round(list(mind.get_hidden())[0].activation_value,10)
                
                second_layer = sigmoid(sum([first_layer*weights[2],
                                            output.bias]))
                
                assert round(outputs[output.id],10) == round(second_layer,10)
        
        def test_activate_random_networks(self):
            n_links = np.random.randint(12,20)
            n_nodes = np.random.randint(10,20)
            weights = np.random.uniform(-1,1,n_links)
            
            nodes = []
            nodes.append(Node(node_type=NodeType.BIAS))
            n_inputs = 0
            n_outputs = 0
            for _ in range(n_nodes):
                node_type = np.random.choice([NodeType.INPUT, NodeType.OUTPUT, NodeType.HIDDEN])
                if node_type == NodeType.INPUT:
                    n_inputs += 1
                elif node_type == NodeType.OUTPUT:
                    n_outputs += 1
                nodes.append(Node(node_type=node_type))
            
            genes = []
            
            for i, _ in enumerate(range((n_links))):
                valid = False
                while not valid:
                    in_node, out_node = np.random.choice(nodes, 2)
                    valid = (in_node.type != NodeType.OUTPUT and
                            out_node.type != NodeType.INPUT)
                    
                genes.append(Link(in_node=in_node,
                                out_node=out_node,
                                weight=weights[i])) 
                
            nodes_dict = {node.id: node for node in nodes}
            genome = Genome(genome_id=0,
                            nodes=nodes_dict,
                            genes=genes)
            
            network = Network.genesis()   
            inputs = np.random.uniform(-1,1,n_inputs)
            outputs = network.activate(np.array(inputs))
            assert len(outputs) == n_outputs
            