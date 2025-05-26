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

# Color scheme (colorblind friendly)
def agent_portrayal(agent):
    if isinstance(agent, CreatureAgent):
        state_color = {
            CreatureState.PEACEFUL: "black",
            CreatureState.CAUTIOUS: "purple",
            CreatureState.VENGEFUL: "red",
        }
        return state_color[agent.state]
  
    elif isinstance(agent, HumanAgent):
        if agent.trust < 0:
            return "#D55E00"  # red-orange
        elif agent.trust == 0:
            return "#999999"  # gray
        else:
            return "#009E73"  # teal-green
    return "#000000"  # fallback black

@solara.component
def NetPlot(model):
    update_counter.get()
    fig = Figure()
    ax = fig.subplots()

    color_dict = {}
    for node in model.G.nodes():
        agents = model.grid.get_cell_list_contents([node])
        if agents:
            color_dict[node] = agent_portrayal(agents[0])
        else:
            color_dict[node] = "#CCCCCC"  # default gray for empty

    node_colors = [color_dict[n] for n in model.G.nodes()]

    nx.draw(
        model.G,
        ax=ax,
        pos=nx.spring_layout(model.G, seed=42),
        node_color=node_colors,
        edge_color="#CCCCCC",
        with_labels=False,
        node_size=100
    )

    solara.FigureMatplotlib(fig)

# Optional future expansion: trust level chart
Chart = make_plot_component({
    "Fearful": "#D55E00",
    "Neutral": "#999999",
    "Compassionate": "#009E73"
})

# Initialize the model
model1 = FrankensteinNetworkModel()

# Create Solara app layout
page = SolaraViz(
    model1,
    components=[
        NetPlot,
        Chart
    ],
    model_params=model_params,
    name="Frankenstein Moral Drift"
)

page
