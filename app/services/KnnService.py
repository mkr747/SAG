import math
from collections import Counter

class KnnService:
    def __intit__(self):
        self.data = []

    def addData(self, query):
        self.data.append(query)

    def clean(self):
        self.data = []

    def CalculateCenter(self):
        center = []
        rowNumber = 0
        for row in self.data:
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
            center[elementNumber] = center[elementNumber] / len(self.data)
            elementNumber = elementNumber + 1

        return center

    def GetEuclidesMeasure(self, data1, data2):
        data1Rows = len(data1)
        data2Rows = len(data2)

        if data1Rows != data2Rows:
            return 'Vectors must have the same length!'

        rowNumber = 0
        euclidesMeasure = 0
        for _ in data1:
            euclidesMeasure = euclidesMeasure + pow(data1[rowNumber] - data2[rowNumber],2)
            rowNumber = rowNumber + 1
        euclidesMeasure = math.sqrt(euclidesMeasure)

        return euclidesMeasure

    def Knn(self, query):

        rowNumber = 0
        euclidesMeasures = []
        for row in self.data:
            euclidesMeasures.append(self.GetEuclidesMeasure(row[:-1], query))
            rowNumber = rowNumber + 1
        print (euclidesMeasures)

        indexes = []
        classes = []
        # liczba sasiadow
        k= len(euclidesMeasures) - 1
        for _ in range(0, k+1):
            indexOfMinValue = euclidesMeasures.index(min(euclidesMeasures))
            indexes.append(indexOfMinValue)
            euclidesMeasures[indexOfMinValue] = max(euclidesMeasures) +1
            classes.append(self.data[indexOfMinValue][len(self.data[0])-1])

        print (indexes)
        print (classes)

        most_common,num_most_common = Counter(classes).most_common(1)[0]
        print(most_common, num_most_common)

        return [most_common, num_most_common]