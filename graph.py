import pandas as pd

def getlist(file):
    #function that standarize intensity
    def stand_intensity(dataframe):
        dataframe.Gray_Value = dataframe.Gray_Value * 100 / dataframe.Gray_Value.max()

    #function that standerize intensity with fold increase from minimum (average first 4% of gonad)

    def fold_increase_standarize(list):
        #if you want 6% take 3 points, 8% take 4...
        minimun_average_of_first_4percent = (list[0]+list[1])/2
        newlist = []
        for i in range(len(list)):
            newlist.append(list[i]/minimun_average_of_first_4percent)
        return newlist


    #function that standarize lenght
    def stand_length(dataframe):
        dataframe["Distance_(pixels)"] = dataframe["Distance_(pixels)"] * 100 / dataframe["Distance_(pixels)"].max()


    df = pd.read_csv(file)
    # Comment this if you dont want standardised intensity
    # stand_intensity(df)
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
    #if you want to use fold increase respect 4% start of gonad(value can be changed in the function), apply
    #fold-increase_standarize to the return and comment stand_intensity function
    # # return fold_increase_standarize(point_list_50)
    return point_list_50

def dataframe_proccess(dictionary):
    df = pd.DataFrame(dictionary)
    df["average"] = round(df.mean(axis=1),2)
    df["stddev"] = round(df.std(axis=1),2)
    return df



