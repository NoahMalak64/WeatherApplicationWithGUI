import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import datetime

def snowfall_grid(data_location):
    with open("../json/cleanData.json", "r") as f:
        data = json.load(f)

    large_data_frame = np.zeros((7,52))

    #Find highest value to normalize snowfall levels 
    highest_snowfall_per_day = 0
    for date, locations in data.items():
        for current_location in locations:
            if current_location["location"].lower() == data_location.lower():
                if current_location["snow"] > highest_snowfall_per_day:
                    highest_snowfall_per_day = current_location["snow"]

    #populate the data object large_data_frame
    for date, locations in data.items():
        for current_location in locations:
            if current_location["location"].lower() == data_location.lower():
                # this_date = datetime.date(current_location["datetime"])
                this_date = datetime.datetime.strptime(current_location["datetime"], "%Y-%m-%d")
                day_number = this_date.timetuple().tm_yday
                column, row = divmod(day_number, 7)
                if (highest_snowfall_per_day != 0):
                    large_data_frame[row][column] = (current_location["snow"]/highest_snowfall_per_day)
                
    custom_cmap = LinearSegmentedColormap.from_list(
        "my_cmap", [(0, 0, 1, 0.1), (0, 0, 1, 1)]
    )

    rows, cols = large_data_frame.shape
    figure, ax = plt.subplots(figsize=(30, 4))
    for i in range(rows):
        for j in range(cols):
            ax.add_patch(plt.Rectangle(
                (j, i), 0.8, 0.8,   # smaller than 1×1 → leaves gap
                facecolor=custom_cmap(large_data_frame[i, j]),
                edgecolor="none"
            ))
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor("none")   # transparent background
    ax.set_aspect("equal")
    figure.patch.set_alpha(0.0)   # transparent figure background

    #Disables black line around outside
    for spine in ax.spines.values():
        spine.set_visible(False)

    figure.savefig("../Graphs/52WeekPlot.png", transparent=True, bbox_inches="tight")


def snowfall_week(data_location):
    with open("../json/cleanData.json", "r") as f:
        data = json.load(f)

    df = pd.DataFrame(columns=["date", "snowfall_cm"])
    
    # loop through all the days properly
    for date, locations in data.items():
        for cur in locations:
            if cur["location"].lower() == data_location.lower():
                df.loc[len(df)] = [date, cur["snow"]]

    # convert to datetime for sorting
    df["date"] = pd.to_datetime(df["date"])

    # sort dates
    df = df.sort_values("date")
    # last 7 days
    week = df.tail(7)
    week["date_str"] = week["date"].dt.strftime('%Y-%m-%d')
    # print(week.to_string())
    # plot
    plt.figure(figsize=(10, 9))
    plot = sns.barplot(data=week, x="date_str", y="snowfall_cm")
    plt.title(f"Snowfall Last 7 Days - {data_location}")
    plt.xlabel("Date")
    plt.ylabel("Snowfall (cm)")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    # plt.show()

    figure = plot.get_figure()
    
    figure.savefig("../Graphs/SnowfallWeekGraph.png")

def temperature_week(data_location):
    with open("../json/cleanData.json", "r") as f:
        data = json.load(f)

    #date, temp type, num
    df = pd.DataFrame(columns=["date", "temp_type", "temp"])

    # loop through all the days properly
    for date, locations in data.items():
        for cur in locations:
            if cur["location"].lower() == data_location.lower():
                df.loc[len(df)] = [date, "Max", cur["tempmax"]]
                df.loc[len(df)] = [date, "Min", cur["tempmin"]]
                df.loc[len(df)] = [date, "Average", cur["average_temp"]]


    # convert to datetime for sorting
    df["date"] = pd.to_datetime(df["date"])

    # sort dates
    df = df.sort_values("date")
    
    # last 7 days
    week = df.tail(21)
    # print(week)
    # plot
    plt.figure(figsize=(10, 9))
    plot = sns.lineplot(data=week, x="date", y="temp", hue="temp_type")
    plt.title(f"Temperature Last 7 Days - {data_location}")
    plt.xlabel("Date")
    plt.ylabel("Temperature (F)")
    plt.xticks(rotation=25)
    plt.tight_layout()
    # plt.show()

    figure = plot.get_figure()

    figure.savefig("../Graphs/TemperatureWeekGraph.png")


#snowfall_week("houghton, MI")
# temperature_week("houghton, MI")
