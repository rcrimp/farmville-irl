import csv
import json

fileName = 'fertiliser/2020 AJ C EE FF GR K KK NW S U.csv'

f = open(fileName, 'r', encoding='utf-8-sig')
reader = csv.DictReader(f)

## perm data
class Fert:
    def __init__(self, name, date, area):
        self.name = name
        self.date = date # date crop planted
        self.area = area

class Crop:
    def __init__(self, name, date, area):
        self.name = name
        self.date = date
        self.area = area
        self.ferts = []

class Field:
    def __init__(self, name, area):
        self.name = name
        self.area = area
        if self.area is None:
            self.area = 0
        self.crops = []

class Farm:
    def __init__(self, name):
        self.name = name
        self.fields = []

    def addField(self, fieldName, fieldArea):
        # check if field entry already exists
        for f in self.fields:
            if f.name == fieldName:
                return
        self.fields.append(Field(fieldName, fieldArea))

    def addCrop(self, fieldName, cropName, cropDate, cropArea):
        for f in self.fields:
            if f.name == fieldName:
                # check if crop entry already exists
                for c in f.crops:
                    if c.name == cropName:
                        return
                f.crops.append(Crop(cropName, cropDate, cropArea))

    def addFert(self, fieldName, cropName, fertName, fertDate, fertArea):
        for f in self.fields:
            if f.name == fieldName:
                for c in f.crops:
                    if c.name == cropName:
                        c.ferts.append(Fert(fertName, fertDate, fertArea.strip()))

    def print(self):
        print(self.name)
        for f in self.fields:
            print(' Field: ', f.name, f.area, 'ha')
            for c in f.crops:
                print('   Crop: ', c.name, c.date, c.area, 'ha')
                for a in c.ferts:
                    print('     Fert: ', a.name, a.date, a.area, 'ha')
            
## extracted data preserved between row reads
farm = None
fieldName = None
fieldArea = None # always none
cropName = None
cropDate = None
cropHarvestDate = None # unused
cropArea = None
fertDate = None
fertName = None
fertArea = None

farm = Farm('farm-name')
for row in reader:

    # extract relevant data from row
    fieldName = row['Field Name']
    cropName = row['Crop']
    cropArea = row['Crop Area'].split(' ')[0]
    fertDate = row['Activity Date']
    fertName = row['Product']
    fertArea = row['Treated Area'].split(' ')[0]

    # add data to thing
    farm.addField(fieldName, fieldArea)
    farm.addCrop(fieldName, cropName, cropDate, cropArea)
    farm.addFert(fieldName, cropName, fertName, fertDate, fertArea)

# print it out ?
# farm.print()

# serialise farm data
serialFarm = {"FarmName" : farm.name, "Fields" : []}
for f in farm.fields:
    serialField = {"Name": f.name, "Area": f.area, "Crops": []}
    for c in f.crops:
        serialCrop = {"Name": c.name, "Area": c.area, "Date": c.date, "Ferts": []}
        for a in c.ferts:
            serialFert = {"Name": a.name, "Area": a.area, "Date": a.date}
            serialCrop['Ferts'].append(serialFert)
        serialField['Crops'].append(serialCrop)
    serialFarm['Fields'].append(serialField)

# output as JSON
with open("data_file.json", "w") as write_file:
    json.dump(serialFarm, write_file, indent=4)
