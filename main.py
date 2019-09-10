from flask import Flask, render_template, url_for, request, redirect
from models import *
import datetime

app = Flask(__name__)

db = Database()

add = []

@app.template_filter('avg_rating')
def avg(ratings):
    add.append(ratings)
    return add
# routes
@app.route('/', methods=['GET', 'POST'])
def index():
    messages = {
        "message": "Imported models",
        "top_msg": "Remarks",
        "created": ""
    }
    if request.method == 'POST':
        if request.form.get("create") == "Create database tables":
            event = request.form.get("event_table_name")
            post = request.form.get("post_table_name")

            if db.create_table(event, post):
                messages["created"] = "Successfully created tables"
            else:
                messages["created"] = "Error in creating database tables"
        #print(request.form.get("event_desc"))
        if request.form.get("create") == "Create event":
            # event_name, event_date, event_desc
            name = request.form.get("event_name")
            date = request.form.get("event_date")
            desc = request.form.get("event_desc")
            loc = request.form.get("event_location")

            # create_event(self, table_name, event_name, event_date, event_desc, event_posts=''):
            if db.create_event('event', name, date, desc, loc):
                messages["created"] = "Added event successfully"
            else:
                messages["created"] = "Error in adding event"

    return render_template('index.html', **messages)

@app.route('/show', methods=['GET', 'POST'])
def show():
    #db.delete_event('Q5PM60', 'event', 'post')
    ret = [_[0] for _ in db.return_events('event')]
    all_events = {
        "all":db.return_events('event'),
        # "today": str(datetime.datetime.today().day)
        "msg":"",
        "allof": ret,
        "posts": [db.return_child_posts('event', _, 'post') for _ in ret],
        "ev":[],
        "ret":[],
        "db":db,
        "child_post":[],
        "rating":[]
    }
    
    events = all_events["posts"]
    for _ in events:
        for __ in _:
            #print(all_events['ev'],"lol")
            #print(__[4])
            all_events["ev"].append(__[4])
            break
            #print(__, 'fuck')
    for _ in all_events["ev"]:
        all_events['ret'].append(_)

    if request.method == 'POST':
        writer = request.form.get('writer')
        body = request.form.get('body')
        event = request.form.get('event')
        date = request.form.get('date')
        rating = float(request.form.get('rating'))
        if db.create_post('post', writer, body, event, date, 'event', rating):
            all_events["msg"] = "Successfully added post"
        else:
            all_events["msg"] = "Error in adding post"

        return redirect('/show')
    events.pop(-1)
    for _ in events:
        for __ in _:
            #print(__[4])
        #print(_)
            all_events["child_post"].append(db.return_child_post_ids('event', __[4], 'post'))
            break

    return render_template('show.html', **all_events)

@app.route('/posts', methods=['GET', 'POST'])
def posts():
    ret = [_[0] for _ in db.return_events('event')]
    all_posts = {
        "all": ret,
        "posts": [db.return_child_posts('event', _, 'post') for _ in ret],
        "ev":[],
        "ret":[],
        "db":db
    }
    # for _ in all_posts["all"]:
    #     posts = db.return_child_posts('event', _, 'post')
    #events = [_ for _ in all_posts["posts"]]
    events = all_posts["posts"]
    for _ in events:
        for __ in _:
            all_posts["ev"].append(__[4])
    for _ in all_posts["ev"]:
        all_posts['ret'].append(_)
        
    return render_template('post.html', **all_posts)

app.run(debug=True)