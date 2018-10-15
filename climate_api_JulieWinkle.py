import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def index():
    
    return (
        "<h1>SQL Alchemy Homework</h1>"
        f"<a href=""/api/v1.0/stations"">Stations</a><br/>"
        f"<a href=""/api/v1.0/tobs"">Temperature observations from last year</a><br/>"
        f"<a href=""/api/v1.0/precipitation"">Precipitation observations from last year</a><br/>"
        f"<a href=""/api/v1.0/temp/2016-01-01"">MIN, AVG, MAX temperature from one date</a><br/>"
        f"<a href=""api/v1.0/temp/2016-01-01/2016-01-15"">MIN, AVG, MAX temperature for two weeks</a><br/>"
        )


@app.route("/api/v1.0/stations")
def stations():
    
    # Return a JSON list of stations from the dataset.
    stations_list = session.query(Station.station).all()
    stations_list

    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():

    # Return a JSON list of Temperature Observations (tobs) for the previous year
    # Calculate the date one year from the last date in data set.

    twelve_months = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    temps = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.date >= twelve_months).all()

    # Convert list of tuples into normal list
    temps_list = list(np.ravel(temps))

    return jsonify(temps_list)


@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Calculate the date one year from the last date in data set.
    twelve_months = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the dates and temperature observations from the last year.
    twelve_months_data = session.query(Measurement.date, Measurement.prcp).\
                         filter(Measurement.date >= twelve_months).all()

    # Convert the query results to a Dictionary using date as the key and prcp as the value.
    dict_ = {date: prcp for date, prcp in twelve_months_data}
           
    # Return the JSON representation of your dictionary.
    return jsonify(dict_)
        
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature 
    # for a given start or start-end range.
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal 
    # to the start date
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start 
    # and end date inclusive.

def dates(start=None, end=None):

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        data = session.query(*sel).\
                   filter(Measurement.date >= start).all()
        # Unravel results into an array and convert to a list
        one_date = list(np.ravel(data))
        return jsonify(one_date)

    # calculate TMIN, TAVG, TMAX with start and stop
    data = session.query(*sel).\
           filter(Measurement.date >= start).\
           filter(Measurement.date <= end).all()

    # Unravel results into an array and convert to a list
    date_range = list(np.ravel(data))
    return jsonify(date_range)


if __name__ == '__main__':
    app.run(debug=True)
