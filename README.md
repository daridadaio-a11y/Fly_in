*This project has been created as part of the 42 curriculum by mkitagaw.*

# Fly-in

English submission version. A Japanese translation is available in
[`README_JA.md`](README_JA.md).

## Description

Fly-in is a turn-based drone-routing simulation. It reads a map containing
zones and bidirectional connections, then plans routes that deliver every
drone from the start hub to the end hub while respecting movement costs and
capacity limits.

The program handles normal, priority, restricted, and blocked zones. Normal
and priority zones take one turn to enter, restricted zones take two turns,
and blocked zones cannot be entered. Zone capacity and undirected connection
capacity are enforced for every relevant turn. The start and end hubs have
unlimited capacity.

The main objective is to finish the simulation in as few turns as practical
without creating zone or connection conflicts.

## Instructions

### Requirements

- Python 3.10 or later
- [uv](https://docs.astral.sh/uv/)
- A graphical desktop environment when using the optional Pygame view

### Installation

Install the application and development dependencies:

```bash
make install
```

### Running the simulation

Run the included sample map:

```bash
make run
```

Run a specific map:

```bash
make run MAP=maps/easy/01_linear_path.txt
```

The equivalent direct command is:

```bash
uv run python fly_in.py maps/easy/01_linear_path.txt
```

### Visual representation

Open the optional Pygame network view:

```bash
make visual MAP=maps/easy/01_linear_path.txt
```

The visualizer draws zones at their map coordinates, draws their connections,
and displays every drone at its current zone. During a two-turn move into a
restricted zone, the drone is displayed on the connection. The view advances
through the simulation states automatically once per second, smoothly moves
drones between consecutive states, and shows the current turn and
delivered-drone count in a translucent panel. White outlines and a fixed star
background keep the map readable while giving it a playful appearance. This
makes the network topology, simultaneous movement, waiting, and
restricted-zone transit easier to understand. Restricted zones have a
persistent orange glow, and a connection glows while a drone is moving through
it toward a restricted zone. Zone colors use the map's `color` metadata when
Pygame recognizes the color name. For an unknown color
name, the start hub falls back to green, the end hub falls back to yellow, and
any other zone falls back to gray.

Visualizer controls:

- `Space`: play or pause
- `Right Arrow`: advance one turn and pause
- `Left Arrow`: go back one turn and pause
- `R`: return to turn 0
- `Esc`: close the visualizer

### Development commands

```bash
make lint
make lint-strict
make debug MAP=sample_map.txt
make clean
```

`make lint` runs the mandatory flake8 and mypy checks. `make lint-strict` uses
the stricter mypy configuration. `make clean` removes generated caches and
build artifacts but preserves the virtual environment.

## Input format

A map starts with a positive drone count, followed by zone definitions and
connection definitions:

```text
nb_drones: 2
start_hub: start 0 0 [color=green]
hub: middle 1 0 [zone=normal color=blue max_drones=2]
end_hub: goal 2 0 [color=yellow]
connection: start-middle [max_link_capacity=2]
connection: middle-goal [max_link_capacity=2]
```

Metadata is optional. A regular zone defaults to `zone=normal`, `color=none`,
and `max_drones=1`. A connection defaults to `max_link_capacity=1`. Lines may
contain comments beginning with `#`.

## Expected output

Each output line represents one simulation turn. Only drones that move during
that turn are printed:

```text
D1-middle D2-middle
D1-goal D2-goal
```

A normal move is written as `D<ID>-<zone>`. During the first turn of a
two-turn move into a restricted zone, the connection is printed as
`D<ID>-<source>-<destination>`. The destination zone is printed on the next
turn. A waiting drone is omitted from that turn's output.

## Algorithm explanation

### 1. Parsing and graph construction

`Parser` reads the map from top to bottom. It validates the drone count, zone
roles, coordinates, metadata, capacities, duplicate names, duplicate
undirected connections, and references to undefined zones. The parsed data is
converted into a custom adjacency-list graph; no external graph library is
used.

### 2. Reservation-free shortest path

`PathFinder` uses Dijkstra's algorithm to calculate a shortest path without
reservations. The cost of an edge is based on the destination zone: one turn
for normal or priority zones and two turns for restricted zones. Blocked zones
are excluded. When paths have the same movement cost, paths containing more
priority zones are preferred.

This first result supplies the minimum unreserved travel time used by the
multi-drone planner.

### 3. Time-aware path planning

`PathPlanner` plans drones sequentially from ID 1 upward. For each drone,
`ReservationPathFinder` searches states represented by `(zone, turn)`. A state
may produce either a one-turn wait or a move to a neighboring zone. Before a
candidate is accepted, the planner checks the destination-zone capacity at
the arrival turn and the undirected connection capacity at the traversal
turn.

A restricted destination produces a two-turn move. The drone occupies the
connection during the intermediate turn and must arrive at the restricted
zone on the following turn; it cannot wait on the connection.

After a complete path is found, `ReservationTable` reserves all of its zone
and connection usage. Later drones therefore search around the capacity used
by earlier drones. The process supports waiting, overlapping routes, multiple
available routes, and start/end hubs with unlimited capacity.

This is a prioritized, sequential planning strategy. It produces valid and
fast solutions for the supplied maps, but it does not mathematically guarantee
the globally minimum number of turns for every possible map because earlier
drone routes are not replanned after later drones are considered.

### 4. Simulation output

`Simulation` converts the planned timed paths into per-turn states. Each state
contains movement strings, drone positions, zone usage, connection usage, and
the delivered-drone count. The standard command prints only the movement
strings required by the subject format and stops after every drone reaches the
end hub.

## Project structure

- `fly_in.py`: command-line entry point and complete workflow
- `read_map.py`: input parser and validation
- `models.py`: shared data models and type aliases
- `graph.py`: custom graph representation and movement costs
- `pathfinding.py`: reservation-free shortest path
- `reservation_pathfinder.py`: time-aware path search for one drone
- `reservation_table.py`: zone and connection capacity reservations
- `path_planner.py`: planning and reservation for all drones
- `simulation.py`: per-turn state generation and required output
- `visualizer.py`: Pygame event loop and turn playback controls
- `renderer.py`: scalable drawing of connections, zones, drones, and status

## Design decisions and limitations

- Connections are treated as undirected for traversal and capacity.
- Capacity is reserved by turn rather than by modifying the graph.
- Start and end hubs ignore `max_drones` and have unlimited capacity.
- Waiting is represented by repeating the same zone on the next turn.
- Planning one drone at a time keeps the implementation understandable and
  deterministic, but the result is not guaranteed to be globally optimal.
- The graphical view smoothly interpolates each drone's position between
  consecutive discrete turn states.

## Resources

- [Python documentation](https://docs.python.org/3/)
- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)
- [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Cooperative pathfinding](https://www.davidsilver.uk/wp-content/uploads/2020/03/coop-path-AIWisdom.pdf)
- The Fly-in subject and peer-evaluation criteria supplied with the project

### Use of AI

AI was used as a review and learning aid for the following tasks:

- comparing the implementation with the subject and evaluation criteria;
- identifying missing submission requirements and edge cases;
- discussing class responsibilities and the data flow between parsing,
  planning, reservations, and simulation;
- suggesting tests and explaining test or lint results; and
- reviewing documentation wording.

The generated suggestions were checked against the subject, the current
source code, and executed tests before being accepted. The project owner is
responsible for understanding and explaining the final implementation.
