from project.src.rtNEAT.genes import (ActivationFuncType, AggregationFuncType,
                                      LinkGene, NodeGene, NodeType)
from project.src.rtNEAT.phenes import Link, Node


class TestPhenes:
    def test_create_node(self):
        node = Node(node_id=0)
        assert type(node) == Node
    
    def test_node_fields(self):
        node = Node(node_id=1,
                    node_type=NodeType.BIAS,
                    enabled=False)
        
        assert node.__slots__ == ('activation_phase', 'activation_value',
                                  'activation_function', 'aggregation_function',
                                  'incoming', 'outgoing', 'type', 'bias',
                                  'associated_values', 'output_type')
        
        assert node.id == 1
        assert node.type == NodeType.BIAS
        assert node.enabled == False
        assert node.aggregation_function == sum
        # assert node.activation_function == sigmoid
        assert node.activation_phase == 0
        assert node.activation_value == 0.0
        assert node.incoming == {}
        assert node.outgoing == {}
                
    def test_create_link(self):
        link = Link(link_id=0,
                    weight=0.5,
                    in_node=Node(0),
                    out_node=Node(1))
        
        assert type(link) == Link
        
    def test_link_fields(self):
        link = Link(link_id=1,
                    weight=0.5,
                    in_node=Node(0),
                    out_node=Node(1),
                    enabled=False)
        
        assert link.__slots__ == ('weight', 'in_node', 'out_node')
        
        assert link.id == 1
        assert link.weight == 0.5
        assert link.in_node.id == 0
        assert link.out_node.id == 1
        assert link.enabled == False
    
    class TestPhenesMethhods:  
        def test_synthesis(self):
            node_gene = NodeGene()
            
            node = Node.synthesis(node_gene.transcript())
            assert type(node) == Node
            assert node.id == node_gene.id
            assert node.type == node_gene.type
            
            node2 = Node.synthesis(NodeGene().transcript())

            link_gene = LinkGene(in_node=node.id,
                                out_node=node2.id)
            
            """ dict_link = 
            dict_link['in_node'] = node
            dict_link['out_node'] = node2 """
            
            link = Link.synthesis(link_gene.transcript())
            assert type(link) == Link
            assert link.id == link_gene.id
            assert link.weight == link_gene.weight
