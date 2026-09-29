import math
from shapely.geometry import Polygon, MultiPolygon, mapping
from shapely.affinity import rotate

class FloorplanPartitionModel:
    """
    Architectural Strata Partition Model (ISO 19152 compliant).
    Dynamically scales strata unit partitions based on physical plinth area (m²)
    and principal structural facade orientation (OBB).
    """
    # Metric conversion factors at Kolkata latitude (~22.57° N)
    LAT_METERS = 111320.0
    LON_METERS = 111320.0 * math.cos(math.radians(22.57))  # ~102,790 m

    def __init__(self, target_unit_sqm=160.0):
        self.target_unit_sqm = target_unit_sqm

    def calculate_plinth_sqm(self, geom):
        """Converts geographic degrees area to metric square meters."""
        return geom.area * self.LAT_METERS * self.LON_METERS

    def determine_unit_count(self, geom):
        """Calculates realistic strata unit count based on footprint area."""
        area_sqm = self.calculate_plinth_sqm(geom)
        if area_sqm < 180.0:
            return 1   # Single holding / detached plinth
        elif area_sqm < 420.0:
            return 2   # 2 units per floor
        elif area_sqm < 850.0:
            return 3   # 3 units per floor
        elif area_sqm < 1500.0:
            return 4   # 4 units per floor
        elif area_sqm < 2400.0:
            return 5   # 5 units per floor
        else:
            return 6   # 6 commercial suites per floor

    def partition(self, geom, num_units=None):
        if num_units is None:
            num_units = self.determine_unit_count(geom)

        # Single holding: return full plinth
        if num_units <= 1 or geom.area < 1e-10:
            return [mapping(geom)]

        # 1. Compute Oriented Bounding Box (OBB)
        obb = geom.minimum_rotated_rectangle
        coords = list(obb.exterior.coords)[:-1]
        if len(coords) < 4:
            return [mapping(geom)]

        # 2. Extract principal structural facade alignment angle
        longest_len = -1.0
        best_angle = 0.0
        for i in range(len(coords)):
            p1 = coords[i]
            p2 = coords[(i + 1) % len(coords)]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dist = math.hypot(dx, dy)
            if dist > longest_len:
                longest_len = dist
                best_angle = math.atan2(dy, dx)

        centroid = geom.centroid
        angle_deg = math.degrees(best_angle)

        # 3. Rotate building into local orthogonal coordinate space
        rotated_geom = rotate(geom, -angle_deg, origin=centroid)
        minx, miny, maxx, maxy = rotated_geom.bounds
        width = maxx - minx
        height = maxy - miny

        units = []
        if width >= height:
            step = width / float(num_units)
            for i in range(num_units):
                u_minx = minx + i * step
                u_maxx = minx + (i + 1) * step
                cutter = Polygon([
                    [u_minx, miny - 0.0001],
                    [u_maxx, miny - 0.0001],
                    [u_maxx, maxy + 0.0001],
                    [u_minx, maxy + 0.0001],
                    [u_minx, miny - 0.0001]
                ])
                sub = rotated_geom.intersection(cutter)
                if not sub.is_empty and sub.area > (rotated_geom.area * (0.35 / num_units)):
                    if sub.geom_type == "MultiPolygon":
                        sub = max(sub.geoms, key=lambda g: g.area)
                    restored = rotate(sub, angle_deg, origin=centroid)
                    units.append(mapping(restored))
        else:
            step = height / float(num_units)
            for i in range(num_units):
                u_miny = miny + i * step
                u_maxy = miny + (i + 1) * step
                cutter = Polygon([
                    [minx - 0.0001, u_miny],
                    [maxx + 0.0001, u_miny],
                    [maxx + 0.0001, u_maxy],
                    [minx - 0.0001, u_maxy],
                    [minx - 0.0001, u_miny]
                ])
                sub = rotated_geom.intersection(cutter)
                if not sub.is_empty and sub.area > (rotated_geom.area * (0.35 / num_units)):
                    if sub.geom_type == "MultiPolygon":
                        sub = max(sub.geoms, key=lambda g: g.area)
                    restored = rotate(sub, angle_deg, origin=centroid)
                    units.append(mapping(restored))

        return units if len(units) > 0 else [mapping(geom)]