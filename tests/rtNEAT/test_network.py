import pytest, os, sys
from numpy.random import choice

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'rtNEAT')))
from project.src.rtNEAT.network import Network
from project.src.rtNEAT.genes import NodeGene, LinkGene, NodeType, reset_innovation_table
from project.src.rtNEAT.phenes import Node, Link
from project.src.rtNEAT.genome import Genome


class TestNetwork:
    def test_network_fields(self):
        network = Network()
        
        assert type(network) == Network
        assert {'id', 'inputs', 'outputs', 'bias', 'hidden',
                'all_nodes', 'activation_phase', 'frozen', 
                'number_nodes','number_links'}.issubset(vars(network))
        
    class TestNetworkMethods:
        def test_syntethize_nodes(self):
            node_genes = {}
            node_types = [None, NodeType.BIAS, NodeType.INPUT, 
                        NodeType.HIDDEN, NodeType.OUTPUT]
            
            for i, _ in enumerate(range(4),1):
                node_genes[i] = NodeGene(node_type=node_types[i])
             
            assert len(node_genes) == len(node_types)-1
            
            network = Network(network_id=0)   
            network._synthetize_nodes(node_genes=node_genes)
            
            for i, node in network.all_nodes.items():
                assert node.id == i
                assert node.__class__.__name__ == "Node"
                assert node.type == node_types[i]
            
            #Sorted      
            for node in network.bias.values():
                assert node.type == NodeType.BIAS
                
            for node in network.inputs.values():
                assert node.type == NodeType.INPUT
                
            for node in network.hidden.values():
                assert node.type == NodeType.HIDDEN    
            
            for node in network.outputs.values():
                assert node.type == NodeType.OUTPUT
                            
        def test_synthetize_links(self):
            genome = Genome(genome_id=0)
            for _ in range(50):
                genome.insert_node(NodeGene(node_type=choice(list(NodeType))))
                
            for _ in range(10):
                in_node, out_node = choice(list(genome.node_genes.values()), 2)
                genome.add_gene(LinkGene(in_node=in_node, out_node=out_node))
                
            network = Network(network_id=genome.id)
            network._synthetize_nodes(node_genes=genome.node_genes)
            network._synthetize_links(link_genes=genome.link_genes)
            
            assert len(network.links) == 10
            for link in network.links.values():
                assert link.__class__.__name__ == 'Link'
                
            # ALl link have been attributed to incoming and outgoing links
            assert sum([len(node.incoming) for node in network.all_nodes.values()]) == 10
            assert sum([len(node.outgoing) for node in network.all_nodes.values()]) == 10
            
            network.calculate_properties()
            assert network.number_links == 10
            assert network.number_nodes == 50
            
        def test_network_genesis(self):
            genome = Genome(genome_id=0)
            for _ in range(100):
                genome.insert_node(NodeGene(node_type=choice(list(NodeType))))
                
            for _ in range(1000):
                in_node, out_node = choice(list(genome.node_genes.values()), 2)
                genome.add_gene(LinkGene(in_node=in_node, out_node=out_node))
                
            network = Network.genesis(genome)
            
            assert network.id == genome.id
            assert network.n_links == 1000
            assert network.n_nodes == 100
            assert network.n_inputs > 0
            assert network.n_outputs > 0
           