import json

from flask import Flask
from flask import request
from flask import render_template
from flask import url_for
from flask import g

import redis
import requests
app = Flask(__name__)
app.debug = True
store = {
    'queue': [],
}

@app.route('/', methods=['GET', 'POST'])
def classify():
    if len(store.get('queue')) == 0:
        refillQueue()
    if request.method == 'POST':
        jresp = store.get(request.form['id'])
        if jresp == None:
            print 'Error: json data not found'
            return show_message()
        resp = json.loads(jresp)
        if request.form.get('spam', None):
            resp['spam'] = True
        else:
            resp['spam'] = False
        jresp = json.dumps(resp)
        store[request.form['id']] =  jresp
    return show_message()


def show_message():
    responseId = store['queue'].pop()
    jsonResponse = store.get(responseId)
    response = json.loads(jsonResponse)
    return render_template('classify.html', description=response['description'],
        happy=response['happy'], id=responseId)

def dump_to_file():
    fout = open('out.json', 'w')
    json.dump(store, fout)

def refillQueue():
    dump_to_file()
    url = "https://input.mozilla.org/api/v1/feedback/?locales=en-US"
    r = requests.get(url)
    jr = r.json()
    for resp in jr['results']:
        store['queue'].append(resp['id'])
        store[resp['id']] =  json.dumps(resp)


if __name__ == '__main__':
    print 'app running'
    app.run(debug=True, port=33507)
