import os
import sys

import pytest

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'rtNEAT')))
from project.src.rtNEAT.brain import Brain


class TestBrain:
    def test_create_brain(self):
        brain = Brain(brain_id=0)
        
        assert type(brain) == Brain 
        
    def test_brain_fields(self):
        brain = Brain(brain_id=0)
        
        assert brain.id == 0

        
    class TestBrainMethods:
        def test_brain_genesis(self):
            gen_data = {'n_inputs':96,
                        'n_outputs':15,
                        'n_actions':0,
                        'actions':{}}
            brain = Brain.genesis(brain_id=0,
                                  genome_data=gen_data)
            
            assert brain.id == 0
            assert brain.genotype.id == 0
            assert brain.phenotype.id == 0
        
        def test_brain_reproduce(self):
            gen_data = {'n_inputs':96,
                        'n_outputs':15,
                        'n_actions':0,
                        'actions':{}}
            brain1 = Brain.genesis(brain_id=0,
                                  genome_data=gen_data)
            
            gen_data = {'n_inputs':96,
                        'n_outputs':15,
                        'n_actions':0,
                        'actions':{}}
            brain2 = Brain.genesis(brain_id=1,
                                  genome_data=gen_data)
            
            brain3 = Brain.crossover(brain_id=2,
                                     parent1=brain1,
                                     parent2=brain2)
            
            assert brain3.id == 2
            assert brain3.genotype.id == 2
            assert brain3.phenotype.id == 2
            
        
        
        
    
        