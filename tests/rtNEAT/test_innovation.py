import pytest, os, sys


sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'rtNEAT')))
from project.src.rtNEAT.innovation import Innovation, InnovTable


class TestInnovTable:
    @pytest.fixture(autouse=True)
    def setup(self):
        yield
        InnovTable.reset_innovation_table()
            
    def test_increment(self):
        # Link
        assert InnovTable.get_link_number() == 1
        InnovTable.increment_link()
        assert InnovTable.get_link_number() == 2
        InnovTable.increment_link(amount=5)
        assert InnovTable.get_link_number() == 7
        
        # Node
        assert InnovTable.get_node_number() == 1
        InnovTable.increment_node()
        assert InnovTable.get_node_number() == 2
        InnovTable.increment_node(amount=4)
        assert InnovTable.get_node_number() == 6
    
    def test_setter_and_getter(self):
        # Link
        assert InnovTable.link_number == 1
        InnovTable.link_number = 8
        assert InnovTable.link_number == 8
        InnovTable.link_number = 4
        assert InnovTable.link_number == 8
        
        # Node
        assert InnovTable.node_number == 1
        InnovTable.node_number = 8
        assert InnovTable.node_number == 8
        InnovTable.node_number = 4
        assert InnovTable.node_number == 8
        
    
""" @pytest.fixture(autouse=True)
def setup(self):
    sensor_node = Node(node_type=NodeType.INPUT)
        
    action_node = Node(node_type=NodeType.OUTPUT)
    
    gene0 = Gene(in_node=sensor_node,
                out_node=action_node,
                weight=1.0,
                innovation_number=7,
                mutation_number=0)
    
    self.nodes = np.array([sensor_node, action_node])
    self.genes = np.array([gene0])
    
    yield
    InnovTable.reset_innovation_table() 
    
def test_check_innovation_already_exists(self):
        innovation_type = InnovationType.NEW_LINK
        node1, node2 = self.nodes[:2]
        weight = 1.0
        innovation_number1 = 0
        recurrence = False
        
        # exists
        innovation = Innovation(node_in_id=node1.id,
                                node_out_id=node2.id,
                                innovation_type=innovation_type,
                                new_weight=weight,
                                innovation_number1=innovation_number1)
        
        exists = InnovTable._check_innovation_already_exists(the_innovation=innovation,
                                                                innovation_type=innovation_type,
                                                                in_node=node1,
                                                                out_node=node2,
                                                                recurrence=recurrence)
        assert exists 
        
        exists = InnovTable._check_innovation_already_exists(the_innovation=innovation,
                                                                innovation_type=innovation_type,
                                                                in_node=node1,
                                                                out_node=node2,
                                                                recurrence=not recurrence)  
        assert not exists
        
        exists = InnovTable._check_innovation_already_exists(the_innovation=innovation,
                                                                innovation_type=innovation_type,
                                                                in_node=node2,
                                                                out_node=node1,
                                                                recurrence=recurrence) 
        assert not exists
        
        exists = InnovTable._check_innovation_already_exists(the_innovation=innovation,
                                                                innovation_type=InnovationType.NEW_NODE,
                                                                in_node=node1,
                                                                out_node=node2,
                                                                recurrence=recurrence) 
        assert not exists
        
def test_get_innovation(self):
    node1, node2 = self.nodes[:2]
    assert InnovTable.get_innovation_number() == 1
    
    # new innovation
    innovation = InnovTable.get_innovation( in_node=node1,
                                            out_node=node2,
                                            innovation_type=InnovationType.NEW_NODE,
                                            recurrence=False)
    
    assert innovation.innovation_type == InnovationType.NEW_NODE
    assert innovation.node_in_id == node1.id
    assert innovation.node_out_id == node2.id
    assert innovation.recurrence_flag == False
    assert innovation.new_node_id == InnovTable.get_node_number() - 1
    assert innovation.innovation_number1 == InnovTable.get_innovation_number() - 2
    assert innovation.innovation_number2 == InnovTable.get_innovation_number() - 1
    assert InnovTable.get_innovation_number() == 3
    
    # same innovaiton
    innovation = InnovTable.get_innovation( in_node=node1,
                                            out_node=node2,
                                            innovation_type=InnovationType.NEW_NODE,
                                            recurrence=False)
    
    assert innovation.innovation_type == InnovationType.NEW_NODE
    assert innovation.node_in_id == node1.id
    assert innovation.node_out_id == node2.id
    assert innovation.recurrence_flag == False
    assert innovation.new_node_id == InnovTable.get_node_number() - 1
    assert innovation.innovation_number1 == InnovTable.get_innovation_number() - 2
    assert innovation.innovation_number2 == InnovTable.get_innovation_number() - 1
    assert InnovTable.get_innovation_number() == 3
        
def test_create_innovation(self):
    node1, node2  = self.nodes[:2]
    initial_innov_num = 4
    initial_node_num = 5
    InnovTable.increment_node(amount=initial_node_num-1)
    InnovTable.increment_innov(amount=initial_innov_num-1)
    current_innovation = InnovTable.get_innovation_number()
    
    assert InnovTable.get_innovation_number() == initial_innov_num
    
    # New link
    innovation = InnovTable._create_innovation(in_node=node1,
                                                out_node=node2,
                                                innovation_type=InnovationType.NEW_LINK)
    
    assert InnovTable.get_innovation_number() == current_innovation + 1
    assert innovation.innovation_type == InnovationType.NEW_LINK
    assert innovation.node_in_id == node1.id
    assert innovation.node_out_id == node2.id
    assert innovation.recurrence_flag == False
    assert innovation.innovation_number1 == current_innovation
    assert innovation.innovation_number2 == -1
    assert innovation.weight != -1
    assert innovation.old_innovation_number == -1
    assert innovation.new_node_id == -1
    
    # New node
    current_innovation = InnovTable.get_innovation_number()
    innovation = InnovTable._create_innovation(in_node=node1,
                                                out_node=node2,
                                                innovation_type=InnovationType.NEW_NODE,
                                                old_innovation_number=8)
    
    assert innovation.innovation_number1 == current_innovation
    assert innovation.innovation_number2 == current_innovation + 1
    assert InnovTable.get_innovation_number() == current_innovation + 2
    assert innovation.innovation_type == InnovationType.NEW_NODE
    assert innovation.node_in_id == node1.id
    assert innovation.node_out_id == node2.id
    assert innovation.recurrence_flag == False
    assert innovation.weight == -1
    assert innovation.new_node_id == 7
    assert innovation.old_innovation_number == 8 """