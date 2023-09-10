import pandas as pd
import collections
import json
import re
import requests

from typing import Tuple, Dict, List
from shapely.geometry import Polygon


def read_aggregates_and_geoboundaries(agg_loc:str, cadastral_loc:str) -> Tuple[pd.DataFrame, Dict]:
    """ Loads the uber movement aggregates csv and the cadastral geojson. """
    df = pd.read_csv(agg_loc, dtype="str")
    with open(cadastral_loc) as f:
        geoboundaries = json.load(f)
    return df, geoboundaries


def flatten_points(nested_points: List) -> List:
    """ Unpacks nested lists with the coordinates of a polygon. """
    if isinstance(nested_points, collections.Iterable) and not isinstance(nested_points[0], float):
        return [p for i in nested_points for p in flatten_points(i)]
    else:
        return [nested_points]


def polygon_preprocessing(polygons: Dict) -> Dict:
    """ Returns the latitude and longitude pairs of the centroid of geoboundaries. """
    centres = []
    centres_lat = []
    centres_lon = []
    movement_id = []
    name = []
    for i in range(len(polygons["features"])):
        points = polygons['features'][i]['geometry']['coordinates']
        points = flatten_points(points)
        ref_polygon = Polygon(points)
        uber_id = str(polygons['features'][i]['properties']["MOVEMENT_ID"])
        postal_code = polygons['features'][i]['properties']['GEOCODIGO']
        lat_lon = ref_polygon.centroid.wkt.split()
        a = float(re.sub(r'[(]', ' ', lat_lon[1]))
        b = float(re.sub(r'[)]', ' ', lat_lon[2]))
        centres_lat.append(b)
        centres_lon.append(a)
        movement_id.append(uber_id)
        name.append(postal_code)
    stacked_coordinates = pd.DataFrame({"movement_id": movement_id, "latitude": centres_lat, "longitude": centres_lon, "postcode": name})
    return stacked_coordinates


def sort_and_filter_trips(merged: pd.DataFrame) :
    k = df_c.groupby(['name_x','name_y']).size().reset_index().rename(columns={0:'count'})
    return k.sort_values(by = ["count"], ascending=False)


def request_distance_unique_trips(trips: pd.DataFrame, centroids: pd.DataFrame) -> Tuple[Dict, pd.DataFrame]:
    lookup_distances = {}
    df_merged = pd.merge(trips, centroids, left_on='dstid', right_on='movement_id', how='left')
    df_c = pd.merge(df_merged, centroids, left_on='sourceid', right_on='movement_id', how='left', suffixes=('_dest', '_source'))
    unique_trips = df_c.groupby(['postcode_source','postcode_dest','latitude_source','longitude_source', 'latitude_dest','longitude_dest']).size().reset_index().rename(columns={0:'count'})
    for i, (source, dest) in enumerate(zip(unique_trips['postcode_source'], unique_trips['postcode_dest'])):
        coords = f"{unique_trips['longitude_source'].iloc[i]},{unique_trips['latitude_source'].iloc[i]};{unique_trips['longitude_dest'].iloc[i]},{unique_trips['latitude_dest'].iloc[i]}"
        lookup_distances.update({f"{source},{dest}": osm_distance(coords)})
    return lookup_distances, df_c


def osm_distance(coords:str) -> pd.DataFrame:
    url = f"http://localhost:5000/route/v1/driving/{coords}?annotations=false&overview=false"
    response = requests.get(url)
    res = json.loads(response.text)
    return res['routes'][0]['legs'][0]['distance']


def expand_df_with_distance(lookup:Dict, df:pd.DataFrame) -> pd.DataFrame:
    distances = [lookup.get(f"{source},{dest}") for source, dest in zip(df['postcode_source'], df['postcode_dest'])]
    df["distance"] = distances
    df.drop(columns=["sourceid", "dstid", "standard_deviation_travel_time","geometric_mean_travel_time","geometric_standard_deviation_travel_time","movement_id_dest","movement_id_source"], inplace=True)
    return df

def extraction_pipeline() -> pd.DataFrame:
    df_q1_2019, geoboundaries =read_aggregates_and_geoboundaries("data/madrid-codigos_postales-2019-3-All-HourlyAggregate.csv", "data/madrid_codigos_postales.json")
    centroids = polygon_preprocessing(geoboundaries)
    lookup, df = request_distance_unique_trips(df_q1_2019, centroids)
    df = expand_df_with_distance(lookup, df)
    return df
