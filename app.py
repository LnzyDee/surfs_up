import datetime as dt
from statistics import mean
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# allow access and query SQLite db file
engine = create_engine("sqlite:///hawaii.sqlite")
# reflect db into our classes
Base = automap_base()
# reflect the db
Base.prepare(engine, reflect=True)
# save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# create a session link from python to database
session = Session(engine)

# define Flask app; create Flask application called "app"
app = Flask(__name__)
# define the welcome route
@app.route("/")
# add precip, stations, tobs, and temp routes
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API
    Available Routes:
    /api/v1.0/preciptation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')

# create the preciptation analysis route
@app.route("/api/v1.0/precipitation")

# create the precipitation() function
def precipitation():
    # calculate the date one year ago from most recent date in db
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # write query to get the date and precipitation for the previous year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    # use jsonify to format results into a JSON structured file
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

# create the stations route
@app.route("/api/v1.0/stations")

# create new function stations()
def stations():
    # create a query to get all stations in db
    results = session.query(Station.station).all()
    # convert unraveled results into list using list() then jsonify list and return as JSON
    stations = list(np.ravel(results))
    # 'stations=stations' formats list into json
    return jsonify(stations=stations)

# create the temp observations for prev year
@app.route("/api/v1.0/tobs")

# create function temp_monthly()
def temp_monthly():
    # calculate date one year ago from last date in db
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # query primary station for all temp observations from prev year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    # unravel results into one-dimensional array and convert to list then jsonify list
    temps = list(np.ravel(results))
    # jsonify temps list and return it
    return jsonify(temps=temps)

# create route for min, avg, and max temps
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

# create function stats(), add parameters start and end
def stats(start=None, end=None):
    # create query to select min, avg, and max temps from db
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    # to determine start and end date add if-not statement
    if not end:
        # query db using list made above
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # unravel results into one-dimensional array and convert to list
        temps = list(np.ravel(results))
        # jsonify results and return them
        return jsonify(temps)
    # calculate temp min, avg, and max with start and end dates using sel list
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)