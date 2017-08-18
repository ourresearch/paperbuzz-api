from flask import make_response
from flask import request
from flask import abort
from flask import render_template
from flask import jsonify
from collections import defaultdict

import json
import os
import logging
import sys
import requests
import re

from app import app
from util import clean_doi



# try it at https://doi-events.herokuapp.com/10.1371/journal.pone.0000308

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
def index_endpoint():
    return jsonify({
        "version": "0.1",
        "name": "doi-events",
        "description": "wrapper for crossrev event data api.",
        "documentation_url": "none yet",
        "msg": "Don't panic"
    })


@app.route("/<path:doi>", methods=["GET"])
def get_doi_endpoint(doi):
    doi = clean_doi(doi)

    url = "http://query.eventdata.crossref.org/events?rows=10000&filter=from-collected-date:1990-01-01,until-collected-date:2099-01-01,obj-id:{}".format(
        doi
    )
    r = requests.get(url)
    data = r.json()
    total_results = data["message"]["total-results"]
    events = data["message"]["events"]
    event_counts = defaultdict(int)
    event_summary = defaultdict(list)
    for event in events:
        source = event["source_id"]
        event_counts[source] += 1
        try:
            author_url = event["subj"]["author"]["url"]
        except KeyError:
            author_url = None
        event_summary[source].append({
            "url": event["subj_id"],
            "author": author_url,
            "timestamp": event["occurred_at"]
        })

    response = {
        "doi": doi,
        "total_results": total_results,
        "event_counts": event_counts,
        "event_summary": event_summary
    }
    return jsonify(response)



@app.route("/event/<path:event_id>", methods=["GET"])
def get_event_endpoint(event_id):
    response = {
        "event_id": event_id
    }
    return jsonify(response)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)

















