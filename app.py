import os
import json
import datetime
import urllib.parse
from flask import Flask, render_template, request, jsonify
import pymongo
import psycopg2
import pandas as pd

app = Flask(__name__, static_url_path='')

BINDINGS_ROOT = '/bindings'

def get_bndg_param(bdir, bparam):
    fname = (BINDINGS_ROOT + '/' + bdir + '/' + bparam)
    if os.path.exists(fname):
        with open(fname) as f:
            return f.readlines()[0]
    else:
        return None

atlasbndg = False
cbbndg = False

if os.path.exists(BINDINGS_ROOT):
    for bdir in os.listdir(BINDINGS_ROOT):
        btype = get_bndg_param(bdir, 'type')
        if btype == 'mongodb':
            atlashost = get_bndg_param(bdir, 'host')
            atlasusr = get_bndg_param(bdir, 'username')
            tmppwd = get_bndg_param(bdir, 'password')
            atlaspwd = urllib.parse.quote_plus(tmppwd)
            atlasdb = 'mystrk'
            atlasbndg = True
        elif btype == 'postgresql':
            cbhost = get_bndg_param(bdir, 'host')
            cbusr = get_bndg_param(bdir, 'username')
            cbpwd = get_bndg_param(bdir, 'password')
            cbdb = 'postgres'
            cbbndg = True

### Crunchy Bridge

if not cbbndg:
    cbhost = os.environ['PGHOST']
    cbusr = os.environ['PGUSER']
    cbpwd = os.environ['PGPASSWORD']
    cbdb = os.environ['PGDB']

cbconn = psycopg2.connect (
    host=cbhost, 
    database=cbdb,
    user=cbusr,
    password=cbpwd
    )

### Mongo Atlas

#if not atlasbndg:
atlashost = os.environ['ATLAS_HOST']
atlasusr = os.environ['ATLAS_USERNAME']
atlaspwd = urllib.parse.quote_plus(os.environ['ATLAS_PASSWORD'])
atlasdb = os.environ['ATLAS_DB']

mngconnstr = 'mongodb+srv://' + \
atlasusr + ':' + \
atlaspwd + '@' + \
atlashost + '/' + \
atlasdb + \
'?retryWrites=true&w=majority'

mngclient = pymongo.MongoClient(mngconnstr)
trkdb = mngclient.mystrk
trkcol = trkdb.tracks

### Google Maps

gmapskey = os.environ['GMAPS_KEY']

### Flask Routes

@app.route('/')
def hanndler_get_index():
    return render_template('index.html.jinja',
                           googlemapskey=gmapskey,
                           atlas=atlasbndg, cb=cbbndg)

@app.route('/events', methods=['GET'])
def handler_get_events():
    # return e.g. [{'title': 'Mys Rsvd', 'start': '2022-01-23'},
    #              {'title': 'Mys Rsvd', 'start': '2022-01-24'},
    #              {'title': 'Track', 'start': '2022-01-24'}]
    start = request.args.get('start')
    end = request.args.get('end')
    sqlstr = "SELECT DISTINCT res_date FROM reservations WHERE \
    CAST (res_date AS TIMESTAMP) >= \
    CAST ( '" + start + "' AS TIMESTAMP) AND \
    CAST (res_date AS TIMESTAMP) <= \
    CAST ( '" + end + "' AS TIMESTAMP)"
    resdates = pd.read_sql_query(sqlstr, cbconn)

    evlist = []

    for i in resdates.index:
        resdate = (str(resdates['res_date'][i])[0:10])
        evlist.append({'title': 'Mys Rsvd', 'start': resdate})

    strtdto = datetime.date.fromisoformat(start[0:10])
    enddto = datetime.date.fromisoformat(end[0:10])
    
    #trkdates = trkcol.find({'date': {'$eleMatch': {'$gte': strtdto,
    #                                             '$lte': enddto}}})

    trks = trkcol.find()
    for trk in trks:
        dtstr = trk.get('date')
        dto = datetime.date.fromisoformat(dtstr)
        if dto >= strtdto and dto <= enddto:
            evlist.append({'title': 'Track', 'start': dtstr})

    return jsonify(evlist)

@app.route('/track')
def hanndler_get_track():
    # return e.g. [["2021-12-09T10:01:45", "37.870490",
    #                                      "-122.498100"]
    #              ["2021-12-09T10:28:43", "37.870500",
    #                                      "-122.497900"]]
    dat = request.args.get('date')
    trk = trkcol.find_one({'date': dat})
    pts = trk.get('points')
    resstr = json.dumps(pts)
    return resstr

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
