
import numpy as np
import pytest
from numpy.random import choice
from project.src.rtNEAT.genes import (LinkGene, NodeGene, NodeType,
                                      OutputNodeGene, OutputType,
                                      reset_innovation_table, sigmoid)
from project.src.rtNEAT.genome import Genome
from project.src.rtNEAT.network import Network
from project.src.rtNEAT.phenes import Link, Node


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
            self.mind = Network(network_id=self.genome.id)
                                   
            
            yield 
            
            self.genome._node_genes = {}
            self.genome._link_genes = {}
            self.mind._links = {}
            if self.genome:
                self.genome.node_genes.clear()
                self.genome.link_genes.clear()
            if self.mind:
                self.mind.inputs.clear()
                self.mind.all_nodes.clear()
                self.mind.outputs.clear()
                self.mind.hidden.clear()
            
                            
        def test_syntethize_nodes(self):
            node_genes = {}
            node_types = [None, NodeType.BIAS, NodeType.INPUT, 
                        NodeType.HIDDEN, NodeType.OUTPUT]
            
            for i, _ in enumerate(range(4),1):
                node_genes[i] = NodeGene(node_type=node_types[i])
             
            assert len(node_genes) == len(node_types)-1
            
            self.mind._synthetize_nodes(node_genes=node_genes)
            
            for i, node in self.mind._all_nodes.items():
                assert node.id == i
                assert node.__class__.__name__ == "Node"
                assert node.type == node_types[i]
            
            #Sorted                     
            for node in self.mind.get_inputs():
                assert node.type == NodeType.INPUT
                
            for node in self.mind.get_hidden():
                assert node.type == NodeType.HIDDEN    
            
            for node in self.mind.get_outputs():
                assert node.type == NodeType.OUTPUT
                            
        def test_synthetize_links(self):
            for _ in range(50):
                self.genome.add_node(NodeGene()) #node_type=choice(list(NodeType))
                
            for _ in range(10):
                in_node, out_node = choice(list(self.genome._node_genes.values()), 2)
                self.genome.add_link(LinkGene(in_node=in_node.id,
                                                out_node=out_node.id))
                
            self.mind._synthetize_nodes(node_genes=self.genome._node_genes)
            self.mind._synthetize_links(link_genes=self.genome._link_genes)
            
            assert len(self.mind._links) == 10
            for link in self.mind._links.values():
                assert link.__class__.__name__ == 'Link'
                
            # ALl link have been attributed to incoming and outgoing links
            assert sum([len(node.incoming) for node in self.mind._all_nodes.values()]) == 10
            assert sum([len(node.outgoing) for node in self.mind._all_nodes.values()]) == 10
            
            assert self.mind.n_links == 10
            assert self.mind.n_nodes == 50
            
        def test_network_genesis(self):
            reset_innovation_table()
            for _ in range(99):
                self.genome.add_node(NodeGene(node_type=choice(list(NodeType))))
                
            hidden_node = NodeGene()
            self.genome.add_node(hidden_node)
                
            for _ in range(1000):
                in_node, out_node = choice(list(self.genome._node_genes.values()), 2)
                if in_node.type == NodeType.OUTPUT:
                    in_node = hidden_node
                if out_node.type == NodeType.INPUT or NodeType.BIAS:
                    out_node = hidden_node
                
                self.genome.add_link(LinkGene(in_node=in_node.id,
                                              out_node=out_node.id))
                
            self.mind = Network.genesis(self.genome)
            
            assert self.mind.id == self.genome.id
            assert self.mind.n_links == 1000
            assert self.mind.n_nodes == 100
            assert self.mind.n_inputs > 0
            assert self.mind.n_outputs > 0
            
        def test_not_same_instance(self):
            gen1_data = {'n_inputs':10,
                            'n_outputs':10,
                            'n_actions':0,
                            'actions':{}}
            gen2_data = {'n_inputs':10,
                            'n_outputs':10,
                            'n_actions':0,
                            'actions':{}}
            gen1 = Genome.genesis(genome_id=1,
                                  genome_data=gen1_data)
            gen2 = Genome.genesis(genome_id=2,
                                  genome_data=gen2_data)
            
            net1 = Network.genesis(genome=gen1)
            net2 = Network.genesis(genome=gen2)
             
            assert gen1 != gen2
            assert gen1.link_genes != gen2.link_genes 
                       
            assert net1 != net2
            assert net1.id != net2.id
            assert net1.all_nodes != net2.all_nodes
            assert net1.inputs != net2.inputs
            assert net1.outputs != net2.outputs
            assert net1.links != net2.links
            
        def test_brain_structure(self):
            reset_innovation_table()
            gen_data = {'n_inputs':96,
                            'n_outputs':15,
                            'n_actions':0,
                            'actions':{}}
            gen = Genome.genesis(genome_id=1,
                                 genome_data=gen_data)
            
            net = Network.genesis(genome=gen)
            # Complete
            for node in net.get_outputs():
                assert {n.in_node.id for n in node.get_incoming()} == set(net.inputs.keys())
                assert not node.outgoing
                
            for node in net.get_inputs():
                assert {n.out_node.id for n in node.get_outgoing()} == set(net.outputs.keys())
                assert not node.incoming
                         
            
    class TestActivation: 
        @pytest.fixture(autouse=True)
        def setup(self):
            self.links = []
            self.nodes = []
            self.genome = None
            self.mind = None
            
            yield
            self.links.clear()
            self.nodes.clear()
            if self.genome:
                self.genome.node_genes.clear()
                self.genome.link_genes.clear()
            if self.mind:
                self.mind.inputs.clear()
                self.mind.all_nodes.clear()
                self.mind.outputs.clear()
                self.mind.hidden.clear()
            
        def test_activate_callable_functions(self):
            values = [1,2,3,4,5]
            node = Node(node_id=1)
            node.aggregation_function.value(values) == sum(values)
            node.activation_function.value(node.aggregation_function.value(values)) == sigmoid(sum(values))
            
        def test_activate_complete_no_hidden_nodes(self):
            n_inputs, n_outputs = np.random.randint(3,10,2)
            gen_data = {'n_inputs':n_inputs,
                        'n_outputs':n_outputs,
                        'n_actions':n_outputs,
                        'actions':{f"{i}":[] for i in range(n_outputs)}}
            self.genome = Genome.genesis(genome_id=10,
                                         genome_data=gen_data)
            
            dim = (n_inputs+1) * n_outputs
            weights = np.random.uniform(-1,1,dim)
            l_inputs = np.random.uniform(-1,1,n_inputs)
            new_weights = {}
                        
            genes = self.genome.get_link_genes()
            for link_gene in genes:
                link_gene.weight = weights[link_gene.id-1]
                new_weights[link_gene.id-1] = weights[link_gene.id-1]
                    
            self.mind = Network.genesis(genome=self.genome)
            
            for node in self.mind.get_all_nodes():
                assert node.activation_phase == 0
            
            outputs = self.mind.activate(input_values=l_inputs)
            
            link_count = 0
            unsorted_inputs = self.mind.inputs
            sorted_inputs = [unsorted_inputs[key] for key in sorted(unsorted_inputs.keys(), reverse=False)]
            for value, node in zip(l_inputs, sorted_inputs):
                assert node.activation_value == value
                assert node.activation_phase == 1
                for link in node.get_outgoing():
                    assert link.weight == weights[link.id-1]
                    link_count += 1
            
            for node in self.mind.get_outputs():
                assert node.activation_phase == 1
                for link in node.get_incoming():
                    assert link.weight == weights[link.id-1]
            
            # inputs = list(l_inputs)
            for key, output_value in outputs.items():
                output = self.mind.outputs[key]
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
                output = OutputNodeGene(name="",
                                        node_id = 0,
                                        output_type=OutputType.TRIGGER,
                                        associated_values=set())
                # output = NodeGene(node_type=NodeType.OUTPUT)
                
                link1 = LinkGene(in_node=input1.id,
                                out_node=hidden.id,
                                weight=weights[0])
                link2 = LinkGene(in_node=input2.id,
                                out_node=hidden.id,
                                weight=weights[1])
                link3 = LinkGene(in_node=hidden.id,
                                out_node=output.id,
                                weight=weights[2])
                
                nodes_dict = {}
                links_dict = {}
                self.nodes =  [input1, input2, hidden, output]
                nodes_dict = {node.id: node for node in self.nodes}
                self.links = [link1, link2, link3]
                links_dict = {link.id: link for link in self.links}
                
                
                self.genome = Genome(genome_id=i,
                                node_genes=nodes_dict,
                                link_genes=links_dict)
        
                self.mind = Network.genesis(genome=self.genome)
                
                inputs = np.random.uniform(-1,1,2)
                outputs = self.mind.activate(np.array(inputs))
                
                first_layer = sigmoid(sum([inputs[0]*weights[0],
                                            inputs[1]*weights[1],
                                            hidden.bias]))
                
                assert round(first_layer, 10) == round(list(self.mind.get_hidden())[0].activation_value,10)
                
                second_layer = sigmoid(sum([first_layer*weights[2],
                                            output.bias]))
                
                assert round(outputs[output.id],10) == round(second_layer,10)
      
        
        def test_activate_random_networks(self):
            n_links = np.random.randint(12,20)
            n_nodes = np.random.randint(10,20)
            weights = np.random.uniform(-1,1,n_links)
            
            self.nodes = []
            self.nodes.append(NodeGene(node_type=NodeType.BIAS))
            hidden_node = NodeGene()
            self.nodes.append(hidden_node)
            n_inputs = 0
            n_outputs = 0
            for _ in range(n_nodes):
                node_type = np.random.choice([NodeType.INPUT, NodeType.OUTPUT, NodeType.HIDDEN])
                if node_type == NodeType.INPUT:
                    n_inputs += 1
                elif node_type == NodeType.OUTPUT:
                    n_outputs += 1
                self.nodes.append(NodeGene(node_type=node_type))
            
            self.links = []
            
            for i, _ in enumerate(range((n_links))):
                valid = False
                while not valid:
                    in_node, out_node = np.random.choice(self.nodes, 2)
                    
                    if in_node.type == NodeType.OUTPUT:
                        in_node = hidden_node
                    if out_node.type == NodeType.INPUT or NodeType.BIAS:
                        out_node = hidden_node
                        
                    valid = (in_node.type != NodeType.OUTPUT and
                            out_node.type != NodeType.INPUT)
                    
                self.links.append(LinkGene(in_node=in_node.id,
                                    out_node=out_node.id,
                                    weight=weights[i])) 
                
            nodes_dict = {node.id: node for node in self.nodes}
            genes_dict = {link.id: link for link in self.links}
            genome3 = Genome(genome_id=0,
                            node_genes=nodes_dict,
                            link_genes=genes_dict)
            
            network2 = Network.genesis(genome=genome3)   
            inputs = np.random.uniform(-1,1,n_inputs)
            # outputs = network2.activate(np.array(inputs))
            outputs = network2.n_outputs
            assert outputs == n_outputs
            