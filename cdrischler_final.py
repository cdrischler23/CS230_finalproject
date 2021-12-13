"""
Name: Carly Drischler
CS 230.004
Data: Volcanoes
URL:

Description:
This program provides the user with an interactive experience to help them visualize locations of volcanoes
based on their region, visualize the number of volcanoes in a particular country, their average elevation,
and for some, see how many are above/below sea level. Lastly, the program has a sort of mini-game where they must
guess what is most prevalent and the answer and visual of that data will not appear until they give the correct
response.
"""

import streamlit as st
import matplotlib.pyplot as plt
import csv
import pandas as pd
import numpy as np
import pydeck as pdk


from PIL import Image
image = Image.open('volcano.jpg')

FILENAME = "volcanoes.csv"

# READ IN DATA
def read_data():
    return pd.read_csv(FILENAME).set_index("Volcano Number")

# QUERY ONE
def all_regions():
    df = read_data()
    lst = []
    for ind, row in df.iterrows():
        # Code to remove region of Mexico and Central America as Mexico had an unexpected character
        if row["Region"] not in lst and not row["Region"].endswith("and Central America"):
            lst.append(row["Region"])
    sort_list = sorted(lst, key=str.lower)
    return sort_list

def min_elevation():
    df = read_data()
    min = 0
    for ind, row in df.iterrows():
        if row["Elevation (m)"] < min:
            min = row["Elevation (m)"]
    return min

def max_elevation():
    df = read_data()
    max = 0
    for ind, row in df.iterrows():
        if row["Elevation (m)"] > max:
            max = row["Elevation (m)"]
    return max

def map_data(sel_region, sel_elevation):
    df = read_data()
    df = df.loc[df["Region"] == sel_region]
    df = df.loc[df["Elevation (m)"] > sel_elevation]
    return df

def map(df):
    map_df = df.filter(["Volcano Name", "Latitude", "Longitude"])
    view_state = pdk.ViewState(latitude=map_df["Latitude"].mean(),
                               longitude=map_df["Longitude"].mean(), zoom=2)
    layer = pdk.Layer('ScatterplotLayer',
                      data=map_df,
                      get_position='[Longitude, Latitude]',
                      get_radius=50000,
                      get_color=[200, 10, 55],
                      pickable=True)
    tool_tip = {'html': 'Volcano Name:<br><b>{Volcano Name}</b>',
                'style': {'backgroundColor': 'darkorange', 'color': 'white'}}

    map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                   initial_view_state=view_state,
                   layers=[layer],
                   tooltip=tool_tip)

    st.pydeck_chart(map)


def q1():
    st.markdown(""" <style> .font {font-size:45px ; font-family: 'Courier'; color: #FF9632;} </style> """,
                unsafe_allow_html=True)
    st.markdown('<p class="font">VISUALIZE DATA WITH PYTHON</p>', unsafe_allow_html=True)
    st.sidebar.write("What is your name?")
    name = st.sidebar.text_input("Name: ", "Carly")
    st.write("Welcome", name, "to this Volcano Data!")
    st.image(image)
    st.write(" ")
    st.sidebar.title("Query One")
    st.sidebar.write("For what region and elevation would you like to map?")
    region = st.sidebar.radio("Select a region: ", all_regions())
    elevation = st.sidebar.slider("Min Elevation (in meters): ", min_elevation(), max_elevation())
    st.sidebar.write(" ")

    data = map_data(region, elevation)

    if len(region) > 0:
        st.header(f"Map of volcanoes:")
        st.write("Map of Volcanoes in:", region)
        map(data)


q1()


def pivot1():
    df = read_data()
    check = st.sidebar.checkbox("Would you like more information on regional volcanoes?", False)
    pivot = df.pivot_table(index=['Region'], values=['Elevation (m)'], aggfunc='count')
    st.write(" ")
    if check:
        st.header("Total Number of Volcanoes in Each Region:")
        st.write(pivot)
pivot1()


# QUERY TWO
def all_countries():
    global sort_list
    df = read_data()
    lst = []
    for ind, row in df.iterrows():
        if row["Country"] not in lst:
            lst.append(row["Country"])
    sort_list = sorted(lst, key=str.lower)
    return sort_list


def bar_data(sel_country):
    df = read_data()
    df = df.loc[df["Country"].isin(sel_country)]
    return df

def country_elevation(df):
    elevations = [row["Elevation (m)"] for ind, row in df.iterrows()]
    countries = [row["Country"] for ind, row in df.iterrows()]

    dict = {}
    for country in countries:
        dict[country] = []

    for i in range(len(elevations)):
        dict[countries[i]].append(elevations[i])

    return dict

def country_averages(dict_elevations):
    dict = {}
    for key in dict_elevations.keys():
        dict[key] = np.mean(dict_elevations[key])
    return dict


def bar_chart(dict_averages):
    plt.figure()

    x = dict_averages.keys()
    y = dict_averages.values()
    plt.bar(x, y, color="darkorange")
    plt.xlabel("Country")
    plt.ylabel("Average Elevation (in meters)")
    plt.title("Average Elevation By Country")

    return plt


def s_data(df):
    g = df.groupby('Country')['Elevation (m)']
    counts = g.agg(pos_count = lambda s: s.gt(0).sum(), neg_count = lambda s: s.lt(0).sum())
    tail = counts.tail(5)
    #print(tail)
    above = tail['pos_count'].to_list()
    #print(above)
    below = tail['neg_count'].to_list()
    #print(below)
    x = ["UK", "US", "Vanuatu", "Vietnam", "Yemen"]
    plt.bar(x, above, color="darkred")
    plt.bar(x, below, color="darkorange", bottom=above)
    plt.xlabel("Country")
    plt.ylabel("Number of volcanoes")
    plt.title("Number Volcanoes Above/Below Sea Level")
    plt.legend(labels=["Above", "Below"])
    return plt



def average_bar():
    st.write(" ")
    st.sidebar.title("Query Two")
    st.sidebar.write("For which countries would you like to see elevation information on?")
    countries = st.sidebar.multiselect("Select your countries: ", all_countries())
    df = read_data()
    st.write(" ")
    data = bar_data(countries)
    elev = (country_elevation(data))
    averages = country_averages(elev)
    st.sidebar.write("Please choose at least two (but not more than five) countries to see data on for chart to appear.")
    if len(countries) < 2:
        st.header("Number of Volcanoes Above/Below Sea Level:")
        st.write("For the United Kingdom, United States, Vanuatu, Vietnam, and Yemen.")
        st.pyplot(s_data(read_data()))
    if len(countries) > 1 and len(countries) < 6:
        st.header("Average Volcano Elevation:")
        st.write("Bar Chart of Average Volcano Elevation in Selected Countries:")
        st.pyplot(bar_chart(averages))
    st.sidebar.write(" ")

average_bar()

def pivot2():
    df = read_data()
    check1 = st.sidebar.checkbox("Would you like more information on volcanoes by country?", True)
    pivot = df.pivot_table(index=['Country'], values=['Elevation (m)'], aggfunc='count')
    st.write(" ")
    if check1:
        st.header("Total Number of Volcanoes in Each Country:")
        st.write(pivot)

pivot2()


# QUERY THREE

def all_activities():
    df = read_data()
    lst = []
    for ind, row in df.iterrows():
        if row["Activity Evidence"] not in lst:
            lst.append(row["Activity Evidence"])
    return lst

locations = [row for row in csv.DictReader(open(FILENAME, "r"))]

evidence_types = []
for l in locations:
    if l["Activity Evidence"] not in evidence_types:
        evidence_types.append(l["Activity Evidence"])

def count_act_ev(evidence_type = evidence_types, df = read_data()):
    return [df.loc[df["Activity Evidence"].isin([evidence])].shape[0] for evidence in evidence_type]

def pie_chart(counts, sel_type):
    plt.figure()

    explodes = [0 for i in range(len(counts))]
    max = counts.index(np.max(counts))
    explodes[max] = 0.15

    plt.pie(counts, labels=sel_type, explode=explodes, autopct="%1.2f%%")
    plt.title("Proportions of Activity Evidence Types")

    return plt

def pie():
    st.sidebar.title("Query Three")
    st.sidebar.write("Which type of volcanic activity evidence do you believe is most prevalent? Chart will show with correct response.")
    activity = st.sidebar.radio("Select an activity evidence type: ", all_activities())
    data = read_data()
    counts = count_act_ev()
    if len(activity) > 1:
        if activity == "Eruption Observed":
            st.header("Pie Chart of Activity Evidence Types: ")
            st.sidebar.write("You're correct! Most volcanoes most recent activity status is described as 'Eruption Observed.'")
            st.pyplot(pie_chart(counts, evidence_types))
            st.markdown(""" <style> .font {font-size:30px ; font-family: 'Courier'; color: #FF9632;} </style> """,
                unsafe_allow_html=True)
            st.markdown('<p class="font">THE END. THANK YOU!!</p>', unsafe_allow_html=True)
        else:
            st.sidebar.write("Sorry, that response is incorrect :(")

pie()


