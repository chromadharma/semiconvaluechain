# Global Semiconductor Supply Chain — Infrastructural Power & Structural Chokepoints

**Working Paper · Sahasrik Rudraveera Ragani · Ahmedabad University · 2026**

→ **[Live Visualisation](https://chromadharma.github.io/semiconductor-supply-chain)**
→ **[Methodology](https://rudraveera.github.io/semiconductor-supply-chain/methodology.html)**
→ **[Findings Paper](findings.md)**

---

## What This Is

An interactive network visualisation of the global semiconductor supply chain, modelled as a six-layer directed graph. The project applies betweenness centrality to identify structural chokepoints — nodes through which a disproportionate share of global supply-chain traffic must pass — and argues that these chokepoints, not formal diplomatic relationships, are where geopolitical power in the semiconductor system actually resides.

The analysis draws on Benjamin Braun's concept of infrastructural power, Bruno Latour's actor-network theory, and Jackson & Wolinsky's network formation game theory.

---

## Repository Structure

```
semiconductor-supply-chain/
├── data/
│   ├── Raw/                          ← Source files (download instructions below)
│   │   ├── usgs_gallium_ts.xlsx
│   │   ├── oecd_tiva_C26.csv
│   │   ├── comtrade_hs8486_2022.csv
│   │   ├── comtrade_hs8542_2022.csv
│   │   ├── comtrade_hs8541.csv
│   │   ├── comtrade_hs852351_852352_852359_2022.csv
│   │   └── ne_centroids.geojson
│   └── Processed/                    ← R pipeline outputs (committed for convenience)
│       ├── nodes.json
│       ├── edges.json
│       └── meta.json
├── scripts/
│   └── 01_network_pipeline.R         ← Full auditable pipeline
├── web/                              ← Frontend (deploy this folder to GitHub Pages)
│   ├── index.html
│   ├── methodology.html
│   ├── findings.md
│   ├── nodes.json                    ← Copy from data/Processed/
│   ├── edges.json
│   └── meta.json
├── findings.md                       ← Analytical findings document
├── README.md                         ← This file
└── .gitignore
```

---

## Reproducing from Scratch

### Prerequisites

- R 4.0+ with RStudio
- R packages: `tidyverse`, `readxl`, `jsonlite`, `igraph`
- Python 3 (for local server only)
- A browser with WebGL support (Chrome or Firefox recommended)

### Step 1 — Clone

```bash
git clone https://github.com/rudraveera/semiconductor-supply-chain
cd semiconductor-supply-chain
```

### Step 2 — Download Raw Data

Download each file and place it in `data/Raw/` with the exact filename shown.

| File | Source | URL |
|------|--------|-----|
| `usgs_gallium_ts.xlsx` | USGS National Minerals Information Center | [usgs.gov/centers/national-minerals-information-center/gallium-statistics-and-information](https://www.usgs.gov/centers/national-minerals-information-center/gallium-statistics-and-information) |
| `oecd_tiva_C26.csv` | OECD TiVA 2025 edition — Principal Indicators, levels | [stats.oecd.org](https://stats.oecd.org/Index.aspx?DataSetCode=TIVA_2023_C1) · Measure: EXGR_DVA · Sector: C26 · Years: 2015–2022 |
| `comtrade_hs8486_2022.csv` | UN Comtrade Plus — HS 8486, 2022 | [comtradeplus.un.org](https://comtradeplus.un.org) · HS 8486 · Year 2022 · Flow X+M |
| `comtrade_hs8542_2022.csv` | UN Comtrade Plus — HS 8542, 2022 | As above · HS 8542 |
| `comtrade_hs8541.csv` | UN Comtrade Plus — HS 8541, 2022 | As above · HS 8541 |
| `comtrade_hs852351_852352_852359_2022.csv` | UN Comtrade Plus — HS 852351/52/59, 2022 | As above · HS 852351, 852352, 852359 |
| `ne_centroids.geojson` | Natural Earth Admin-0 | [raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson](https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson) |

**Note on Comtrade access:** Comtrade Plus requires a free account for bulk exports. Register at [comtradeplus.un.org](https://comtradeplus.un.org). Filter to: Reporter = All, Partner = World (W00), Year = 2022, Flow = Both.

### Step 3 — Run the R Pipeline

```r
# In RStudio: open scripts/01_network_pipeline.R
# The RAW and PROC paths are hardcoded at the top — update them to your machine

# Install packages once:
install.packages(c("tidyverse", "readxl", "jsonlite", "igraph"))

# Then hit Ctrl+Shift+S to source the script
# Expected runtime: < 2 minutes
# Expected output:
#   data/Processed/nodes.json  (39 nodes)
#   data/Processed/edges.json  (485 edges)
#   data/Processed/meta.json   (layer definitions)
```

### Step 4 — Copy Processed Files to Web Folder

```bash
cp data/Processed/nodes.json web/
cp data/Processed/edges.json web/
cp data/Processed/meta.json  web/
```

### Step 5 — Serve Locally

```bash
cd web/
python -m http.server 8000
# Open http://localhost:8000 in Chrome or Firefox
```

---

## Deploying to GitHub Pages

1. Push the contents of `web/` to the root of your `gh-pages` branch, OR
2. In repository Settings → Pages → Source, select your main branch and `/web` folder.
3. The site will be live at `https://[username].github.io/semiconductor-supply-chain/`

---

## Network Statistics (current pipeline output)

| Metric | Value |
|--------|-------|
| Total nodes | 39 (24 countries + 15 firms) |
| Total edges | 485 |
| Supply chain layers | 6 |
| Top betweenness node | ASML (Equipment, BC = 0.98) |
| Second highest | TSMC (Fabrication, BC = 0.95) |
| Highest concentration layer | Raw Extraction (HHI = 0.680) |
| Most dispersed layer | Design & IP (HHI = 0.150) |

---

## Data Sources & Citations

```
USGS (2026). Mineral Commodity Summaries 2026: Gallium. U.S. Geological Survey.
  https://pubs.usgs.gov/periodicals/mcs2026/

OECD (2025). Trade in Value Added (TiVA) 2025 Edition.
  https://stats.oecd.org/Index.aspx?DataSetCode=TIVA_2023_C1

UN Comtrade (2022). International Trade Statistics Database.
  HS codes: 8486, 8541, 8542, 852351, 852352, 852359.
  https://comtradeplus.un.org

Natural Earth (2023). Admin-0 Countries, 1:110m scale.
  https://www.naturalearthdata.com/

SEMI (2023). Materials Market Data Subscription. Semiconductor Equipment and Materials International.

SIA (2023). State of the U.S. Semiconductor Industry 2023. Semiconductor Industry Association.

IC Insights (2023). Global Wafer Capacity 2023-2027. IC Insights / Knometa Research.

Gartner (2022). EDA Market Share Analysis. Gartner, Inc.

Jackson, M.O. & Wolinsky, A. (1996). A Strategic Model of Social and Economic Networks.
  Journal of Economic Theory, 71(1), 44–74.

Brandes, U. (2001). A Faster Algorithm for Betweenness Centrality.
  Journal of Mathematical Sociology, 25(2), 163–177.

Braun, B. (2023). Infrastructural Power. Annual Review of Political Science (forthcoming).
```

---

## Theoretical Framework

Three bodies of theory underpin the analysis:

**1. Infrastructural Power (Braun):** Power that derives from control over critical infrastructure rather than ownership of assets or formal authority. Applied here to argue that TSMC's and ASML's leverage is infrastructural — it operates through their position in the network, not through any formal diplomatic relationship.

**2. Actor-Network Theory (Latour):** Refuses the distinction between human and non-human actors. ASML's EUV machines, Japan's photoresist chemistry, and TSMC's process nodes are enrolled as actants — not neutral substrates, but participants that shape what is possible. Chokepoints are effects of stabilised actor-networks, not pre-given structural features.

**3. Network Formation Games (Jackson & Wolinsky):** Predicts that when direct link costs exceed the marginal benefit of bypassing a hub, the equilibrium network topology is a star. Provides the formal mechanism for why decoupling from TSMC is not individually rational under current cost structures.

---

## Licence

Code: MIT License
Data: Derived from public sources; see citations above. Raw data files retain their original licences.
Analysis and written content: CC BY 4.0

---

## Contact

Sahasrik Rudraveera Ragani · Ahmedabad University
sahasrik.ragani@gmail.com
