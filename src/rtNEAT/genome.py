import numpy as np

class Genome:
    def __init__(self,
                 genome_id: int,
                 nodes: np.array,
                 genes: np.array):
        
        self.id: int = genome_id
        self.nodes: np.array = nodes # List of Nodes for the Network
        self.genes: np.array = genes # List of innovation-tracking genes
        self.size = len(genes)
   
def compatibility(self, genome: Genome):
    p1_innovation: int
    p2_innovation: int
    
    mutation_difference: float
    
    number_disjoint: int
    number_excess: int = 0
    mutation_difference_total: float
    number_matching: int = 0
    
    max_genome_size: int = max(self.size, genome.size)

    p1_genome = iter(self.genes)
    p2_genome = iter(genome.genes)
    
    p1_size = self.size
    p2_size = genome.size
    p1_gene = next(p1_genome)
    p2_gene = next(p2_genome)
    while True:
        try:
            if p1_gene == self.genes[-1]:
                p2_gene = next(p2_genome)
                number_excess += 1
            elif p2_gene == genome.genes[-1]:
                p1_gene = next(p1_genome)
                number_excess += 1
            else:
                p1_innovation = p1_gene.innovation_number
                p2_innovation = p2_gene.innovation_number
                
                if(p1_innovation==p2_innovation):
                    number_matching += 1
                    mutation_difference = abs(p1_gene.mutation_number - p2_gene.mutation_number)
                    mutation_difference_total += mutation_difference
                    
                    p1_gene = next(p1_genome)
                    p2_gene = next(p1_genome)
                elif p1_innovation < p2_innovation:
                    p1_gene = next(p1_genome)
                    number_disjoint += 1
                elif p2_innovation < p1_innovation:
                    p2_gene = next(p2_genome)
                    number_disjoint += 1
        except StopIteration:
            pass
    
    return (NEAT.disjoint_coeff(number_disjoint) +
            NEAT.excess_coeff(num_excess) +
            NEAT.mutation_difference_total(mutation_difference_total(number_matching)))
                 