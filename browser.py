from flask import Flask
from flask import render_template
from flask import request
import read_lyrics
import insertUrl
import os
app = Flask(__name__)
# ws = GeventWebSocket(app)
listColors = ["#00FFFF", "#7FFF00", "#FF8C00","#FF1493", "#FFD700", "#CD5C5C","#FF00FF", "#FFFF00","#00FF7F", "#1E90FF"]
hard_words = {
    'nigga':['N' ,'IH' ,'G' ,'AH'],
    'niggas':['N' ,'IH' ,'G' ,'AH' ,'Z'],
    'aingt':['EY' ,'N' ,'T']
    }

@app.route('/returnFast',  methods=['POST', 'GET'])
def getReturnFast():
    print('in method')
    error = None
    url = None
    rr = None
    if request.method == 'POST':
        if(request.form['url'] != ''):
            print("into url post")
            url = request.form['url']
            # rr, body = read_lyrics.rhyme_finder(url)
            title = read_lyrics.drawOutTitle(url)
            listWords = read_lyrics.drawOutWords(url)
            mydb = insertUrl.databaseConnect("url.db")
            if(mydb.checkVisited(url) is None):
                mydb.creatURLDB(url=url,url2=title,listWords=listWords)
        else:
            error = 'Input Required'

    #         error = 'Invalid username/password'
    # if request.method == 'GET':
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('returnFast.html', rr = 100, url = url, error=error)

@app.route('/')
def start_temp():
    return render_template('index.html')

@app.route('/setVisited',methods=['POST'])
def setVisited():
    if request.method == 'POST':
        if(request.form['url'] != ''):
            url = request.form['url']
            mydb = insertUrl.databaseConnect("url.db")
            mydb.setVisited(url)
        else:
            print('ERROR URL NONE')
    return 'None'

@app.route('/getAllWords',methods=['POST'])
def getAllWords():
    finalAdd = ''
    print("got in getAllWords")
    if request.form['url'] != '':
        url = request.form['url']
        title = read_lyrics.drawOutTitle(url)
        mydb = insertUrl.databaseConnect("url.db")
        myWords = mydb.getAllValues(title)
        visited = mydb.checkVisited(url)
        if visited:
            for i in range(mydb.getCount(title)):
                mainWord = myWords[i][1]
                textcolor = ";color:#FFFFFF'>"
                usedword = mainWord
                color = myWords[i][2]
                if(color != 'NA'):
                    textcolor = ";color:#000000'>"
                textcolor = "'>"
                last = textcolor + mainWord + " </span>"
                nextElement = "<span style='color: " + color + last
                if(mainWord == 'NEWLINE'):
                    nextElement = '<br>'
                elif(mainWord == 'BREAKBREAK'):
                    nextElement = '<br><br>'
                finalAdd += nextElement
        else:
            for i in range(mydb.getCount(title)):
                mainWord = myWords[i][1]
                if(mainWord == 'NEWLINE'):
                    nextElement = '<br>'
                    finalAdd += nextElement
                    continue
                elif(mainWord == 'BREAKBREAK'):
                    nextElement = '<br><br>'
                    finalAdd += nextElement
                    continue
                textcolor = ";color:#FFFFFF'>"
                usedword = mainWord
                if not read_lyrics.knownWord(mainWord):
                    print('MAINWORD: ' + mainWord)
                    usedword = usedword.replace("'","")

                    while (not read_lyrics.knownWord(usedword)) and len(usedword) > 1:
                        usedword = usedword[1:len(usedword)]
                    print('USEDWORD: ' + usedword)

                if read_lyrics.knownWord(usedword):
                    for j in range(1,20):
                        if i+j >= len(myWords):
                            break
                        newWord = myWords[i+j][1]
                        if(newWord == 'BREAKBREAK'):
                            break
                        elif(newWord == 'NEWLINE'):
                            continue
                        if not read_lyrics.knownWord(newWord):
                            newWord = newWord.replace("'","")
                            while (not read_lyrics.knownWord(newWord)) and len(newWord) > 1:
                                newWord = newWord[1:len(newWord)]
                        if(read_lyrics.two_rhyme(usedword, newWord) >= 150):
                            if(myWords[i][2] == 'NA'):
                                mydb.setColor(title, i,listColors[0])
                                mydb.setColor(title, j+i,listColors[0])
                                myWords[i][2] = listColors[0]
                                myWords[i+j][2] = listColors[0]
                                listColors.append(listColors.pop(0))
                            else:
                                mydb.setColor(title, j+i,myWords[i][2])
                                myWords[i+j][2] = myWords[i][2]
                color = myWords[i][2]
                textcolor = "'>"
                last = textcolor + mainWord + " </span>"
                nextElement = "<span style='color: " + color + last
                finalAdd += nextElement
        return finalAdd

if __name__ == '__main__':
    HOST = '0.0.0.0' if 'PORT' in os.environ else '127.0.0.1'
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host=HOST, port=PORT)
