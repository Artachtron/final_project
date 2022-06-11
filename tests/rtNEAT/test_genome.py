import pytest, os, sys

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'rtNEAT')))
from project.src.rtNEAT.genome import Genome
from project.src.rtNEAT.genes import NodeGene, LinkGene, reset_innovation_table

class TestGenome:
    def test_create_genome(self):
        genome = Genome(genome_id=0)
        
        assert type(genome) == Genome 
        
    def test_genome_fields(self):
        nodes = {0: NodeGene(0), 1: NodeGene(1)}
        genes = {0: LinkGene(link_id=0,
                            in_node_id=nodes[0].id,
                            out_node_id=nodes[1].id)}
        
        genome = Genome(genome_id=0,
                        nodes=nodes,
                        genes=genes)
        
        assert {'id','nodes','genes'}.issubset(vars(genome))
        
        assert genome.id == 0
        assert genome.nodes == nodes
        assert genome.genes == genes
        
    class TestGenomeMethods:
        @pytest.fixture(autouse=True)
        def setup(self):
            self.genome = Genome(genome_id=0)
            yield 
            self.genome == None
            reset_innovation_table()       
        
        def test_insert_node(self):
            node = NodeGene(node_id=1)
            nodes_dict = Genome.insert_node_in_dict(nodes_dict={},
                                                    node=node)
            
            assert nodes_dict == {1: node}
            assert self.genome.nodes == {}
            
            self.genome.insert_node(node=node)
            assert self.genome.nodes == nodes_dict
            
        def test_genesis(self):
            for _ in range(1, 10):
                self.genome.insert_node(NodeGene())
            
            assert len(self.genome.nodes) == 9