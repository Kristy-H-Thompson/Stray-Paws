
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request
import json, requests
from datetime import datetime
from random import randint
from numpy.random import shuffle, seed
import mysql, mysql.connector
#from dogtime import DogTime
import os
from dotenv import load_dotenv
#project_folder = os.path.expanduser('***')  [commented out for security reasons]
# load_dotenv(os.path.join(***)) [commented out for security reasons]

app = Flask(__name__)


def get_db_connection():
    cnx = mysql.connector.connect(
      #host="***", [commented out for security reasons]
      #user="***",[commented out for security reasons]
      #password=os.getenv("***"),[commented out for security reasons]
      #database="***")[commented out for security reasons]
    return cnx

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM animal WHERE (status LIKE "Available%" || status LIKE "Fospice" || status LIKE "Pending" || status LIKE "%(adoptable)%") ORDER BY RAND() LIMIT 5;')
    response = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("home.html", featured=response)

@app.route('/about')
def about():
    def getEventsFromShelterluv():
        api_key = os.getenv("***") #[commented out for security reasons]
        response = requests.get('https://www.shelterluv.com/api/v1/events', headers={'***': api_key}).json()
        return response

    def getAnimalsFromShelterluv():
        api_key = os.getenv("***") #[commented out for security reasons]
        response = requests.get('https://www.shelterluv.com/api/v1/animals', headers={'***': api_key}).json() #[commented out for security reasons]
        return response

    response = getEventsFromShelterluv()
    all_animals = getAnimalsFromShelterluv()['animals']
    results = {'total_adopted':0, 'dog_intake':0, 'cat_intake':0}
    res_ids = []
    results_last_year = {'total_adopted':0, 'dog_intake':0, 'cat_intake':0}
    last_ids = []
    for animal in response['events']:
        try:
            if "Outcome.Adoption" in animal['Type']:
                if datetime.fromtimestamp(int(animal['Time'])).year == datetime.now().year:
                    results['total_adopted'] += 1
                    res_ids.append(animal['AssociatedRecords'][0]['Id'])
                elif datetime.fromtimestamp(int(animal['Time'])).year == datetime.now().year -1:
                    results_last_year['total_adopted'] += 1
                    res_ids.append(animal['AssociatedRecords'][0]['Id'])
            if "Intake" in animal['Type'] and not "FosterReturn" in animal['Type']:
                if datetime.fromtimestamp(int(animal['Time'])).year == datetime.now().year:
                    #results['dog_intake'] += 1
                    last_ids.append(animal['AssociatedRecords'][0]['Id'])
                elif datetime.fromtimestamp(int(animal['Time'])).year == datetime.now().year -1:
                    #results_last_year['dog_intake'] += 1
                    last_ids.append(animal['AssociatedRecords'][0]['Id'])
        except:
            print("COULD NOT CHECK TYPE OF ANIMAL:", animal)

    for animal in all_animals:
        for rid in res_ids:
            if rid == animal['Internal-ID']:
                if animal['Type'] == "Dog":
                    results['dog_intake'] += 1
                elif animal['Type'] == "Cat":
                    results['cat_intake'] += 1
                continue
        for rid in last_ids:
            if rid == animal['Internal-ID']:
                if animal['Type'] == "Dog":
                    results_last_year['dog_intake'] += 1
                elif animal['Type'] == "Cat":
                    results_last_year['cat_intake'] += 1
                continue

    print("animals adopted this year", results)
    print("animals adopted last year", results_last_year)
    return render_template("about.html", this_year=results, last_year=results_last_year)



@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/donate')
def donate():
    return render_template("donate.html")


@app.route('/gallery')
def gallery():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM animal WHERE (status LIKE "Available%" || status LIKE "Fospice" || status LIKE "Pending" || status LIKE "%(adoptable)%") ORDER BY RAND() LIMIT 20;')
    response = cursor.fetchall()

    for idx, animal in enumerate(response):
        cursor.execute("SELECT * FROM photos WHERE animal_id = %s", ([animal['id']]))
        photos = cursor.fetchall()
        if len(photos) >= 1:
            animal['Photos'] = photos
        else:
            response.pop(idx)

    return render_template("gallery.html", animals=response)

@app.route('/store')
def store():
    return render_template("store.html")

@app.route('/news')
def news():
    return render_template("news.html")

@app.route('/events')
def events():
    return render_template("events.html")

@app.route('/sponsorship')
def sponsorship():
    return render_template("sponsorship.html")

@app.route('/forms')
def forms():
    return render_template("forms.html")

@app.route('/animals', methods=('GET', 'POST'))
def animals():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM animal WHERE type = "Dog" && (status LIKE "Available%" || status LIKE "Pending" || status LIKE "%(adoptable)%") ORDER BY RAND();')
    doglist = cursor.fetchall()
    cursor.execute('SELECT * FROM animal WHERE type = "Cat" && (status LIKE "Available%" || status LIKE "Pending" || status LIKE "%(adoptable)%") ORDER BY RAND();')
    catlist = cursor.fetchall()


    if request.method == "POST":
        searchterm = request.form.get('search', '')
        cat_match = request.form.get('good-with-cats', False)
        dog_match = request.form.get('good-with-dogs', False)
        kid_match = request.form.get('good-with-kids', False)
        print(cat_match, dog_match, kid_match)

        def filterResponse(response):
            r = []
            for animal in response:
                if animal not in r:
                    cursor.execute("SELECT * FROM attributes WHERE animal_id = %s", ([animal['id']]))
                    attributelist = cursor.fetchall()
                    for term in searchterm.split(' '):
                        if term in animal['name']:# or term in animal['sex'] or term in animal['size'] or term in animal['breed'] or term in animal['color'] or term in animal['description']:
                            if cat_match or dog_match or kid_match:
                                attributes = []
                                for attribute in attributelist:
                                    attributes.append(attribute['attribute_name'])
                                if cat_match and dog_match and kid_match:
                                    if "Good with Cats" in attributes and "Good with Dogs" in attributes and "Good with Kids" in attributes:
                                        r.append(animal)
                                elif cat_match and dog_match:
                                    if "Good with Cats" in attributes and "Good with Dogs" in attributes:
                                        r.append(animal)
                                elif cat_match and kid_match:
                                    if "Good with Cats" in attributes and "Good with Kids" in attributes:
                                        r.append(animal)
                                elif dog_match and kid_match:
                                    if "Good with Dogs" in attributes and "Good with Kids" in attributes:
                                        r.append(animal)
                                elif cat_match:
                                    if "Good with Cats" in attributes:
                                        r.append(animal)
                                elif dog_match:
                                    if "Good with Dogs" in attributes:
                                        r.append(animal)
                                elif kid_match:
                                    if "Good with Kids" in attributes:
                                        r.append(animal)
                            else:
                                r.append(animal)
            return r

        doglist = filterResponse(doglist)
        catlist = filterResponse(catlist)
        cursor.close()
        conn.close()


    return render_template("animals.html", dogs=doglist[:5], cats=catlist[:5])

from flask_paginate import Pagination, get_page_parameter


@app.route('/doglist', methods=("GET", "POST"))
def doglist():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM animal WHERE type = "Dog" && (status LIKE "Available%" || status LIKE "Pending" || status LIKE "%(adoptable)%");')
    doglist = cursor.fetchall()

    search = False
    q = request.args.get('q')
    if q:
        search = True

    per_page = 20
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = (page - 1) * per_page

    response = doglist[offset:]
    total_count = len(doglist)

    if request.method == "POST":
        searchterm = request.form.get('search', '')
        cat_match = request.form.get('good-with-cats', False)
        dog_match = request.form.get('good-with-dogs', False)
        kid_match = request.form.get('good-with-kids', False)
        print(cat_match, dog_match, kid_match)

        def filterResponse(response):
            r = []
            for animal in response:
                if animal not in r:
                    cursor.execute("SELECT * FROM attributes WHERE animal_id = %s", ([animal['id']]))
                    attributelist = cursor.fetchall()
                    for term in searchterm.split(' '):
                        if term in animal['name']:# or term in animal['sex'] or term in animal['size'] or term in animal['breed'] or term in animal['color'] or term in animal['description']:
                            if cat_match or dog_match or kid_match:
                                attributes = []
                                for attribute in attributelist:
                                    attributes.append(attribute['attribute_name'])
                                if cat_match and dog_match and kid_match:
                                    if "Good with Cats" in attributes and "Good with Dogs" in attributes and "Good with Kids" in attributes:
                                        r.append(animal)
                                elif cat_match and dog_match:
                                    if "Good with Cats" in attributes and "Good with Dogs" in attributes:
                                        r.append(animal)
                                elif cat_match and kid_match:
                                    if "Good with Cats" in attributes and "Good with Kids" in attributes:
                                        r.append(animal)
                                elif dog_match and kid_match:
                                    if "Good with Dogs" in attributes and "Good with Kids" in attributes:
                                        r.append(animal)
                                elif cat_match:
                                    if "Good with Cats" in attributes:
                                        r.append(animal)
                                elif dog_match:
                                    if "Good with Dogs" in attributes:
                                        r.append(animal)
                                elif kid_match:
                                    if "Good with Kids" in attributes:
                                        r.append(animal)
                            else:
                                r.append(animal)
            return r

        response = filterResponse(response)

    shuffle(response)
    response = response[:per_page]

    pagination = Pagination(page=page, per_page=per_page, total=int(total_count), search=search, record_name='dogs')

    return render_template('doglist.html',
                           animals=response,
                           pagination=pagination,
                           page_title = "Adoptable Dogs",
                           )

@app.route('/catlist', methods=("GET", "POST"))
def catlist():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM animal WHERE type = "Cat" && (status LIKE "Available%" || status LIKE "Pending" || status LIKE "%(adoptable)%");')
    catlist = cursor.fetchall()

    search = False
    q = request.args.get('q')
    if q:
        search = True

    per_page = 20
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = (page - 1) * per_page

    response = catlist[offset:]
    total_count = len(catlist)

    if request.method == "POST":
        searchterm = request.form.get('search', '')
        cat_match = request.form.get('good-with-cats', False)
        dog_match = request.form.get('good-with-dogs', False)
        kid_match = request.form.get('good-with-kids', False)
        print(cat_match, dog_match, kid_match)

        def filterResponse(response):
            r = []
            for animal in response:
                if animal not in r:
                    cursor.execute("SELECT * FROM attributes WHERE animal_id = %s", ([animal['id']]))
                    attributelist = cursor.fetchall()
                    for term in searchterm.split(' '):
                        if term in animal['name']:# or term in animal['sex'] or term in animal['size'] or term in animal['breed'] or term in animal['color'] or term in animal['description']:
                            if cat_match or dog_match or kid_match:
                                attributes = []
                                for attribute in attributelist:
                                    attributes.append(attribute['attribute_name'])
                                if cat_match and dog_match and kid_match:
                                    if "Good with Cats" in attributes and "Good with Dogs" in attributes and "Good with Kids" in attributes:
                                        r.append(animal)
                                elif cat_match and dog_match:
                                    if "Good with Cats" in attributes and "Good with Dogs" in attributes:
                                        r.append(animal)
                                elif cat_match and kid_match:
                                    if "Good with Cats" in attributes and "Good with Kids" in attributes:
                                        r.append(animal)
                                elif dog_match and kid_match:
                                    if "Good with Dogs" in attributes and "Good with Kids" in attributes:
                                        r.append(animal)
                                elif cat_match:
                                    if "Good with Cats" in attributes:
                                        r.append(animal)
                                elif dog_match:
                                    if "Good with Dogs" in attributes:
                                        r.append(animal)
                                elif kid_match:
                                    if "Good with Kids" in attributes:
                                        r.append(animal)
                            else:
                                r.append(animal)
            return r

        response = filterResponse(response)

    response = response[:per_page]

    shuffle(response)

    pagination = Pagination(page=page, per_page=per_page, total=int(total_count), search=search, record_name='cats')

    return render_template('doglist.html',
                           animals=response,
                           pagination=pagination,
                           page_title = "Adoptable Cats",
                           )

@app.route('/fosters', methods=("GET", "POST"))
def fosters():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM animal WHERE (status LIKE "%Need Foster%");')
    catlist = cursor.fetchall()

    search = False
    q = request.args.get('q')
    if q:
        search = True

    per_page = 20
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = (page - 1) * per_page

    response = catlist[offset:]
    total_count = len(catlist)

    if request.method == "POST":
        searchterm = request.form.get('search', '')
        cat_match = request.form.get('good-with-cats', False)
        dog_match = request.form.get('good-with-dogs', False)
        kid_match = request.form.get('good-with-kids', False)
        print(cat_match, dog_match, kid_match)

        def filterResponse(response):
            r = []
            for animal in response:
                if animal not in r:
                    cursor.execute("SELECT * FROM attributes WHERE animal_id = %s", ([animal['id']]))
                    attributelist = cursor.fetchall()
                    for term in searchterm.split(' '):
                        if term in animal['name']:# or term in animal['sex'] or term in animal['size'] or term in animal['breed'] or term in animal['color'] or term in animal['description']:
                            if cat_match or dog_match or kid_match:
                                attributes = []
                                for attribute in attributelist:
                                    attributes.append(attribute['attribute_name'])
                                if cat_match and dog_match and kid_match:
                                    if "Good with Cats" in attributes and "Good with Dogs" in attributes and "Good with Kids" in attributes:
                                        r.append(animal)
                                elif cat_match and dog_match:
                                    if "Good with Cats" in attributes and "Good with Dogs" in attributes:
                                        r.append(animal)
                                elif cat_match and kid_match:
                                    if "Good with Cats" in attributes and "Good with Kids" in attributes:
                                        r.append(animal)
                                elif dog_match and kid_match:
                                    if "Good with Dogs" in attributes and "Good with Kids" in attributes:
                                        r.append(animal)
                                elif cat_match:
                                    if "Good with Cats" in attributes:
                                        r.append(animal)
                                elif dog_match:
                                    if "Good with Dogs" in attributes:
                                        r.append(animal)
                                elif kid_match:
                                    if "Good with Kids" in attributes:
                                        r.append(animal)
                            else:
                                r.append(animal)
            return r

        response = filterResponse(response)

    response = response[:per_page]

    shuffle(response)

    pagination = Pagination(page=page, per_page=per_page, total=int(total_count), search=search, record_name='animals')

    return render_template('doglist.html',
                           animals=response,
                           pagination=pagination,
                           page_title = "Animals in Need of Foster",
                           )


@app.route('/success')
def success():
    def getAllAnimalsFromShelterluv():
        api_key = os.getenv("API_KEY")
        response = requests.get('https://www.shelterluv.com/api/v1/animals?type=publishable', headers={'X-API-Key': api_key}).json()
        return response

    response = getAllAnimalsFromShelterluv()
    results = []
    for animal in response['animals']:
        try:
            if "Healthy In Home" in animal['Status']:
                results.append(animal)
        except:
            print("COULD NOT CHECK TYPE OF ANIMAL:", animal)

    return render_template("success.html", stories=results[:5])

@app.route('/adoption')
def adoption():
    return render_template("adoption.html")


@app.route('/information/<int:animal_id>')
def information(animal_id):
    animal = get_animal(animal_id)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if animal['type'] != "Dog" or animal['breed'] == "None" or type(animal['breed']) == None or "Mixed" in animal['breed']:
            breed_link = animal['breed']
        elif "," in animal['breed'] or "/" in animal['breed']:
            if "Terrier" in animal['breed'] or "Bulldog" in animal['breed'] or "Siberian" in animal['breed']:
                try:
                    breeds = []
                    breeds_initial = animal['breed'].split(", ")
                    for breed in breeds_initial:
                        breeds += breed.split("/ ")
                except:
                    try:
                        breeds = animal['breed'].split("/ ")
                    except:
                        breeds = animal['breed'].split(", ")
                breed_link = "<a href='https://dogtime.com/dog-breeds/" + breeds[1].replace(" ", "-") + '-' + breeds[0].replace(" ", "-") + "'>" + animal['breed'] + "</a> "
            else:
                breed_link = ""
                breeds = []
                breeds_initial = animal['breed'].split(", ")
                for breed in breeds_initial:
                    breeds += breed.split("/ ")
                for breed in breeds:
                    breed_link += "<a href='https://dogtime.com/dog-breeds/" + breed.replace(" ", "-") + "'>" + breed + "</a> "
        else:
            breed_link = "<a href='https://dogtime.com/dog-breeds/" + animal['breed'].replace(" ", "-") + "'>" + animal['breed'] + "</a>"
    except:
        breed_link = animal['breed']
    cursor.execute("SELECT * FROM fees WHERE id = %s", ([animal_id]))
    fees = cursor.fetchall()
    if len(fees) > 0:
        adoptionfee = fees[0]['name'] + " - $" + fees[0]['price']
    else:
        adoptionfee = "Please contact Stray Paws Rescue for the adoption fee."
    cursor.execute("SELECT * FROM attributes WHERE animal_id = %s", ([animal_id]))
    attributes = cursor.fetchall()
    cursor.execute("SELECT * FROM videos WHERE animal_id = %s", ([animal_id]))
    videos = cursor.fetchall()
    cursor.execute("SELECT * FROM photos WHERE animal_id = %s", ([animal_id]))
    photos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("information.html", animal=animal, breed=breed_link, adoptionfee=adoptionfee, attributes=attributes, photos=photos, videos=videos)

""" DOGTIME INTEGRATION (NOT IN USE)
@app.route('/information/<int:animal_id>')
def information(animal_id):
    dog = get_animal(animal_id)
    try:
        dogtime_breed = get_dogtime_breed(dog['Breed'])
    except:
        dogtime_breed = "none"
    print(dogtime_breed)
    return render_template("information.html", animal=dog, breed=dogtime_breed)
"""

def get_animal(animal_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM animal WHERE id = %s', ([animal_id]))
    response = cursor.fetchall()[0]
    cursor.close()
    conn.close()
    return response

"""
def get_dogtime_breed(dog_breed):
    D = DogTime(data_dir='data/')
    return D.get_breed_details(dog_breed)
"""

@app.route('/test', methods=("GET", "POST"))
def test():
    return render_template("test.html")



@app.route('/testtwo', methods=("GET", "POST"))
def testtwo():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM animal WHERE (status LIKE "%Need Foster%");')
    catlist = cursor.fetchall()

    search = False
    q = request.args.get('q')
    if q:
        search = True

    per_page = 20
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = (page - 1) * per_page

    response = catlist[offset:]
    total_count = len(catlist)

    if request.method == "POST":
        searchterm = request.form.get('search', '')
        cat_match = request.form.get('good-with-cats', False)
        dog_match = request.form.get('good-with-dogs', False)
        kid_match = request.form.get('good-with-kids', False)
        print(cat_match, dog_match, kid_match)

        def filterResponse(response):
            r = []
            for animal in response:
                if animal not in r:
                    cursor.execute("SELECT * FROM attributes WHERE animal_id = %s", ([animal['id']]))
                    attributelist = cursor.fetchall()
                    for term in searchterm.split(' '):
                        if term in animal['name']:# or term in animal['sex'] or term in animal['size'] or term in animal['breed'] or term in animal['color'] or term in animal['description']:
                            if cat_match or dog_match or kid_match:
                                attributes = []
                                for attribute in attributelist:
                                    attributes.append(attribute['attribute_name'])
                                if cat_match and dog_match and kid_match:
                                    if "Good with Cats" in attributes and "Good with Dogs" in attributes and "Good with Kids" in attributes:
                                        r.append(animal)
                                elif cat_match and dog_match:
                                    if "Good with Cats" in attributes and "Good with Dogs" in attributes:
                                        r.append(animal)
                                elif cat_match and kid_match:
                                    if "Good with Cats" in attributes and "Good with Kids" in attributes:
                                        r.append(animal)
                                elif dog_match and kid_match:
                                    if "Good with Dogs" in attributes and "Good with Kids" in attributes:
                                        r.append(animal)
                                elif cat_match:
                                    if "Good with Cats" in attributes:
                                        r.append(animal)
                                elif dog_match:
                                    if "Good with Dogs" in attributes:
                                        r.append(animal)
                                elif kid_match:
                                    if "Good with Kids" in attributes:
                                        r.append(animal)
                            else:
                                r.append(animal)
            return r

        response = filterResponse(response)

    response = response[:per_page]

    shuffle(response)

    pagination = Pagination(page=page, per_page=per_page, total=int(total_count), search=search, record_name='animals')

    return render_template('testlist.html',
                           animals=response,
                           pagination=pagination,
                           page_title = "Animals in Need of Foster",
                           )


