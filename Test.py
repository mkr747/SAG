from sklearn.neighbors import KNeighborsClassifier
import pandas as pd

class DataProvider:
    def __init__(self):
        self.norm = dict()
        self.scaled_data_with_labels = None
        self.scaled_data = None
        self.data = None
        self.labels = None

    def get_data(self, filepath):
        try:
            raw_data = pd.read_csv(filepath, sep=",")
            self.labels = raw_data[raw_data.columns[-1]]
            self.data = raw_data.iloc[:, :-1]
            self.scaled_data = self.normalize_data(self.data)
            self.scaled_data_with_labels = self.scaled_data.copy()
            self.scaled_data_with_labels['quality'] = self.labels
        except IOError as e:
            print(f'Cannot open file. {e}')
    
    def get_test_data(self, filepath):
            try:
                raw_data = pd.read_csv(filepath, sep=",")
                labels = raw_data[raw_data.columns[-1]]
                data = raw_data.iloc[:, :-1]
                self.test_scaled_data = self.normalize_data(data)
                self.test_scaled_data_with_labels = self.test_scaled_data.copy()
                self.test_scaled_data_with_labels['quality'] = labels
            except IOError as e:
                print(f'Cannot open file. {e}')

    def normalize_data(self, data):
        print(data)
        for columnName, columnData in data.iteritems():
            if len(self.norm) is not len(self.data.columns):
                self.norm[columnName] = max(columnData)
            data[columnName] = data[columnName] / self.norm[columnName]
        return data


data = DataProvider()
data.get_data(".\\data\\winequality-white.csv")
data.get_test_data(".\\data\\winequality-white-test.csv")
model = KNeighborsClassifier(n_neighbors=3) # Train the model using the training sets
model.fit(data.scaled_data, data.labels) #Predict Output
predicted= model.predict(data.test_scaled_data) # 0:Overcast, 2:Mild 
counter = 0
print(predicted)
for i in range(len(predicted)):
    print(i)
    if predicted[i] == data.test_scaled_data_with_labels['quality'][i]:
        counter += 1
print(predicted)
print(data.test_scaled_data_with_labels['quality'])
print(f'Correctness: {counter / len(predicted) * 100} %')