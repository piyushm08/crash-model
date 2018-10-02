# Designed to create a smaller map from a larger map
# Can be used for making test datasets, or for debugging
import argparse
from shapely.geometry import LineString, Point, box
import geojson
from data.util import read_geojson, get_reproject_point
from data.util import prepare_geojson, output_from_shapes
import sys


def get_buffer(filename, lat=None, lon=None, radius=None, boundingbox=None):
    """
    Given a geojson file, latitude and longitude in 4326 projection,
    and a radius, write to file (as geojson) all the LineStrings and
    Points that overlap a circular buffer around the coordinates.
    Args:
        filename
        lat
        lon
        radius
    Returns:
        A list of overlapping geojson features 4326 projection
    """

    segments = read_geojson(filename)

    # Calculate the bounding circle
    overlapping = []
    buffered_poly = None
    if radius:
        point = get_reproject_point(lat, lon)
        buffered_poly = point.buffer(radius)
    else:
        minx, miny, maxx, maxy = boundingbox
        top_left = get_reproject_point(maxy, minx)
        bottom_right = get_reproject_point(miny, maxx)
        buffered_poly = box(top_left.x, bottom_right.y,
                            bottom_right.x, top_left.y)
        output_from_shapes([(buffered_poly, {})], 'test2.geojson')

    for segment in segments:
        if segment[0].intersects(buffered_poly):
            
            if type(segment[0]) == LineString:
                coords = [x for x in segment[0].coords]
                overlapping.append({
                    'geometry': {'coordinates': coords, 'type': 'LineString'},
                    'type': 'Feature',
                    'properties': segment[1]
                })
            elif type(segment[0]) == Point:
                overlapping.append({
                    'geometry': {
                        'coordinates': [segment[0].x, segment[0].y],
                        'type': 'Point'
                    },
                    'properties': segment[1]
                })
            elif type(segment[0]) == 'MultiLineString':
                print("MultiLineString not implented yet, skipping...")

    if overlapping:
        overlapping = prepare_geojson(overlapping)
    return overlapping


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", type=str,
                        help="Geojson file used",
                        required=True)
    parser.add_argument("-lat", "--latitude", type=str,
                        help="Latitude of center point")
    parser.add_argument("-lon", "--longitude", type=str,
                        help="Longitude of center point")
    parser.add_argument("-r", "--radius", type=int,
                        help="Radius of buffer around coordinates, in meters")
    parser.add_argument("-minx", "--minx", type=float,
                        help="minx of a bounding box")
    parser.add_argument("-miny", "--miny", type=float,
                        help="miny of a bounding box")
    parser.add_argument("-maxx", "--maxx", type=float,
                        help="maxx of a bounding box")
    parser.add_argument("-maxy", "--maxy", type=float,
                        help="maxy of a bounding box")
    parser.add_argument("-o", "--outputfile", type=str,
                        help="Output filename",
                        required=True)
    args = parser.parse_args()
    if not ((args.minx and args.miny, args.maxx, args.maxy)
            or (args.radius and args.latitude, args.longitude)):
        sys.exit("Either minx, miny, maxx, and maxy or " +
                 "radius and lat/lon required")

    overlapping = get_buffer(args.filename, lat=args.latitude,
                             lon=args.longitude, radius=args.radius,
                             boundingbox=[args.minx, args.miny,
                                          args.maxx, args.maxy])

    if overlapping:
        with open(args.outputfile, 'w') as outfile:
            geojson.dump(overlapping, outfile)
        print("Copied {} features to {}".format(
            len(overlapping['features']), args.outputfile))
    else:
        print("No overlapping elements found")
