from models import Connection, Zone, MapData
from errors import MapParseError

def paser(file_path) -> MapData:
    with open(file_path, "r") as file:
        map_binder = {}
        road_list = {}
        drones = 0
        line_num = 0
        for line in file:
            line_num += 1
            clean_line = line.strip()
            if not clean_line or clean_line.startswith("#"):
                continue
            if "[" in clean_line and "]" in clean_line:
                first, second = clean_line.split("[")
                second = second.strip("]")
            else:
                first = clean_line
                second = ""
            parts = first.split()
            if not parts:
                continue
            prefix = parts[0]
            if prefix == "nb_drones:":
                drones = int(parts[1])
            elif prefix in ("hub:", "start_hub:", "end_hub:"):
                coordinates_x = int(parts[2])
                coordinates_y = int(parts[3])
                metadata_dict = {
                    "zone": "normal",
                    "color": "none",
                    "max_drones": 1,
                }
                if second:
                    meta_parts = second.split()
                    for item in meta_parts:
                        key, value = item.split("=")
                        if key in metadata_dict:
                            metadata_dict[key] = value
                my_room = Zone(name=parts[1], role=parts[0], metadata=metadata_dict,
                               x=coordinates_x, y=coordinates_y)
                zone_name = parts[1]
                if zone_name in map_binder:
                    raise MapParseError(line_num, f"The zone name'{zone_name}'"
                                        "is a duplicate.")
                map_binder[zone_name] = my_room
            elif prefix == "connection:":
                z1
                metadata_dict = {
                    "max_link_capacity": 1,
                }
                if second:
                    meta_parts = second.split()
            
def parse_line(line_num: int, )

                