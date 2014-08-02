import os
from sha import sha
import json
from Queue import Queue
from datetime import datetime

from flask import Flask
from flask import request
from flask import render_template
from flask import url_for
from flask import g

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import requests

from divideandconquer.models import Base, User, Response, JobQueue

app = Flask(__name__)
engine = create_engine(os.environ['DATABASE_URL'])
Base.metadata.create_all(engine) 
sessionFactory = sessionmaker(engine)
q = Queue()

def get_from_db(key):
    session = sessionFactory()
    query = session.query(Response).filter(Response.json_hash==key)
    try:
        query_response = query.one()
    except:
        print 'Error: key not found!' + str(key)
    try:
        response = json.loads(query_response.json)
    except:
        print 'Error: json invalid!' + str(json_response)
    return response

def put_jsons_in_db(jsons):
    session = sessionFactory()
    for value in jsons:
        jvalue = json.dumps(value)
        key = sha(jvalue).hexdigest() + str(datetime.now())
        push_to_queue(key)
        # is_spam is a trinary value
        # 1 is true
        # 2 is false
        # 3 is unknown
        data = Response(json_hash=key, is_spam=3, json=jvalue)
        session.add(data)
    session.commit()

def update_spam_status(key, status):
    session = sessionFactory()
    query = session.query(Response).filter(Response.json_hash==key)
    try:
        query_response = query.one()
        query_response.is_spam = status
        session.add(query_response)
    except:
        print 'Error: key not found!' + str(key)
    session.commit()

def pop_from_queue():
    return q.get()

def push_to_queue(key):
    q.put(key)

def queue_is_empty():
    return q.empty()

@app.route('/', methods=['GET', 'POST'])
def classify():
    if queue_is_empty():
        refillQueue()
    if request.method == 'POST':
        #respon = get_from_db(request.form['id'])
        #if jresp == None:
        #    print 'Error: json data not found'
        #    return show_message()
        #resp = json.loads(jresp)
        if request.form.get('spam', None):
            update_spam_status(request.form['id'], 1)
        else:
            update_spam_status(request.form['id'], 0)
    return show_message()


def show_message():
    responseId = pop_from_queue()
    response = get_from_db(responseId)
    return render_template('classify.html', description=response['description'],
        happy=response['happy'], id=responseId)

def dump_to_file():
    fout = open('out.json', 'w')
    json.dump(store, fout)

def refillQueue():
    url = "https://input.mozilla.org/api/v1/feedback/?locales=en-US"
    r = requests.get(url)
    jr = r.json()
    put_jsons_in_db(jr['results'])

def refill_queue_from_db():
    session = sessionFactory()
    query = session.query(Response).filter(Response.is_spam==3)
    query_response = query.all()
    for resp in query_response:
        push_to_queue(resp.json_hash)
    session.add(query_response)
    session.commit()


#refill_queue_from_db()
if __name__ == '__main__':
    print 'app running'
    app.run(debug=True, port=33507)
