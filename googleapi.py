from bottle import route, run, template, get, request, redirect
import operator
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from apiclient.errors import HttpError
from apiclient.discovery import build
import httplib2

ranking = {}

flow = OAuth2WebServerFlow(
	client_id="697082725785-rbo99p5bebnds8ugdud0t40jc224dl71.apps.googleusercontent.com",
	client_secret='bBXXPeCK6d8hlt0wPYie5jHx',
	redirect_uri="http://localhost:8080/oauth2callback",
	scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email'
	)

@route('/', 'GET')
def home():

	uri = flow.step1_get_authorize_url()
	redirect(str(uri))

@route('/oauth2callback', 'GET')
def init():
	credentials = flow.step2_exchange(request.query.get('code',''))
	
	http = httplib2.Http()
	http = credentials.authorize(http)
	# Get user email
	users_service = build('oauth2', 'v2', http=http)
	user_document = users_service.userinfo().get().execute()
	user_email = str(user_document['email'])
	
	print type(user_email)
	
	return user_email
