import json
from sha import sha
from datetime import datetime
from Queue import Queue
import requests

from flask import g

from divideandconquer import app 
from divideandconquer.models import Response
from divideandconquer import db

q = Queue()

def init_q():
    with app.app_context():
        if not hasattr(g, 'q'):
            g.q = Queue()

def refillQueue():
    url = "https://input.mozilla.org/api/v1/feedback/?locales=en-US"
    r = requests.get(url)
    jr = r.json()
    put_jsons_in_db(jr['results'])

def refill_queue_from_db():
    with app.app_context():
        session = g.sessionFactory()
    query = User.query.filter_by(is_spam=3)
    query_response = query.all()
    for resp in query_response:
        g.q.put(resp.json_hash)
    session.add(query_response)
    session.commit()


def put_jsons_in_db(jsons):
    for value in jsons:
        jvalue = json.dumps(value)
        key = sha(jvalue).hexdigest() + str(datetime.now())
        q.put(key)
        # is_spam is a trinary value
        # 1 is true
        # 2 is false
        # 3 is unknown
        data = Response(json_hash=key, is_spam=3, json=jvalue)
        db.session.add(data)
    db.session.commit()
