import math 
from collections import Counter

data = [[7.4,0.7,0,1.9,0.076,11,34,0.9978,3.51,0.56,9.4,5],
        [7.8,0.88,0,2.6,0.098,25,67,0.9968,3.2,0.68,9.8,5],
        [7.8,0.76,0.04,2.3,0.092,15,54,0.997,3.26,0.65,9.8,5],
        [11.2,0.28,0.56,1.9,0.075,17,60,0.998,3.16,0.58,9.8,6],
        [7.4,0.7,0,1.9,0.076,11,34,0.9978,3.51,0.56,9.4,5],
        [7.4,0.66,0,1.8,0.075,13,40,0.9978,3.51,0.56,9.4,5],
        [7.9,0.6,0.06,1.6,0.069,15,59,0.9964,3.3,0.46,9.4,5],
        [7.3,0.65,0,1.2,0.065,15,21,0.9946,3.39,0.47,10,7],
        [7.8,0.58,0.02,2,0.073,9,18,0.9968,3.36,0.57,9.5,7],
        [7.5,0.5,0.36,6.1,0.071,17,102,0.9978,3.35,0.8,10.5,5]]

def CalculateCenter(data):
    center = []
    rowNumber = 0
    for row in data:        
        columnNumber = 0
        for element in row:   
            if rowNumber>0:                  
                center[columnNumber] = center[columnNumber] + element
            else :
                center.append(element)
            columnNumber = columnNumber + 1
        rowNumber = rowNumber + 1

    elementNumber = 0
    for element in center:
        center[elementNumber] = center[elementNumber] / len(data)
        elementNumber = elementNumber + 1

    return center

def GetEuclidesMeasure(data1, data2):
    data1Rows = len(data1)
    data2Rows = len(data2)

    if data1Rows != data2Rows:
        return 'Vectors must have the same length!'
    
    rowNumber = 0
    euclidesMeasure = 0
    for row in data1:
        euclidesMeasure = euclidesMeasure + pow(data1[rowNumber] - data2[rowNumber],2)
        rowNumber = rowNumber + 1
    euclidesMeasure = math.sqrt(euclidesMeasure)

    return euclidesMeasure

def Knn(data, query):
    
    rowNumber = 0
    euclidesMeasures = []
    for row in data:
        euclidesMeasures.append(GetEuclidesMeasure(row[:-1], query))
        rowNumber = rowNumber + 1
    print (euclidesMeasures)
    
    indexes = []
    classes = []
    # liczba sasiadow
    k= len(euclidesMeasures) - 1
    for x in range(0, k+1):
        indexOfMinValue = euclidesMeasures.index(min(euclidesMeasures))
        indexes.append(indexOfMinValue)
        euclidesMeasures[indexOfMinValue] = max(euclidesMeasures) +1
        classes.append(data[indexOfMinValue][len(data[0])-1])
        
    print (indexes)
    print (classes)

    most_common,num_most_common = Counter(classes).most_common(1)[0]

    print(most_common, num_most_common)


a = CalculateCenter(data)

query = [7.9,0.32,0.51,1.8,0.341,17,56,0.9969,3.04,1.08,9.2]
print (min(query))
print(query.index(min(query)))


Knn(data, query)


