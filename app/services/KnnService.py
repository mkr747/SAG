import math
import pandas as pd
from collections import Counter


class KnnService:
    def __init__(self):
        self.data = pd.DataFrame()
        self.center = []

    def add_data(self, row):
        self.data = self.data.append(pd.Series(row), ignore_index=True)
        self.data = self.data[row.keys()]

    def clean(self):
        self.data = pd.DataFrame()

    def calculate_center(self, row):
        if len(self.data) < 2:
            center = []
            row_number = 0
            for index, row_v in self.data.iterrows():
                row_v = row_v.iloc[:-1]
                column_number = 0
                for element in row_v:
                    if row_number > 0:
                        center[column_number] = center[column_number] + element
                    else:
                        center.append(element)
                    column_number = column_number + 1
                row_number = row_number + 1

            element_number = 0
            for _ in center:
                center[element_number] = center[element_number] / len(self.data)
                element_number = element_number + 1

            self.center = center
        else:
            center = self.center
            column_number = 0
            del row['quality']
            for element in row:
                center[column_number] = (center[column_number] * (len(self.data) - 1) + row[element]) / len(self.data)
                column_number = column_number + 1
            self.center = center
        return center

    @staticmethod
    def get_euclidean_measure(data1, data2):
        data1_rows = len(data1)
        data2_rows = len(data2)
        if data1_rows != data2_rows:
            return 'Vectors must have the same length!'

        row_number = 0
        euclidean_measure = 0
        for _ in data1:
            euclidean_measure = euclidean_measure + pow(data1[row_number] - data2[row_number], 2)
            row_number = row_number + 1
        euclidean_measure = math.sqrt(euclidean_measure)

        return euclidean_measure

    def knn(self, query):
        row_number = 0
        euclidean_measures = []
        for index, row in self.data.iterrows():
            row = row.iloc[:-1]
            euclidean_measures.append(self.get_euclidean_measure(row, list(query.values())))
            row_number = row_number + 1
        # TODO
        #  mozna przemyslec wage, odleglosc (przykladu od centrum) powinna miec wplyw
        indexes = []
        classes = []

        # liczba sasiadow
        k = math.floor(len(self.data) * 0.2)
        for _ in range(0, k):
            index_of_min_value = euclidean_measures.index(min(euclidean_measures))
            indexes.append(index_of_min_value)
            euclidean_measures[index_of_min_value] = max(euclidean_measures) + 1
            classes.append(self.data.iloc[index_of_min_value]['quality'])

        most_common, num_most_common = Counter(classes).most_common(1)[0]

        return [most_common, num_most_common / k]
