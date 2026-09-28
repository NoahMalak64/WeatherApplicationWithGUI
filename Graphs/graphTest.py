import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def main():
    # Load JSON file
    with open("cleanData.json", "r") as f:
        data = json.load(f)
    
    # creating empty df with those columns, can change as needed
    df = pd.DataFrame(columns=["date", "snowfall_cm", "city"])

    # iterate through each of the dates in cleanData.json
    for date in data:
        # print(data[date])
        # add to the end of the dataframe a row containing [the date, the snowfall of the date, the location/city of the date]
        # as you add more locations to the date, iterate through instead of [0]
        df.loc[len(df)] = [date, data[date][0]["snow"], data[date][0]["location"]]

    # df = pd.json_normalize(data)  
    
    print(df)
    # return

    # Set Seaborn theme
    sns.set_theme(style="whitegrid")

    # Create relational line plot
    sns.relplot(
        data=df,
        x="date",
        y="snowfall_cm",
        hue="city",
        kind="line",
        marker="o"
    )

    plt.title("Average Monthly Snowfall by City")
    plt.show()

if __name__ == '__main__':
    main()