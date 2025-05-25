'''

Agent definitions for Frankenstein Moral Drift ABM, updated with scale-invariant thresholds
- CreatureAgent: evolving empathy/resentment, state transitions based on 75%/25% rule
- HumanAgent: mutable trust (-1,0,1) with learning and vengeful override
'''
from mesa import Agent
import random


class HumanAgent(Agent):
    """
    Human archetype with mutable 'trust' score:
      - fearful (trust = -1)
      - neutral  (trust =  0)
      - compassionate (trust = +1)

    Learning rules:
      * Pre-vengeful Creature: only fearful agents learn harmlessness:
        - on peaceful meet, trust -1 -> 0
      * Neutral (0) and compassionate (+1) never update pre-vengeful
      * Once Creature is 'vengeful', all humans reset trust to -1 and reject
    """
    def __init__(self, unique_id, model, h_type="neutral"):
        super().__init__(unique_id, model)
        mapping = {"fearful": -1, "neutral": 0, "compassionate": 1}
        self.trust = mapping[h_type]
        self.h_type = h_type

    def interact(self, creature_state) -> str:
        """
        Determine interaction outcome based on Creature state and current trust:
        - If Creature is vengeful: force trust=-1 and reject
        - Else: reject if trust<0, accept if trust>0, random if trust==0
        """
        if creature_state == "vengeful":
            # Creature now a monster: reset trust and reject
            self.trust = -1
            return "reject"

        # Pre-vengeful behavior
        if self.trust < 0:
            return "reject"
        elif self.trust > 0:
            return "accept"
        else:
            return random.choice(["accept", "reject"])

    def learn(self, outcome: str):
        """
        Update fearful agents on peaceful outcome:
        - trust -1 -> 0 on 'accept'
        - no change for neutral or compassionate pre-vengeful
        """
        if self.trust == -1 and outcome == "accept":
            self.trust = 0

    def step(self):
        # Humans are passive; learning occurs via Creature interactions
        pass


class CreatureAgent(Agent):
    """
    The Creature wanders, interacts, and updates its emotions and state.
    On each step:
      1) move to a random landmark
      2) interact with all humans in same cell
      3) update emotions and trigger human learning

    State transitions use scale-invariant thresholds:
      - resentment threshold = 0.75 * max_emotion (default 7.5)
      - empathy threshold   = 0.25 * max_emotion (default 2.5)
    """
    def __init__(self, unique_id, model, empathy_init=10, resentment_init=0):
        super().__init__(unique_id, model)
        self.empathy = empathy_init         # 0..10
        self.resentment = resentment_init   # 0..10
        self.state = "peaceful"            # 'peaceful' | 'cautious' | 'vengeful'

    def move(self):
        """
        Move to a random landmark (coordinates provided by model)
        """
        new_pos = random.choice(self.model.landmarks)
        self.model.grid.move_agent(self, new_pos)

    def interact(self):
        """
        Interact with each HumanAgent in the same cell:
        - human decides outcome based on trust & creature_state
        - creature updates emotions
        - human learns if peaceful
        """
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        for obj in cellmates:
            if isinstance(obj, HumanAgent):
                outcome = obj.interact(self.state)
                self.update_emotions(outcome)
                obj.learn(outcome)

    def update_emotions(self, outcome: str):
        """
        Adjust empathy & resentment, then state transitions:
          accept: empathy+1, resentment-1
          reject: empathy-1, resentment+1

        Uses model thresholds:
          rt = self.model.res_threshold  # e.g., 7.5
          et = self.model.emp_threshold  # e.g., 2.5

        State logic:
          if resentment > rt and empathy < et: 'vengeful'
          elif resentment > 0.6 * rt:      'cautious'
          else:                             'peaceful'
        """
        if outcome == "accept":
            self.empathy = min(self.empathy + 1, 10)
            self.resentment = max(self.resentment - 1, 0)
        else:
            self.empathy = max(self.empathy - 1, 0)
            self.resentment = min(self.resentment + 1, 10)

        rt = self.model.res_threshold
        et = self.model.emp_threshold
        if self.resentment > rt and self.empathy < et:
            self.state = "vengeful"
        elif self.resentment > 0.6 * rt:
            self.state = "cautious"
        else:
            self.state = "peaceful"

    def step(self):
        self.move()
        self.interact()
