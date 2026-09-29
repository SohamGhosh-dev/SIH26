# 3D ULPIN Cadastral Digital Twin & Strata Land Management System

An ISO 19152 (Land Administration Domain Model - LADM) compliant 3D Cadastral Digital Twin system designed for high-density urban jurisdictions. The platform integrates high-resolution satellite imagery, airborne LiDAR point clouds, and legal cadastral records to provide volumetric 3D ULPIN (Unique Land Parcel Identification Number) tracking, automated building discrepancy audits, and multi-tier subterranean utility visualization.

---

## Key Highlights

* **Decoupled System Architecture:** Independent **Identification Model** (spatial ingestion, OBB strata partitioning, and 3D ULPIN generation) and **Segregation Model** (data-fusion confidence metrics and compliance classification).


* **BhuNaksha-Compliant 2D/3D Cadastre:** Photorealistic ESRI World Satellite basemap overlaid with bright yellow statutory cadastral plot boundaries and dynamic Mouza/sector segmentation.
* **Tri-State Pattern Audit Engine:** Automated cross-referencing between user claims, government revenue databases, and on-ground LiDAR/drone surveys:


* 🟩 **Green (Verified Match / TRUE):** Complete consensus across user claims, master plans, and physical survey.


* 🟥 **Red (Suspicious / Legal Mismatch):** Structural height encroachments (e.g., unauthorized floors) or statutory setback violations.


* 🟧 **Orange (Detected but Unclaimed):** Asset detected via satellite/LiDAR feature extraction but unrecorded in municipal tax rolls or missing citizen title claims.




* **Multi-Sensor Audit Confidence Score:** Weighted consensus engine fusing LiDAR point cloud density, AI blueprint vectorization ($91.8\%$ mIoU), and statutory GIS setback alignment.


* **Oriented Bounding Box (OBB) Strata Partitioning:** Area-aware architectural decomposition that detects the principal facade orientation angle ($\theta$) and partitions floorplates into realistic, orthogonal strata units.
* **Multi-Tier Subterranean Engineering Strata:** True cylindrical and conduit sweeps (`polylineVolume`) for deep transit tunnels (Metro: $-14\text{ m}$), municipal water mains (DN800: $-5.2\text{ m}$), and high-voltage power/telecom duct banks ($-2.2\text{ m}$).
* **Role-Based Portals:** Role-segregated views for **Citizen Self-Service** and **Government Revenue Authorities**.


* **Engineering CAD & Legal Reporting:** Instant in-browser ASCII AutoCAD (`.dxf`) 3D face export and print-ready Municipal Section 217 Audit Clearance Certificates.

---

## System Architecture

```text
+---------------------------------------------------------------------------------------+
|                                    DATA LAYERS                                        |
|  OSM Vector Buildings  |  Airborne LiDAR (.LAS)  |  Citizen Declarations  |  Govt DB  |
+---------------------------------------------------------------------------------------+
                                            │
                                            ▼
+---------------------------------------------------+  +--------------------------------+
|              1> IDENTIFICATION MODEL              |  |      2> SEGREGATION MODEL      |
|                                                   |  |                                |
|  • BhuNaksha 2D Cadastral Plot Boundary Alignment |  |  • Multi-Sensor Data Fusion    |
|  • Facade Orientation (OBB Affine Alignment)      |  |  • Confidence Score Engine     |
|  • Area-Proportional Strata Unit Partitioning     |  |  • Tri-State Verification:     |
|  • 3D PolylineVolume Utility Sweeps               |  |     🟩 Green  : True Match     |
|  • Deterministic 3D ULPIN Minting                 |  |     🟥 Red    : Legal Mismatch |
|    <State>-<Dist>-<Plot>:<Tower>-<Floor>-<Unit>   |  |     🟧 Orange : Unclaimed      |
+---------------------------------------------------+  +--------------------------------+
                                            │                              │
                                            └──────────────┬───────────────┘
                                                           │
                                                           ▼
+---------------------------------------------------------------------------------------+
|                                  ROLE-BASED PORTALS                                   |
+---------------------------------------------------+-----------------------------------+
|                  CITIZEN PORTAL                   |         GOVERNMENT PORTAL         |
|  • Public 2D/3D Cadastral Map                     |  • Full Spatial Audit Stack       |
|  • Individual 3D ULPIN Title Verification         |  • 3D ULPIN Resident Roster       |
|  • Unit Claim Submission                          |  • Municipal Tax Assessment Dues  |
|  • Public Compliance Notices                      |  • Internal Unresolved API Flags  |
+---------------------------------------------------+-----------------------------------+

```

---

## Directory Structure

```text
Project/
├── datasets/
│   ├── buildings.geojson               # OpenStreetMap physical building vector footprints
│   ├── sample_lidar.las                # Calibrated LiDAR point cloud (Ground datum = 11.5m)
│   ├── floorplans_dataset/             # Architectural blueprint raster segmentation dataset
│   ├── user_verified_registry.json     # Dataset 1: Citizen-claimed properties and deeds
│   ├── govt_property_db.json           # Dataset 2: Municipal sanctions, tax status, and audit tags
│   ├── resident_registry.json          # Dataset 3: Strata unit tenant profiles indexed to 3D ULPIN
│   ├── generate_dual_registries.py     # Administrative registry and resident profile generator
│   └── local_district_2d.geojson       # Pipeline-compiled district runtime dataset
│
├── models/
│   ├── __init__.py
│   ├── floorplan_partition_model.py    # OBB affine rotation and orthogonal strata slicer
│   ├── identification_model.py         # Spatial plinth, mother plot, and 3D ULPIN engine
│   └── segregation_model.py            # Confidence score calculator and tri-state pattern engine
│
├── static/
│   ├── css/
│   └── js/
│
├── index.html                          # Entry role selection gateway (Citizen vs. Govt)
├── viewer.html                         # CesiumJS 3D digital twin application
├── pipeline_runner.py                  # End-to-end spatial processing orchestrator
├── launch.bat                          # Automated background server bootstrapper
├── stop.bat                            # Process termination script
└── README.md

```

---

## Dataset Schema

The system integrates real physical geometries with administrative cadastral registries:

1. **Physical Geospatial Geometries (Real):**
* `buildings.geojson`: Surveyed vector plinths and parcel outlines covering Sector V / New Town, Kolkata.
* `sample_lidar.las`: Airborne point cloud establishing the terrain base ($Z = 11.5\text{ m}$) and structural rooftop limits.
* `floorplans_dataset/`: Semantic architectural blueprints benchmarked for interior wall and boundary extraction.


2. **Administrative Cadastral Registries (Synthesized):**
* `user_verified_registry.json`: Citizen self-declarations (claimed storeys, registered usage, deed filing dates).
* `govt_property_db.json`: Municipal back-office master plans (permissible Floor Area Ratios, tax liabilities, LiDAR change-detection alerts, and statutory setback buffers).
* `resident_registry.json`: Unit-by-unit occupancy roster (occupant name, masked identity hash, carpet area, lease category, and municipal property tax clearance) keyed directly to vertical 3D ULPINs.



---

## 3D ULPIN Format Specification

The minted 3D ULPIN adheres to hierarchical spatial decomposition standards:

$$\mathbf{3D\text{ }ULPIN} = \underbrace{\text{WB-KOL-PLOT-IIF-04}}_{\text{2D Mother Plot}} \,:\, \underbrace{\text{T1}}_{\text{Structure}} \,-\, \underbrace{\text{F16}}_{\text{Storey Level}} \,-\, \underbrace{\text{U02}}_{\text{Strata Unit}}$$

* **Subsurface Utility Token:** `WB-SUB-WATER-01:Z-DN800-TRUNK`
* **Subsurface Transit Token:** `WB-SUB-METRO-01:Z-SUB-TUNNEL`

---

## Installation & Setup

### Prerequisites

* **Python 3.10+** (Ensure Python is added to system `PATH`)
* Web browser with WebGL support (Chrome, Edge, or Firefox)

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/SIH26.git
cd <repo-name>

```

### 2. Install Dependencies

Install required spatial computation libraries:

```bash
pip install shapely

```

### 3. Generate Datasets and Compile Runtime Geometry

Compile the administrative registries and execute the identification and segregation pipeline:

```bash
python datasets/generate_dual_registries.py
python pipeline_runner.py

```

---

## Running the Application

### Quick Launch (Windows)

* **To Start:** Double-click `launch.bat`. This terminates any hanging processes on port `8000`, boots a background HTTP server, and opens `http://localhost:8000/index.html`.
* **To Stop:** Double-click `stop.bat` to terminate the server process and free port `8000`.

### Manual Launch

Start a local server from the project root:

```bash
python -m http.server 8000

```

Navigate to:

* **Role Selection Portal:** `http://localhost:8000/index.html`
* **Government Revenue Gateway:** `http://localhost:8000/viewer.html?role=govt`
* **Citizen Public Portal:** `http://localhost:8000/viewer.html?role=citizen`

---

## Navigation & Controls

| Action | Control |
| --- | --- |
| **Select / Inspect Parcel** | Left-Click on plot boundary, building plinth, or utility corridor |
| **Extrude Building Storeys** | Left-Click on any green, red, or orange building plinth |
| **Inspect Strata Flat / Unit** | Left-Click on individual 3D unit slab to view dossier and 3D ULPIN |
| **Subsurface Inspection** | Left-Click on any subterranean utility corridor (Metro, Water, Power) |
| **Tilt Camera Angle** | Middle-Click + Drag **or** `Ctrl` + Left-Click + Drag |
| **Rotate View** | Right-Click + Drag |
| **Zoom** | Mouse Scroll Wheel |
| **Reset to 2D Cadastre** | Click `← Back to 2D Cadastral Map` in the HUD card |
| **Locate Specific Parcel** | Type plot ID or ULPIN into top search bar and click `Find` |
| **Export to AutoCAD** | Select any 3D strata unit and click `📐 Export 3D Strata Unit to CAD (.DXF)` |
| **Print Audit Notice** | Select any unit and click `📄 Generate Official Audit Certificate` |

---

## Standards Compliance

* **ISO 19152 (LADM):** Implements Core Land Administration profiles (`LA_SpatialUnit`, `LA_BAUnit`, `LA_LegalSpaceUtilityNetwork`).
* **ULPIN Guidelines (Department of Land Resources, India):** Integrates 2D geospatial coordinates with vertical strata and sub-parcel identifiers.
* **RERA & Municipal Building By-Laws:** Detects Floor Area Ratio (FAR) violations, unauthorized vertical extensions, and mandatory road setback infringements.
