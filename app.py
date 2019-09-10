from flask import Flask, render_template, url_for, request, redirect, json
from models import *
import time

app = Flask(__name__)
db = Database()
print(db.create_table('event', 'post'))

# for i in db.return_events('event'):
# 	print(db.return_child_posts('event', i[0], 'post'))

# routes for pages 
@app.route('/')
def index():
	return redirect('/home')

@app.route('/home', methods=['GET', 'POST'])
def home():
	data = {
		"db":db,
		"all":db.return_events('event'),
		"len":len,
	}
	return render_template('index.html', **data)

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/post')
def post():
	return render_template('post.html')

@app.route('/search', methods=['GET','POST'])
def search():
	data = {
		"len":len,
		"all":''
	}
	if request.method == 'POST':
		search = request.form.get("search")
		data['all'] = db.search_event('event', search)

	return render_template('search.html', **data)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
	messages = {
		"created":''
	}
	if request.method == 'POST':
		name = request.form.get("event_name")
		date = request.form.get("event_date")
		desc = request.form.get("event_desc")
		loc = request.form.get("event_location")
		price = request.form.get("price")

            # create_event(self, table_name, event_name, event_date, event_desc, event_posts=''):
		if db.create_event('event', name, date, desc, loc, price):
			messages["created"] = "Added event successfully"
		else:
			messages["created"] = "Error in adding event"
		return redirect('/')
	return render_template('upload.html')

@app.route('/contact')
def contact():
	return render_template('contact.html')

@app.route('/event/<event_id>', methods=['GET', 'POST'])
def event(event_id):
	#print(event_id)
	data = {
		"db": db,
		"event": db.return_events('event', False, event_id),
		"len":len,
		"child_posts":[db.return_child_posts('event', event_id, 'post')],
		"msg":''
	} 
	if request.method == 'POST':
		writer = request.form.get('name')
		body = request.form.get('body')
		rating = float(request.form.get('rating'))
		#print(db.create_post('post', writer, body, event_id, datetime.datetime.today(), 'event', rating))
		if db.create_post('post', writer, body, event_id, datetime.datetime.today(), 'event', rating):
			data["msg"] = "Successfully added post"
		else:
			data["msg"] = "Error in adding post"
		#time.sleep(1)
		return redirect(f'/event/{event_id}')
	#print(db.create_post('post', 'Josh', 'Hated this event!!', f'{event_id}', datetime.datetime.today(), 'event', 1.9))
	#print(data['child_posts'])

	return render_template('event.html', **data)

app.run(debug=True)