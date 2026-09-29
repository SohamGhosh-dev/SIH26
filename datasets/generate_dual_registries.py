import os
import sys
import json
import random

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from models.identification_model import IdentificationModel

buildings_file = os.path.join(ROOT_DIR, "datasets", "buildings.geojson")
user_claims_file = os.path.join(ROOT_DIR, "datasets", "user_verified_registry.json")
govt_db_file = os.path.join(ROOT_DIR, "datasets", "govt_property_db.json")
resident_file = os.path.join(ROOT_DIR, "datasets", "resident_registry.json")

print("[+] Synthesizing 3 Required Data Categories (User Verified vs. Govt DB vs. Unregistered)...")
id_model = IdentificationModel(buildings_path=buildings_file).load_and_index()
spatial_records = id_model.generate_parcels_and_entities()

user_verified_db = {}
govt_property_db = {}
resident_db = {}

first_names = ["Amit", "Pooja", "Rahul", "Ananya", "Sourav", "Debolina", "Vikram", "Sneha", "Rohan", "Priyanka"]
last_names = ["Chatterjee", "Banerjee", "Mukherjee", "Sen", "Ghosh", "Dutta", "Roy", "Bose", "Das", "Sarkar"]

building_counter = 0

for record in spatial_records:
    parcel_id = record["parcel_id"]
    etype = record.get("entity_type", "building")
    name = record.get("name", f"Asset {parcel_id}")

    if etype == "vacant_land":
        # ORANGE CASE: Detected on Satellite/LiDAR, but Unclaimed & No Govt record
        govt_property_db[parcel_id] = {
            "parcel_id": parcel_id,
            "entity_type": "vacant_land",
            "name": name,
            "audit_state": "ORANGE",
            "verification_status": "UNCLAIMED_UNREGISTERED",
            "audit_note": "Physical plot perimeter detected on Satellite Imagery; No citizen title claim submitted; Municipal register unassigned.",
            "confidence_score": 89.2,
            "sensor_source": "Satellite Optical Multispectral + Municipal Drone Survey",
            "tax_status": "UNASSESSED"
        }
        continue

    elif etype == "water_body":
        # GREEN CASE: Municipal Environmental Protection Cadastre
        govt_property_db[parcel_id] = {
            "parcel_id": parcel_id,
            "entity_type": "water_body",
            "name": name,
            "audit_state": "GREEN",
            "verification_status": "STATUTORY_WATER_RESERVE",
            "audit_note": "State Wetland Conservation Zone; Verified alignment between Satellite Water Index (NDWI) and Revenue Map.",
            "confidence_score": 99.1,
            "sensor_source": "Sentinel-2 NDWI Water Extraction + NKDA Master Plan",
            "tax_status": "EXEMPT"
        }
        continue

    elif etype != "building":
        continue

    building_counter += 1
    levels = record.get("levels", 6)
    num_units = record.get("num_units", 3)
    is_hero = record.get("is_hero", False)

    # --- THREE AUDIT CONDITIONS SPECIFIED BY LEAD ---
    # 1. RED: Suspicious / Mismatched Property
    # (Exists, but built != sanctioned OR claimed by someone other than owner)
    if is_hero or (building_counter in [8, 24, 45]):
        audit_state = "RED"
        actual_levels = levels
        sanctioned_levels = levels - 1 if is_hero else levels - 2
        verification_status = "LEGAL_MISMATCH_SUSPICIOUS"
        audit_note = (
            "LiDAR point cloud detected unapproved Storey 16 (+28% Volume); Mismatch between registered deed and physical height."
            if is_hero else
            "Suspicious Boundary Conflict: Structural plinth breaches sanctioned setback; Citizen claim conflicts with Revenue survey."
        )
        conf_score = 96.8 if is_hero else 95.4
        sensor_source = "Airborne LiDAR 3D Mesh + Drone Orthophoto Verification"
        tax_status = "DEFAULT"

    # 2. ORANGE: Detected but Unclaimed / No Government Record
    elif building_counter % 7 == 0:
        audit_state = "ORANGE"
        actual_levels = levels
        sanctioned_levels = levels
        verification_status = "DETECTED_UNCLAIMED"
        audit_note = "Building footprint segmented from Satellite Imagery, but unrecorded in municipal tax rolls; No citizen title claim filed."
        conf_score = 87.5
        sensor_source = "High-Res Satellite Feature Extraction (Unregistered Asset)"
        tax_status = "UNREGISTERED"

    # 3. GREEN: Verified / True Match
    else:
        audit_state = "GREEN"
        actual_levels = levels
        sanctioned_levels = levels
        verification_status = "VERIFIED_MATCH"
        audit_note = "Full Consensus: Citizen claimed parameters match Government Municipal records and Satellite/LiDAR scans."
        conf_score = round(94.2 + (building_counter % 50) * 0.1, 1)
        sensor_source = "Municipal Cadastre GIS + LiDAR Elevation Alignment"
        tax_status = "PAID"

    # --- DATASET 1: User-Verified Property Data ---
    user_verified_db[parcel_id] = {
        "parcel_id": parcel_id,
        "claimed_by": "Mani Square Ltd / Casadona Enterprise" if is_hero else f"{random.choice(first_names)} {random.choice(last_names)}",
        "declared_floors": sanctioned_levels,
        "declared_use": "Commercial IT / ITES" if is_hero else "Residential Apartment",
        "user_verification_timestamp": "2026-04-12 10:30 IST",
        "claim_status": "CLAIMED_AND_VERIFIED" if audit_state != "ORANGE" else "UNCLAIMED"
    }

    # --- DATASET 2: Government Database Records ---
    govt_property_db[parcel_id] = {
        "parcel_id": parcel_id,
        "khasra_no": f"KH-{1200 + building_counter}",
        "khatian_no": f"KT-{600 + building_counter}",
        "sanctioned_levels": sanctioned_levels,
        "actual_detected_levels": actual_levels,
        "num_units_per_floor": num_units,
        "audit_state": audit_state,
        "verification_status": verification_status,
        "audit_note": audit_note,
        "confidence_score": conf_score,
        "sensor_source": sensor_source,
        "annual_tax_inr": 480000 if is_hero else 28000 + (building_counter * 350),
        "tax_status": tax_status
    }

    # --- Resident Strata Registry (Linked to 3D ULPIN) ---
    for floor in range(1, actual_levels + 1):
        for unit in range(1, num_units + 1):
            ulpin = f"{parcel_id}:T1-F{floor:02d}-U{unit:02d}"
            is_unauthorized = (audit_state == "RED" and floor > sanctioned_levels)
            tenant = "Under Demolition Notice" if is_unauthorized else f"{random.choice(first_names)} {random.choice(last_names)}"
            unit_sqft = 1200 if num_units == 1 else max(450, int(1800 / num_units) + (unit * 35))

            resident_db[ulpin] = {
                "3D_ULPIN": ulpin,
                "parcel_id": parcel_id,
                "floor_level": floor,
                "unit_number": f"Unit {unit:02d}",
                "occupant_name": tenant,
                "occupancy_type": "Commercial Office" if is_hero else "Residential Strata",
                "masked_aadhaar": f"XXXX-XXXX-{random.randint(1000, 9999)}",
                "carpet_area_sqft": unit_sqft,
                "user_claim_verified": (not is_unauthorized and audit_state != "ORANGE"),
                "legal_status": "ILLEGAL_UNAUTHORIZED" if is_unauthorized else "VALID_TITLE",
                "tax_clearance": "DEFAULT" if audit_state in ["RED", "ORANGE"] else "PAID"
            }

with open(user_claims_file, "w", encoding="utf-8") as f:
    json.dump(user_verified_db, f, indent=2)

with open(govt_db_file, "w", encoding="utf-8") as f:
    json.dump(govt_property_db, f, indent=2)

with open(resident_file, "w", encoding="utf-8") as f:
    json.dump(resident_db, f, indent=2)

print(f"[OK] Dataset 1 (User Claims): {len(user_verified_db)} records written to '{user_claims_file}'")
print(f"[OK] Dataset 2 (Govt DB): {len(govt_property_db)} records written to '{govt_db_file}'")
print(f"[OK] Strata Registry: {len(resident_db)} 3D ULPIN records written to '{resident_file}'")