import csv
import json

fileName = 'fertiliser/Belmont Farm May 18 Muddy boots summary excel (1).csv'

f = open(fileName, 'r') #, encoding='utf-8-sig')
reader = csv.reader(f)

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

def rowEmpty(row):
    for d in row:
        if d:
            return False
    return True

rowCount = 0
for row in reader:

    # skip empty rows
    if rowEmpty(row):
        continue
    # skip header row
    if row[0] == 'Planned':
        continue
    # finish
    if row[0] == '©Muddy Boots Software Ltd 2018':
        break

    # get farm name
    if farm is None:
        if not row[0]: # empty string
            continue
        farm = Farm(row[0])
        continue

    # get field data
    if fieldName is None:
        fieldData = row[0].split(', ')

        fieldName = fieldData[0]

        cropName = fieldData[1]
        for c in fieldData[2:-1]:
            cropName = cropName + ' ' + c
        
        cropArea = fieldData[-1].split(' ')[0]
        
        cropDate = fieldData[-1].split(' ')[2:][0][1:]
        # harvest date is unused
        cropHarvestDate = fieldData[-1].split(' ')[2:][3][:-1]

        farm.addField(fieldName, fieldArea)
        farm.addCrop(fieldName, cropName, cropDate, cropArea)
        continue

    # end fertiliser data, re-get field data
    if row[3] == 'Total nutrients:':
        continue
    if row[3] == 'Available nutrients:':
        fieldName = None
        continue
        
    # get fert data
    # ['Planned', 'No', 'Product', 'Reason / Analysis', '', 'Area (ha)', 'Plan Rate', 'Actual Rate', 'Total', 'Applied', '', '']
    if not row[0] and not row[1]:
        fertDate = row[11]
        fertName = row[4]
        fertArea = row[6]
        farm.addFert(fieldName, cropName, fertName, fertDate, fertArea)
        continue
    

    # add data to thing
    # farm.addField(Field(fieldName, ''))
    # farm.addCrop(fieldName, Crop(cropName, cropArea))
    # farm.addFert(fieldName, cropName, Fertilising(fertName, fertDate, fertArea))
    
    # prin the unconsumed input
    print('DEBUG', row)
    rowCount += 1
    if rowCount > 20:
        break

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
with open("data_file2.json", "w") as write_file:
    json.dump(serialFarm, write_file, indent=4)
