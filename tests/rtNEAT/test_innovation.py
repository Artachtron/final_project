import pytest, os, sys


sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'rtNEAT')))
from project.src.rtNEAT.innovation import  InnovTable, Innovation, InnovationType
from project.src.rtNEAT.genes import NodeGene, LinkGene, NodeType

class TestInnovTable:
    @pytest.fixture(autouse=True)
    def setup(self):
        InnovTable.reset_innovation_table()
        sensor_node = NodeGene(node_type=NodeType.INPUT)
        
        action_node = NodeGene(node_type=NodeType.OUTPUT)
        
        link0 = LinkGene(in_node=sensor_node,
                        out_node=action_node,
                        weight=1.0)
        
        nodes = [sensor_node, action_node]
        links = [link0]
        
        self.nodes = {node.id: node for node in nodes}
        self.links = {link.id: link for link in links}
                
     
        
            
    def test_increment(self):
        # Link
        assert InnovTable.get_link_number() == 2
        InnovTable.increment_link()
        assert InnovTable.get_link_number() == 3
        InnovTable.increment_link(amount=5)
        assert InnovTable.get_link_number() == 8
        
        # Node
        assert InnovTable.get_node_number() == 3
        InnovTable.increment_node()
        assert InnovTable.get_node_number() == 4
        InnovTable.increment_node(amount=4)
        assert InnovTable.get_node_number() == 8
    
    def test_setter_and_getter(self):
        # Link
        assert InnovTable.link_number == 2
        InnovTable.link_number = 8
        assert InnovTable.link_number == 8
        InnovTable.link_number = 4
        assert InnovTable.link_number == 8
        
        # Node
        assert InnovTable.node_number == 3
        InnovTable.node_number = 8
        assert InnovTable.node_number == 8
        InnovTable.node_number = 4
        assert InnovTable.node_number == 8
        
    
    def test_check_innovation_already_exists(self):
            innovation_type = InnovationType.NEW_LINK
            node1, node2 = self.nodes[1], self.nodes[2]
            weight = 1.0
            innovation_number1 = 1
            
            # exists
            innovation = Innovation(node_in_id=node1.id,
                                    node_out_id=node2.id,
                                    innovation_type=innovation_type,
                                    new_weight=weight,
                                    innovation_number1=innovation_number1)
            
            exists = InnovTable._check_innovation_already_exists(the_innovation=innovation,
                                                                    innovation_type=innovation_type,
                                                                    in_node=node1.id,
                                                                    out_node=node2.id)
            assert exists 
            
            
            # Not exists
                      
            exists = InnovTable._check_innovation_already_exists(the_innovation=innovation,
                                                                    innovation_type=innovation_type,
                                                                    in_node=node2.id,
                                                                    out_node=node1.id)
            assert not exists
            
            exists = InnovTable._check_innovation_already_exists(the_innovation=innovation,
                                                                    innovation_type=InnovationType.NEW_NODE,
                                                                    in_node=node1.id,
                                                                    out_node=3) 
            assert not exists
     
    def test_get_innovation(self):
        node1, node2 = self.nodes[1], self.nodes[2]
        assert InnovTable.link_number == 2
        
        # new innovation
        innovation = InnovTable.get_innovation( in_node=node1.id,
                                                out_node=node2.id,
                                                innovation_type=InnovationType.NEW_NODE)
        
        assert innovation.innovation_type == InnovationType.NEW_NODE
        assert innovation.node_in_id == node1.id
        assert innovation.node_out_id == node2.id
        assert innovation.new_node_id == InnovTable.node_number - 1
        assert innovation.innovation_number1 == InnovTable.link_number - 2
        assert innovation.innovation_number2 == InnovTable.link_number - 1
        assert InnovTable.node_number == 4
        assert InnovTable.link_number == 4
        
        # same innovaiton
        innovation = InnovTable.get_innovation( in_node=node1.id,
                                                out_node=node2.id,
                                                innovation_type=InnovationType.NEW_NODE)
        
        assert innovation.innovation_type == InnovationType.NEW_NODE
        assert innovation.node_in_id == node1.id
        assert innovation.node_out_id == node2.id
        assert innovation.new_node_id == InnovTable.node_number - 1
        assert innovation.innovation_number1 == InnovTable.link_number - 2
        assert innovation.innovation_number2 == InnovTable.link_number - 1
        assert InnovTable.node_number == 4
        assert InnovTable.link_number == 4
 
    
            
    def test_create_innovation(self):
        node1, node2 = self.nodes[1], self.nodes[2]
        initial_link_num = 4
        initial_node_num = 5
        InnovTable.node_number = initial_node_num
        InnovTable.link_number = initial_link_num
        current_innovation = InnovTable.link_number
        assert InnovTable.link_number == initial_link_num
        assert InnovTable.node_number == initial_node_num
        
        # New link
        innovation = InnovTable._create_innovation(in_node=node1.id,
                                                    out_node=node2.id,
                                                    innovation_type=InnovationType.NEW_LINK)
        
        assert InnovTable.link_number == initial_link_num + 1
        assert InnovTable.node_number == initial_node_num
        assert innovation.innovation_type == InnovationType.NEW_LINK
        assert innovation.node_in_id == node1.id
        assert innovation.node_out_id == node2.id
        assert innovation.innovation_number1 == current_innovation
        assert innovation.innovation_number2 == -1
        assert innovation.weight != -1
        assert innovation.old_innovation_number == -1
        assert innovation.new_node_id == -1
        
        # New node
        current_innovation = InnovTable.link_number
        innovation = InnovTable._create_innovation(in_node=node1.id,
                                                    out_node=node2.id,
                                                    innovation_type=InnovationType.NEW_NODE,
                                                    old_innovation_number=8)
        
        assert innovation.innovation_number1 == current_innovation
        assert innovation.innovation_number2 == current_innovation + 1
        assert InnovTable.link_number == current_innovation + 2
        assert InnovTable.node_number == initial_node_num + 1
        assert innovation.innovation_type == InnovationType.NEW_NODE
        assert innovation.node_in_id == node1.id
        assert innovation.node_out_id == node2.id
        assert innovation.weight == -1
        assert innovation.new_node_id == initial_node_num
        assert innovation.old_innovation_number == 8