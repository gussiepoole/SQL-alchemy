import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# Using Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine) 
# Precipitation for the last 12 months 
    """Precipitation analysis in Hawaii over the last year"""
    results = session.query(measurement.date, func.avg(measurement.prcp))\
        .filter(measurement.date > '2016-08-22')\
        .group_by(measurement.date)\
        .order_by(measurement.date.desc())\
        .all()


    session.close()

    # Return the JSON representation of your dictionary.

    precipitation_results = []
    for date, prcp, in results:
        precipitation_dict = {}
        precipitation_dict["precipitation"] = prcp
        precipitation_dict ["date"]= date
        precipitation_results.append(precipitation_dict)


    return jsonify(precipitation_results)


# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # create our session (link) from Python to the DB
    session = Session(engine)
    """Return a list of all the active Weather stations in Hawaii"""
    station_query = session.query(station.station, station.id).all()
    
    session.close()

    station_results = []
    for station, id, in station_query:
        station_dict = {}
        station_dict['station'] = station
        station_dict['id'] = id
        station_results.append(station_dict)
    return jsonify (station_results)


#Create a route that queries the dates and temp observed for the most active station for the last year of data and returns a JSON list of the temps observed for the last year
@app.route("/api/v1.0/tobs") 
def tobs():
    session = Session(engine)
    """Return the  dates and temperature observations of the most-active station for the previous year of data"""
    most_active_query = session.query(measurement.tobs, measurement.station).filter(measurement.date > '2016-08-22').all()
    session.close()

    # Create list for the date, tob and station to be entered into
    most_active_results = []

    for station, date, tobs in most_active_query:
        most_active_dict = {}
        most_active_query['station'] = station
        most_active_dict['date'] = date
        most_active_dict['tobs'] = tobs
        most_active_results.append(most_active_dict)

    return jsonify(most_active_results)
   

# Create a route that when given the start date only, returns the minimum, average, and maximum temperature observed for all dates greater than or equal to the start date entered by a user
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    
    session = Session(engine)
    
    # if both start and end date
    if end != None:
        spec_date = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()
    
        # if only start date
    else:
        spec_date = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    
        session.close()

# Create a list for min, avg and max dicts to be appended to query

    min_max_avg_results = []
    for min, max, avg in spec_date:
        min_max_avg_dict = {}
        min_max_avg_dict['min'] = min
        min_max_avg_dict['average'] = avg
        min_max_avg_dict['max'] = max
        min_max_avg_results.append(min_max_avg_dict)
    
    return jsonify(min_max_avg_results)







# # Define function, set start and end dates entered by user as parameters for start_end_date decorator
# @app.route("/api/v1.0/<start>")
# @app.route("/api/v1.0/<start>/<end>")
# def start_end(start, end):
#     # return (
#     # f"start {start}<br/>"
#     # f"end {end}<br/>"
#     #  )
#     session = Session(engine)
#     session.query(measurement.date, measurement.prcp)\
#         .filter(measurement.date >= start)\
#         .filter(measurement.date <= end)\
#         .order_by(measurement.date.desc())\
#         .all()

#     session.close()




if __name__ == '__main__':
    app.run(debug=True)