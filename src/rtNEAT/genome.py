import numpy as np

class Genome:
    def __init__(self,
                 genome_id: int,
                 nodes: np.array,
                 genes: np.array):
        
        self.id = genome_id
        self.nodes = nodes
        self.genes = genes
                