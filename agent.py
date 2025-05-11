"""
Agents for “Frankenstein Moral Drift” ABM

• CreatureAgent – the single learning agent whose empathy and
   resentment evolve as he wanders a small landscape.

• HumanAgent – generic human with a fixed behavioral archetype
   (fearful, neutral, compassionate).

"""

# ------------------------------------------------------------------

from mesa import Agent
import random


# ------------------------------------------------------------
# Creature Agent
# ------------------------------------------------------------
class CreatureAgent(Agent):
    """
    The Creature starts peaceful (high empathy, low resentment).
    Each human encounter returns either 'accept' or 'reject'.
    Emotional variables update, and thresholds may switch state.
    """

    def __init__(self, unique_id, model,
                 empathy_init=10, resentment_init=0):
        super().__init__(unique_id, model)
        self.empathy = empathy_init         # 0..10
        self.resentment = resentment_init   # 0..10
        self.state = "peaceful"             # 'peaceful' | 'cautious' | 'vengeful'

    # ----------------- Movement ---------------------------------
    def move(self):
        """
        Pick one of the landscape landmarks at random.
        Landmark coordinates are stored on the model (self.model.landmarks).
        """
        new_pos = random.choice(self.model.landmarks)
        self.model.grid.move_agent(self, new_pos)

    # ----------------- Interaction ------------------------------
    def interact(self):
        """
        Called once per step after moving.
        Loop through cellmates; if any HumanAgent present, interact.
        Multiple humans in same cell → multiple interactions that step.
        """
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        for obj in cellmates:
            if isinstance(obj, HumanAgent):
                outcome = obj.interact()          # 'accept' or 'reject'
                self.update_emotions(outcome)

    # ----------------- Emotion Update ---------------------------
    def update_emotions(self, outcome: str):
        """
        Update empathy & resentment according to encounter outcome,
        then check thresholds to possibly switch moral state.
        """
        if outcome == "accept":
            self.empathy = min(self.empathy + 1, 10)
            self.resentment = max(self.resentment - 1, 0)
        else:  # outcome == 'reject'
            self.empathy = max(self.empathy - 1, 0)
            self.resentment = min(self.resentment + 1, 10)

        # --- State transition rules -----------------------------
        if (self.resentment > self.model.res_threshold and
                self.empathy < self.model.emp_threshold):
            self.state = "vengeful"
        elif self.resentment > self.model.res_threshold * 0.6:
            self.state = "cautious"
        else:
            self.state = "peaceful"

    # ----------------- Step (scheduler hook) --------------------
    def step(self):
        self.move()
        self.interact()


# ------------------------------------------------------------
# Human Agents
# ------------------------------------------------------------
class HumanAgent(Agent):
    """
    Human archetypes have fixed interaction rules:

    fearful        → always reject
    neutral        → 50/50 accept vs. reject
    compassionate  → always accept
    """

    def __init__(self, unique_id, model, h_type="fearful"):
        super().__init__(unique_id, model)
        assert h_type in {"fearful", "neutral", "compassionate"}
        self.h_type = h_type

    # Interaction rule that returns 'accept' or 'reject'
    def interact(self) -> str:
        if self.h_type == "fearful":
            return "reject"
        elif self.h_type == "compassionate":
            return "accept"
        else:   # neutral
            return random.choice(["accept", "reject"])

    # Humans are passive—no scheduled action needed, but we keep
    # step method for completeness / future extensions
    def step(self):
        pass
