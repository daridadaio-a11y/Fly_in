import sys

from read_map import parser

if __name__ == "__main__":
    try:
        file_path = sys.argv[1]
        map_data = parser(file_path)
    except IndexError:
        print("Please write mapfile")
    except Exception as e:
        print(e)