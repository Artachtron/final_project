import pytest, os, sys
import numpy as np

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'rtNEAT')))
from project.src.rtNEAT.genome import Genome
from project.src.rtNEAT.genes import NodeGene, LinkGene, reset_innovation_table, NodeType

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
                        node_genes=nodes,
                        link_genes=genes)
        
        assert {'id','node_genes','link_genes'}.issubset(vars(genome))
        
        assert genome.id == 0
        assert genome.node_genes == nodes
        assert genome.link_genes == genes
        
    def test_genesis(self):
        genome = Genome.genesis(genome_id=0,
                                n_inputs=3,
                                n_outputs=5)
        
        assert genome.n_node_genes == 3 + 5 + 1
        assert genome.n_link_genes == 4 * 5
        assert list(genome.size.values()) == [9, 20]
        
    class TestGenomeMethods:
        @pytest.fixture(autouse=True)
        def setup(self):
            sensor_node = NodeGene(node_type=NodeType.INPUT)
            
            sensor_node2 = NodeGene(node_type=NodeType.INPUT)
   
            sensor_node3 = NodeGene(node_type=NodeType.INPUT)
            
            action_node = NodeGene(node_type=NodeType.OUTPUT)
            
            action_node2 = NodeGene(node_type=NodeType.OUTPUT)
            
            action_node3 = NodeGene(node_type=NodeType.OUTPUT)
            
            gene0 = LinkGene(in_node=sensor_node,
                            out_node=action_node,
                            weight=1.0,
                            mutation_number=0)
            
            gene1 = LinkGene(in_node=sensor_node2,
                            out_node=action_node2,
                            weight=1.0,
                            mutation_number=0)
            
            gene2 = LinkGene(in_node=sensor_node3,
                            out_node=action_node3,
                            weight=1.0,
                            mutation_number=0)
                    
            gene3 = LinkGene(in_node=sensor_node3,
                            out_node=action_node3,
                            weight=1.0,
                            mutation_number=1)
 
            nodes = [sensor_node, action_node, sensor_node2, action_node2, sensor_node3, action_node3]
            genes = [gene0, gene1, gene2, gene3]
            self.nodes = {node.id: node for node in nodes}
            self.links = {gene.id: gene for gene in genes}
            
            self.genome1 = Genome(genome_id=0,
                            node_genes=self.nodes,
                            link_genes=self.genes)
            
            np.random.seed(1)

            yield
            
            reset_innovation_table()   

        def test_insert_node(self):
            node = NodeGene(node_id=1)
            nodes_dict = Genome.insert_gene_in_dict(genes_dict={},
                                                    gene=node)
            genome = Genome(genome_id=0,
                                 node_genes={},
                                 link_genes={})
            
            assert nodes_dict == {1: node}
            assert genome.node_genes == {}
            
            genome.insert_node(node=node)
            assert genome.node_genes == nodes_dict
            

            

            
        