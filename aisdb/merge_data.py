#import asyncio

import numpy as np

from common import *
from track_gen import trackgen
from gebco import Gebco
from wsa import wsa
from shore_dist import shore_dist_gfw
from webdata import marinetraffic


def merge_tracks_shoredist(tracks):
    with shore_dist_gfw() as sdist:
        for track in tracks:
            track['km_from_shore'] = np.array([sdist.getdist(x, y) for x, y in zip(track['lon'], track['lat']) ])
            track['dynamic'] = set(track['dynamic']).union(set(['km_from_shore']))
            yield track

def merge_tracks_bathymetry(tracks):
    with Gebco() as bathymetry:
        for track in tracks:
            track['depth_metres'] = np.array([bathymetry.getdepth(x, y) for x,y in zip(track['lon'], track['lat']) ]) * -1
            track['dynamic'] = set(track['dynamic']).union(set(['depth_metres']))
            yield track

def merge_tracks_hullgeom(tracks):
    with marinetraffic.scrape_tonnage() as hullgeom:
        for track in tracks:
            track['deadweight_tonnage'] = hullgeom.get_tonnage_mmsi_imo(track['mmsi'], track['imo'] or 0)
            track['submerged_hull_m^2'] = wsa(track['deadweight_tonnage'], track['ship_type'] or 0)
            track['static'] = set(track['static']).union(set(['submerged_hull_m^2', 'deadweight_tonnage']))
            yield track


def merge_layers(tracks):
    ''' generator function to merge AIS row data with shore distance, bathymetry, and geometry databases

        same as above functions, but all combined in one

        args:
            tracks: dictionary generator 
                yields track dictionary objects

        yields:
            sets of rows grouped by MMSI sorted by time with additional columns appended

        # set start method in main script
        #import os; from multiprocessing import set_start_method
        #if os.name == 'posix' and __name__ == '__main__': 
        #    set_start_method('forkserver')
    
    '''
    #from webdata import marinetraffic 

    # read data layers from disk to merge with AIS
    print('aggregating ais, shore distance, bathymetry, vessel geometry...')
    with shore_dist_gfw() as sdist, Gebco() as bathymetry, marinetraffic.scrape_tonnage() as hullgeom:

        #for rows in list(rowgen):
        for track in tracks:

            # vessel tonnage from marinetraffic.com
            track['deadweight_tonnage'] = hullgeom.get_tonnage_mmsi_imo(track['mmsi'], track['imo'] or 0)

            # wetted surface area - regression on tonnage and ship type
            track['submerged_hull_m^2'] = wsa(track['deadweight_tonnage'], track['ship_type'] or 0)

            # shore distance from cell grid
            track['km_from_shore'] = np.array([sdist.getdist(x, y) for x, y in zip(track['lon'], track['lat']) ])

            # seafloor depth from cell grid
            track['depth_metres'] = np.array([bathymetry.getdepth(x, y) for x,y in zip(track['lon'], track['lat']) ]) * -1

            # seafloor depth from nonnegative border cells
            track['depth_border_cells_average'] = np.array([bathymetry.getdepth_cellborders_nonnegative_avg(x, y) for x,y in zip(track['lon'], track['lat'])])

            # update indices
            track['static'] = set(track['static']).union(set(['submerged_hull_m^2', 'deadweight_tonnage']))
            track['dynamic'] = set(track['dynamic']).union(set(['km_from_shore', 'depth_metres', 'depth_border_cells_average']))
            #track['dynamic'] = set(track['dynamic']).union(set(['km_from_shore', 'depth_metres']))

            yield track
