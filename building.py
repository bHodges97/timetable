import collections
import geopy.distance
import re

class Building:
    def __init__(self, name, lattitude, longitude):
        self.name = name
        self.coords = (lattitude,longitude)

    def add_room(self, room, capacity):
        self.room = room
        self.capacity = capacity

    def distance_to(self, building):
        return geopy.distance.distance(self.coords,building.coords).m

class Room:
    def __init__(self, name, building,capacity):
        self.name = name
        self.building = building
        self.capacity = capacity
        self.equipment = collections.defaultdict(int)

    def load_equipment(self, equip_list):
        equipments = equip_list.split(';')
        for equipment in equipments:
            count,name = equipment.replace(' ','').split('x',2)
            self.equipment[name] = count

class Rooms(collections.MutableMapping):
    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        return self.store[self._keytransform(key)]

    def __setitem__(self, key, value):
        self.store[self._keytransform(key)] = value

    def __delitem__(self, key):
        del self.store[self._keytransform(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def _keytransform(self, key):
        key = key.lower()
        key = key.replace('harry','h')
        key = key.replace('nursten','n')
        key = key.replace('foxh','fh')
        key = key.replace('jjthom','jjt')
        key = key.replace('hopk','hp')
        key = key.replace('wkh','wh')
        key = key.replace('pc','')
        key = key.replace('em','')
        key = key.replace('-','')
        key = key.replace(' ','')
        while 'l0' in key:
            key = key.replace('l0','l')
        #print(key)
        return key


