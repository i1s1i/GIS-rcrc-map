# 🏙️ Riyadh Interactive GIS Dashboard

> **An interactive geospatial dashboard for Riyadh city, built with Python, Dash, Plotly & Folium — powered by open data from the Royal Commission for Riyadh City (RCRC).**



---

## 📌 Project Overview

This project is a **full-stack GIS (Geographic Information System) dashboard** that visualizes open data published by the **Royal Commission for Riyadh City (RCRC)** on their [Open Data Platform](https://data.rcrc.gov.sa). It combines an **interactive choropleth map** of Riyadh's districts with **analytical charts and KPI cards**, giving stakeholders a single-pane-of-glass view into the city's demographics, housing, transportation, culture, and environment.

### What It Demonstrates

| Skill Area | Details |
|---|---|
| **GIS & Spatial Analysis** | Fetching & rendering GeoJSON polygons from OpenStreetMap Overpass API; classifying 130+ districts into 5 geographic sectors using coordinate-based trigonometric classification |
| **Data Engineering** | Automated ETL pipeline: scraping the RCRC Opendatasoft catalog API → cleaning with Pandas → merging with geospatial data |
| **Dashboard Development** | Production-ready Dash web application with reactive callbacks, dark-themed design system, and RTL Arabic layout |
| **Data Visualization** | Plotly pie & bar charts, Folium interactive map with rich HTML popups, real-time sector filtering |
| **API Integration** | RESTful API consumption from `data.rcrc.gov.sa` (Opendatasoft v2.1 API) |

---

## 🗺️ Key Features

### 1. Interactive District Map
- **130+ Riyadh districts** rendered as GeoJSON polygons on a dark CartoDB basemap
- Districts are **color-coded by sector** (North ⬆️, East ➡️, South ⬇️, West ⬅️, Center 🎯)
- **Click any district** to reveal a rich popup with all available datasets organized by theme
- Hover tooltips show district name and sector
- Layer controls for toggling sector visibility

### 2. Sector Filtering
- Checkbox-based filter panel on the sidebar
- All charts and the map update reactively when sectors are toggled
- Real-time district count per sector displayed as KPI cards

### 3. Analytical Charts
- **Donut chart**: District distribution by sector (proportional breakdown)
- **Horizontal bar chart**: Top 10 datasets ranked by record count
- **Sidebar dataset list**: Full catalog summary with theme icons and record counts

### 4. Rich Data Popups
- Every district popup contains the full RCRC dataset catalog
- Datasets organized by **6 thematic categories**:
  - 👥 Population, Rights & Institutions
  - 🏠 Housing, Energy & Environment
  - 💼 Economy & Employment
  - 🎭 Culture & Communication
  - 🚇 Regions, Transport & Services
  - 🌍 Riyadh at the National & Global Level
- Each dataset entry shows: title, record count, keyword badges, and a direct link to the RCRC platform

### 5. Design System
- **Dark theme** with carefully curated color palette (`#0A0E17` background, `#D4A843` gold accents)
- Full **RTL (Right-to-Left) Arabic** support
- Responsive card layout with consistent border radius and spacing
- Scrollable sidebar with overflow management

---

## 🏗️ Architecture & Project Structure

```
GIS rcrc map/
│
├── app.py                  # Main Dash application (449 lines)
│                           #   - Design tokens & color palette
│                           #   - Data loading (CSV + GeoJSON)
│                           #   - Popup HTML generation
│                           #   - Folium map builder
│                           #   - Dash layout & callbacks
│
├── fetch_geo.py            # GeoJSON data pipeline
│                           #   - Queries Overpass API for Riyadh districts
│                           #   - Builds polygons from OSM relations
│                           #   - Classifies sectors via trigonometry
│                           #   - Outputs data/riyadh_districts.geojson
│
├── fetcher.py              # RCRC API data fetcher
│                           #   - Fetches records from Opendatasoft API
│                           #   - Saves JSON files for 6 key datasets
│
├── datasets.csv            # RCRC open data catalog (36 datasets)
│                           #   - 202 KB, 36 rows of metadata
│                           #   - Titles, descriptions, themes, keywords
│                           #   - Record counts & API endpoint IDs
│
├── data/
│   └── riyadh_districts.geojson  # District boundaries (180 KB)
│                                 #   - 130+ polygons with properties:
│                                 #     name_ar, name_en, sector, color
│
└── venv/                   # Python virtual environment
```

---

## ⚙️ Technical Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | Python 3.10+ | Core runtime |
| **Web Framework** | Dash (by Plotly) | Reactive dashboard server |
| **Charting** | Plotly Express + Graph Objects | Interactive pie/bar charts |
| **Mapping** | Folium (Leaflet.js wrapper) | Choropleth map with popups |
| **Data Processing** | Pandas | CSV/JSON parsing, aggregation |
| **Basemap** | CartoDB Dark Matter | Free dark-themed tile layer |
| **Geospatial Source** | OpenStreetMap Overpass API | District boundary polygons |
| **Data Source** | RCRC Opendatasoft API | Open government datasets |

---

## 🚀 Getting Started

### Prerequisites

- Python **3.10** or higher
- pip (Python package manager)

### Installation

```bash
# 1. Clone or download the project
cd "GIS rcrc map"

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install dash plotly folium pandas requests

# 4. (Optional) Regenerate district boundaries from OpenStreetMap
python fetch_geo.py

# 5. (Optional) Fetch latest records from RCRC API
python fetcher.py
```

### Running the Dashboard

```bash
python app.py
```

The dashboard will start at **http://localhost:8050**. Open it in your browser to explore the interactive map and charts.

---

## 📊 Data Sources

All data is sourced from the **Royal Commission for Riyadh City (RCRC)** open data platform:

| Dataset Category | Count | Examples |
|---|---|---|
| **Population & Demographics** | 7 datasets | Population by nationality/age/gender, marital status, dependency ratio |
| **Housing & Environment** | 12 datasets | Home ownership, dwelling types, building materials, air quality stations |
| **Transport & Infrastructure** | 4 datasets | Metro stations (94), metro lines (6), bus stops (3,010), bus routes (117) |
| **Land Use** | 2 datasets | Residential land use by type, land occupation by sector |
| **Culture & Events** | 3 datasets | Noor Riyadh Festival stats, historical milestones, World Expo data |

**API Endpoint**: `https://data.rcrc.gov.sa/api/explore/v2.1/catalog/datasets/{id}/records`

---

## 🔧 How It Works

### Data Pipeline

```
OpenStreetMap Overpass API          RCRC Opendatasoft API
         │                                  │
    fetch_geo.py                        fetcher.py
         │                                  │
         ▼                                  ▼
 riyadh_districts.geojson              datasets.csv
 (130+ district polygons)          (36 dataset metadata)
         │                                  │
         └──────────── app.py ──────────────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
         Folium Map   Plotly     Dash
         (Leaflet)   Charts    Layout
              │          │          │
              └──────────┼──────────┘
                         ▼
              http://localhost:8050
```

### Sector Classification Algorithm

Districts are classified into 5 sectors based on their centroid coordinates relative to Riyadh's center point (24.7136°N, 46.6753°E):

```python
# Trigonometric classification
angle = atan2(delta_lon, delta_lat)  # degrees

if distance < 0.08°:  → Center (وسط)
elif -45° ≤ angle < 45°:  → North (شمال)
elif 45° ≤ angle < 135°:  → East (شرق)
elif angle ≥ 135° or < -135°:  → South (جنوب)
else:  → West (غرب)
```

---

## 🎨 Design Decisions

| Decision | Rationale |
|---|---|
| **Dark theme** | Reduces eye strain for data-heavy dashboards; makes the colored map sectors stand out |
| **RTL layout** | Primary audience reads Arabic; all content is right-aligned |
| **Embedded Folium via Iframe** | Folium produces standalone HTML; embedding via `srcDoc` in Dash avoids external file dependencies |
| **Pre-generated popups** | Computing 130+ rich HTML popups at startup avoids lag on user interaction |
| **Sector-based filtering** | Provides a meaningful geographic subdivision without requiring sub-municipality data |

---

## 📈 Future Enhancements

- [ ] Add real-time metro station and bus stop markers with clustering
- [ ] Integrate population heatmaps per district
- [ ] Add time-series charts for population growth (2010–2022)
- [ ] Implement bilingual toggle (Arabic ↔ English)
- [ ] Deploy to a free hosting platform (Render / Railway)
- [ ] Add light/dark mode toggle

---

## 📄 License

This project uses open data published under the **Saudi Arabia Open Data License**, which permits free use, reuse, and redistribution with proper attribution to the source.

**Data Source**: [Royal Commission for Riyadh City — Open Data Platform](https://data.rcrc.gov.sa)

---

<div align="center">

**Built with ❤️ for Riyadh 🏙️**

*Showcasing Python · GIS · Data Engineering · Dashboard Development*

</div>
