import pytest, os, sys

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'rtNEAT')))
from src.rtNEAT.brain import Brain

""" class TestOrganism:
    def test_create_organism(self):
        organism = Organism()
        
        assert organism.genotype.id == organism.id
        assert organism.mind.id == organism.id """
        