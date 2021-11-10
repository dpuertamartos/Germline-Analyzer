import pandas as pd
import os

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
    #divide the number of points to take 50 points
    window50 = int(len(df.Gray_Value)/50)
    #create the rolling average taking the previous 2% of pixels
    roll_df = df.rolling(window=window50).mean()
    #take the dataframe Gray Value and convert it to a list
    roll_df_list = roll_df["Gray_Value"].tolist()
    #Create a 50 values list (gray value average each 2% of the germline)
    #For this it takes the rolling average value each (window50) pixels
    point_list_50 = [value for x, value in enumerate(roll_df_list) if (x+1) % window50 == 0]
    print(point_list_50)
    print(len(roll_df_list)/window50)
    print(len(point_list_50))


entries = os.listdir('Values/')
print(entries)

for file in entries:
    getlist(f'Values/{file}')

# TODO 6: be able to aggregate multiple germlines

# TODO 7: show graph and descriptive statistics

# TODO 8: make it a webapp with flask
