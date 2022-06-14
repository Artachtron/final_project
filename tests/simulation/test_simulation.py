from project.src.simulation.simulation import Simulation


class TestSimulation:
    def test_create_simulation(self):
        sim = Simulation(sim_id=0)
        assert type(sim) == Simulation