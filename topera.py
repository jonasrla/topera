from bottle import route, run, template, get, request, redirect
import operator
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from apiclient.errors import HttpError
from apiclient.discovery import build
import httplib2

# GOOGLE API CODE --------------------BEGINS-----------------
flow = OAuth2WebServerFlow(
	client_id="697082725785-rbo99p5bebnds8ugdud0t40jc224dl71.apps.googleusercontent.com",
	client_secret='bBXXPeCK6d8hlt0wPYie5jHx',
	redirect_uri="http://localhost:8080/oauth2callback",
	scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email'
	)

@route('/autenticate', 'GET')
def autenticate_1():
	uri = flow.step1_get_authorize_url()
	redirect(str(uri))

@route('/oauth2callback', 'GET')
def autenticate_2():
	credentials = flow.step2_exchange(request.query.get('code',''))
	
	http = httplib2.Http()
	http = credentials.authorize(http)
	# Get user email
	users_service = build('oauth2', 'v2', http=http)
	user_document = users_service.userinfo().get().execute()
	user_email = str(user_document['email'])
	
	print type(user_email)
	
	return user_email

#GOOGLE API CODE -------------------END----------------

ranking = {}

@get('/')
def init():
    return template("templates/index.html", ordered_word=get_top_20())

def word_counter(string):
    global ranking
    list_words = string.split(" ")
    result = {}
    for word in list_words:
        if word in result:
            result[word]+=1
            ranking[word]+=1
        if word not in result:    
            result[word]=1
            if word not in ranking:
                ranking[word]=1
            else:
                ranking[word]+=1
    print result
    return result

@route('/result', method=['GET'])
def show_result():
    print request.query.get('keywords','').strip()
    table_word_count = word_counter(request.query.get('keywords','').strip())
    return template("templates/result.html", table_word_count=table_word_count, ordered_word=get_top_20())

def get_top_20():
    global ranking
    ordered_words = sorted(ranking.items(), key=operator.itemgetter(1), reverse=True)[:20]
    return ordered_words

if __name__ == "__main__":
    run(host='localhost',port=8080)
