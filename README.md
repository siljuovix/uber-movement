# Description

Data extraction pipeline to add geographic features from [OpenStreetMap](https://www.openstreetmap.org/#map=6/51.330/10.453) to the trips information from Uber movement [Uber movement](https://movement.uber.com/?lang=en-US) . Possible applications for this workflow are ETA prediction models or traffic and seasonality analysis.

# Requirements

- Hourly aggregate csv file from Uber movement download page. This file contains the aggregated data of the trips that start and end
within the same cadastral zone of a city. For downloads, users must register for free beforehand.
- Cadastral distribution of the city in hand, also downloadable from Uber movement. This file is a json file with the names of the zones of the cadastral zones in the
hourly aggregate csv and the coordinates of the polygon that delimits the zones.
- Distance between the cadastral zones can be queried using OSRM, an routing engine based on OpenStreetMap (OSM) maps. The [OSRM docker image](https://hub.docker.com/r/osrm/osrm-backend/) is probably the simplest way to get the routing engine up and accepting requests.
-  OSM extracts for the places to be queried. [Geofabrik](http://download.geofabrik.de/europe/spain/madrid.html) offers different map segmentation options for the whole planet.  

Both the hourly aggregate csv and the cadastral information json are expected in a folder named data/ in the root folder.

In addition, run inside the dev environment:

```sh
pip install -r requirements.txt
```

# Example usage

The code in the pipeline was developed for the city of Madrid. The files in Uber movement for other cities might be slightly different, a thing to check before running the extraction.

```sh
from uber_movement import data_extraction

madrid_trips = data_extraction.extraction_pipeline()

```

In the example, madrid trips will be a pandas dataframe with the following columns:
- hod (hour of the day)

- mean_travel_time

- latitude_dest (the latitude of the center of the polygon of the destination zone)

- longitude_dest (the longitude of the center of the polygon of the zone)

- postcode_dest (postal code of the destination zone)

- latitude_source

- longitude_source

- postcode_source

- distance (fastest driving route distance between source and destination according to OSRM)
