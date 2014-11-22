from bottle import route, run, template, get, request, redirect, app, hook
import operator
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from apiclient.errors import HttpError
from apiclient.discovery import build
import httplib2
from beaker.middleware import SessionMiddleware

@route('/')
def index():
	return("templates/index.html")

@route('/result', method=['GET'])
def result():
	word_search = query_word_db(word, max=10)


@error(404)
def error404(error):
	return("templates/error404.html")
