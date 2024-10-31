from search_algorithms import _utils
from search_algorithms import BFS


def main():
    listMap = _utils.listMaps()
    print(listMap)
    map_number = input("Enter the map number you want to use: ")
    map_filename = "Map" + map_number + ".txt"
    BFS.execute(map_filename)

if __name__ == '__main__':
    main()
