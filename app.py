# Steven Liang
# ITP-216 Spring 2022
# Section: 31885
# Final Project

from flask import Flask, redirect, render_template, request, session, url_for, Response
import os
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io

from numpy import true_divide

app = Flask(__name__)

# route to home page
@app.route("/")
def start():
    return render_template("home.html")

# route to home page
@app.route("/home")
def home():
    return render_template("home.html")

# route to selected state
@app.route("/state/<state_>")
def state(state_):
    return render_template("state.html", state=state_)

# route to selected county
@app.route("/county/<county_>")
def county(county_):
    return render_template("county.html", county=county_)

# create route for matplotlib plot as png file
@app.route('/plot.png')
def plot_png():
    # create matplotlib figure
    fig = create_figure(session["county"], session["state"], session["type"])

    output = io.BytesIO()
    # save as png
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


# check for successful lookup and redirect to appropriate page
@app.route("/lookup", methods=["POST", "GET"])
def lookup():
    if request.method == "POST":
        session["county"] = request.form["county"].title()
        session["state"] = request.form["state"].title()
        session["type"] = request.form["type"]
    # check that valid county and state are entered
    if not checkValid(session["county"], session["state"]):
        return redirect(url_for("home"))
    # redirect to county page
    if session["type"] == "County":
        return redirect(url_for("county", county_ = session["county"]))
    # redirec to state page
    elif session["type"] == "State":
        return redirect(url_for("state", state_ = session["state"]))

# redirect between pages
@app.route("/redir", methods=["POST", "GET"])
def redir():
    if request.method == "POST":
        # redirect back to home
        if request.form["redir"] == "Start Over":
            return redirect(url_for("home"))
        # redirect to state from county page
        elif request.form["redir"] == "View State":
            session["type"] = "State"
            return redirect(url_for("state", state_ = session["state"]))
        # redirect to county from state page
        elif request.form["redir"] == "View County":
            session["type"] = "County"
            return redirect(url_for("county", county_ = session["county"]))

# check that the queried county and state are in the data set
def checkValid(county, state):
    df = pd.read_csv("co-est2019-annres.csv", encoding = "ISO-8859-1")
    df = df.dropna()

    # need to create new columns for county and state
    df['County'] = df['Area'].str.split(',').str[0]
    df['County'] = df['County'].str.replace(' County', '')
    
    df['State'] = df['Area'].str.split(',').str[1].str.strip()

    # get list of states
    state_list = df['State'].unique()

    # check if state is in the list
    if state not in state_list:
        return False
    
    states = df.groupby('State')
    # get list of counties in selected state
    counties = states.get_group(state)
    county_list = counties['County'].unique()
    # check if county is in the list
    if county not in county_list:
        return False
    
    return True
    


# creates and returns the matplotlib figure for the selected state/county
def create_figure(county, ST, form):
    # read in data from csv
    df = pd.read_csv("co-est2019-annres.csv", encoding = "ISO-8859-1")
    df = df.dropna()

    # need to create new columns for county and state
    df['County'] = df['Area'].str.split(',').str[0]
    df['County'] = df['County'].str.replace(' County', '')
    
    df['State'] = df['Area'].str.split(',').str[1].str.strip()

    # list of available years in the data
    years = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']

    # create plot for county's population
    if form == 'County':
        cnty = df[ df['County'] == county]
        y = []
        # each year is a separate column so need to create list
        for year in years:
            y.append(float(cnty[year].values[0]))

        fig, ax = plt.subplots()
        # plot and set axes and title
        ax.plot(years, y, label = county)
        ax.set(title = county + " County Population: 2010-2019", xlabel = "Year", ylabel = "Population")
        ax.ticklabel_format(axis='y', style='plain')
        ax.legend()

        fig.tight_layout()
    # create plot for state's population
    elif form == 'State':
        df_grouped = df.groupby('State')
        # df of all counties in the state
        state = df_grouped.get_group(ST)
        pop = []
        
        for year in years:
            # sum the populations of all counties in the state for a year and append to list
            pop.append(state[year].sum())

        fig, ax = plt.subplots()
        # plot data and set axes and title
        ax.plot(years, pop, label = ST)
        ax.set(title = ST + " Population: 2010-2019", xlabel = "Year", ylabel = "Population")
        ax.ticklabel_format(axis='y', style='plain')
        ax.legend()

        fig.tight_layout()
    
    # return generated figure
    return fig


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)