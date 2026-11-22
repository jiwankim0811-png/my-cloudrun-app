# Algorithmic Lens - Design System

## Brand & Style
The design system establishes a focused, high-precision laboratory environment for computer science pedagogy and algorithmic inspection. Targeted at students, software engineers, and researchers, the interface prioritizes observational clarity, structural transparency, and real-time execution feedback.

Drawing from technical developer consoles, aerospace instrumentation, and high-performance developer tooling, the visual language balances rigorous academic utility with modern telemetry aesthetics. Deep slate environments eliminate peripheral distractions, while surgical, vibrant chromatic assignments cleanly delineate divergent algorithmic behaviors: expansive water-like wavefronts for BFS, and piercing, vine-like directional descents for DFS. UI containers feel dense, tactile, and structured, utilizing hairline borders and low-luminance surfaces rather than heavy illustrative ornament.

## Colors
The palette operates on an absolute dark-mode foundation, rooted in `#0B1120` (canvas base) and `#0F172A` (instrument panel elevation). Surface layers transition into `#1E293B` for sub-containers and controls, articulated by `#334155` for crisp hairline borders and structural dividers.

Chromatic mapping is semantic and non-interchangeable:
- **Primary (BFS Domain / Wavefront / Queue):** `#38BDF8` (Sky) as the primary active marker and current node, paired with `#2563EB` (Cobalt) for settled/visited path clusters and level-order frontiers.
- **Secondary (DFS Domain / Branch Descent / Stack):** `#34D399` (Mint) as the active probing marker, paired with `#059669` (Deep Emerald) for backtrack-resolved segments and deep recursive trails.
- **Tertiary & System Feedback:** `#6366F1` (Indigo) reserved for neutral graph overlays (unvisited cells, global grid reference, start/target nodes), `#F43F5E` for collision walls/dead ends, and `#F59E0B` for traversal pauses and runtime warnings.
- **Text & Neutral Contrast:** Primary data readouts use `#F8FAFC`, secondary documentation `#94A3B8`, and structural grid hints `#475569`.

## Typography
- **Space Grotesk**: Display tier for algorithm identities, stage headings, and comparative outcome banners.
- **Geist**: Readability for descriptive theory, algorithm complexity notations (Big-O analysis), and configuration labels.
- **JetBrains Mono**: Operational engine for Cartesian grid coordinates `(x, y)`, stack frames, FIFO queues, tick counts, memory overhead allocations, and millisecond counters (`font-variant-numeric: tabular-nums`).

## Layout & Components
- **Global Control Deck**: Playback controls, speed switches, maze presets.
- **Synchronized Step Tick & Scrubber**: Real-time step counter and execution progress.
- **Dual Split-Screen Arena**: Left panel for BFS (FIFO Queue visualization) and right panel for DFS (LIFO Stack visualization).
- **Comparative Metrics**: Explored ratio bars, Big-O complexity comparison, live telemetry stream.
