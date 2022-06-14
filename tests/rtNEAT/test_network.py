import pytest, os, sys
from numpy.random import choice

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'rtNEAT')))
from project.src.rtNEAT.network import Network
from project.src.rtNEAT.genes import NodeGene, LinkGene, NodeType, reset_innovation_table
from project.src.rtNEAT.genome import Genome


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
           