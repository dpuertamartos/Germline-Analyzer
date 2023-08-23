import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename

def read_mitotic_file_into_average(file):
    df = pd.read_csv(file, header=None)
    a = df[0].to_numpy()
    average = str(round(sum(a)/len(a),2))
    dev_standard = str(round(df[0].std(), 2))
    return [average,dev_standard]

def files_to_dictionary(files):
    d = {}
    for file in files:
        filename = secure_filename(file.filename)
        df = pd.read_csv(file)
        d[filename] = df
    return d

def extract_length(list_of_dictionaries):
    final_length_list = []
    for d1 in list_of_dictionaries:
        intermedium_length_list = []
        for key in d1.keys():
            df = d1[key]
            intermedium_length_list.append([df.iloc[-1, 0], df.columns.values.tolist()[0]])
        final_length_list.append(intermedium_length_list)
    return final_length_list

def extract_min_length(list_of_length_lists):
    m = None
    for strain in list_of_length_lists:
        for gonad in strain:
            if m is None or gonad[0] < m:
                m = gonad[0]
    return m

def calculate_average_length(l_list_list, s_name_list):
    average_list = []
    for i , strain in enumerate(l_list_list):
        strain_average = []
        units = set()
        for length in strain:
            strain_average.append(length[0])
            units.add(length[1])
        if len(units) == 1:
            units = list(units)
            average_list.append([s_name_list[i], round(sum(strain_average)/len(strain), 1),
                                 "+-"+str(round(pd.Series(strain_average).std(), 1)), units[0]])
        else:
            average_list.append([None,"Different units in files"])
    return average_list

def determine_same_length_units(l_list_list):
    units = set()
    for strain in l_list_list:
        for length in strain:
            units.add(length[1])
    return [len(units) == 1, list(units)[0]]

class GetList(object):
    def __init__(self, standarized=False, fold_increased=False, number_of_points=50,
                 percentage_for_fold_increase=[0, 0.04], absolute_length=None):
        self.standarized = standarized
        self.fold_increased = fold_increased
        self.file = ""
        self.number_of_points = number_of_points
        self.point_list = []
        self.percentage_for_fold_increase = percentage_for_fold_increase
        self.absolute_length = absolute_length

    def setFile(self, file):
        self.file = file
        self.max_length = file.iloc[-1, 0]
        self.length_type = file.columns.values.tolist()[0]

    def return_length(self):
        return [self.max_length, self.length_type]

    def plot(self):
        plt.plot(self.point_list)
        plt.show()

    def standarizeFile(self):
        if self.fold_increased:
            raise Exception("already fold increased")
        else:
            self.standarized = True
            m = max(self.point_list)
            self.point_list = [round(point * 100 / m, 2) for point in self.point_list]
            return self.point_list

    def fold_increase_standarize(self):
        if self.standarized == True:
            raise Exception("already standarized")
        else:
            self.fold_increased = True
            points = self.point_list
            print(self.percentage_for_fold_increase, self.number_of_points)
            start = int(self.percentage_for_fold_increase[0] * self.number_of_points)
            end = int(self.percentage_for_fold_increase[1] * self.number_of_points)
            minimum_average = 0
            p = 0
            for i in range(start, end):
                p += 1
                minimum_average += points[i]
            minimum_average = minimum_average / p
            newlist = [point/minimum_average for point in points]
            self.point_list = newlist
            return newlist

    def set_fold_increase_comparer(self, percentage=[0, 0.04]):
        self.percentage_for_fold_increase = percentage


    def standarizeLength(self):
        self.file["Distance_(pixels)"] = self.file["Distance_(pixels)"] * 100 / self.file["Distance_(pixels)"].max()


    def createListOfPoints(self):
        if self.absolute_length is not None:
            n = int(self.absolute_length / (self.file.iloc[1, 0] - self.file.iloc[0, 0]))
            self.file = self.file.iloc[:n+1]
        points_to_take = np.linspace(0, len(self.file) - 1, self.number_of_points+1)
        points_to_take = [int(x) for x in points_to_take]
        points_to_take.remove(0)
        # divide the number of pixels between number of points

        window = int(len(self.file.iloc[:, 1]) / self.number_of_points+1)
        # create the rolling average taking the previous (100 / self.number_of_points)% of pixels
        roll_df = self.file.rolling(window=window).mean()
        # take the dataframe Gray Value and convert it to a list
        roll_df_list = roll_df.iloc[:,1].tolist()
        # Create a (number_of_points) values list (gray value average each (100 / self.number_of_points)% of the germline)
        # For this it takes the rolling average value each (window) pixels
        point_list = [round(roll_df_list[i], 2) for i in points_to_take]
        self.point_list = point_list

    def returnList(self):
        return self.point_list


class GermlineAnalyzer(object):
    def __init__(self, dictio, standarized=False, fold_increased=False, number_of_points=50,
                 percentage_for_fold_increase=[0, 0.04], absolute_length=None):
        self.dictio = dictio
        self.getlister = GetList(standarized=standarized,
                                 fold_increased=fold_increased, absolute_length=absolute_length,
                                 number_of_points=number_of_points,percentage_for_fold_increase=percentage_for_fold_increase)
        self.df = None
        self.filenames = None
        self.max_length = None
        self.length_type = None

    def convertDictionaryToDf(self, d):
        df = pd.DataFrame(d)
        df["average"] = round(df.mean(axis=1), 2)
        df["stddev"] = round(df.std(axis=1), 2)
        return df

    def return_filenames(self):
        return self.filenames

    def return_max_length(self):
        if self.df is not None:
            return [self.max_length, self.length_type]
        else:
            print("df not processed yet")

    def process(self):
        d = {}
        filenames = []
        for key in self.dictio.keys():
            self.getlister.setFile(self.dictio[key])
            self.max_length, self.length_type = self.getlister.return_length()
            self.getlister.createListOfPoints()
            if self.getlister.standarized:
                self.getlister.standarizeFile()
            elif self.getlister.fold_increased:
                self.getlister.fold_increase_standarize()
            d[key] = self.getlister.returnList()
            filenames.append(key)

        self.df = self.convertDictionaryToDf(d)
        self.filenames = filenames
        return self.df





