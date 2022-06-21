import pytest, os, sys

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'rtNEAT')))
from project.src.rtNEAT.brain import Brain

class TestBrain:
    def test_create_brain(self):
        brain = Brain(brain_id=0,
                      entity_type='Animal')
        
        assert type(brain) == Brain 
        
    def test_brain_fields(self):
        brain = Brain(brain_id=0,
                      entity_type='Animal')
        
        assert brain.id == 0
        assert brain.entity_type == 'Animal'
        
    class TestBrainMethods:
        def test_brain_genesis(self):
            brain = Brain.genesis(brain_id=0,
                                  entity_type='animal')
            
            assert brain.id == 0
            assert brain.entity_type == 'animal'
            assert brain.genotype.id == 0
            assert brain.phenotype.id == 0
        
        def test_brain_reproduce(self):
            brain1 = Brain.genesis(brain_id=0,
                                   entity_type='animal')
            
            brain2 = Brain.genesis(brain_id=1,
                                   entity_type='animal')
            
            brain3 = Brain.reproduce(brain_id=2,
                                     parent1=brain1,
                                     parent2=brain2)
            
            assert brain3.id == 2
            assert brain3.entity_type == 'animal'
            assert brain3.genotype.id == 2
            assert brain3.phenotype.id == 2
            
        
        
        
    
        