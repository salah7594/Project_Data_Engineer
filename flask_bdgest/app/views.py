from flask import render_template, request

from .forms import AuthorForm, SeriesForm, ComicForm

from app import app
from datetime import datetime
from pymongo import MongoClient

client = MongoClient("mongo")
db = client['bdgest']

def series_by_id(id):
    """
    Returns a series name based on its id.
    It happens that series name will not exist, in which case "N/A" is returned.

    Args:
        id: a series id

    Returns:
        document["name"]: the name of a series
    """
    document = db["series"].find_one({'_id': id})
    
    if document:
        return document["name"]
    else:
        return "N/A"

def author_by_id(id):
    """
    Returns an author's full name based on its id.

    Args:
        id: an author id

    Returns:
        document["name"]: the full name of an author
    """
    document = db["authors"].find_one({'_id': id})
    name = document["full_name"]
    return name

def table_comic(query):
    """
    Returns a list of comics. The name of the author and the series of a comic are added to the returned documents based on the ids.
    Only a few of the fields are kept for display: scenario, illustration, editor, legal_deposit.

    Args:
        query: a mongo query string

    Returns:
        list_document: a list of documents
    """
    list_document = []
    for document in query:
        document_updated = {"redirect_comic": [document["url"], document["title"]]}
        document_updated.update({"redirect_series": ["/series/{0}".format(document["series_id"]), series_by_id(document["series_id"])]})
        document_updated.update({"redirect_author": ["/author/{0}".format(document["author_id"]), author_by_id(document["author_id"])]})
        document_updated.update({"redirect_comic": ["/comic/{0}".format(document["_id"]), document["title"]]})
        document_updated.update({key: (document[key] if document.get(key) else "") for key in ("scenario", "illustration", "editor", "legal_deposit")})
        if document_updated.get("legal_deposit"): document_updated.update({"legal_deposit": "{:%m-%Y}".format(document["legal_deposit"])})
        list_document.append(document_updated)

    return list_document

def table_series(query):
    """
    Returns a list of series. The name of the author of the series is added to the returned documents based on the id.
    Only genre, origin and lang (language) are kept in the final documents to be displayed.

    Args:
        query: a mongo query string
    
    Returns:
        list_document: a list of documents
    """
    list_document = []
    for document in query:
        document_updated = {"redirect_series": ["/series/{0}".format(document["_id"]), document["name"]]}
        document_updated.update({"redirect_author": ["/author/{0}".format(document["author_id"]), author_by_id(document["author_id"])]})
        document_updated.update({key: (document[key] if document.get(key) else "") for key in ("genre", "origin", "lang")})
        list_document.append(document_updated)

    return list_document

def kardesh(query):
    """
    This function deals with queries across multiple collections. For example, for a comic with a specific author and/or series name.
    If the query has the keys author_name and/or series_name, an additional query parses the authors and/or series collections in order
    to retrieve the list of ids matching the authors and/or series name. This retrieve list is used as a condition for the initial query:
    the authors/series id must belong to the list of ids previously retrieved.

    Args:
        query: a mongo formatted query string

    Returns:
        query: the updated query with matching author and/or series ids
    """
    if query.get("author_name"):
        list_author_id = []
        fetch_name = query["author_name"]

        query_match = {}
        query_match.update({'$or': [{'last_name': {'$regex': "\\b" + fetch_name, '$options': 'i'}},
                                {'first_name': {'$regex': "\\b" + fetch_name, '$options': 'i'}},
                                {'nickname': {'$regex': "\\b" + fetch_name, '$options': 'i'}},
                                ]})
        for document in db["authors"].find(query_match):
            list_author_id.append(document["_id"])
        # author_name is removed from the keys because it does not appear in the series and comics collections
        query.pop("author_name")
        query.update({"author_id": {"$in": list_author_id}})
    
    if query.get("series_name"):
        list_series_id = []
        fetch_name = query["series_name"]

        query_match = {}
        query_match.update({"name": {'$regex': "\\b" + fetch_name.strip(), '$options': 'i'}})
        
        for document in db["series"].find(query_match):
            list_series_id.append(document["_id"])

        # series_name is removed because it does not exist in the comics collection
        query.pop("series_name")
        query.update({"series_id": {"$in": list_series_id}})
    
    return query

@app.route('/', methods=['GET', 'POST'])
def home():
    """
    The route for the home page. It displays three different forms, each redirecting to a differente route upon submission.

    Returns:
        render_template: the template is index.html each form is passed to the template.
    """

    author_form = AuthorForm()
    series_form = SeriesForm()
    comic_form = ComicForm()

    return render_template('index.html', author_form=author_form, series_form=series_form, comic_form=comic_form)

@app.route('/author', methods=['POST'])
def author():
    """
    The route for the author result page when the user submits a form for a query of the authors collection.
    A redirection to an author's specific page is proposed.

    Returns:
        render_template: the template page is author.html and the output contains first_name, last_name, nickname, birth_date and death_date.
        Birth_date and death_date are datetime variables which are formatted into day-month-year format.
        The page also includes a redirection to a specific author's page thanks to the redirect_author added to the returned document.
        This redirect_author is processed differently from the rest. It is further explained in the jinja template macros.html.
    """
    output = {}
    author_form = AuthorForm()
    if author_form.validate_on_submit():
        list_document = []

        fetch_name = request.form.get('name', None).strip()
        fetch_country = request.form.get('country', None).strip()

        mongo_formatted_string = {}

        if fetch_name: 
            mongo_formatted_string.update({'$or': [{'last_name': {'$regex': "\\b" + fetch_name, '$options': 'i'}},
                                        {'first_name': {'$regex': "\\b" + fetch_name, '$options': 'i'}},
                                        {'nickname': {'$regex': "\\b" + fetch_name, '$options': 'i'}},
                                        ]})
        if fetch_country:
            mongo_formatted_string.update({'country': {'$regex': "\\b" + fetch_country, '$options': 'i'}})

        if mongo_formatted_string:
            for document in db["authors"].find(mongo_formatted_string):
                document_updated = {"redirect_author": ["/author/{0}".format(document["_id"]), "Go."]}
                document_updated.update({key: (document[key] if document.get(key) else "") for key in ("first_name", "last_name", "nickname", "birth_date", "death_date")})
                if document_updated.get("death_date"): document_updated.update({"death_date": "{:%d-%m-%Y}".format(document["death_date"])})
                if document_updated.get("birth_date"): document_updated.update({"birth_date": "{:%d-%m-%Y}".format(document["birth_date"])})
                list_document.append(document_updated)
            output["list_document"] = list_document

    return render_template('author.html', output=output)


@app.route('/series', methods=['POST'])
def series():
    """
    The route for the series result page. Displays some of the series fields, its author's name.
    Both redirections to the author and series specific pages are possible.

    Returns:
        render_template: the template is series.html. The output information is specified in the table_series function (genre, origin and language).
    """
    output = {}
    series_form = SeriesForm()
    if series_form.validate_on_submit():
        dict_fetch = {}
        for x in ['name', 'genre', 'author_name', 'lang', 'origin', 'status']:
            dict_fetch[x] = request.form.get(x, None)

        mongo_formatted_string = {}
    
        for key, value in dict_fetch.items():
            if value:
                if key == 'status': mongo_formatted_string.update({key: int(value)})
                elif key == "author_name": mongo_formatted_string.update({key: value})
                else: mongo_formatted_string.update({key: {'$regex': "\\b" + value.strip(), '$options': 'i'}})
        
        if mongo_formatted_string:
            mongo_formatted_string = kardesh(mongo_formatted_string)
            output["list_document"] = table_series(db["series"].find(mongo_formatted_string))

    return render_template('series.html', output=output)

@app.route('/comic', methods=['POST'])
def comic():
    """
    The route for the comic result page. Displays the fields specified in the table_comic function.

    Returns:
        render_template: the template name is comic.html.
    """
    output = {}
    comic_form = ComicForm()
    if comic_form.validate_on_submit():
        dict_fetch = {}
        for x in ["title", "editor", "collection", "format", "isbn", "author_name", "series_name"]:
            dict_fetch[x] = request.form.get(x, None)

        mongo_formatted_string = {}

        for key, value in dict_fetch.items():
            if value:
                if key == "isbn": mongo_formatted_string.update({key: {'$regex': value, '$options': 'i'}})
                elif key == "author_name": mongo_formatted_string.update({key: value})
                elif key == "series_name": mongo_formatted_string.update({key: value})
                else: mongo_formatted_string.update({key: {'$regex': "\\b" + value.strip(), '$options': 'i'}})

        if mongo_formatted_string:
            mongo_formatted_string = kardesh(mongo_formatted_string)
            output["list_document"] = table_comic(db["comics"].find(mongo_formatted_string))

    return render_template('comic.html', output=output)

@app.route('/author/<author_id>')
def author_id(author_id):
    """
    The page specific to an author. It displays informations about the author, a visualization of his variety of series genres and their proportions.
    Also displays how many comics per year the author published. Displays a table with his series and another one with his comics.

    Args:
        author_id: an author's id

    Returns:
        return_template: the template file is author_id.html. The output dictionary contains the data aforementioned.
    """
    output = {}
    output["document"] = db["authors"].find_one({"_id": author_id})
    output["list_comic"] = table_comic(db["comics"].find({"author_id": author_id}))
    output["list_series"] = table_series(db["series"].find({"author_id": author_id}))
    
    # The aggregation function is specific to pymongo. It requires the definition of a whole pipeline of commands before.
    # The result of db.command is a dictionary. For our version of pymongo, the results were located in the cursor and then firstBatch.
    # However, other versions of pymongo and mongodb may not be compatible with this query.
    pipeline = [
        {"$match": {"author_id": author_id}},
        {"$group": {"_id":"$genre", "count":{"$sum":1}}}
    ]
    output["pie"] = db.command('aggregate', 'series', pipeline=pipeline, explain=False)["cursor"]["firstBatch"]

    pipeline = [
        {"$match": {"author_id": author_id}},
        {"$group": {"_id": {"$year": "$legal_deposit"}, "count":{"$sum":1}}},
        {"$sort": {"_id": 1}}
    ]
    aggregation_year_count = db.command('aggregate', 'comics', pipeline=pipeline, explain=False)["cursor"]["firstBatch"]
    output["legal_deposit"] = {"year": [year["_id"] for year in aggregation_year_count],
                               "count": [count["count"] for count in aggregation_year_count]}

    return render_template('author_id.html', output=output)

@app.route('/series/<series_id>')
def series_id(series_id):
    """
    The page specific to a series. It displays information about the series and the list of comics which belong to this series.

    Args:
        series_id: a series id

    Returns:
        render_template: the template file is called series_id.html. 
    """
    output = {}
    output["document"] = db["series"].find_one({"_id": series_id})
    output["document"].update({"author_name": author_by_id(output["document"]["author_id"])})
    output["list_comic"] = table_comic(db["comics"].find({"series_id": series_id}))

    return render_template('series_id.html', output=output)

@app.route('/comic/<comic_id>')
def comic_id(comic_id):
    """
    The page specific to a comic. It displays information about the comic.

    Args:
        series_id: a comic id

    Returns:
        render_template: the template file is called comic_id.html. 
    """
    output = {}
    output["document"] = db["comics"].find_one({"_id": comic_id})

    return render_template('comic_id.html', output=output)
