import pandas as pd
import numpy as np

class GetList(object):
    def __init__(self, standarized= True, fold_increase=False, absolute_intensity=False, number_of_points=50, percentage_for_fold_increase=[0, 0.04]):
        self.standarized = standarized
        self.fold_increase = fold_increase
        self.absolute_intensity = absolute_intensity
        self.file = ""
        self.number_of_points = number_of_points
        self.point_list = []
        self.percentage_for_fold_increase = percentage_for_fold_increase

    def setFile(self, file):
        self.file = pd.read_csv(file)

    def standarizeFile(self):
        self.standarized = True
        print("max",self.file.Gray_Value.max())
        self.file.Gray_Value = self.file.Gray_Value * 100 / self.file.Gray_Value.max()
        print(self.file)

    def fold_increase_standarize(self, points):
        start = int(self.percentage_for_fold_increase[0] * self.number_of_points)
        end = int(self.percentage_for_fold_increase[1] * self.number_of_points)
        print(start, end)
        minimum_average = 0
        p = 0
        for i in range(start, end):
            p += 1
            minimum_average += points[i]
        minimum_average = minimum_average / p
        newlist = [point/minimum_average for point in points]
        print(minimum_average, len(newlist), newlist)
        return newlist

    def set_fold_increase_comparer(self, percentage=[0, 0.04]):
        self.percentage_for_fold_increase = percentage


    def standarizeLength(self):
        self.file["Distance_(pixels)"] = self.file["Distance_(pixels)"] * 100 / self.file["Distance_(pixels)"].max()


    def createListOfPoints(self):
        print(self.file)
        points_to_take = np.linspace(0, len(self.file)-1, self.number_of_points+1)
        points_to_take = [int(x) for x in points_to_take]
        points_to_take.remove(0)
        # divide the number of pixels between number of points
        window = int(len(self.file.Gray_Value) / self.number_of_points)
        # create the rolling average taking the previous (100 / self.number_of_points)% of pixels
        roll_df = self.file.rolling(window=window).mean()
        # take the dataframe Gray Value and convert it to a list
        roll_df_list = roll_df["Gray_Value"].tolist()
        # Create a (number_of_points) values list (gray value average each (100 / self.number_of_points)% of the germline)
        # For this it takes the rolling average value each (window) pixels
        point_list = [round(roll_df_list[i], 2) for i in points_to_take]
        self.point_list = point_list
        if self.fold_increase:
            if self.standarized or self.absolute_intensity:
                print("standarized or absolute_intensity are already done")
            else:
                self.point_list = self.fold_increase_standarize(self.point_list)

    def returnList(self):
        print(self.point_list)
        return self.point_list




getlister = GetList(number_of_points=50)
getlister.setFile("../Values/Values1.csv")
getlister.standarizeFile()
getlister.createListOfPoints()
getlister.returnList()

#get absolute
getlister2 = GetList(number_of_points=50)
getlister2.setFile("../Values/Values1.csv")
getlister2.createListOfPoints()
getlister2.returnList()

#get fold_increase
getlister3 = GetList(standarized=False, fold_increase=True, number_of_points=100, percentage_for_fold_increase=[0, 0.015])
getlister3.setFile("../Values/Values1.csv")
getlister3.createListOfPoints()
getlister3.returnList()

