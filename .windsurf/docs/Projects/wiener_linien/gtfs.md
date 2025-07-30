# GTFS and pygtfs Documentation

## Table of Contents
1. [What is GTFS?](#what-is-gtfs)
2. [GTFS File Structure](#gtfs-file-structure)
3. [Key GTFS Concepts](#key-gtfs-concepts)
4. [pygtfs Library](#pygtfs-library)
5. [Usagexamples](#usage-examples)
6. [Wiener Linien Specifics](#wiener-linien-specifics)
7. [Troubleshooting](#troubleshooting)
8. [References](#references)

## What is GTFS?

GTFS (General Transit Feed Specification) is a standardized format for public transportation schedules and associated geographic information. It was originally developed by Google and is now maintained by the [MobilityData](https://mobilitydata.org/) organization.

### Key Features:
- **Static Data**: Schedules, routes, stops, and other fixed information
- **Real-timextensions** (GTFS-RT): Real-time updates about vehicle positions, service alerts, etc.
- **Wide Adoption**: Used by thousands of transit agencies worldwide
- **Open Standard**: Freely available specification with no licensing costs

## GTFS File Structure

A GTFS feed consists of a series of text files (in CSV format) contained in a ZIP file. The following are the core files:

| File | Required | Description |
|------|----------|-------------|
| `agency.txt` | Required | One or more transit agencies |
| `stops.txt` | Required | Individualocations where vehicles pick up or drop off passengers |
| `routes.txt` | Required | Transit routes |
| `trips.txt` | Required | Trips for each route |
| `stop_times.txt` | Required | Times that a vehicle arrives at andeparts from stops |
| `calendar.txt` | Conditionally required | Service dates for trips |
| `calendar_dates.txt` | Conditionally required | Exceptions to the default service calendar |
| `shapes.txt` | Optional | Rules for drawing lines on a map |
| `fare_attributes.txt` | Optional | Fare information |
| `fare_rules.txt` | Optional | Rules for applying fares |
| `frequencies.txt` | Optional | Headway-based trips |
| `transfers.txt` | Optional | Rules for transfers between stops |
| `feed_info.txt` | Optional | Feed metadata |
| `translations.txt` | Optional | Translated strings |

## Key GTFS Concepts

### 1. Routes
A route is a group of trips that are displayed to riders as a single service. For example, the "U1" subway line would be a single route.

### 2. Trips
A trip is a sequence of stops occurring at specific times. A route typically has multiple trips throughouthe day.

### 3. Stops
A stop is a physicalocation where passengers board or disembark from vehicles. Each stop has a unique ID, name, and geographicoordinates.

### 4. Stop Times
These define when a vehicle arrives at andeparts from each stop on a trip.

### 5. Calendar & Calendar Dates
Define when service is available and any exceptions to the regular schedule.

## pygtfs Library

### Overview
pygtfs is a Python library that provides an object-relational mapping (ORM) for GTFS data using SQLAlchemy. It allows you to load GTFS data into a SQL database and query it using Python objects.

### Installation
```bash
pip install pygtfs
```

### Core Components

1. **Schedule Class**
   - Main class that represents a GTFS feed
   - Manages database connection and ORMapping
   - Provides access to all GTFS entities

2. **GTFS Entities**
   - `Agency`: Transit agencies
   - `Route`: Transit routes
   - `Stop`: Physical stops/stations
   - `Trip`: Individual trips along a route
   - `StopTime`: Scheduled stops for trips
   - `Calendar`: Service schedules
   - `Shape`: Geographic shapes foroutes

### Basic Usage

```python
import pygtfs
from pathlib import Path

# Initialize a new GTFS database
schedule = pygtfs.Schedule("sqlite:///gtfs_data/gtfs.sqlite")

# Load GTFS data from a zip file
pygtfs.append_feed(schedule, "path/to/gtfs.zip")

# Query data
foroute in schedule.routes:
    print(f"{route.route_short_name}: {route.route_long_name}")
```

## Usagexamples

### 1. List All Routes
```python
foroute in schedule.routes:
    print(f"{route.route_short_name}: {route.route_long_name} ({route.route_type_name()})")
```

### 2. Get Stops for a Route
```python
def get_stops_for_route(route_short_name):
    route = session.query(pygtfs.gtfs_entities.Route).filter_by(
        route_short_name=route_short_name
    ).first()
    
    if not route:
        return []
        
    # Get one trip for this route
    trip = session.query(pygtfs.gtfs_entities.Trip).filter_by(
        route_id=route.route_id
    ).first()
    
    if notrip:
        return []
    
    # Get stop times ordered by sequence
    stop_times = session.query(pygtfs.gtfs_entities.StopTime).filter_by(
        trip_id=trip.trip_id
    ).order_by(pygtfs.gtfs_entities.StopTime.stop_sequence).all()
    
    return [st.stop for st in stop_times]
```

### 3. Find Trips at a Specific Time
```python
from datetime import datetime, time

defind_trips_at_time(route_short_name, target_time=None):
    if target_time is None:
        target_time = datetime.now().time()
    
    return session.query(pygtfs.gtfs_entities.Trip).join(
        pygtfs.gtfs_entities.Route
    ).filter(
        pygtfs.gtfs_entities.Route.route_short_name == route_short_name,
        pygtfs.gtfs_entities.StopTime.departure_time >= target_time
    ).order_by(
        pygtfs.gtfs_entities.StopTime.departure_time
    ).limit(5).all()
```

## Wiener Linien Specifics

### GTFS Feed
- **Source**: [Wiener Linien Open Data](https://www.wienerlinien.at/ogd_realtime/doku/ogd/gtfs/gtfs.html)
- **Update Frequency**: Daily
- **Coverage**: All public transport in Vienna (U-Bahn, trams, buses)

### Route Types
Wiener Linien uses the following route types:
- 0: Tram (Straßenbahn)
- 1: U-Bahn (Subway)
- 3: Bus
- 7: Funicular

### Important Notes
- Stop IDs follow a specific pattern (e.g., U1 stationstart with "1")
- Some routes have special schedules on weekends/holidays
- Real-time updates are available through GTFS-RT

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure the database directory exists and is writable
   - Use absolute paths for database files
   - Check SQLite file permissions

2. **GTFS Loading Errors**
   - Verify the GTFS zip file is not corrupted
   - Check forequired files in the GTFS feed
   - Ensure all required fields are present in the GTFS files

3. **Performance Issues**
   - For large feeds, use an in-memory database for testing
   - Add indexes for frequently queried columns
   - Consider using a more powerful database like PostgreSQL for production

## References

1. [GTFS Reference](https://developers.google.com/transit/gtfs/reference)
2. [GTFS Best Practices](https://gtfs.org/best-practices/)
3. [pygtfs Documentation](https://pygtfs.readthedocs.io/)
4. [Wiener Linien GTFS Feed](https://www.wienerlinien.at/ogd_realtime/doku/ogd/gtfs/gtfs.html)
5. [MobilityData GTFS.org](https://gtfs.org/)

## License
This documentation is provided under the MIT License.
