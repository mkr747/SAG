import math
import pandas as pd
from collections import Counter

class KnnService:
    def __init__(self):
        self.data = pd.DataFrame()
        self.center = []

    def addData(self, row):
        self.data = self.data.append(pd.Series(row), ignore_index = True)
        self.data = self.data[row.keys()]

    def clean(self):
        self.data = pd.DataFrame()

    def CalculateCenter(self, row):
        if len(self.data) <2:
            center = []
            rowNumber = 0
            for index, roww in self.data.iterrows():
                roww = roww.iloc[:-1]
                columnNumber = 0
                for element in roww:
                    if rowNumber > 0:
                        center[columnNumber] = center[columnNumber] + element
                    else:
                        center.append(element)
                    columnNumber = columnNumber + 1
                rowNumber = rowNumber + 1

            elementNumber = 0
            for element in center:
                center[elementNumber] = center[elementNumber] / len(self.data)
                elementNumber = elementNumber + 1

            self.center = center
        else:
            center = self.center
            column_number = 0
            del row['quality']
            for element in row:
                center[column_number] = (center[column_number] * (len(self.data)-1) + row[element]) / len(self.data)
                column_number = column_number + 1
            self.center = center
        return center


    @staticmethod
    def GetEuclidesMeasure(data1, data2):
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
        for index, row in self.data.iterrows():
            row = row.iloc[:-1]
            euclidesMeasures.append(self.GetEuclidesMeasure(row, query.values()))
            rowNumber = rowNumber + 1

        indexes = []
        classes = []
        # liczba sasiadow
        k= 5
        for _ in range(0, k+1):
            indexOfMinValue = euclidesMeasures.index(min(euclidesMeasures))
            indexes.append(indexOfMinValue)
            euclidesMeasures[indexOfMinValue] = max(euclidesMeasures) + 1
            classes.append(self.data.iloc[indexOfMinValue]['quality'])

        most_common,num_most_common = Counter(classes).most_common(1)[0]

        return [most_common, num_most_common]