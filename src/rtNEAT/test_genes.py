from gene import BaseGene, LinkGene, NodeGene, NodeType, ActivationFuncType, AggregationFuncType

class TestGene:
    def test_create_base_gene(self):
        base_gene = BaseGene(gene_id=1,
                             enable=True,
                             freeze=False)  
        
        assert type(base_gene) == BaseGene 
        
    def test_base_gene_fields(self):
        base_gene = BaseGene(gene_id=1,
                             enable=True,
                             freeze=False) 
        
        assert set(['id', 'enabled', 'frozen']).issubset(vars(base_gene))
        assert base_gene.id == 1
        assert base_gene.enabled == True
        assert base_gene.frozen == False
        
    def test_create_link_gene(self):
        link_gene = LinkGene(in_node_id=1,
                             out_node_id=2)
        
        assert type(link_gene) == LinkGene
        assert issubclass(type(link_gene), BaseGene)
        
    def test_link_gene_fields(self):
        link_gene = LinkGene(in_node_id=1,
                             out_node_id=2,
                             weight=0.5,
                             mutation_number=0,
                             recurrence=True,
                             enable=True,
                             freeze=False)
        
        assert {'id', 'enabled', 'frozen', 'in_node', 'out_node',
                'weight', 'mutation_number','innovation_number',
                'recurrence'}.issubset(vars(link_gene))
        
        assert link_gene.id == 1
        assert link_gene.enabled == True
        assert link_gene.frozen == False
        assert link_gene.in_node == 1
        assert link_gene.out_node == 2
        assert link_gene.weight == 0.5
        assert link_gene.mutation_number == 0
        assert link_gene.innovation_number ==1
        assert link_gene.recurrence == True
        
    def test_create_node_gene(self):
        node_gene = NodeGene() 
        
        assert type(node_gene) == NodeGene
        assert issubclass(type(node_gene), BaseGene)
        
    def test_node_gene_fields(self):
        node_gene = NodeGene(node_type=NodeType.BIAS,
                             enable=False,
                             freeze=True)
        
        assert {'id', 'enabled', 'frozen', 'type', 'activation_phase',
                'activation_value','activation_function',
                'aggregation_function'}.issubset(vars(node_gene))
        
        assert node_gene.id == 1
        assert node_gene.enabled == False
        assert node_gene.frozen == True
        assert node_gene.type == NodeType.BIAS
        assert node_gene.activation_phase == 0
        assert node_gene.activation_value == 0.0
        assert node_gene.activation_function == ActivationFuncType.SIGMOID
        assert node_gene.aggregation_function == AggregationFuncType.SUM