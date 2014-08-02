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
r_server = redis.Redis("localhost")
print 'redis up'

@app.route('/', methods=['GET', 'POST'])
def classify():
    if request.method == 'POST':
        jresp = r_server.get(request.form['id'])
        resp = json.loads(jresp)
        if request.form.get('spam', None):
            resp['spam'] = True
        else:
            resp['spam'] = False
        jresp = json.dumps(resp)
        r_server.set(request.form['id'], jresp)
    if r_server.llen('queue') == 0:
        refillQueue()
    responseId = r_server.lpop('queue')
    jsonResponse = r_server.get(responseId)
    response = json.loads(jsonResponse)
    return render_template('classify.html', description=response['description'],
        happy=response['happy'], id=responseId)

def refillQueue():
    url = "https://input.mozilla.org/api/v1/feedback/?locales=en-US"
    r = requests.get(url)
    jr = r.json()
    for resp in jr['results']:
        r_server.lpush('queue', resp['id'])
        r_server.lpush('all', resp['id'])
        r_server.set(resp['id'], json.dumps(resp))


#if __name__ == '__main__':
#    app.run()
#    print 'app running'
