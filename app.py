import mesa
import solara
import networkx as nx
from matplotlib.figure import Figure
from agent import CreatureAgent, HumanAgent, CreatureState
from model import FrankensteinNetworkModel
from mesa.visualization import Slider, SolaraViz, make_plot_component
from mesa.visualization.utils import update_counter

# Model parameter sliders (colorblind friendly GUI)
model_params = {
    "n_humans": Slider("Number of Humans", 30, 10, 100, 1),
    "fearful_frac": Slider("Fraction Fearful", 0.4, 0.0, 1.0, 0.05),
    "compassionate_frac": Slider("Fraction Compassionate", 0.2, 0.0, 1.0, 0.05),
    "avg_degree": Slider("Average Degree", 4, 1, 10, 1),
    "rewiring_prob": Slider("Rewiring Probability", 0.1, 0.0, 1.0, 0.01),
    "initial_edges": Slider("Initial Creature Edges", 3, 1, 10, 1),
}

@solara.component
def NetPlot(model):
    update_counter.get()
    fig = Figure()
    ax = fig.subplots()

    colors = []
    sizes = []
    shapes = []

    for node in model.G.nodes():
        agents = model.grid.get_cell_list_contents([node])
        creature_here = any(isinstance(a, CreatureAgent) for a in agents)

        if creature_here:
            colors.append("black")
            sizes.append(300)
            shapes.append("s")
        elif agents:
            a = agents[0]
            label = a.get_trust_label() if hasattr(a, "get_trust_label") else "neutral"
            color_map = {
                "fearful": "#D55E00",       # orange-red
                "neutral": "#999999",       # gray
                "compassionate": "#009E73"  # teal
            }
            colors.append(color_map[label])
            sizes.append(100)
            shapes.append("o")
        else:
            colors.append("#CCCCCC")  # empty node
            sizes.append(100)
            shapes.append("o")

    pos = nx.spring_layout(model.G, seed=42)

    # Draw humans (circles)
    human_nodes = [n for n, shape in zip(model.G.nodes(), shapes) if shape == "o"]
    nx.draw_networkx_nodes(
        model.G, pos, nodelist=human_nodes,
        node_color=[c for c, s in zip(colors, shapes) if s == "o"],
        node_size=[sz for sz, s in zip(sizes, shapes) if s == "o"],
        ax=ax
    )

    # Draw creature (square)
    creature_nodes = [n for n, shape in zip(model.G.nodes(), shapes) if shape == "s"]
    nx.draw_networkx_nodes(
        model.G, pos, nodelist=creature_nodes,
        node_color=[c for c, s in zip(colors, shapes) if s == "s"],
        node_size=[sz for sz, s in zip(sizes, shapes) if s == "s"],
        node_shape="s",
        edgecolors="white",
        linewidths=1.5,
        ax=ax
    )

    nx.draw_networkx_edges(model.G, pos, ax=ax, edge_color="#CCCCCC")
    solara.FigureMatplotlib(fig)


# Optional future expansion: trust level chart
Chart = make_plot_component({
    "Fearful": "#D55E00",
    "Neutral": "#999999",
    "Compassionate": "#009E73"
})

def post_process_creature_plot(ax):
    if not ax.lines:
        return  

    df = ax.lines[0].get_xydata()
    ax.clear()

    for i in range(1, len(df)):
        x = [df[i - 1, 0], df[i, 0]]
        y = [df[i - 1, 1], df[i, 1]]
        state = int(df[i - 1, 1])

        color = {
            0: "black",     # Peaceful
            1: "purple",    # Cautious
            2: "red"        # Vengeful
        }.get(state, "gray")

        ax.plot(x, y, color=color)

    ax.set_ylim(-0.2, 2.2)
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["Peaceful", "Cautious", "Vengeful"])
    ax.set_ylabel("Creature State")


CreatureStatePlot = make_plot_component(
    {"Creature State": "black"},  
    post_process=post_process_creature_plot
)


# Initialize the model
model1 = FrankensteinNetworkModel()

def display_creature_state(model):
    creature = next((a for a in model.agents if isinstance(a, CreatureAgent)), None)
    if creature:
        return solara.Text(f"Creature is currently: {creature.get_display_state()}")
    return solara.Text("Creature not found")

solara.Markdown("## Frankenstein Simulation")

# Create Solara app layout
page = SolaraViz(
    model1,
    components=[
        NetPlot,
        Chart,
        CreatureStatePlot,
        display_creature_state,
    ],
    model_params=model_params,
    name="Frankenstein Moral Drift"
)

page
