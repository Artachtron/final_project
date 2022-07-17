import os
import random
import sys

import numpy as np
import pytest
from numpy.random import choice

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'rtNEAT')))
from project.src.rtNEAT.genes import (LinkGene, NodeGene, NodeType,
                                      reset_innovation_table)
from project.src.rtNEAT.genome import Genome
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

        assert {'_node_genes','_link_genes'}.issubset(vars(genome))

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

                gene0 = LinkGene(in_node=sensor_node.id,
                                out_node=action_node.id,
                                weight=1.0,
                                mutation_number=0)

                gene1 = LinkGene(in_node=sensor_node2.id,
                                out_node=action_node2.id,
                                weight=1.0,
                                mutation_number=0)

                gene2 = LinkGene(in_node=sensor_node3.id,
                                out_node=action_node3.id,
                                weight=1.0,
                                mutation_number=0)

                gene3 = LinkGene(in_node=sensor_node3.id,
                                out_node=action_node3.id,
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

                self.genome2_extended.add_node(NodeGene(gene_id=1,
                                                        mutation_number=1))

                self.genome2_extended.add_link(LinkGene(link_id=1,
                                                        in_node=sensor_node.id,
                                                        out_node=action_node.id,
                                                        weight=1.0,
                                                        mutation_number=1))

                self.genome3 = Genome(genome_id=3,
                                    node_genes={node.id: node for node in self.nodes.values() if node.id in [1,2,3,5,6]},
                                    link_genes={link.id: link for link in self.links.values() if link.id < 5})

                self.genome4 = Genome(genome_id=4,
                                    node_genes={node.id: node for node in self.nodes.values() if node.id in list(range(1,7))},
                                    link_genes={link.id: link for link in self.links.values() if link.id in list(range(2,5))})

                random.seed(1)

                yield

                reset_innovation_table()

            def test_insert_gene_in_dict(self):
                node = NodeGene(gene_id=1)
                nodes_dict = Genome.insert_gene(genes_dict={},
                                                        gene=node)
                genome = Genome(genome_id=0,
                                    node_genes={},
                                    link_genes={})

                assert nodes_dict == {1: node}
                assert genome._node_genes == {}

                genome.add_node(node=node)
                assert genome._node_genes == nodes_dict

            def test_genetic_gene_distance(self):
                # Node distance
                ## Excess nodes
                dist = Genome._genetic_gene_distance( gene_dict1 = self.genome1._node_genes,
                                                      gene_dict2 = self.genome2._node_genes)
                assert dist == 2

                ## Disjoint
                dist = Genome._genetic_gene_distance( gene_dict1 = self.genome3._node_genes,
                                                      gene_dict2 = self.genome4._node_genes)
                assert dist == 1

                ## Mutation
                dist = Genome._genetic_gene_distance( gene_dict1 = self.genome2._node_genes,
                                                      gene_dict2 = self.genome2_extended._node_genes)
                assert dist == 0.5/4

                # Link distance
                ## Excess nodes
                dist = Genome._genetic_gene_distance( gene_dict1 = self.genome1._link_genes,
                                                      gene_dict2 = self.genome2._link_genes)
                assert dist == 2

                ## Disjoint
                dist = Genome._genetic_gene_distance( gene_dict1 = self.genome3._link_genes,
                                                      gene_dict2 = self.genome4._link_genes)
                assert dist == 1

                ## Mutation
                dist = Genome._genetic_gene_distance( gene_dict1 = self.genome2._link_genes,
                                                      gene_dict2 = self.genome2_extended._link_genes)
                assert dist == 0.5/2

            def test_genetic_distance(self):
                # Full distance
                ## Excess nodes
                dist = Genome.genetic_distance( genome1 = self.genome1,
                                                genome2 = self.genome2)
                assert dist == 4

                ## Disjoint
                dist = Genome.genetic_distance( genome1 = self.genome3,
                                                genome2 = self.genome4)
                assert dist == 2

                ## Mutation
                dist = Genome.genetic_distance( genome1 = self.genome2,
                                                genome2 = self.genome2_extended)
                assert dist == 0.5/2 + 0.5/4

        class TestMutation:
            @pytest.fixture(autouse=True)
            def setup(self):
                sensor_node = NodeGene(node_type=NodeType.INPUT)

                sensor_node2 = NodeGene(node_type=NodeType.INPUT)

                sensor_node3 = NodeGene(node_type=NodeType.INPUT)

                action_node = NodeGene(node_type=NodeType.OUTPUT)

                action_node2 = NodeGene(node_type=NodeType.OUTPUT)

                action_node3 = NodeGene(node_type=NodeType.OUTPUT)

                gene0 = LinkGene(in_node=sensor_node.id,
                                out_node=action_node.id,
                                weight=1.0,
                                mutation_number=0)

                gene1 = LinkGene(in_node=sensor_node2.id,
                                out_node=action_node2.id,
                                weight=1.0,
                                mutation_number=0)

                gene2 = LinkGene(in_node=sensor_node3.id,
                                out_node=action_node3.id,
                                weight=1.0,
                                mutation_number=0)

                gene3 = LinkGene(in_node=sensor_node3.id,
                                out_node=action_node3.id,
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

                #np.random.seed(1)
                random.seed(2)
                yield

                reset_innovation_table()

            def test_mutate_links_weight(self):
                """ Config.weight_mutate_prob = 1.0
                Config.new_link_prob = 0.5
                Config.weight_mutate_power = 0.5 """

                weights = [gene.weight for gene in self.genome1.get_link_genes()]
                self.genome1._mutate_links()
                new_weights = [gene.weight for gene in self.genome1.get_link_genes()]

                assert new_weights != weights

            def test_find_random_link(self):
                # Random link in link genes' list
                link = self.genome1._find_random_link()
                assert link in self.genome1.get_link_genes()

                # No link valid
                for link in self.genome1.get_link_genes():
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
                                                                in_node=in_node.id,
                                                                out_node=out_node.id,
                                                                innovation_number1=1,
                                                                innovation_number2=2,
                                                                old_weight=0.34)

                assert node.id == 3
                assert node.type.name == NodeType.HIDDEN.name
                assert link1.in_node == in_node.id
                assert link1.out_node == node.id
                assert link1.weight == 1.0
                assert link1.id == 1
                assert link2.in_node == node.id
                assert link2.out_node == out_node.id
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
                assert len(self.genome1.get_link_genes()) == initial_link_size

                count_success = 0
                for _ in range(1,10):
                    if self.genome1._mutate_add_link(tries=20):
                        count_success += 1
                        assert self.genome1.n_link_genes == initial_link_size + count_success


        class TestReproduction:
            @pytest.fixture(autouse=True)
            def setup(self):
                reset_innovation_table()
                random.seed(1)
                yield


            def test_is_IO_node(self):
                hidden_node = NodeGene(node_type=NodeType.HIDDEN)
                input_node = NodeGene(node_type=NodeType.INPUT)
                output_node = NodeGene(node_type=NodeType.OUTPUT)

                #Hidden
                assert not Genome._is_edge_node(node=hidden_node)
                #Input
                assert Genome._is_edge_node(node=input_node)
                #Output
                assert Genome._is_edge_node(node=output_node)

            def test_check_genes_conflict(self):
                # Nodes
                nodes = {}
                Genome.insert_gene(genes_dict=nodes,
                                           gene=NodeGene())

                Genome.insert_gene(genes_dict=nodes,
                                            gene=NodeGene())

                ## conflict
                conflict = Genome._check_gene_conflict(chosen_genes=nodes,
                                                        chosen_gene=nodes[1])
                assert conflict

                ## no conflict
                conflict = Genome._check_gene_conflict(chosen_genes=nodes,
                                                        chosen_gene=NodeGene())
                assert not conflict

                # Links
                links = {}
                Genome.insert_gene(genes_dict=links,
                                           gene=LinkGene(in_node=1,
                                                         out_node=2))
                ## conflict
                conflict = Genome._check_gene_conflict(chosen_genes=links,
                                                        chosen_gene=links[1])
                assert conflict

                ## conflict 2
                conflict = Genome._check_gene_conflict(chosen_genes=links,
                                                        chosen_gene=LinkGene(in_node=2,
                                                                             out_node=1))
                assert conflict

                ## no conflict
                conflict = Genome._check_gene_conflict(chosen_genes=links,
                                                        chosen_gene=LinkGene(in_node=NodeGene(),
                                                                             out_node=2))
                assert not conflict

            def test_insert_non_conflict_gene(self):
                 # Nodes
                nodes = {}
                Genome.insert_gene(genes_dict=nodes,
                                           gene=NodeGene())

                Genome.insert_gene(genes_dict=nodes,
                                            gene=NodeGene())

                assert len(nodes) == 2
                ## conflict
                Genome._insert_non_conflict_gene(genes_dict=nodes,
                                                 gene=nodes[1])
                assert len(nodes) == 2

                ## no conflict
                Genome._insert_non_conflict_gene(genes_dict=nodes,
                                                 gene=NodeGene())
                assert len(nodes) == 3

                # Links
                links = {}
                Genome.insert_gene(genes_dict=links,
                                           gene=LinkGene(in_node=1,
                                                         out_node=2))
                assert len(links) == 1
                ## conflict
                Genome._insert_non_conflict_gene(genes_dict=links,
                                                 gene=links[1])
                assert len(links) == 1

                ## conflict 2
                Genome._insert_non_conflict_gene(genes_dict=links,
                                                 gene=LinkGene(in_node=2,
                                                                out_node=1))
                assert len(links) == 1

                ## no conflict
                Genome._insert_non_conflict_gene(genes_dict=links,
                                                 gene=LinkGene(in_node=NodeGene().id,
                                                               out_node=2))
                assert len(links) == 2


            def test_choose_gene_to_transmit(self):
                nodes = {}
                links = {}

                for _ in range(1,100):
                    Genome.insert_gene(genes_dict=nodes,
                                               gene=NodeGene())
                for i in range(1,50):
                    Genome.insert_gene(genes_dict=links,
                                               gene=LinkGene(in_node=i,
                                                             out_node=2*i))

                links1 = {link.id: link for link in links.values() if link.id%2 == 0}
                links2 = {link.id: link for link in links.values() if link.id%2 == 1}
                links3 = {link.id: link.duplicate() for link in links1.values()}

                # No disjoint
                chosen_genes = Genome._genes_to_transmit(main_genome=links1,
                                                                sub_genome=links2)

                assert len(chosen_genes) == len(links1)

                for gene, link in zip(chosen_genes, links1):
                    assert gene == link

                # No disjoint 2
                chosen_genes = Genome._genes_to_transmit(main_genome=links2,
                                                                sub_genome=links1)

                assert len(chosen_genes) == len(links2)

                for gene, link in zip(chosen_genes, links2):
                    assert gene == link


                # Disjoint
                chosen_genes = Genome._genes_to_transmit(main_genome=links1,
                                                                sub_genome=links3)

                assert len(chosen_genes) == len(links1)

                for gene, link, link3 in zip(chosen_genes, links1.values(), links3):
                    assert gene == link  or gene == link3

            def test_add_missing_nodes(self):
                new_nodes = {}
                main_nodes = {}
                for _ in range(10):
                    node = NodeGene()
                    Genome.insert_gene(genes_dict=new_nodes,
                                               gene=node)
                    Genome.insert_gene(genes_dict=main_nodes,
                                               gene=node)

                for _ in range(20):
                   node = NodeGene()
                   Genome.insert_gene( genes_dict=main_nodes,
                                               gene=node)
                # No missing node
                chosen_links = {}
                Genome.insert_gene(genes_dict=chosen_links,
                                           gene=LinkGene(in_node=2,
                                                         out_node=5))

                assert len(new_nodes) == 10
                Genome._add_missing_nodes(new_links=chosen_links,
                                          new_nodes=new_nodes,
                                          main_nodes=main_nodes)

                assert len(new_nodes) == 10

                # one missing node
                Genome.insert_gene(genes_dict=chosen_links,
                                           gene=LinkGene(in_node=12,
                                                         out_node=5))

                Genome._add_missing_nodes(new_links=chosen_links,
                                          new_nodes=new_nodes,
                                          main_nodes=main_nodes)

                assert len(new_nodes) == 11

                # two missing nodes
                Genome.insert_gene(genes_dict=chosen_links,
                                           gene=LinkGene(in_node=13,
                                                         out_node=14))

                Genome._add_missing_nodes(new_links=chosen_links,
                                          new_nodes=new_nodes,
                                          main_nodes=main_nodes)

                assert len(new_nodes) == 13

                # Three missing nodes
                Genome.insert_gene(genes_dict=chosen_links,
                                           gene=LinkGene(in_node=23,
                                                         out_node=24))

                Genome.insert_gene(genes_dict=chosen_links,
                                           gene=LinkGene(in_node=25,
                                                         out_node=23))

                Genome.insert_gene(genes_dict=chosen_links,
                                           gene=LinkGene(in_node=25,
                                                         out_node=23))

                Genome.insert_gene(genes_dict=chosen_links,
                                           gene=LinkGene(in_node=14,
                                                         out_node=13))

                Genome._add_missing_nodes(new_links=chosen_links,
                                          new_nodes=new_nodes,
                                          main_nodes=main_nodes)

                assert len(new_nodes) == 16

            def test_crossover(self):
                nodes = {}
                links = {}

                for _ in range(1,101):
                    Genome.insert_gene(genes_dict=nodes,
                                       gene=NodeGene(node_type=choice([NodeType.HIDDEN,
                                                                       NodeType.INPUT,
                                                                       NodeType.OUTPUT])))
                for i in range(1,51):
                    Genome.insert_gene(genes_dict=links,
                                       gene=LinkGene(in_node=i,
                                                     out_node=2*i))

                links1 = {link.id: link for link in links.values() if link.id%2 == 0}
                links2 = {link.id: link for link in links.values() if link.id%2 == 1}

                genome =  Genome(genome_id=0,
                                 node_genes=nodes,
                                 link_genes=links)

                genome1 = Genome(genome_id=1,
                                 node_genes=nodes,
                                 link_genes=links1)

                genome2 = Genome(genome_id=2,
                                 node_genes=nodes,
                                 link_genes=links2)

                baby = Genome.crossover(genome_id=4,
                                        parent1=genome1,
                                        parent2=genome2)

                assert baby.id == 4
                assert baby.n_link_genes == 25
                assert baby.n_node_genes == 100

                #genome dominant
                baby = Genome.crossover(genome_id=5,
                                        parent1=genome1,
                                        parent2=genome)

                assert baby.id == 5
                assert baby.n_link_genes == 25
                assert baby.n_node_genes == 100

                #genome1 dominant
                baby = Genome.crossover(genome_id=6,
                                        parent1=genome1,
                                        parent2=genome)

                assert baby.id == 6
                assert baby.n_link_genes == 50
                assert baby.n_node_genes == 100


                # unlinked nodes
                nodes2 = {key: node.duplicate() for key, node in nodes.items()}
                genome3 = Genome(genome_id=3,
                                 node_genes=nodes2,
                                 link_genes=links)

                for _ in range(200):
                    Genome.insert_gene(genes_dict=nodes2,
                                       gene=NodeGene())
                # genome3 dominant
                baby = Genome.crossover(genome_id=7,
                                        parent1=genome,
                                        parent2=genome3)

                assert baby.id == 7
                assert baby.n_link_genes == 50
                assert baby.n_node_genes == 300



                # genome dominant
                baby = Genome.crossover(genome_id=8,
                                        parent1=genome3,
                                        parent2=genome)

                assert baby.id == 8
                assert baby.n_link_genes == 50
                assert baby.n_node_genes == 100

