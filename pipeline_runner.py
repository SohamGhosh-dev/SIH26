import os
import sys
import json

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from models.identification_model import IdentificationModel
from models.segregation_model import SegregationModel

print("[*] Running 1> Identification Model (Multi-Entity 2D/3D Cadastre)...")
buildings_path = os.path.join(ROOT_DIR, "datasets", "buildings.geojson")
id_model = IdentificationModel(buildings_path=buildings_path).load_and_index()
spatial_records = id_model.generate_parcels_and_entities()
print(f"[OK] Identification complete: Extracted {len(spatial_records)} multi-type property entities.")

print("[*] Running 2> Segregation Model (Tri-State Audit Comparison)...")
user_path = os.path.join(ROOT_DIR, "datasets", "user_verified_registry.json")
govt_path = os.path.join(ROOT_DIR, "datasets", "govt_property_db.json")
seg_model = SegregationModel(user_db_path=user_path, govt_db_path=govt_path)

final_features = []
for record in spatial_records:
    parcel_id = record["parcel_id"]
    is_subsurface = record.get("is_subsurface", False)
    utility_type = record.get("utility_type", None)
    entity_type = record.get("entity_type", "building")
    is_plot = record.get("is_plot_boundary", False)

    conf_score, sensor_src = seg_model.calculate_confidence(parcel_id, is_subsurface, utility_type)
    audit = seg_model.audit_property(parcel_id, is_subsurface, utility_type, entity_type)

    props = {
        "parcel_id": parcel_id,
        "name": record["name"],
        "entity_type": entity_type,
        "is_building": record.get("is_building", False),
        "is_plot_boundary": is_plot,
        "is_subsurface": is_subsurface,
        "utility_type": utility_type,
        "confidence_score": conf_score,
        "sensor_source": sensor_src,
        "audit_state": audit["audit_state"],
        "audit_status": audit["status"],
        "alert": audit["alert"],
        "fill_color": audit["color"]
    }

    if is_subsurface:
        props["centerline"] = record.get("centerline")
        props["sub_depth_center"] = record.get("sub_depth_center")
        props["sub_radius"] = record.get("sub_radius")
        props["sub_width"] = record.get("sub_width")
        props["sub_height"] = record.get("sub_height")

    if record.get("is_building"):
        props["levels"] = record["levels"]
        props["num_units"] = record.get("num_units", 3)
        props["is_hero"] = record.get("is_hero", False)
        props["has_discrepancy"] = (audit["audit_state"] == "RED")
        props["units_2d"] = record.get("units_2d", [])

    final_features.append({
        "type": "Feature",
        "properties": props,
        "geometry": record["geometry"]
    })

output_geojson = {"type": "FeatureCollection", "features": final_features}
out_path = os.path.join(ROOT_DIR, "datasets", "local_district_2d.geojson")

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output_geojson, f, indent=2)

print(f"[OK] Success: Generated '{out_path}' with {len(final_features)} classified cadastral parcels & entities!")