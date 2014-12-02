from bottle import route, run, template, get, request, redirect, app, hook, error, static_file
import operator
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from apiclient.errors import HttpError
from apiclient.discovery import build
import httplib2
from beaker.middleware import SessionMiddleware
from database.models import *

# GOOGLE API CODE --------------------BEGINS-----------------
flow = OAuth2WebServerFlow(
	client_id="697082725785-rbo99p5bebnds8ugdud0t40jc224dl71.apps.googleusercontent.com",
	client_secret='bBXXPeCK6d8hlt0wPYie5jHx',
	redirect_uri="http://localhost:8080/oauth2callback",
	scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email'
	)

session_opts = {
	'session.type': 'file',
	'session.cookie_expires': 300,
	'session.data_dir': './data',
	'session.auto': True
}
app = SessionMiddleware(app(), session_opts)

@hook('before_request')
def setup_request():
	request.session = request.environ.get('beaker.session')

# @route('/test')
# def test():
# 	s = request.environ.get('beaker.session')
# 	s['test'] = s.get('test',0) + 1
# 	s.save()
# 	return 'Test counter: %d' % s['test']

@route('/autenticate', 'GET')
def autenticate_1():
	uri = flow.step1_get_authorize_url()
	redirect(str(uri))

@route('/oauth2callback', 'GET')
def autenticate_2():
	global users_data
	credentials = flow.step2_exchange(request.query.get('code',''))

	http = httplib2.Http()
	http = credentials.authorize(http)
	# Get user email
	users_service = build('oauth2', 'v2', http=http)
	user_document = users_service.userinfo().get().execute()
	user_email = str(user_document['email'])

	print type(user_email)
	request.session['logged'] = True
	request.session['user_email'] = user_email
	# if user_email not in users_data:
	# 	users_data[user_email] = {}

	request.session.save()

	print users_data
	
	redirect('/')

#GOOGLE API CODE -------------------END----------------

@route('/static/<filename:path>')
def server_static(filename):
	return static_file(filename, root='./static')


@route('/logout')
def logout():
	request.session['logged'] = False
	redirect('/')

users_data = {}


@get('/')
def init():
	logged = request.session.get('logged', False)
	if logged:
		if request.session['user_email'] not in users_data:
			users_data[request.session['user_email']] = {}
	word = request.query.get('keywords','').strip()
	if word != "":
		redirect("/result/0?keywords="+"+".join(word.split()))
	return template("templates/index.html", ordered_word=get_top_20(), logged=logged)

def word_counter(string, logged):
	"""
	Input: string (str): user's query;
		   logged (bool): user's login status.
	Output: (dict) Dictionary with the words counting.
	Obs: updates the session's dictionary of the user's words counting history"""
	global users_data
	list_words = string.split(" ")
	result = {}
	for word in list_words:
		if word in result:
			result[word]+=1
			if logged:
				users_data[request.session['user_email']][word]+=1
		if word not in result:
			result[word]=1
			if logged:
				if word not in users_data[request.session['user_email']]:
					users_data[request.session['user_email']][word]=1
				else:
					users_data[request.session['user_email']][word]+=1
	return result

def get_operator_fn(op):
	return {
		'+' : operator.add,
		'-' : operator.sub,
		'*' : operator.mul,
		'/' : operator.div,
		'^' : operator.pow,
		}[op]


def evaluate(string):
	"""
	Input: string (str): Query input
	Output: (float): Evaluated expression
			None: if it's not a mathematical expression
	"""
	operations = ["-","+","/","*","^"]
	accu = 0
	try:
		return float(string)
	except ValueError:
		try:
			for op in operations:
				num_list = string.split(op)
				if len(num_list) > 1:
					break
			if len(num_list) > 1:
				accu = evaluate(num_list[0])
				# if accu == None:
				# 	return None
				for num in num_list[1:]:
					accu = get_operator_fn(op)(accu, evaluate(num))
				return accu
			else:
				return None
		except TypeError:
			return None
	except TypeError:
		return None

def teste(evaluated, original):
	"""
	Input: evaluated (float/None): evaluate Output
		   original (str): Query input
	Output: (bool): True if the evaluated is mathematical expression and not just a number, otherwise False
	"""
	if evaluated == None:
		return False
	try:
		float(original)
		return False
	except Exception:
		return True

@route('/result/<page_number>', method=['GET'])
def show_result(page_number=0):
	number = int(page_number)
	logged = request.session.get('logged', False)
	query = request.query.get('keywords','').strip()
	word = query.split()[0]
	value = evaluate(query)
	documents = [str(elem.document) for elem in Documents.select().join(InvertedIndex).join(Lexicon).where(Lexicon.word==word).order_by(Documents.page_rank.desc())]
	table_word_count = word_counter(request.query.get('keywords','', ).strip(),logged)
	if not teste(value, query):
		return template("templates/result.html", number=number, result=documents, ordered_word=get_top_20(), logged=logged, query=word, value=False)
	else:
		return template("templates/result.html", number=number, result=documents, ordered_word=get_top_20(), logged=logged, query=word, value="%s = %s" % (" ".join(query.split()), value))


def get_top_20():
	"""
	Input: -
	Output: (list): List of words ordered by it's occurance
	"""
	global users_data
	if request.session.get('logged', False):
		ordered_words = sorted(users_data[request.session['user_email']].items(), key=operator.itemgetter(1), reverse=True)[:20]
	else:
		ordered_words = []
	return ordered_words

@error(404)
def error404(error):
	return template("templates/error404.html")

if __name__ == "__main__":
	run(app=app, host='localhost',port=8080)
