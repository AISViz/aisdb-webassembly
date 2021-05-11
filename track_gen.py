from functools import reduce
from datetime import timedelta

import numpy as np


def trackgen(rows: np.ndarray) -> dict:
    '''
        each row contains columns from database: 
            mmsi time lon lat cog sog name type
        rows must be sorted by first by mmsi, then time

        TODO: update code to work with a variable number of columns

    '''
    tracks_idx = np.append(np.append([0], np.nonzero(rows[:,0].astype(int)[1:] != rows[:,0].astype(int)[:-1])[0]+1), len(rows))
    for i in range(len(tracks_idx)-1): 
        yield dict(
            mmsi=int(rows[tracks_idx[i]][0]),
            name=str(rows[tracks_idx[i]][6]).rstrip(),
            type=rows[tracks_idx[i]][7],
            time=rows[tracks_idx[i]:tracks_idx[i+1]].T[1],
            **{ n : rows[tracks_idx[i]:tracks_idx[i+1]].T[c].astype(float) for c,n in zip(range(2, 6),['lon','lat','cog','sog'])},
        )


#def segment(track: dict, maxdelta: timedelta, minsize: int) -> filter:
#    splits_idx = lambda track: np.append(np.append([0], np.nonzero(track['time'][1:] - track['time'][:-1] >= maxdelta)[0]+1), [len(track['time'])])
#    return filter(lambda seg: len(seg) >= minsize, list(map(range, splits_idx(track)[:-1], splits_idx(track)[1:])))

def segment(track: dict, maxdelta: timedelta, minsize: int) -> filter:
    splits_idx = lambda track: np.append(np.append([0], np.nonzero(track['time'][1:] - track['time'][:-1] >= maxdelta.total_seconds())[0]+1), [len(track['time'])])
    return filter(lambda seg: len(seg) >= minsize, list(map(range, splits_idx(track)[:-1], splits_idx(track)[1:])))


def filtermask(track, rng, filters):
    '''
    from .gis import compute_knots
    filters=[
            lambda track, rng: track['time'][rng][:-1] != track['time'][rng][1:],
            #lambda track, rng: compute_knots(track, rng) < 40,
            lambda track, rng: (compute_knots(track, rng[:-1]) < 40) & (compute_knots(track, rng[1:]),
            lambda track, rng: np.full(len(rng)-1, 201000000 <= track['mmsi'] < 776000000, dtype=np.bool), 
        ]
    '''
    mask = reduce(np.logical_and, map(lambda f: f(track, rng), filters))
    #return np.logical_and(np.append([True], mask), np.append(mask, [True]))
    return np.append([True], mask)


def writecsv(rows, pathname='/data/smith6/ais/scripts/output.csv', mode='a'):
    with open(pathname, mode) as f: 
        f.write('\n'.join(map(lambda r: ','.join(map(lambda r: r.replace(',','').replace('#',''), map(str.rstrip, map(str, r)))), rows))+'\n')


def readcsv(pathname='/data/smith6/ais/scripts/output.csv', header=True):
    with open(pathname, 'r') as csvfile: 
        reader = csv.reader(csvfile, delimiter=',')
        rows = np.array(list(reader), dtype=object)
        if header: columns, rows = rows[0], rows[1:]
    return np.array([c.astype(t) for c,t in zip(rows.T, 
        [np.uint32, str, str, str, np.float32, np.float32, np.float32, np.float32, np.float32, str, str, str, str, str]
        )], dtype=object).T

