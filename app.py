#Load Dependencies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func
from flask import Flask, jsonify

#Create database engine
engine=create_engine("sqlite:///Resources/hawaii.sqlite")

#Reflect an existing database into a new model
Base=automap_base()

#Reflect the tables
Base.prepare(engine,reflect=True)

#Save references to each table
Measurement=Base.classes.measurement
Station=Base.classes.station

#Flask Setup
app=Flask(__name__)

#Flask Routes
@app.route('/')
def welcome():
    """List all available api routes."""
    return (
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/START_DATE (Date to be entered as Year-Month-Day ie. 2016-2-4)<br/>'
        f'/api/v1.0/START_DATE/END_DATE (2 Dates to be entered as Year-Month-Day ie. 2016-2-4/2017-2-4)'
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data available"""

    #Open a communication session with the database
    session=Session(engine)

    #Calculate the date 1 year ago from the last data point in the database
    lastdate=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    lastdate=lastdate[0]
    lastdate=dt.datetime.strptime(lastdate,'%Y-%m-%d').date()
    querydate=lastdate-dt.timedelta(days=365)

    #Perform a query to retrieve the date and precipitation scores available
    precipdata=session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>=querydate).all()

    #Close the session to end the communication with the database
    session.close()

    #Create a dictionary from the row data and append to precipitation data
    precip=[]
    for data in precipdata:
        precip_dict={}
        precip_dict[data.date]=data.prcp
        precip.append(precip_dict)
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of weather stations available"""

    #Open a communication session with the database
    session=Session(engine)

    #Perform a query to retrieve the weather stations available
    stationdata=session.query(Station.station,Station.name).all()

    #Close the session to end the communication with the database
    session.close()

    #Create a dictionary from the row data and append to station data
    station=[]
    for data in stationdata:
        station_dict={}
        station_dict[data.station]=data.name
        station.append(station_dict)
    return jsonify(station)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the last 12 months of temperature observation data available"""

    #Open a communication session with the database
    session=Session(engine)

    #Calculate the date 1 year ago from the last data point in the database
    lastdate=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    lastdate=lastdate[0]
    lastdate=dt.datetime.strptime(lastdate,'%Y-%m-%d').date()
    querydate=lastdate-dt.timedelta(days=365)

    #Perform a query to retrieve the date and temperature observations available
    tobsdata=session.query(Measurement.date,Measurement.tobs).filter(Measurement.date>=querydate).all()

    #Close the session to end the communication with the database
    session.close()

    #Create a dictionary from the row data and append to station data
    temp=[]
    for data in tobsdata:
        temp_dict={}
        temp_dict[data.date]=data.tobs
        temp.append(temp_dict)
    return jsonify(temp)

@app.route("/api/v1.0/<start>")
def startdate(start):
    """Return the minimum, average, and maximum temperature observations after a date"""

    #Open a communication session with the database
    session=Session(engine)

    #Perform a query to retrieve the minimum, average, and maximum temperature observations after a date
    startdata=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date>=start).all()

    #Close the session to end the communication with the database
    session.close()

    #Create a dictionary from the row data and append to data
    startlist=list(np.ravel(startdata))
    return jsonify(startlist)

@app.route("/api/v1.0/<start>/<end>")
def betweendates(start,end):
    """Return the minimum, average, and maximum temperature observation between two dates"""

    #Open a communication session with the database
    session=Session(engine)

    #Perform a query to retrieve the minimum, average, and maximum temperature observations between two dates
    betweendata=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
            filter(Measurement.date>=start).filter(Measurement.date<=end).all()

    #Close the session to end the communication with the database
    session.close()

    #Create a dictionary from the row data and append to data
    betweenlist=[]
    between_dict={}
    between_dict['TMIN']=betweendata[0][0]
    between_dict['TAVG']=betweendata[0][1]
    between_dict['TMAX']=betweendata[0][2]
    betweenlist.append(between_dict)
    return jsonify(betweenlist)

if __name__=='__main__':
    app.run(debug=True)