# model.py

import networkx as nx
import random
import mesa
from mesa.space import NetworkGrid
from mesa.datacollection import DataCollector
from agent import CreatureAgent, HumanAgent

class FrankensteinNetworkModel(mesa.Model):
    """
    Network-based Frankenstein Moral Drift ABM using updated Mesa API (no mesa.time).
    - Uses NetworkGrid for social links.
    - Uses mesa.Model.agents.shuffle_do() to advance agent steps.
    - Collects data on agent states and trust scores.
    """
    def __init__(
        self,
        n_humans=30,
        fearful_frac=0.4,
        compassionate_frac=0.2,
        avg_degree=4,
        rewiring_prob=0.1,
        initial_edges=3,
        max_emotion=10,
        res_threshold=None,
        emp_threshold=None,
        enable_broadcast=False,
        seed=None
    ):
        super().__init__(seed=seed)

        if res_threshold is None:
            res_threshold = 0.75 * max_emotion
        if emp_threshold is None:
            emp_threshold = 0.25 * max_emotion

        self.res_threshold = res_threshold
        self.emp_threshold = emp_threshold
        self.enable_broadcast = enable_broadcast

        self.n_humans = n_humans
        self.fearful_frac = fearful_frac
        self.compassionate_frac = compassionate_frac
        self.avg_degree = avg_degree
        self.rewiring_prob = rewiring_prob
        self.initial_edges = initial_edges

        # Create a Watts-Strogatz small-world graph
        k = avg_degree if avg_degree % 2 == 0 else avg_degree + 1
        self.G = nx.watts_strogatz_graph(n_humans, k, rewiring_prob)
        creature_node = "creature"
        self.G.add_node(creature_node)
        self.grid = NetworkGrid(self.G)

        # Data collection setup
        self.datacollector = DataCollector(
            model_reporters={
                "Fearful": lambda m: sum(1 for a in m.agents if isinstance(a, HumanAgent) and a.trust <= -0.5),
                "Neutral": lambda m: sum(1 for a in m.agents if isinstance(a, HumanAgent) and -0.5 < a.trust < 0.5),
                "Compassionate": lambda m: sum(1 for a in m.agents if isinstance(a, HumanAgent) and a.trust >= 0.5),
                # "Creature State": lambda m: next(a.state.value for a in m.agents if isinstance(a, CreatureAgent))
                "Creature State": lambda m: next(a.state.value for a in m.agents if isinstance(a, CreatureAgent))
            }
        )

        # Add the Creature node
        # target_nodes = random.sample(list(self.G.nodes - {creature_node}), k=initial_edges)
        # target_nodes = random.sample(list(self.G.nodes - {creature_node}), k=min(initial_edges, len(self.G.nodes) - 1))
        target_nodes = random.sample(
            [n for n in self.G.nodes if n != creature_node],
            k=self.avg_degree
        )

        for target in target_nodes:
            self.G.add_edge(creature_node, target)

        creature = CreatureAgent(creature_node, self)
        self.grid.place_agent(creature, creature_node)
        self.agents.add(creature)

        # Create and place HumanAgents (skip creature's node)
        for node in self.G.nodes():
            if node == creature_node:
                continue  # Do not overwrite the creature!

            r = random.random()
            if r < fearful_frac:
                h_type = "fearful"
            elif r < fearful_frac + compassionate_frac:
                h_type = "compassionate"
            else:
                h_type = "neutral"

            human = HumanAgent(node, self, h_type, enable_broadcast=self.enable_broadcast)
            self.grid.place_agent(human, node)
            self.agents.add(human)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        # Creature moves along a random edge
        creature = next(a for a in self.agents if isinstance(a, CreatureAgent))
        neighbors = list(self.G.neighbors(creature.unique_id))
        if neighbors:
            self.grid.move_agent(creature, random.choice(neighbors))

        # Agents take their steps (shuffle_do is the new scheduler)
        self.agents.shuffle_do("step")

        # Collect data
        self.datacollector.collect(self)
