import pytest
from project.src.rtNEAT.genes import (ActivationFuncType, AggregationFuncType,
                                      BaseGene, LinkGene, NodeGene, NodeType,
                                      reset_innovation_table)


class TestGene:
    @pytest.fixture(autouse=True)
    def setup(self):
        yield
        reset_innovation_table()
         
    def test_create_link_gene(self):
        link_gene = LinkGene(in_node=1,
                             out_node=2)
        
        assert type(link_gene) == LinkGene
        assert issubclass(type(link_gene), BaseGene)
        
    def test_link_gene_fields(self):
        link_gene = LinkGene(in_node=1,
                             out_node=2,
                             weight=0.5,
                             mutation_number=0,
                             enabled=True,
                             frozen=False)
        
        assert ('in_node', 'out_node', 'weight') == link_gene.__slots__
        
        assert link_gene.id == 1
        assert link_gene.enabled == True
        assert link_gene.frozen == False
        assert link_gene.in_node == 1
        assert link_gene.out_node == 2
        assert link_gene.weight == 0.5
        assert link_gene.mutation_number == 0
        
    def test_create_node_gene(self):
        node_gene = NodeGene() 
        
        assert type(node_gene) == NodeGene
        assert issubclass(type(node_gene), BaseGene)
        
    def test_node_gene_fields(self):
        node_gene = NodeGene(node_type=NodeType.BIAS,
                             enabled=False,
                             frozen=True)
        
        assert ('type', 'bias', 'activation_function', 'aggregation_function') == node_gene.__slots__
        
        assert node_gene.id == 1
        assert node_gene.enabled == False
        assert node_gene.frozen == True
        assert node_gene.type == NodeType.BIAS
        # assert node_gene.activation_function == ActivationFuncType.SIGMOID
        assert node_gene.aggregation_function == AggregationFuncType.SUM
        
    def test_genes_comparison(self):
        node_gene1 = NodeGene()
        node_gene2 = NodeGene()
        node_gene3 = node_gene1

        assert node_gene1 < node_gene2
        assert node_gene2 > node_gene1
        assert node_gene1 == node_gene3
        assert node_gene3 != node_gene2
        
        link_gene1 = LinkGene(in_node=node_gene1.id,
                              out_node=node_gene2.id)
        link_gene2 = LinkGene(in_node=node_gene1.id,
                              out_node=node_gene2.id)
        link_gene3 = link_gene1
        
        assert link_gene1 < link_gene2
        assert link_gene2 > link_gene1
        assert link_gene1 == link_gene3
        assert link_gene3 != link_gene2
        
    class TestGeneMethods:
        @pytest.fixture(autouse=True)
        def setup(self):
            self.node_gene1 = NodeGene()
            self.node_gene2 = NodeGene()
            yield
            self.node_gene1 = None
            self.node_gene2 = None
            reset_innovation_table()
            
        def test_distance(self):
            self.node_gene1.bias = 1
            self.node_gene2.bias = 0.5
            dist = self.node_gene1.distance(other_node=self.node_gene2)
            
            assert dist == 0.5
            
            self.node_gene1.aggregation_function = None
            dist = self.node_gene1.distance(other_node=self.node_gene2)
            
            assert dist == 0.5 + 1
            
            self.node_gene2.activation_function = None
            dist = self.node_gene2.distance(other_node=self.node_gene1)
            
            assert dist == 0.5 + 1 + 1
            
            
        def test_gene_copy(self):
            # Nodes
            node = NodeGene()
            copy_node = node.duplicate()
            
            assert node.type == copy_node.type
            assert node.id == copy_node.id
            
            copy_node.type = NodeType.INPUT
                
            assert node.type != copy_node.type
            
            # Links
            link = LinkGene(in_node=node,
                            out_node=copy_node)
            
            copy_link = link.duplicate()
                        
            assert link.id == copy_link.id
            assert link.in_node == copy_link.in_node
            assert link.out_node == copy_link.out_node
            assert link.weight == copy_link.weight
           
            copy_link.in_node = link.out_node  
            copy_link.out_node = link.in_node
            copy_link.weight = link.weight + 0.01
            
            assert id(copy_link.in_node) != id(link.in_node)
            assert id(copy_link.out_node) != id(link.out_node)
            assert id(copy_link.weight) != id(link.weight)
                              
        def test_is_allele(self):
            node = NodeGene()
            node2 = NodeGene()
            copy_node = node.duplicate()
            
            assert node.is_allele(copy_node)
            assert not node.is_allele(node2)
            
            link = LinkGene(in_node=node,
                            out_node=node2)
            
            link2 = LinkGene(in_node=node,
                            out_node=node2)
            
            link3 = LinkGene(in_node=node2,
                             out_node=node)
            
            link4 = LinkGene(in_node=node,
                             out_node=copy_node)
            
            assert link.is_allele(link2)
            # assert link.is_allele(link3)
            assert not link.is_allele(link4)
            
            
            