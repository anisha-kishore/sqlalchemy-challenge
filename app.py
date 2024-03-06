# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#Taken from Week 10, Class 3, Activity 10
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
#Base.prepare(autoload_with=engine)
Base.prepare(engine, reflect=True)
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(bind=engine)


#################################################
# Flask Setup
#Taken from Week 10, Class 3, Activity 8
#################################################
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

#################################################
# Flask Routes  
#Taken from Week 10, Class 3, Activity 10
#################################################

####Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    year_ago= dt.date(2017,8,23)-dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    #From ChatGPT
    results = session.query(Measurement.date, Measurement.prcp) \
    .filter(Measurement.date >= year_ago) \
    .all()
    session.close()

    precipitation_data = []
    for Measurement.date, Measurement.prcp in results:
        precipitation_dict = {}
        precipitation_dict["Measurement.date"] = Measurement.prcp
        precipitation_data.append(precipitation_dict)

    return jsonify(precipitation_data)

###Stations Route
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Perform a query to retrieve the station names
    results = session.query((Station.station)).all()
    session.close()

    # Convert list of tuples into normal list
    station_names = list(np.ravel(results))
    return jsonify(station_names)

###TOBS Route
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #find time span
    year_ago = dt.datetime.strptime('2017-08-23', '%Y-%m-%d').date() - dt.timedelta(days=365)

    # Perform a query to retrieve the most active station
    active_stations = session.query(Measurement.station, func.count(Measurement.station)) \
    .group_by(Measurement.station) \
    .order_by(func.count(Measurement.station).desc()) \
    .all()
    #Most Active Station
    most_active_station_id = active_stations[0][0]

    #Calculations
    temperature_stats = session.query(Measurement.tobs, Measurement.tobs)\
        .filter(Measurement.station == most_active_station_id) \
        .filter(Measurement.date >= year_ago) \
        .all()

    # Convert list of tuples into normal list
    tobs_data = list(np.ravel(temperature_stats))

    return jsonify(tobs_data)


###Start Route
#Accepts the start date as a parameter from URL
#Return min, max, and avg. temps. calculated from given start date to end of dataset

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def startend(start=None,end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    if not end:
        # Perform a query to retrieve the temperature statistics
        startdate = dt.datetime.strptime(start, '%Y-%m-%d')
        temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)) \
            .filter(Measurement.date >= startdate) \
            .all()

        temperature_stats_list = list(np.ravel(temperature_stats))

        session.close()

        return jsonify(temperature_stats_list)
    

    # Perform a query to retrieve the temperature statistics
    startdate = dt.datetime.strptime(start, '%Y-%m-%d')
    enddate = dt.datetime.strptime(end, '%Y-%m-%d')


    start_end_temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)) \
        .filter(Measurement.date >= startdate, Measurement.date <= enddate) \
        .all()


    session.close()

    start_end_temperature_stats_list = list(np.ravel(start_end_temperature_stats))

    session.close()

if __name__ == '__main__':
    app.run(debug=True)

