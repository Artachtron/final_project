
import os, sys

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'rtNEAT')))
from project.src.rtNEAT.phenes import Link, Node
from project.src.rtNEAT.genes import NodeType, ActivationFuncType, AggregationFuncType
from project.src.rtNEAT.genes import LinkGene, NodeGene


class TestPhenes:
    def test_create_node(self):
        node = Node(node_id=0)
        assert type(node) == Node
    
    def test_node_fields(self):
        node = Node(node_id=1,
                    node_type=NodeType.BIAS,
                    enabled=False)
        
        assert {'id', 'type', 'enabled',
                'activation_function','aggregation_function',
                'activation_phase', 'activation_value',
                'incoming','outgoing'}.issubset(vars(node))
        
        assert node.id == 1
        assert node.type == NodeType.BIAS
        assert node.enabled == False
        assert node.aggregation_function.name == AggregationFuncType.SUM.name
        assert node.activation_function.name == ActivationFuncType.SIGMOID.name
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
        
        assert {'id', 'weight', 'in_node', 'out_node',
                'enabled'}.issubset(vars(link))
        
        assert link.id == 1
        assert link.weight == 0.5
        assert link.in_node.id == 0
        assert link.out_node.id == 1
        assert link.enabled == False
    
    class PhenesMethhods:  
        def test_synthesis(self):
            node_gene = Node()
            
            node = Node.synthesis(**node_gene.transcript())
            assert type(node) == Node
            assert node.id == node_gene.id
            
            node2 = Node.synthesis(**Node().transcript())

            link_gene = LinkGene(in_node=node.id,
                                out_node=node2.id)
            
            """ dict_link = 
            dict_link['in_node'] = node
            dict_link['out_node'] = node2 """
            
            link = Link.synthesis(**link_gene.transcript())
            assert type(link) == Link
            assert link.id == link_gene.id