from bottle import route, run, template, get, request
import operator

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