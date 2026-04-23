# Mythos Latent UI Design Specifications

## Vision
The Mythos Latent UI is not just a dashboard; it's a window into the **Continuous Latent Space** of the Recurrent-Depth Transformer. It visualizes the silent "thinking" that happens inside the model's loops and the orchestrated dance of the Agent Matrix.

## Core Components

### 1. The Reasoning Spiral (Recurrent Loop Visualizer)
- **Concept**: Visualizes the `max_loop_iters` (e.g., 16, 32, 64) as a glowing, pulsating spiral.
- **Interaction**: As the model runs a forward pass, the spiral glows brighter with each iteration.
- **Data**: Real-time loop index and ACT (Adaptive Computation Time) halting probabilities.

### 2. The Agent Matrix (The Hive)
- **Concept**: A dynamic node graph representing the matrix of spawned agents.
- **Visualization**: Nodes glow when an agent is active. Chaining is shown as flowing data streams between nodes.
- **Details**: Clicking an agent shows its specific role, system prompt, and local memory.

### 3. The Integrity Gate (SWD Panel)
- **Concept**: A high-tech verification terminal.
- **Function**: Shows `[FILE_ACTION]` blocks being parsed. Displays the "Snapshot -> Verify -> Execute" pipeline with SHA-256 hash comparisons.
- **UX**: Green "Verified" badges for successful matches; red "Drift Detected" warnings with rollback options.

### 4. The Authoritative Log (Sacred Log)
- **Concept**: A beautifully rendered version of `MEMORY.md`.
- **Search**: Integrated FTS5 search bar to query the SQLite memory index instantly.
- **Detail**: "Time-travel" capability to see the state of the project at any previous log entry.

## Aesthetic (Visual Identity)
- **Primary Color**: Deep Obsidian (`#050505`) - The "Void" of latent space.
- **Accent 1**: Cyber Cyan (`#00f5ff`) - Represents data and execution.
- **Accent 2**: Mythos Gold (`#d4af37`) - Represents the "Sacred" authority of memory.
- **Motion**: Fluid, organic transitions using Framer Motion to mimic the "recurrent" nature of the model.

## Tech Stack
- **Backend**: FastAPI with WebSockets for real-time state streaming.
- **Frontend**: React + Vite + Tailwind CSS.
- **Graphics**: Three.js for the Reasoning Spiral and Agent Hive visualization.
- **State Management**: Zustand for light-weight, high-performance state syncing with the backend.
