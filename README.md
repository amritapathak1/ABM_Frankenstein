# Frankenstein Moral Drift: An Agent-Based Model of Social Rejection and Moral Deviation

This repository contains the code, outputs, and documentation for **ABM_Frankenstein**, an agent-based model that simulates how sustained social rejection affects the emotional trajectory and moral behavior of a stigmatized agent. Inspired by Mary Shelley's *Frankenstein* and grounded in psychological theory, the model explores how exclusion, stigma, and compassion shape moral drift over time.

## Project Overview

In the simulation, Frankenstein’s Creature begins as a peaceful and empathetic agent. Over time, repeated social rejection increases its **resentment** and decreases its **empathy**. When these emotions cross key thresholds, the Creature transitions into **Cautious** or **Vengeful** states. The model tracks this transformation based on:

- The type and frequency of interactions with human agents.
- The structure of the social network.
- Parameter variations including population composition, threshold sensitivity, and influence diffusion.

The project investigates:  
> **Under what social conditions can early inclusion prevent the moral collapse of a stigmatized agent?**

## Model Features

- **CreatureAgent**: A central agent with mutable emotional states (`empathy`, `resentment`) and a dynamic moral state (`Peaceful`, `Cautious`, `Vengeful`).
- **HumanAgent**: Agents with fixed trust dispositions:  
  - `Fearful`: Always reject the Creature  
  - `Neutral`: 50% chance to accept or reject  
  - `Compassionate`: Always accept  

- **Social Network**: Watts-Strogatz small-world graph topology using NetworkX.
- **Emotion Threshold Logic**: Transitions are governed by:
  - `res_threshold`: If resentment exceeds this
  - `emp_threshold`: If empathy drops below this
- **Broadcasting**: Optional mechanism where compassionate humans influence neighbors' trust levels.
- **Batch Mode**: Parameter sweeps across trust ratios, network features, and thresholds.

## Batch Results

The model includes batch-run analysis and plots showing key trends:

- `avg_creature_state.png`: Average state of the Creature over time.
- `avg_trust_over_time.png`: Count of Fearful, Neutral, Compassionate humans across steps.
- `final_creature_state_dist.png`: Histogram of final moral state across multiple runs.
- `compassionate_minus_fearful.png`: Difference between compassionate and fearful agents over time.
- `batch_results.csv`: Aggregated simulation outputs for plotting and evaluation.

All outputs can be found in the [`outputs/`](./outputs) folder.

## Repository Structure


| File/Folder | Description |
|-------------|-------------|
| [`agent.py`](./agent.py) | Agent logic for both the Creature and Human agents |
| [`model.py`](./model.py) | Model setup, step function, and network initialization |
| [`app.py`](./app.py) | Solara-based interactive GUI to visualize the simulation |
| [`run_batch.py`](./run_batch.py) | Batch simulation script for parameter sweeps |
| [`outputs/`](./outputs) | Simulation outputs: plots and `.csv` results |
| [`README.md`](./README.md) | You are here — project documentation |



---

Note: This README.md was written with the assistance of AI (ChatGPT) to ensure clarity, structure, and alignment with academic documentation standards. All content reflects the author's original project and model implementation.

