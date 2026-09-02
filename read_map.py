from models import Connection, Zone


def parser() -> dict:   
    with open("test_parser.txt", "r") as file:
        map_binder = {}

        road_list = []
        total_drones = 0
        for line in file:
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
            metadata_dict = {}
            if second:
                meta_parts = second.split()
                for item in meta_parts:
                    key, value = item.split("=")
                    metadata_dict[key] = value
            if prefix == "nb_drones:":
                total_drones = int(parts[1])
            elif prefix in ("hub:", "start_hub:", "end_hub:"):
                coordinates_x = int(parts[2])
                coordinates_y = int(parts[3])
                my_room = Zone(name=parts[1], role=parts[0],
                            metadata=metadata_dict, x=coordinates_x,
                            y=coordinates_y)
                map_binder[parts[1]] = my_room
            elif prefix == "connection:":
                z1, z2 = parts[1].split("-")
                road = Connection(zone1=z1, zone2=z2, metadata=metadata_dict)
                road_list.append(road)
        return road_list
            """print("部屋を見つけた！")
                print(f"名前： {name}")
                print(f"座標： X={coordinates_x}, Y={coordinates_y}")"""