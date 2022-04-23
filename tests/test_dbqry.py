import os
from datetime import datetime

from aisdb import DBQuery, data_dir, sqlfcn_callbacks

db = os.path.join(data_dir, 'test1.db')
start = datetime(2020, 9, 1)
end = datetime(2020, 10, 1)


def cleanup():
    if os.path.isfile(db):
        os.remove(db)


def test_query_emptytable():
    q = DBQuery(
        start=start,
        end=end,
        callback=sqlfcn_callbacks.in_timerange_validmmsi,
    )
    q.check_idx(dbpath=db)
    _rows = q.run_qry(dbpath=db)
    cleanup()