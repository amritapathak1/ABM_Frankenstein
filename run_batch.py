# run_batch.py

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import product
from model import FrankensteinNetworkModel  # Ensure model.py is in the same directory

# Ensure local output directory exists
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

def run_simulation(n_steps=50, **model_kwargs):
    model = FrankensteinNetworkModel(**model_kwargs)
    results = []
    for step in range(n_steps):
        model.step()
        data = model.datacollector.get_model_vars_dataframe().copy()
        data["Step"] = step
        results.append(data.iloc[-1])
    return pd.DataFrame(results)

def run_batch(param_grid, n_runs=3, n_steps=50):
    all_results = []
    for i, param_set in enumerate(param_grid):
        for run in range(n_runs):
            df = run_simulation(n_steps=n_steps, **param_set)
            df["Run"] = run
            for k, v in param_set.items():
                df[k] = v
            all_results.append(df)
    return pd.concat(all_results, ignore_index=True)

def generate_plots(df):
    df["Step"] = df["Step"].astype(int)
    df["Compassionate_minus_Fearful"] = df["Compassionate"] - df["Fearful"]
    avg_trust_over_time = df.groupby("Step")[["Fearful", "Neutral", "Compassionate"]].mean()
    avg_creature_state = df.groupby("Step")["Creature State"].mean()
    final_state_per_run = df.groupby("Run").last()["Creature State"]

    fig1, ax1 = plt.subplots()
    avg_trust_over_time.plot(ax=ax1)
    ax1.set_title("Average Trust Levels Over Time")
    ax1.set_ylabel("Number of Agents")
    plt.tight_layout()
    fig1.savefig(f"{output_dir}/avg_trust_over_time.png")

    fig2, ax2 = plt.subplots()
    avg_creature_state.plot(ax=ax2, color='black')
    ax2.set_title("Average Creature State Over Time")
    ax2.set_ylabel("State (0=Peaceful, 1=Cautious, 2=Vengeful)")
    plt.tight_layout()
    fig2.savefig(f"{output_dir}/avg_creature_state.png")

    fig3, ax3 = plt.subplots()
    sns.histplot(final_state_per_run, bins=[-0.5, 0.5, 1.5, 2.5], ax=ax3, discrete=True)
    ax3.set_title("Final Creature State Distribution Across Runs")
    ax3.set_xlabel("Creature State")
    plt.tight_layout()
    fig3.savefig(f"{output_dir}/final_creature_state_dist.png")

    fig4, ax4 = plt.subplots()
    df.groupby("Step")["Compassionate_minus_Fearful"].mean().plot(ax=ax4)
    ax4.set_title("Average (Compassionate - Fearful) Over Time")
    ax4.set_ylabel("Compassionate - Fearful")
    plt.tight_layout()
    fig4.savefig(f"{output_dir}/compassionate_minus_fearful.png")

if __name__ == "__main__":
    # Key batch experiment dimensions (inspired by your research question)
    fearful_vals = [0.2, 0.4, 0.6, 0.8]
    compassionate_vals = [0.0, 0.2, 0.4]
    avg_degree_vals = [2, 4, 6]
    initial_edges_vals = [1, 3, 5]
    res_threshold_vals = [5, 7.5]
    emp_threshold_vals = [2.5, 5]
    broadcast_vals = [True, False]

    param_grid = []
    for f, c, d, e, r, m, b in product(
        fearful_vals, compassionate_vals,
        avg_degree_vals, initial_edges_vals,
        res_threshold_vals, emp_threshold_vals, broadcast_vals
    ):
        if f + c <= 1.0:
            param_grid.append({
                "n_humans": 30,
                "fearful_frac": f,
                "compassionate_frac": c,
                "avg_degree": d,
                "initial_edges": e,
                "res_threshold": r,
                "emp_threshold": m,
                "enable_broadcast": b
            })

    df_results = run_batch(param_grid, n_runs=5, n_steps=50)
    df_results.to_csv(f"{output_dir}/batch_results.csv", index=False)
    print("Saved batch_results.csv to outputs/")
    generate_plots(df_results)
    print("Saved plots to outputs/")
