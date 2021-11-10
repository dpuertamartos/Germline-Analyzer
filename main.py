import pandas as pd

# TODO 1: Full germline image , make the line in imageJ
# Manual
# TODO 2: imageJ plot profile
# Manual width 50 segmented line from mid of first distal cell to mid of first unique cell of proximal gonad
# Generate .csv files (1 per germline)
# TODO 3: standarize to 100% intensity
df = pd.read_csv("Values1.csv")

def stand_intensity(dataframe):
    dataframe.Gray_Value = dataframe.Gray_Value * 100 / dataframe.Gray_Value.max()


stand_intensity(df)

# TODO 4: standarize to 100% lenght

def stand_length(dataframe):
    dataframe["Distance_(pixels)"] = dataframe["Distance_(pixels)"] * 100 / dataframe["Distance_(pixels)"].max()

stand_length(df)

# TODO 5: make the rolling average 2%
#divide the number of points to take 50 points
window50 = int(len(df.Gray_Value)/50)

#create the rolling average taking the previous 2% of pixels
roll_df = df.rolling(window=window50).mean()
#take the dataframe Gray Value and convert it to a list
roll_df_list = roll_df["Gray_Value"].tolist()

#Create a 50 values list (gray value average each 2% of the germline)
#For this it takes the rolling average value each (window50) pixels

point_list_50 = [value for x, value in enumerate(roll_df_list) if (x+1) % 30 == 0]


# TODO 6: be able to aggregate multiple germlines

# TODO 7: show graph and descriptive statistics

# TODO 8: make it a webapp with flask
