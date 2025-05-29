from enum import Enum
import random
import mesa

class TrustLevel(Enum):
    FEARFUL = -1
    NEUTRAL = 0
    COMPASSIONATE = 1

class CreatureState(Enum):
    PEACEFUL = 0
    CAUTIOUS = 1
    VENGEFUL = 2

class HumanAgent(mesa.Agent):
    """
    Humankind with mutable trust levels and social broadcasting.
    - trust ∈ {-1 (fearful), 0 (neutral), +1 (compassionate)}
    - learns harmlessness on peaceful meets
    - broadcasts trust update to neighbors
    """
    # def __init__(self, unique_id, model, h_type="neutral"):
    def __init__(self, unique_id, model, h_type="neutral", enable_broadcast=False):

        # Initialize agent
        self.unique_id = unique_id
        self.enable_broadcast = enable_broadcast
        self.model = model
        self.pos = None  # for NetworkGrid
        # Accept either string or TrustLevel
        if isinstance(h_type, str):
            # Map lowercase string to enum
            self.h_type = TrustLevel[h_type.upper()]
        else:
            self.h_type = h_type
        self.trust = float(self.h_type.value)

    def interact(self, creature_state: CreatureState) -> str:
        # Vengeful creature resets trust, always rejects
        if creature_state is CreatureState.VENGEFUL:
            self.trust = TrustLevel.FEARFUL.value
            return "reject"
        # Pre-vengeful: reject if fearful, accept if compassionate, 50/50 if neutral
        if self.trust < 0:
            return "reject"
        elif self.trust > 0:
            return "accept"
        else:
            return "accept" if self.random.random() < 0.5 else "reject"

    def learn(self, outcome: str):
        # Fearful -> neutral on peaceful meet
        if self.trust == TrustLevel.FEARFUL.value and outcome == "accept":
            self.trust = TrustLevel.NEUTRAL.value

    
    # def broadcast_trust(self):
    #     """
    #     Convert fearful neighbors to neutral via trust signal.
    #     """
    #     neighbors = self.model.grid.get_neighbors(self.pos, include_center=False)
    #     for agent in neighbors:
    #         if isinstance(agent, HumanAgent) and agent.trust == TrustLevel.FEARFUL.value:
    #             agent.trust = TrustLevel.NEUTRAL.value

    def broadcast_trust(self):
        """
        Nudge neighbors toward compassion if broadcasting is enabled.
        """
        if not self.enable_broadcast or self.trust <= 0:
            return

        neighbor_ids = self.model.grid.get_neighbors(self.pos, include_center=False)
        for nid in neighbor_ids:
            agents = self.model.grid.get_cell_list_contents([nid])
            for agent in agents:
                if isinstance(agent, HumanAgent) and agent.trust < self.trust:
                    agent.trust = min(agent.trust + 0.1, 1.0)  # Cap at +1.0


    def get_trust_label(self):
        """Map continuous trust to categorical label for visualization."""
    
        if self.trust <= -0.5:
            return "fearful"
        elif self.trust >= 0.5:
            return "compassionate"
        else:
            return "neutral"


    def step(self):
        # Passive: broadcasting happens immediately after learning in Creature.interact()
        pass

class CreatureAgent(mesa.Agent):
    """
    The Creature wanders a social network, evolves emotion and state.
    On each step:
      1) move along a random edge to neighboring human
      2) interact, updating emotions and triggering learning/broadcasts
    """
    def __init__(self, unique_id, model, empathy_init=10, resentment_init=0):
        self.unique_id = unique_id
        self.model = model
        self.pos = None
        self.empathy = empathy_init
        self.resentment = resentment_init
        self.state = CreatureState.PEACEFUL
        self.enable_broadcast = True  

    def move(self):
        # Hop to a random connected node
        neighbors = list(self.model.G.neighbors(self.unique_id))
        if neighbors:
            next_node = random.choice(neighbors)
            self.model.grid.move_agent(self, next_node)

    def interact(self):
        # Meet and learn with all humans at current node
        for obj in self.model.grid.get_cell_list_contents([self.pos]):
            if isinstance(obj, HumanAgent):
                outcome = obj.interact(self.state)
                self.update_emotions(outcome)
                obj.learn(outcome)
                if outcome == "accept":
                    obj.broadcast_trust()


    def update_emotions(self, outcome: str):
        if outcome == "accept":
            self.empathy = min(self.empathy + 1, 10)
            self.resentment = max(self.resentment - 1, 0)
        else:
            self.empathy = max(self.empathy - 1, 0)
            self.resentment = min(self.resentment + 1, 10)
        # State transition thresholds from model
        rt = self.model.res_threshold
        et = self.model.emp_threshold
        if self.resentment > rt and self.empathy < et:
            self.state = CreatureState.VENGEFUL
        elif self.resentment > 0.6 * rt:
            self.state = CreatureState.CAUTIOUS
        else:
            self.state = CreatureState.PEACEFUL

    def step(self):
        self.move()
        self.interact()

    def get_display_state(self):
        return self.state.name.capitalize()
