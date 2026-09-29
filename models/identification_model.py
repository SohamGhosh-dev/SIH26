import os
import sys
import json
import math
from shapely.geometry import shape, mapping, Polygon, LineString

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from models.floorplan_partition_model import FloorplanPartitionModel

class IdentificationModel:
    def __init__(self, buildings_path=None, hero_idx=3506):
        if buildings_path is None:
            self.buildings_path = os.path.join(ROOT_DIR, "datasets", "buildings.geojson")
        else:
            self.buildings_path = buildings_path

        self.hero_idx = hero_idx
        self.hero_building_idx = None
        self.hero_geom = None
        self.compound_geom = None
        self.selected_features = []
        self.partition_model = FloorplanPartitionModel()

    def load_and_index(self):
        with open(self.buildings_path, "r", encoding="utf-8") as f:
            osm_data = json.load(f)

        features = osm_data["features"]
        self.compound_geom = shape(features[self.hero_idx]["geometry"])
        centroid = self.compound_geom.centroid

        for idx, feat in enumerate(features):
            if idx == self.hero_idx:
                continue
            geom = shape(feat["geometry"])
            if self.compound_geom.contains(geom.centroid) or (self.compound_geom.intersection(geom).area / geom.area > 0.85):
                self.hero_building_idx = idx
                self.hero_geom = geom
                break

        local = []
        for idx, feat in enumerate(features):
            geom = shape(feat["geometry"])
            dist = centroid.distance(geom.centroid)
            if dist < 0.011:
                local.append((dist, idx, feat, geom))

        local.sort(key=lambda x: x[0])
        self.selected_features = local[:220]
        return self

    def generate_parcels_and_entities(self):
        records = []
        minx, miny, maxx, maxy = self.compound_geom.bounds

        # 1. Mother Parcel (Mani Casadona Compound)
        records.append({
            "parcel_id": "WB-KOL-PLOT-IIF-04",
            "name": "Mani Casadona Mother Cadastral Parcel",
            "entity_type": "mother_parcel",
            "is_building": False,
            "is_plot_boundary": True,
            "is_subsurface": False,
            "geometry": mapping(self.compound_geom)
        })

        # 2. Buildings, Vacant Plots & Commercial Parcels
        for dist, orig_idx, feat, geom in self.selected_features:
            if orig_idx == self.hero_idx:
                continue

            is_hero_tower = (orig_idx == self.hero_building_idx)
            parcel_id = "WB-KOL-PLOT-IIF-04" if is_hero_tower else f"WB-KOL-PLOT-{orig_idx:04d}"
            props = feat.get("properties", {})
            name = "Mani Casadona Main Tower" if is_hero_tower else props.get("name", f"Structure #{orig_idx:04d}")

            # Statutory 2D Land Parcel (BhuNaksha Plot Boundary)
            if not is_hero_tower:
                plot_geom = geom.convex_hull.buffer(0.00008)
                records.append({
                    "parcel_id": parcel_id,
                    "name": f"Cadastral Plot #{orig_idx:04d}",
                    "entity_type": "land_plot",
                    "is_building": False,
                    "is_plot_boundary": True,
                    "is_subsurface": False,
                    "geometry": mapping(plot_geom)
                })

            raw_levels = props.get("building:levels")
            if is_hero_tower:
                levels = 16
            elif raw_levels and raw_levels.isdigit():
                levels = int(raw_levels)
            else:
                levels = 4 + (orig_idx % 6)

            unit_footprints = self.partition_model.partition(geom)
            num_units = len(unit_footprints)

            records.append({
                "parcel_id": parcel_id,
                "building_id": f"BLD-{orig_idx:04d}",
                "name": name,
                "entity_type": "building",
                "levels": levels,
                "num_units": num_units,
                "is_building": True,
                "is_plot_boundary": False,
                "is_hero": is_hero_tower,
                "is_subsurface": False,
                "units_2d": unit_footprints,
                "geometry": mapping(geom)
            })

        # 3. Entity Type: Vacant Development Parcel (Unconstructed Land)
        vacant_poly = Polygon([
            [maxx + 0.0010, miny - 0.0010],
            [maxx + 0.0028, miny - 0.0010],
            [maxx + 0.0028, miny + 0.0012],
            [maxx + 0.0010, miny + 0.0012],
            [maxx + 0.0010, miny - 0.0010]
        ])
        records.append({
            "parcel_id": "WB-KOL-VACANT-088",
            "name": "HIDCO Commercial Reserve Plot (Vacant)",
            "entity_type": "vacant_land",
            "is_building": False,
            "is_plot_boundary": False,
            "is_subsurface": False,
            "geometry": mapping(vacant_poly)
        })

        # 4. Entity Type: Municipal Water Body / Retention Basin (Eco-Cadastre)
        waterbody_poly = Polygon([
            [minx - 0.0035, maxy + 0.0005],
            [minx - 0.0012, maxy + 0.0005],
            [minx - 0.0015, maxy + 0.0028],
            [minx - 0.0038, maxy + 0.0025],
            [minx - 0.0035, maxy + 0.0005]
        ])
        records.append({
            "parcel_id": "WB-KOL-WATER-014",
            "name": "New Town Municipal Water Retention Lake",
            "entity_type": "water_body",
            "is_building": False,
            "is_plot_boundary": False,
            "is_subsurface": False,
            "geometry": mapping(waterbody_poly)
        })

        # 5. Subsurface Utility Networks
        metro_centerline = [
            [minx - 0.004, miny + 0.00065],
            [maxx + 0.004, miny + 0.00065]
        ]
        metro_poly = LineString(metro_centerline).buffer(0.00028, cap_style=2, join_style=2)
        records.append({
            "parcel_id": "WB-SUB-METRO-01",
            "name": "East-West Subsurface Metro Corridor",
            "entity_type": "subsurface_utility",
            "is_building": False,
            "is_plot_boundary": False,
            "is_subsurface": True,
            "utility_type": "metro",
            "centerline": metro_centerline,
            "sub_depth_center": -14.0,
            "sub_radius": 3.2,
            "geometry": mapping(metro_poly)
        })

        water_centerline = [
            [minx - 0.003, maxy + 0.002],
            [minx + 0.0004, miny + 0.0006],
            [minx + 0.0012, miny - 0.0018],
            [maxx + 0.0025, miny - 0.0035]
        ]
        water_poly = LineString(water_centerline).buffer(0.00012, cap_style=2, join_style=2)
        records.append({
            "parcel_id": "WB-SUB-WATER-01",
            "name": "NKDA Subsurface Potable Water Main (DN800 Trunk)",
            "entity_type": "subsurface_utility",
            "is_building": False,
            "is_plot_boundary": False,
            "is_subsurface": True,
            "utility_type": "water",
            "centerline": water_centerline,
            "sub_depth_center": -5.2,
            "sub_radius": 0.85,
            "geometry": mapping(water_poly)
        })

        elec_centerline = [
            [minx - 0.004, miny - 0.0002],
            [maxx + 0.003, miny - 0.0002],
            [maxx + 0.003, maxy + 0.002]
        ]
        elec_poly = LineString(elec_centerline).buffer(0.00008, cap_style=2, join_style=2)
        records.append({
            "parcel_id": "WB-SUB-ELEC-01",
            "name": "WBSEDCL Subsurface 33kV Power Conduit & Telecom Duct",
            "entity_type": "subsurface_utility",
            "is_building": False,
            "is_plot_boundary": False,
            "is_subsurface": True,
            "utility_type": "electric",
            "centerline": elec_centerline,
            "sub_depth_center": -2.2,
            "sub_width": 1.8,
            "sub_height": 1.0,
            "geometry": mapping(elec_poly)
        })

        return records