"""
Frankenstein Moral-Drift ABM 

• 10×10 MultiGrid with four landmark cells:
     0 = forest, 1 = village, 2 = cottage, 3 = market
• Single CreatureAgent moves each step; humans are fixed.
• DataCollector logs empathy, resentment, and moral state.

"""

# ------------------------------------------------------------------

from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import random

from ABM_Frankenstein.agent import CreatureAgent, HumanAgent


class FrankensteinModel(Model):
    """
    Parameters
    ----------
    n_humans       : int   total number of humans
    pct_fearful    : float proportion of humans that are fearful (0–1)
    pct_neutral    : float proportion neutral
                     remaining humans are compassionate
    emp_threshold  : int   empathy level below which Creature can flip
    res_threshold  : int   resentment level above which Creature can flip
    seed           : int   optional RNG seed for reproducibility
    """

    def __init__(
        self,
        n_humans=15,
        pct_fearful=0.80,
        pct_neutral=0.15,
        emp_threshold=3,
        res_threshold=7,
        width=10,
        height=10,
        seed=None,
    ):
        super().__init__()
        if seed is not None:
            random.seed(seed)
            self.seed = seed

        # ---- Model-level parameters ---------------------------------
        self.emp_threshold = emp_threshold
        self.res_threshold = res_threshold

        # ---- Grid & scheduler ---------------------------------------
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)

        # ---- Landmark coordinates -----------------------------------
        # (forest, village, cottage, market)
        self.landmarks = [(1, 1), (8, 1), (1, 8), (8, 8)]

        # ---- Create Creature ----------------------------------------
        self.creature = CreatureAgent("Creature", self)
        self.schedule.add(self.creature)
        self.grid.place_agent(self.creature, self.landmarks[0])  # start in forest

        # ---- Create Human population --------------------------------
        n_fear = int(pct_fearful * n_humans)
        n_neu = int(pct_neutral * n_humans)
        n_comp = n_humans - n_fear - n_neu

        human_types = (
            ["fearful"] * n_fear + ["neutral"] * n_neu + ["compassionate"] * n_comp
        )
        random.shuffle(human_types)

        for i, h_type in enumerate(human_types):
            h = HumanAgent(f"H{i}", self, h_type=h_type)
            self.schedule.add(h)
            # Place humans randomly at landmarks (they stay put)
            self.grid.place_agent(h, random.choice(self.landmarks))

        # ---- Data Collector -----------------------------------------
        self.datacollector = DataCollector(
            model_reporters={
                "Step": lambda m: m.schedule.time,
                "Creature_state": lambda m: m.creature.state,
                "Creature_empathy": lambda m: m.creature.empathy,
                "Creature_resentment": lambda m: m.creature.resentment,
            },
            agent_reporters={
                # Save just for Creature; Humans return None
                "empathy": lambda a: getattr(a, "empathy", None),
                "resentment": lambda a: getattr(a, "resentment", None),
            },
        )

    # ----------------------------------------------------------------
    # One simulation tick
    # ----------------------------------------------------------------
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()


    def run_model(self, steps=50):
        for _ in range(steps):
            self.step()
        return self.datacollector.get_model_vars_dataframe()
