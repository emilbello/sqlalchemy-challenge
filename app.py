# Import dependencies
import numpy as np
import datetime as dt
from flask import Flask, jsonify
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


# creating an engine using the hawaii.sqlite database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

## declaring a Base using 'automap_base()'
Base = automap_base()

# Using the Base class to reflect the dabase tables 
Base.prepare(engine, reflect=True)

# Saving the references to each table by assigning the classes (measurement and station), to variables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Creating the app
app = Flask(__name__)

# Flask routes
@app.route("/")
def home_page():
    return(
        "Welcome to the Climate App API"
        "Available Routes<br/>"
        "/api/v1.0/precipitation<br/>" 
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/start<br/>"
        "/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
       
    results = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= query_date).all()
    session.close()
    prep_dict = {k:v for k, v in results}

    return jsonify(prep_dict)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station.station).all()
    station_list = np.ravel(stations).tolist()
    session.close()
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
                    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    station_tobs_12m = session.query(Measurement.tobs).\
                filter(Measurement.station == active_stations[0][0]).\
                filter(Measurement.date >= query_date).all()
    session.close()
    tobs_list = [tobs[0] for tobs in station_tobs_12m]
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_temp(start):
    
    session = Session(engine)

    calc_results = session.query(func.min(Measurement.tobs),\
                                func.avg(Measurement.tobs),\
                                func.max(Measurement.tobs)).\
                                filter(Measurement.date >= start).all()
                                
    session.close()
    return_val = list(np.ravel(calc_results))

    results_dict = {"Start Date": start,
                    "TMIN": return_val[0],
                    "TAVG": return_val[1],
                    "TMAX": return_val[2]}

    return jsonify(results_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end_temp(start, end):
    
    session = Session(engine)

    calc_results = session.query(func.min(Measurement.tobs),\
                                func.avg(Measurement.tobs),\
                                func.max(Measurement.tobs)).\
                                filter(Measurement.date >= start).\
                                filter(Measurement.date <= end).all()
                                
    session.close()
    return_val = list(np.ravel(calc_results))

    results_dict = {"Start Date": start,
                    "End Date": end,
                    "TMIN": return_val[0],
                    "TAVG": return_val[1],
                    "TMAX": return_val[2]}

    return jsonify(results_dict)

if __name__ == "__main__":
    app.run(debug=True)