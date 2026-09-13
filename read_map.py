from models import Connection, Zone, MapData
from errors import MapParseError


def parser(file_path) -> MapData:   
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
            if "[" in clean_line:
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
                if metadata_dict:
                metadata_dict["zone"] = "normal"
                metadata_dict["color"] = "none"
                metadata_dict["max_drones"] = 1
                my_room = Zone(name=parts[1], role=parts[0],
                               metadata=metadata_dict, x=coordinates_x,
                               y=coordinates_y)
                zone_name = parts[1]
                if zone_name in map_binder:
                    raise MapParseError(line_num, f"The zone name'{zone_name}'"
                                        "is a duplicate.")
                map_binder[zone_name] = my_room
            elif prefix == "connection:":
                z1, z2 = parts[1].split("-")
                connection_key = tuple(sorted((z1, z2)))
                if z1 not in map_binder:
                    raise MapParseError(line_num,
                                        f"Zone '{z1}' is not defined.")
                if z2 not in map_binder:
                    raise MapParseError(line_num,
                                        f"Zone '{z2}' is not defined.")
                if connection_key in road_list:
                    raise MapParseError(line_num,
                                        f"The connection '{z1} - {z2}'"
                                        " is a duplicate.")
                road = Connection(zone1=z1, zone2=z2, metadata=metadata_dict)
                road_list[connection_key] = road
        return MapData(total_drones=drones, zones=map_binder,
                       connections=road_list)