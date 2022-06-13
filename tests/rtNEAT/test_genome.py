import pytest, os, sys
import numpy as np
from numpy.random import choice, randint

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'rtNEAT')))
from project.src.rtNEAT.genome import Genome
from project.src.rtNEAT.genes import NodeGene, LinkGene, reset_innovation_table, NodeType
from project.src.rtNEAT.neat import Config

Config.configure()

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
        
        assert {'id','_node_genes','_link_genes'}.issubset(vars(genome))
        
        assert genome.id == 0
        assert genome._node_genes == nodes
        assert genome._link_genes == genes
        
    def test_genesis(self):
        genome = Genome.genesis(genome_id=0,
                                n_inputs=3,
                                n_outputs=5)
        
        assert genome.n_node_genes == 3 + 5
        assert genome.n_link_genes == 3 * 5
        assert list(genome.size.values()) == [8, 15]
        
        genome2 = Genome.genesis(   genome_id=2,
                                    n_inputs=3,
                                    n_outputs=5)
        
        for id1, id2 in zip(genome._node_genes, genome2._node_genes):
            assert id1 == id2
        
        for id1, id2 in zip(genome._link_genes, genome2._link_genes):
            assert id1 == id2
            
    class TestGenomeMethods:
        class TestGeneticDistance:
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
                
                self.genome1 = Genome(genome_id=1,
                                node_genes=self.nodes,
                                link_genes=self.links)
                
                self.genome2 = Genome(genome_id=2,
                                    node_genes={node.id: node for node in self.nodes.values() if node.id < 5},
                                    link_genes={link.id: link for link in self.links.values() if link.id < 3})
                
                self.genome2_extended = Genome(genome_id=2,
                                        node_genes={node.id: node for node in self.nodes.values() if node.id < 5},
                                        link_genes={link.id: link for link in self.links.values() if link.id < 3})
                
                self.genome2_extended.add_node(NodeGene(node_id=1,
                                                        mutation_number=1))
                
                self.genome2_extended.add_link(LinkGene(link_id=1,
                                                        in_node=sensor_node,
                                                        out_node=action_node,
                                                        weight=1.0,
                                                        mutation_number=1))
                    
                self.genome3 = Genome(genome_id=3,
                                    node_genes={node.id: node for node in self.nodes.values() if node.id in [1,2,3,5,6]},
                                    link_genes={link.id: link for link in self.links.values() if link.id < 4})
                
                self.genome4 = Genome(genome_id=4,
                                    node_genes={node.id: node for node in self.nodes.values() if node.id in list(range(1,7))},
                                    link_genes={link.id: link for link in self.links.values() if link.id in list(range(2,5))})
                            
                np.random.seed(1)

                yield
                
                reset_innovation_table()   

            def test_insert_gene_in_dict(self):
                node = NodeGene(node_id=1)
                nodes_dict = Genome.insert_gene_in_dict(genes_dict={},
                                                        gene=node)
                genome = Genome(genome_id=0,
                                    node_genes={},
                                    link_genes={})
                
                assert nodes_dict == {1: node}
                assert genome._node_genes == {}
                
                genome.add_node(node=node)
                assert genome._node_genes == nodes_dict
                
            def test_genetical_gene_distance(self):
                # Node distance
                ## Excess nodes
                dist = Genome._genetical_gene_distance( gene_dict1 = self.genome1._node_genes,
                                                        gene_dict2 = self.genome2._node_genes)
                assert dist == 2
                
                ## Disjoint
                dist = Genome._genetical_gene_distance( gene_dict1 = self.genome3._node_genes,
                                                        gene_dict2 = self.genome4._node_genes)
                assert dist == 1
                            
                ## Mutation
                dist = Genome._genetical_gene_distance( gene_dict1 = self.genome2._node_genes,
                                                        gene_dict2 = self.genome2_extended._node_genes)
                assert dist == 0.5/5
                
                # Link distance
                ## Excess nodes
                dist = Genome._genetical_gene_distance( gene_dict1 = self.genome1._link_genes,
                                                        gene_dict2 = self.genome2._link_genes)
                assert dist == 2
                
                ## Disjoint
                dist = Genome._genetical_gene_distance( gene_dict1 = self.genome3._link_genes,
                                                        gene_dict2 = self.genome4._link_genes)
                assert dist == 1
                            
                ## Mutation
                dist = Genome._genetical_gene_distance( gene_dict1 = self.genome2._link_genes,
                                                        gene_dict2 = self.genome2_extended._link_genes)
                assert dist == 0.5/3
                
            def test_genetical_distance(self):
                # Full distance
                ## Excess nodes
                dist = Genome.genetical_distance(   genome1 = self.genome1,
                                                    genome2 = self.genome2)
                assert dist == 4
                
                ## Disjoint
                dist = Genome.genetical_distance(   genome1 = self.genome3,
                                                    genome2 = self.genome4)
                assert dist == 2
                            
                ## Mutation
                dist = Genome.genetical_distance(   genome1 = self.genome2,
                                                    genome2 = self.genome2_extended)
                assert dist == 0.5/3 + 0.5/5
            
        class TestMutation:
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
                
                self.genome1 = Genome(genome_id=1,
                                node_genes=self.nodes,
                                link_genes=self.links)
                
                self.genome2 = Genome(genome_id=2,
                                    node_genes={node.id: node for node in self.nodes.values() if node.id < 5},
                                    link_genes={link.id: link for link in self.links.values() if link.id < 3})
                
                np.random.seed(1)
                
                yield
                
                reset_innovation_table()
            
            def test_mutate_links_weight(self):
                """ Config.weight_mutate_prob = 1.0
                Config.new_link_prob = 0.5
                Config.weight_mutate_power = 0.5 """
                
                weights = [gene.weight for gene in self.genome1.link_genes]
                self.genome1._mutate_link_weights()
                new_weights = [gene.weight for gene in self.genome1.link_genes]
                
                assert new_weights[2] != weights[2] 
            
            def test_find_random_link(self):
                # Random link in link genes' list
                link = self.genome1._find_random_link()
                assert link in self.genome1.link_genes
                
                # No link valid
                for link in self.genome1.link_genes:
                    link.enabled = False
                
                link = self.genome1._find_random_link()    
                assert not link
                
                # only one valid link to choose from
                self.genome1._link_genes[2].enabled = True
                for _ in range(100):
                    link = self.genome1._find_random_link()
                    assert link == self.genome1._link_genes[2]
                    
            def test_create_new_node(self):
                in_node, out_node = list(self.nodes.values())[:2]
                node, link1, link2 = self.genome1._create_node(node_id=3,
                                                                in_node=in_node,
                                                                out_node=out_node,
                                                                innovation_number1=1,
                                                                innovation_number2=2,
                                                                old_weight=0.34)
            
                assert node.id == 3
                assert node.type.name == NodeType.HIDDEN.name
                assert link1.in_node == in_node
                assert link1.out_node == node
                assert link1.weight == 1.0
                assert link1.id == 1
                assert link2.in_node == node
                assert link2.out_node == out_node
                assert link2.weight == 0.34
                assert link2.id == 2
                
            def test_new_node_innovation(self):
                # New innovation
                link = self.genome1._link_genes[1]
                current_node = self.genome1.get_last_node_id() 
                current_link = self.genome1.get_last_link_id()   
                new_node, new_link1, new_link2 = self.genome1._new_node_innovation(old_link=link)
                
                assert new_node.id == current_node + 1
                assert new_link1.id == current_link + 1
                assert new_link1.weight == 1.0
                assert new_link2.id == current_link + 2
                assert new_link2.weight == link.weight
                
                # New innovation2 
                link = self.genome1._link_genes[2]
                new_node, new_link1, new_link2 = self.genome1._new_node_innovation(old_link=link)
                assert new_node.id == current_node + 2
                assert new_link1.id == current_link + 3
                assert new_link2.id == current_link + 4
                
                # Same innovation as first one
                link = self.genome2._link_genes[1]
                link.weight = 0.5
                new_node, new_link1, new_link2 = self.genome1._new_node_innovation(old_link=link)
                assert new_node.id == current_node + 1
                assert new_link1.id == current_link + 1
                assert new_link1.weight == 1
                assert new_link2.id == current_link + 2
                assert new_link2.weight == link.weight 
            
            def test_mutate_add_node(self):
                nodes = {node.id: node for node in self.nodes.values() if node.id > 4}
                links = {link.id: link for link in self.links.values() if link.id > 3}

                genome1 = Genome(genome_id=1,
                                node_genes=nodes,
                                link_genes=links)
                            
                initial_link = genome1.get_last_link_id()
                initial_node = genome1.get_last_node_id()
                
                # Innovation is novel
                assert len(genome1.node_genes) == 2
                assert genome1.n_link_genes == 1
                success = genome1._mutate_add_node()
                assert genome1._link_genes[4].enabled == False
                assert success
                assert genome1.get_last_link_id() == initial_link+2
                assert genome1.get_last_node_id() == initial_node+1
                assert len(genome1.node_genes) == 3
                assert genome1.n_link_genes == 3
                nodes = {node.id: node for node in self.nodes.values() if node.id > 4}
                assert list(set(genome1._node_genes.keys()) - set(nodes.keys()))[0] == 7
                
                # Innovation exists
                links = {link.id: link for link in self.links.values() if link.id > 3}
                genome2 = Genome(genome_id=2,
                                node_genes=nodes,
                                link_genes=links)
                                    
                genome2._link_genes[4].enabled = True
                #assert genome2.get_last_link_id() == initial_innov+2
                new_link = LinkGene(in_node=1,
                                    out_node=2)
                assert new_link.id == initial_link+3
                assert len(genome2.node_genes) == 2
                assert genome2.n_link_genes == 1
                success = genome2._mutate_add_node()
                assert success
                assert genome2.get_last_link_id() == initial_link+2
                assert genome2.get_last_node_id() == initial_node+1
                assert len(genome2.node_genes) == 3
                assert genome2.n_link_genes == 3
                
            def test_is_valid_link(self):
                hidden_node = NodeGene(node_type=NodeType.HIDDEN)
                input_node = NodeGene(node_type=NodeType.INPUT)
                output_node = NodeGene(node_type=NodeType.OUTPUT)
                
                # Valid
                node1, node2 = input_node, output_node
                
                validity = self.genome1._is_valid_link( node_in=node1,
                                                        node_out=node2)
                assert validity
                
                # Not valid, same in and out node
                node1, node2 = hidden_node, hidden_node

                validity = self.genome1._is_valid_link( node_in=node1,
                                                        node_out=node2)
                assert not validity
                
                #Not valid, input as out node
                node1, node2 = hidden_node, input_node
                
                validity = self.genome1._is_valid_link( node_in=node1,
                                                        node_out=node2)
                assert not validity
                
                #Not valid, output as hidden
                node1, node2 = output_node, hidden_node
                
                validity = self.genome1._is_valid_link( node_in=node1,
                                                        node_out=node2)
                assert not validity
                
            def test_find_valid_link(self):
                for _ in range(100):
                    node_in, node_out = self.genome1._find_valid_link()
                    
                    if node_in:
                        assert node_in.type != NodeType.OUTPUT
                        assert node_out.type != NodeType.INPUT  
                        assert node_in != node_out  
                        
            def test_new_link_gene(self):
                #New innovation
                node1, node2 = self.nodes[1], self.nodes[4]
                current_link = self.genome1.get_last_link_id() 
                
                link = self.genome1._new_link_gene( in_node=node1,
                                                    out_node=node2)
                
                assert link.id == current_link + 1
                weight = link.weight
                
                #New innovation 2
                node1, node2 = self.nodes[1], self.nodes[5]
                link = self.genome1._new_link_gene( in_node=node1,
                                                    out_node=node2)
                assert link.id == current_link + 2
                assert link.weight != weight
                
                #Same as first innovation
                node1, node2 = self.nodes[1], self.nodes[4]
                link = self.genome1._new_link_gene( in_node=node1,
                                                    out_node=node2)
                assert link.id == current_link + 1
                assert link.weight == weight
                    
            def test_mutate_add_link(self):
                initial_link_size = self.genome1.n_link_genes
                assert len(self.genome1.link_genes) == initial_link_size
                
                count_success = 0
                for _ in range(1,10):
                    if self.genome1._mutate_add_link(tries=20):
                        count_success += 1
                        assert self.genome1.n_link_genes == initial_link_size + count_success
                        
                        
        class TestReproduction:
            def test_is_IO_node(self):
                hidden_node = NodeGene(node_type=NodeType.HIDDEN)
                input_node = NodeGene(node_type=NodeType.INPUT)
                output_node = NodeGene(node_type=NodeType.OUTPUT)
                
                #Hidden
                assert not Genome._is_IO_node(node=hidden_node)
                #Input
                assert Genome._is_IO_node(node=input_node)
                #Output
                assert Genome._is_IO_node(node=output_node)
            
            def test_choose_gene(self):
                nodes = {}
                links = {}
                
                for _ in range(1,20):
                    Genome.insert_gene_in_dict(genes_dict=nodes,
                                               gene=NodeGene())
                for _ in range(1,10):
                    Genome.insert_gene_in_dict(genes_dict=links,
                                               gene=LinkGene(in_node=nodes[randint(1,20)],
                                                             out_node=nodes[randint(1,20)]))
                
                links1 = {link for link in links}
                    
                genome1 = Genome(genome_id=1,
                                 node_genes=nodes,
                                 link_genes=links)
                
                genome2 = Genome(genome_id=2,
                                 node_genes=nodes,
                                 link_genes=links)
                
                _choose_genes_to_transmit