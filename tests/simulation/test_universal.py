from math import pi, sqrt

import pytest
from project.src.platform.universal import Position


class TestPosition:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.pos1 = Position(1,1)
        self.pos2 = Position(2,2)
        self.pos3 = Position(3,1)
        self.pos4 = Position(2,1)
        
        self.pos5 = Position(1,3)
        self.pos6 = Position(1,2)
    
    def test_distance(self):
        assert self.pos1.distance(other_pos=self.pos2) == round(sqrt(2),2)
        assert self.pos1.distance(other_pos=self.pos3) == 2
        
    def test_angle(self):
        assert self.pos1.angle(other_pos=self.pos3) == 0.0
        assert self.pos3.angle(other_pos=self.pos4) == pi

        assert self.pos1.angle(other_pos=self.pos5) == pi/2
        assert self.pos5.angle(other_pos=self.pos6) == 3*pi/2
        
    def test_normalize_angle(self):
        assert self.pos1.norm_angle(other_pos=self.pos3) == 0.0
        assert self.pos3.norm_angle(other_pos=self.pos4) == 0.5

        assert self.pos1.norm_angle(other_pos=self.pos5) == 0.25
        assert self.pos5.norm_angle(other_pos=self.pos6) == 0.75
