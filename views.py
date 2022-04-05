from datetime import datetime, timedelta
import json
import os
import random
import sys

from flask import abort, jsonify, make_response, render_template, request
from sqlalchemy import desc, func

from app import app, db
from doi import Doi
from event import CedEvent
from util import clean_doi, get_sql_answers
from weekly_stats import WeeklyStats

# try it at https://api.paperbuzz.org/v0/doi/10.1371/journal.pone.0000308


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
        print("rendering output through debug_api.html template")
        resp = make_response(render_template("debug_api.html", data=json_str))
        resp.mimetype = "text/html"
    else:
        resp = make_response(json_str, 200)
        resp.mimetype = "application/json"
    return resp


def abort_json(status_code, msg):
    body_dict = {"HTTP_status_code": status_code, "message": msg, "error": True}
    resp_string = json.dumps(body_dict, sort_keys=True, indent=4)
    resp = make_response(resp_string, status_code)
    resp.mimetype = "application/json"
    abort(resp)


@app.after_request
def after_request_stuff(resp):
    # support CORS
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers[
        "Access-Control-Allow-Methods"
    ] = "POST, GET, OPTIONS, PUT, DELETE, PATCH"
    resp.headers[
        "Access-Control-Allow-Headers"
    ] = "origin, content-type, accept, x-requested-with"

    # without this jason's heroku local buffers forever
    sys.stdout.flush()

    return resp


# ENDPOINTS
#
######################################################################################


@app.route("/", methods=["GET"])
@app.route("/v0", methods=["GET"])
@app.route("/v0/", methods=["GET"])
def index_endpoint():
    return jsonify(
        {
            "version": "0.1",
            "name": "paperbuzz-api",
            "description": "wrapper for crossrev event data api.",
            "documentation_url": "none yet",
            "msg": "Don't panic",
        }
    )


papers_by_discipline = {
    "arts and humanities": [
        "10.1038/549158a",
        "10.1111/phpr.12438",
        "10.1002/ajpa.23308",
        "10.1038/541141a",
        "10.1038/s41598-017-08106-7",
    ],
    "brain and mind": [
        "10.1111/gbb.12373",
        "10.1038/s41562-017-0202-6",
        "10.1038/nn.4637",
        "10.3389/feduc.2017.00037",
        "10.1038/nm.4397",
    ],
    "business": [
        "10.7287/peerj.preprints.3210v1",
        "10.1257/aer.20160812",
        "10.1038/s41562-017-0191-5",
        "10.1287/mnsc.2017.2800",
        "10.1257/aer.20150243",
        "10.1371/journal.pone.0025995",
    ],
    "chemistry": [
        "10.1351/goldbook.c01034",
        "10.1038/s41467-017-00679-1",
        "10.1038/s41467-017-00950-5",
        "10.1038/nchem.2850",
        "10.1038/nchem.2853",
    ],
    "computing": [
        "10.1002/leap.1116",
        "10.1038/nature23461",
        "10.12688/f1000research.12037.1",
        "10.1002/leap.1118",
        "10.1016/j.dsp.2017.07.023",
    ],
    "engineering": [
        "10.1038/s41551-017-0127-4",
        "10.1038/s41467-017-00109-2",
        "10.1038/549026a",
        "10.1038/nmat4972",
        "10.1038/nature23668",
    ],
    "environment": [
        "10.1038/nature23878",
        "10.1038/nj7671-297a",
        "10.1038/nclimate3382",
        "10.1038/s41559-017-0305-5",
        "10.1007/s10584-017-1978-0",
    ],
    "health": [
        "10.1136/bmj.j4030",
        "10.1080/09581596.2017.1371844",
        "10.1136/bmj.j3961",
        "10.1056/nejmsa1702321",
        "10.1056/nejmicm1611578",
    ],
    "life science": [
        "10.7717/peerj.1262",
        "10.1038/549133a",
        "10.1038/s41564-017-0012-7",
        "10.1038/549146a",
        "10.1038/nrg.2017.65",
    ],
    "mathematics": [
        "10.1002/cncy.21915",
        "10.1103/physreve.96.032309",
        "10.1242/dev.153841",
        "10.1103/physrevlett.119.108301",
        "10.1038/s41598-017-07712-9",
    ],
    "physics and astronomy": [
        "10.1038/549143a",
        "10.1038/549149a",
        "10.1038/549131b",
        "10.1038/nphys4254",
        "10.1038/nature23879",
    ],
    "social science": [
        "10.1080/01436597.2017.1369037",
        "10.1057/palcomms.2017.93",
        "10.1007/s13524-017-0611-1",
        "10.1111/dar.12596",
        "10.1038/s41562-017-0195-1",
    ],
}


# of form /2017/week-32
# @app.route("/v0/hot/2017/<week_string>", methods=["GET"])
# def get_hot_week_endpoint(week_string):
#     week_num = week_string.split("-")[1]
#     response_dict = {}
#
#     random.seed(42)
#     for facet_open in [True, None]:
#         if facet_open:
#             oa_where = "and is_open_access=true"
#         else:
#             oa_where = ""
#         for facet_audience in ["public", None]:
#             if facet_audience == "public":
#                 academic_where = "and ratio_academic_unpaywall_events <= 0.10"
#             else:
#                 academic_where = ""
#             query_template = """
#                     SELECT id
#                     FROM (SELECT id,
#                           rank() over (partition by main_discipline order by coalesce(num_twitter_events, 0)+coalesce(num_unpaywall_events, 0) desc nulls last) as rank
#                        FROM weekly_stats
#                        where num_unpaywall_events > 5
#                        {oa_where}
#                        {academic_where}
#                     ) t WHERE rank <= 3"""
#             query = query_template.format(
#                 oa_where=oa_where, academic_where=academic_where
#             )
#             doi_list = get_sql_answers(db, query)
#             papers = (
#                 db.session.query(WeeklyStats).filter(WeeklyStats.id.in_(doi_list)).all()
#             )
#
#             for paper in papers:
#                 if not paper.main_discipline or paper.main_discipline == "unspecified":
#                     continue
#
#                 paper_dict = paper.to_dict_hotness()
#                 paper_dict["sort_score"] = (
#                     paper.num_twitter_events + paper.num_unpaywall_events
#                 )
#
#                 # only save filters if they are restrictive
#                 paper_dict["filters"] = {}
#                 paper_dict["filters"]["topic"] = paper.main_discipline
#                 if facet_open:
#                     paper_dict["filters"]["open"] = paper.is_open_access
#                 if facet_audience:
#                     paper_dict["filters"]["audience"] = facet_audience
#                     if paper.ratio_academic_unpaywall_events:
#                         paper_dict["filters"]["public_percent"] = round(
#                             100 * (1 - paper.ratio_academic_unpaywall_events), 0
#                         )
#                     else:
#                         paper_dict["filters"]["public_percent"] = 100
#
#                 # dedup the papers, saving the most restrictive
#                 if paper.id in response_dict:
#                     if len(list(paper_dict["filters"].keys())) > (
#                         list(response_dict[paper.id]["filters"].keys())
#                     ):
#                         response_dict[paper.id] = paper_dict
#                 else:
#                     response_dict[paper.id] = paper_dict
#         response = list(response_dict.values())
#         response = sorted(response, key=lambda k: k["sort_score"], reverse=True)
#
#     return jsonify({"list": response})


@app.route("/v0/doi/<path:doi>", methods=["GET"])
def get_doi_endpoint(doi):
    my_doi = Doi(clean_doi(doi))
    if my_doi.is_cached_not_expired():
        # responses with many events are cached in the database
        response = my_doi.cached_response()
    else:
        my_doi.get()
        response = my_doi.to_dict()
        my_doi.save_to_cache(response)
    return jsonify(response)


@app.route("/v0/event/<path:event_id>", methods=["GET"])
def get_event_endpoint(event_id):
    response = {"event_id": event_id}
    return jsonify(response)


@app.route("/trending", methods=["GET"])
def trending():
    today = datetime.now()
    days_ago = today - timedelta(days=8)

    events = (
        db.session.query(CedEvent.doi, func.count(CedEvent.doi).label("total"))
        .group_by(CedEvent.doi)
        .filter(CedEvent.occurred_at >= days_ago)
        .order_by(desc("total"))
        .limit(10)
        .all()
    )
    root_url = "https://paperbuzz.org/details/{}"

    results = [
        {"url": root_url.format(event.doi), "count": event.total} for event in events
    ]
    return jsonify(results)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5009))
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
