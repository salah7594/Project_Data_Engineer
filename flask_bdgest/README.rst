flask_bdgest
============

Running run.py launches the web application. Inside the app folder:

- views.py controls the routes, how the data is processed and which templates are rendered
- forms.py defines the structure of each form, i.e. the fields, their labels, their type

Inside the templates folder:

- macros.html contains the jinja macros which render the forms, tables of results and information cards
- dictionaries.html contains some variables so that they do not need to be redefined at many places
- base.html is the base template for all pages of the web application
- index.html defines the homepage and its three forms
- author.html, series.html and comic.html define the result pages for each author, series and comic respectively
- author_id.html defines the page of an author in particular
- series_id.html defines the page of a series in particular
- comic_id.html defines the page of a comic

The static folder contains the CSS and JS libraries responsible for the appearance and mobile responsivity of the web app.
