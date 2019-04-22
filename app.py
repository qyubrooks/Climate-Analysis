
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

import numpy as np
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
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
def welcome():
    """List all available api routes."""

    return(
         f"Welcome to the Hawaii Climate API! <br>"
         f"<br>"
         f"Available API Routes <br>"
         f"<br>"
         f"List of dates and percipitation observations from 2017-08-23 To 2016-08-24:<br>"
         f"/api/v1.0/precipitation <br>"
         f"<br>"
         f"List of Stations:<br>"
         f"/api/v1.0/stations <br>"
         f"<br>"
         f"List of dates and temperatures from 2017-08-23 To 2016-08-24:<br>"
         f"/api/v1.0/tobs <br>"
         f"<br>"
         f"List of minimum temperature, average temperature, max temperature from start date:<br>"
         f"start date format 'yyyy-mm-dd'<br>"
         f"/api/v1.0/start/<start> <br>"
         f"<br>"
         f"List of minimum temperature, average temperature, max temperature from start date to end date:<br>"
         f"start date and end date format 'yyyy-mm-dd'<br>"
         f"/api/v1.0/start/end/<start>/<end> <br>"   
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using date as the key and prcp as the value."""
    #find the last date from measurement table's date column
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # Get the first element of the tuple
    last_date = last_date[0]

    # Calculate the date 1 year ago from the last data point in the database
    one_year_ago_date = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)

    precipitation_results = session.query(Measurement.date, Measurement.prcp).\
                       filter(Measurement.date >= one_year_ago_date).all()

    # Create a dictionary from the row data and append to a list
    precipitation_values = []
    for p in precipitation_results:
        prcp_dict = {}
        prcp_dict["date"] = p.date
        prcp_dict["prcp"] = p.prcp
        precipitation_values.append(prcp_dict)

    return jsonify(precipitation_values)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Query all stations
    station_results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    stations = list(np.ravel(station_results))

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """query for the dates and temperature observations from a year from the last data point"""

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
   
    last_date = last_date[0]

    one_year_ago_date = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)

    temperature_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago_date).all()
    
    all_temp = []
    for t in temperature_results:
        temp_dict = {}
        temp_dict["date"] = t.date
        temp_dict["tobs"] = t.tobs
        all_temp.append(temp_dict)


    return jsonify(all_temp)


@app.route("/api/v1.0/start/<start>")
def start(start): # start date '2017-01-01'
    """Return a JSON list of the minimum temperature, average temperature, max temperature for a given start or start-end range.
    When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date"""
    
    
    start_results = session.query(func.min(Measurement.tobs).label("TMIN"),func.max(Measurement.tobs).label("TMAX"),\
                    func.avg(Measurement.tobs).label("TAVG")).filter(Measurement.date>=start).all()
    
    start_temp = []
    
    for row in start_results:
        row_dict = {}
        row_dict["minimum temperature"] = row.TMIN
        row_dict["maximum temperature"] = row.TMAX
        row_dict["average temperature"] = row.TAVG
        start_temp.append(row_dict)

    return jsonify(start_temp)
  


@app.route("/api/v1.0/start/end/<start>/<end>")
def start_end(start,end): # start date 2017-01-01, end date 2017-01-15
    """When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive"""
    
    start_end = session.query(func.min(Measurement.tobs).label("TMIN"),func.max(Measurement.tobs).label("TMAX"),\
                func.avg(Measurement.tobs).label("TAVG")).filter(Measurement.date>=start).filter(Measurement.date<=end).all()
    

    start_end_temp = []
    
    for t in start_end:
        start_end_dict = {}
        start_end_dict["minimum temperature"] = t.TMIN
        start_end_dict["maximum temperature"] = t.TMAX
        start_end_dict["average temperature"] = t.TAVG
        start_end_temp.append(start_end_dict)

    return jsonify(start_end_temp)


if __name__ == "__main__":
   app.run(debug=True)