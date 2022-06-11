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
                            in_node=nodes[0].id,
                            out_node=nodes[1].id)}
        
        genome = Genome(genome_id=0,
                        nodes=nodes,
                        links=genes)
        
        assert {'id','node_genes','link_genes'}.issubset(vars(genome))
        
        assert genome.id == 0
        assert genome.node_genes == nodes
        assert genome.link_genes == genes
        
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
            assert self.genome.node_genes == {}
            
            self.genome.insert_node(node=node)
            assert self.genome.node_genes == nodes_dict
            
        def test_genesis(self):
            for _ in range(1, 10):
                self.genome.insert_node(NodeGene())
            
            assert len(self.genome.node_genes) == 9