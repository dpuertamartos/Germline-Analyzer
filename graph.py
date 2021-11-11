import pandas as pd
import os
import matplotlib.pyplot as plt

# 1: Full germline image , make the line in imageJ
# Manual
# 2: imageJ plot profile
# Manual width 50 segmented line from mid of first distal cell to mid of first unique cell of proximal gonad
# Generate .csv files (1 per germline)

def getlist(file):
    #function that standarize intensity
    def stand_intensity(dataframe):
        dataframe.Gray_Value = dataframe.Gray_Value * 100 / dataframe.Gray_Value.max()

    #function that standarize lenght
    def stand_length(dataframe):
        dataframe["Distance_(pixels)"] = dataframe["Distance_(pixels)"] * 100 / dataframe["Distance_(pixels)"].max()


    df = pd.read_csv(file)
    stand_intensity(df)
    stand_length(df)

    #Create the points to take list. Points selected are the ones closer to the 2% step change. For example 1.98% if next one is 2.01%.
    #From these points we will take the previous ~2% pixels and make an average
    points_to_take = []

    for i, percentage in enumerate(df["Distance_(pixels)"].tolist()):
        if i+1 == len(df["Distance_(pixels)"].tolist()):
            points_to_take[-1]=i
        elif int(df["Distance_(pixels)"].tolist()[i+1]) > int(df["Distance_(pixels)"].tolist()[i]) and int(df["Distance_(pixels)"].tolist()[i]) % 2 != 0:
            points_to_take.append(i)

    #divide the number of pixels between 50
    window50 = int(len(df.Gray_Value)/50)
    #create the rolling average taking the previous 2% of pixels
    roll_df = df.rolling(window=window50).mean()
    #take the dataframe Gray Value and convert it to a list
    roll_df_list = roll_df["Gray_Value"].tolist()
    #Create a 50 values list (gray value average each 2% of the germline)
    #For this it takes the rolling average value each (window50) pixels
    point_list_50 = [round(value,2) for x, value in enumerate(roll_df_list) if x in points_to_take]
    return point_list_50


# entries = os.listdir('Values/')
# print(entries)
#
# d={}
# for file in entries:
#     d[file] = getlist(f'Values/{file}')
#
# print(d)
#
# df = pd.DataFrame(d)
# df["average"] = round(df.mean(axis=1),2)
# df["stddev"] = round(df.std(axis=1),2)
# print(df)
# plt.errorbar(df.index*2, df.average, df.stddev, linestyle=':', marker='^', capsize=3, elinewidth=0.7)
# plt.title("MES-4::GFP", fontsize=12)
# plt.gca().set_xlabel('Gonad length', fontsize=10)
# plt.gca().set_ylabel('Fluorescence intensity', fontsize=10)
# plt.show()

# TODO 8: make it a webapp with flask
