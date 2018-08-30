=============
scrapy_bdgest
=============

Website: `bdgest <https://www.bdgest.com>`_

What is scraped?
----------------
Authors, series and comics.

But what exactly?
-----------------
Authors:

* author id (mandatory)
* url
* first name
* last name
* nickname
* country
* personal web page
* birth date
* death date
* image

Series:

* series id (mandatory)
* author id
* url
* name
* genre
* status
* number of volumes
* list of volume ids
* origin (country or continent)
* language
* description

Comics:

* comic id (mandatory)
* series id
* author id
* title
* volume number
* scenario
* illustration
* coloring
* legal deposit
* editor
* collection
* format
* ISBN (International Standard Book Number)
* number of pages
* image
* description

Storage
.......
MongoDB

Check the `pipelines.py <https://github.com/nicolasvo95/scrapy_bdgest/blob/master/bdgest/pipelines.py>`_ file for more details.

Commands
........
From the root of the project, execute the following command:

.. code-block:: bash

    > scrapy crawl authors

Inside the bdgest directory:

- items.py defines how each author, series and comic items are defined
- pipelines.py defines how each item is inserted to the Mongo database
- middlewares.py defines how the middleware extracts the response pages and how the spider does the actual scraping. In our case, it is left as it is.

Inside the spiders folder is the authors.py script which defines the spider, i.e.:

- the starting urls (every author from A to Z with the addition of names starting with special characters)
- the parse functions and ultimately the creation of the items which are then sent to the pipeline

N.B.: the spider as it is only retrieves 20 authors for each letter of the alphabet (+ special character).
If you wish to extract more data, feel free to modify or remove the slice at line 32 in the authors.py spider `script <https://github.com/nicolasvo95/OUAP-4314/blob/master/Evaluation/Projet/scrapy_bdgest/bdgest/spiders/authors.py>`_
