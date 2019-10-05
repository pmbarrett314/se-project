from flask import Flask
from flask import render_template
from flask import request
from google.cloud import datastore
import datetime

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

datastore_client = datastore.Client()

@app.route('/')
def hello():
    ip=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr).split(",")[0]
    entry=datastore.Entity(datastore_client.key('Entry'))
    entry.update({
            'ip': ip,
            'time':datetime.datetime.utcnow()
    })
    datastore_client.put(entry)
    return render_template('hello.html', ip=ip)

@app.route('/list')
def list_hits():
    query = datastore_client.query(kind='Entry')
    query.order = ['-time']
    entries = list(query.fetch())
    return render_template("list.html", entries=entries)

@app.route('/clear')
def clear_hits():
    query = datastore_client.query(kind='Entry')
    query.keys_only()
    entries = list(query.fetch())
    keys=[e.key for e in entries]
    count=len(keys)
    datastore_client.delete_multi(keys)
    return "Successfully deleted {} keys".format(count)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
