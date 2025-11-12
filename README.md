# mewantfood

agent-based simulation of the [allegory of the long spoons](https://en.wikipedia.org/wiki/Allegory_of_the_long_spoons)

<img src="preview.png">

Black circles represent the agents seated at the table as they try to eat the red square foods with the long spoons. Partially open circles indicate if the agent has decided to open its mouth to receive food. Numbers next to each agent indicate each agent's hunger level (-0.1 for each timestep unfed, +1 if food ends up in agent's open mouth).

Or in Pacman-style visualization...

<img src="preview_pacman.png">

## Installation

Virtual/conda environment:

```
conda create -n mewantfood python=3.12
conda activate mewantfood
```

Install requirements:

```
pip install -r requirements.txt
```

## Running


```
python simulation.py
```

then playback via PyGame:

```
python playback.py
```