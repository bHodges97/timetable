import os
import csv
import openpyxl as pyxl
import numpy as np
from building import *

def distance_matrix(buildings):
    distances = []
    for x in buildings.values():
        distances.append([x.distance_to(y) for y in buildings.values()])
    distances = np.array(distances)
    #print(distances)
    return distances

def load_buildings(path):
    buildings = dict()
    with open(path,'r') as f:
        reader = csv.reader(f)
        next(reader,None)#skip header
        for name,lattitude,longitude in reader:
            building = Building(name,lattitude,longitude)
            buildings[name] = building
    return buildings

def load_rooms(rooms_path, equip_path buildings):
    rooms = Rooms()
    worksheet = pyxl.load_workbook(path,read_only = True, data_only = True).active
    for room_name,building_name,capacity in worksheet.iter_rows(min_row=2,values_only=True):
        building = buildings[building_name]
        rooms[room_name] = Room(room_name,building,capacity)
    load_equipment(equip_list, rooms)
    return rooms

def load_equipment(path, rooms):
    worksheet = pyxl.load_workbook(path,read_only = True, data_only = True).active
    for room_name,equipment_list in worksheet.iter_rows(min_row=2,max_col=2,values_only=True):
        try:
            rooms[room_name].load_equipment(equipment_list)
        except KeyError:
            print("No capacity listed for:",room_name)



if __name__ == "__main__":
    files = ["Room List.xlsx", "Roomequip.xlsx", "Timetable2018-19.xlsx","buildings.csv"]
    paths = [os.path.join("Data",x) for x in files]

    buildings = load_buildings(paths[3])
    rooms = load_rooms(paths[0], paths[1], buildings)

    timetable = pyxl.load_workbook(paths[2]).active




