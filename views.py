from flask import make_response
from flask import request
from flask import abort
from flask import render_template
from flask import jsonify

import json
import os
import logging
import sys
import requests
import re

from app import app
from app import db
from util import clean_doi
from weekly_stats import WeeklyStats

from doi import Doi



# try it at https://paperbuzz-api.herokuapp.com/doi/10.1371/journal.pone.0000308

def json_dumper(obj):
    """
    if the obj has a to_dict() function we've implemented, uses it to get dict.
    from http://stackoverflow.com/a/28174796
    """
    try:
        return obj.to_dict()
    except AttributeError:
        return obj.__dict__


def json_resp(thing):
    json_str = json.dumps(thing, sort_keys=True, default=json_dumper, indent=4)

    if request.path.endswith(".json") and (os.getenv("FLASK_DEBUG", False) == "True"):
        print u"rendering output through debug_api.html template"
        resp = make_response(render_template(
            'debug_api.html',
            data=json_str))
        resp.mimetype = "text/html"
    else:
        resp = make_response(json_str, 200)
        resp.mimetype = "application/json"
    return resp


def abort_json(status_code, msg):
    body_dict = {
        "HTTP_status_code": status_code,
        "message": msg,
        "error": True
    }
    resp_string = json.dumps(body_dict, sort_keys=True, indent=4)
    resp = make_response(resp_string, status_code)
    resp.mimetype = "application/json"
    abort(resp)


@app.after_request
def after_request_stuff(resp):
    #support CORS
    resp.headers['Access-Control-Allow-Origin'] = "*"
    resp.headers['Access-Control-Allow-Methods'] = "POST, GET, OPTIONS, PUT, DELETE, PATCH"
    resp.headers['Access-Control-Allow-Headers'] = "origin, content-type, accept, x-requested-with"

    # without this jason's heroku local buffers forever
    sys.stdout.flush()

    return resp






# ENDPOINTS
#
######################################################################################


@app.route('/', methods=["GET"])
@app.route('/v0', methods=["GET"])
@app.route('/v0/', methods=["GET"])
def index_endpoint():
    return jsonify({
        "version": "0.1",
        "name": "paperbuzz-api",
        "description": "wrapper for crossrev event data api.",
        "documentation_url": "none yet",
        "msg": "Don't panic"
    })


papers_by_discipline = {
        "all": ["10.1080/01436597.2017.1369037", "10.1136/bmj.j4030", "10.7717/peerj.1262", "10.1038/549133a",
                "10.1038/s41564-017-0012-7"],
        "arts and humanities": ["10.1038/549158a", "10.1111/phpr.12438", "10.1002/ajpa.23308", "10.1038/541141a",
                                "10.1038/s41598-017-08106-7"],
        "brain and mind": ["10.1111/gbb.12373", "10.1038/s41562-017-0202-6", "10.1038/nn.4637", "10.3389/feduc.2017.00037",
                           "10.1038/nm.4397"],
        "business": ["10.7287/peerj.preprints.3210v1", "10.1257/aer.20160812", "10.1038/s41562-017-0191-5",
                     "10.1287/mnsc.2017.2800", "10.1257/aer.20150243", "10.1371/journal.pone.0025995"],
        "chemistry": ["10.1351/goldbook.c01034", "10.1038/s41467-017-00679-1", "10.1038/s41467-017-00950-5",
                      "10.1038/nchem.2850", "10.1038/nchem.2853"],
        "computing": ["10.1002/leap.1116", "10.1038/nature23461", "10.12688/f1000research.12037.1", "10.1002/leap.1118",
                      "10.1016/j.dsp.2017.07.023"],
        "engineering": ["10.1038/s41551-017-0127-4", "10.1038/s41467-017-00109-2", "10.1038/549026a", "10.1038/nmat4972",
                        "10.1038/nature23668"],
        "environment": ["10.1038/nature23878", "10.1038/nj7671-297a", "10.1038/nclimate3382", "10.1038/s41559-017-0305-5",
                        "10.1007/s10584-017-1978-0"],
        "health": ["10.1136/bmj.j4030", "10.1080/09581596.2017.1371844", "10.1136/bmj.j3961", "10.1056/nejmsa1702321",
                   "10.1056/nejmicm1611578"],
        "life science": ["10.7717/peerj.1262", "10.1038/549133a", "10.1038/s41564-017-0012-7", "10.1038/549146a",
                         "10.1038/nrg.2017.65"],
        "mathematics": ["10.1002/cncy.21915", "10.1103/physreve.96.032309", "10.1242/dev.153841",
                        "10.1103/physrevlett.119.108301", "10.1038/s41598-017-07712-9"],
        "physics and astronomy": ["10.1038/549143a", "10.1038/549149a", "10.1038/549131b", "10.1038/nphys4254",
                                  "10.1038/nature23879"],
        "social science": ["10.1080/01436597.2017.1369037", "10.1057/palcomms.2017.93", "10.1007/s13524-017-0611-1",
                           "10.1111/dar.12596", "10.1038/s41562-017-0195-1"]
    }

# of form /2017/week-32
@app.route("/v0/hot/2017/<week_string>", methods=["GET"])
def get_hot_week_endpoint(week_string):
    week_num = week_string.split("-")[1]
    response = []

    for facet_open in [True, None]:
        for facet_audience in ["academic", "public", None]:
            for facet_discipline in papers_by_discipline:
                display_discipline = facet_discipline
                if display_discipline == "all":
                    display_discipline = None
                doi_list = papers_by_discipline[facet_discipline]
                papers = db.session.query(WeeklyStats).filter(WeeklyStats.id.in_(doi_list)).all()
                for paper in papers[0:2]:
                    paper_dict = paper.to_dict_hotness()
                    paper_dict["open"] = facet_open
                    paper_dict["audience"] = facet_audience
                    paper_dict["topic"] = display_discipline
                    response.append(paper_dict)
    return jsonify({"list": response})




@app.route("/v0/doi/<path:doi>", methods=["GET"])
def get_doi_endpoint(doi):
    my_doi = Doi(clean_doi(doi))
    my_doi.get()
    return jsonify(my_doi.to_dict())



@app.route("/v0/event/<path:event_id>", methods=["GET"])
def get_event_endpoint(event_id):
    response = {
        "event_id": event_id
    }
    return jsonify(response)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)

















