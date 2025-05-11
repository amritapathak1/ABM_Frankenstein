# Frankenstein Moral Drift: An Agent-Based Model of Social Rejection and Moral Deviation

This repository contains the code and documentation for the **Frankenstein Moral Drift** agent-based model. The model simulates the emotional and behavioral transformation of a stigmatized agent, inspired by Mary Shelley's *Frankenstein*, through cumulative experiences of social rejection.

---
## Project Overview

This model investigates the research question:

> **How does repeated social rejection influence the emotional trajectory and moral behavior of a stigmatized agent, as modeled through Frankenstein’s Creature?**

Drawing on social psychology, affective neuroscience, and literary theory, the model operationalizes feedback-driven emotional drift where empathy decreases and resentment increases with each rejection, leading to a shift in moral behavior (peaceful → cautious → vengeful).

## Model Structure

- **Grid**: 10×10 `MultiGrid` with four fixed landmarks: forest, village, cottage, and market.
- **Agents**:
  - `CreatureAgent`: a mobile agent with dynamic emotional states (`empathy`, `resentment`, `state`)
  - `HumanAgent`: fixed agents with a `h_type` ("fearful", "neutral", "compassionate") that determine their interaction behavior
- **State Transitions**:
  - Emotional updates based on rejection/acceptance
  - Moral state switches when resentment > `res_threshold` and empathy < `emp_threshold`

## File Structure

Frankenstein-Moral-Drift/
├── [model.py](./model.py)            # Main model logic and environment
├── [agent.py](./agent.py)            # Definitions for Creature and Human agents


