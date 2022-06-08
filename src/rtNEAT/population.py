import numpy as np
from species import Species
from neat import NEAT

# Might not be necessary
class Population:
    def __init__(self,
                 organisms: np.array,
                 species: np.array):
        self.organisms = organisms
        self.species = species
        self.size = len(organisms)
    
    """ def speciate(self):
        comparison_organism = 0
                
        counter: int = 0
        
        # For each organism, search for a species it is compatible to
        for current_organism in self.organisms:
            if len(self.species) == 0:
                counter += 1
                new_species = Species(counter)
                self.species.append(new_species)
                new_species.add_organism(current_organism) # Add the current organism
                current_organism.species = new_species # Point organism to its species
            else:
                comparison_organism = current_species[0]
                for current_species in self.species:
                    if comparison_organism == 0:
                        break
                    
                    if current_organism.genome.compatibility(comparison_organism.genome) < NEAT.threshold:
                        # Found compatible species, so add this organism to it
                        current_species.add_organism(current_organism)
                        current_organism.species = current_species
                        comparison_organism = 0
                    else:
                        # Keep searching for a matching species
                        current_species += 1
                        if current_species != len(self.species) - 1:
                            comparison_organism = current_species[0]
                            
                # If we didn't find a match, create a new species
                if comparison_organism !=0:
                    counter += 1
                    new_species = Species(counter)    
                    self.species.append(new_species)
                    new_species.add_organism(current_organism) # Add the current organism
                    current_organism.species = new_species # Point organism to its species
                     """
