from flask import Flask,render_template,request,session,redirect,url_for,flash,jsonify
from flask_mysqldb import MySQL
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
import MySQLdb.cursors
import pandas as pd 
import os
from werkzeug.utils import secure_filename
from fileinput import filename
from distutils.log import debug
import joblib
from datetime import date ,datetime,timedelta
import re
import json
import requests
import pandas as pd
import random



def clean_tokenize_stop(text):
     
    regexp = RegexpTokenizer('\w+')
    cleaned = regexp.tokenize(text.lower())  
    text = str(regexp.tokenize(text.lower()))
    stopwords = nltk.corpus.stopwords.words("english")
    stopwords.extend(['im','br','ba','eh','kasi','lang','mo','naman','opo','po','si','talaga','yung','akin','aking','ako','alin','am','amin','aming','ang','ano','anumang','apat','at','atin','ating','ay','bababa','bago','bagaman','bakit','bawat','bilang','dahil','dalawa','dapat','dati','dating','din','dito','doon','dumating','gaano','gaanong','gagawin','gayunman','ginagawa','ginawa','ginawang','gumawa','gusto','habang','hanggang','hindi','huwag','iba','ibaba','ibabaw','ibig','ikaw','ilagay','ilalim','ilan','inyong','isa','isang','itaas','ito','iyo','iyon','iyong','ka','kahit','kailangan','kailanman','kami','kamakailan','kanila','kanilang','kanino','kanya','kanyang','kapag','kapwa','karami','karamihan','katiyakan','katulad','kaya','kaysa','ko','kong','kulang','kumuha','kung','laban','lahat','lamang','likod','lima','lugar','maaari','maaaring','maibaba','maging','magkakasunod na','mahusay','makita','mangyaring','marami','marapat','masyado','may','mayroon','mga','minsan','mismo','mula','muli','na','nang','nabanggit','naging','nagkaroon','nais','nakita','namin','napaka','narito','nasaan','ng','ngayon','ni','nila','nilang','nito','niya','niyang','noon','o','pa','paano','pababa','paggawa','pagitan','pagkakaroon','pagkatapos','palabas','pamamagitan','panahon','pangalawa','para','paraan','pareho','pataas','patungo','pero','pinaka','pinakang','pumunta','pumupunta','sa','sa lahat ng lugar','saan','saanman','sabi','sabihin','sa gitna','samakatuwid','samantala','sarili','sila','sino','siya','susunod','tapos','tatlo','tayo','tila','tulad','tuktok','tunay','tungkol','una','wala','walang','walang sino man',',']) 
    cleaned2 = [item for item in cleaned if item not in stopwords]
    wordnet_lem = WordNetLemmatizer()
    cleaned3 = [wordnet_lem.lemmatize(item) for item in cleaned2]
    cleaned4 = ' '.join([word for word in cleaned3]) 
  
    return cleaned4

UPLOAD_FOLDER = os.path.join('staticFiles', 'uploads')
UPLOAD_PROFILE = os.path.join('staticFiles', 'profile')
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__,static_url_path='/static',template_folder='templates')


app.config["DEBUG"] = True
app.secret_key = 'rqweqweqweqweqweqweq21312412412'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] =''
app.config['MYSQL_DB'] = 'sentiment'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_PROFILE'] = UPLOAD_PROFILE

mysql = MySQL(app)
model = joblib.load('model/thesisenglish-tagalog_model51023v5.pkl')



@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.route("/")
def home():
    return render_template("index.html")




@app.route("/loginaccount", methods=['POST','GET'])
def loginaccount():

    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM account WHERE username = % s AND password = % s', (username, password, ))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = "active"
                session['id'] = account['id']
                session['username'] = account['username']
                session['usertype'] = account['acc_type']
                name = account['fname']
                msg = 'Logged in successfully !'
                return dblogin()
            else:
                msg = 'Incorrect username / password !'
            return render_template("login.html", msg = msg)  
    else:
          return dblogin()   
    

@app.route("/gotoindex")
def gethome():
    return render_template("index.html")

@app.route("/logout")
def logout():
    session.clear()
    return login()
    

@app.route("/login")
def login():

    if 'loggedin' not in session or session['loggedin'] != 'active': 
        return render_template("login.html")
    else:
        return dblogin()
        
    
@app.route("/dashboard")
def godb():
    return dblogin()



@app.route('/uploadfile', methods = ['POST','GET'])
def readcsv():
    if request.method == 'POST':
        f = request.files.get('file')
        company = request.form.get('getcompany')
        item = request.form.get('getitem')
        
        if not f or not company or not item: 
            flash("NO FILE SELECTED")
        else:
            company = request.form['getcompany']
            item = request.form['getitem']
            data_filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],data_filename))
            file_path = os.path.join(app.config['UPLOAD_FOLDER'],data_filename)
            parseCSV(file_path,company,item)    
    else:
        flash("ERROR:")
    return redirect(url_for('loginaccount'))


def parseCSV(filePath,company,item):
     cursor = mysql.connection.cursor()
     col_names = ['name','feedback','date','time']
    

     today = date.today()
     getdate = today.strftime("%m/%d/%Y")
     ctime = datetime.today()
     time = ctime.strftime("%H:%M:%S")
     random_number = random.randint(1000000000, 9999999999)
     randomkey=str(random_number)
     
      # Use Pandas to parse the CSV file
     csvData = pd.read_csv(filePath,names=col_names, header=None)
      # Loop through the Rows
     i = 0
     active = ""
    
     for i,row in csvData.iterrows():
        if row['name'] == 'name':
            active = "True"
            break
        else:
            active = "False"    
        
     inputdata = 0
     erorrcount = 0
     for i,row in csvData.iterrows():
          
            if active == "True":  
                    if i !=0:
                        val = len(row['feedback'].split())
                        if  val >= 3 :
                            text = clean_tokenize_stop(row['feedback'])
                            final_text = [text]
                            output = model.predict(final_text)[0]
                            inputdata += 1
                            if output == 0:
                                out =  'Negative'
                            else:
                                out =  'Positive'
                            output +=1
                            ccdate = str(row['date'])
                            cctime = str(row['time'])
                            name = str(row['name'])
                            if name == 'nan':
                               cname = "unknown"
                            else:
                               cname = name
                            if ccdate == 'nan':
                               currentdate = getdate
                            else:
                               currentdate = ccdate
                            if cctime == 'nan':
                               currenttime = time
                            else:
                               currenttime = cctime
                            cursor.execute("INSERT INTO feedback(name, feedback,time,date,sentiment,sentimentValue,item_name,company_name,grp_name) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (cname,row['feedback'],currenttime,currentdate,out,output,item,company,randomkey))
                            mysql.connection.commit()
                        else:
                            erorrcount += 1
                    else :
                        i+=1    
            else:
                flash('Please make sure the file that will be uploaded is in the rigth format(ERROR:404)')
                break
     if active == "True" and inputdata > 0 and erorrcount == 0:
        cursor.execute('INSERT INTO history(company_name, item_name, inserted_data, insert_type, date,user_id,grp_name) VALUES (%s, %s, %s, %s, %s,%s,%s)',(company,item,str(inputdata),"CSV File",currentdate,str(session['id']),randomkey))
        mysql.connection.commit()
        flash('Successfully Inserted Data:'+ str(inputdata))
     elif active == "True" and erorrcount >= 0 and inputdata == 0:  
        flash('Minimum of 3 Words ERROR=404')
     elif active == "True" and erorrcount > 0 and inputdata > 0:
        cursor.execute('INSERT INTO history(company_name, item_name, inserted_data, insert_type, date,user_id,grp_name) VALUES (%s, %s, %s, %s, %s,%s,%s)',(company,item,str(inputdata),"CSV File",currentdate,str(session['id']),randomkey))
        mysql.connection.commit()  
        flash('Successfully Inserted Data:'+ str(inputdata)+ "Minimum of 3 Words"+ str(erorrcount))
     cursor.close()       
           

      

def dblogin():
    name = session['username']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM feedback WHERE sentiment = % s',("Positive",))
    positive = cursor.rowcount
    cursor.execute('SELECT * FROM feedback WHERE sentiment = % s',("Negative",))
    negative = cursor.rowcount
    cursor.execute('SELECT * FROM feedback')
    total = cursor.rowcount
    if positive !=0 and negative !=0:
        average = positive/negative
    else:
        average = 0
    cursor.execute('SELECT MAX(id) As latestcomment FROM feedback')
    lastrow = cursor.fetchone()
    lastrow = lastrow['latestcomment']
    cursor.execute('SELECT * FROM accountcompany WHERE account_id = % s',(session['id'],))
    company = cursor.fetchall()

    
    today = date.today()
    d3 = today.strftime("%m/%d/%Y")
    listdate = []
    listvalue = []
    listneg = []
    tdate = today - timedelta(days=6)
    for i in range(7):
        d = tdate + timedelta(days=i)
        listdate.append(d.strftime('%m/%d/%Y'))
    for i in listdate:
        cursor.execute('SELECT * FROM feedback WHERE date = % s and sentiment = % s',(i,"Positive"))
        line = cursor.rowcount
        listvalue.append(line)
    for i in listdate:
        cursor.execute('SELECT * FROM feedback WHERE date = % s and sentiment = % s',(i,"Negative"))
        line = cursor.rowcount
        listneg.append(line)
            
    
    return render_template("db.html",positive = positive, negative = negative,name = name, total = total,average = str(round(average, 2)), lastrow = lastrow ,listdate=listdate,d3=d3,listvalue=listvalue,listneg=listneg,company=company,usertype=session['usertype'])




@app.route("/databasetable", methods=["GET", "POST"])
def tabledb():

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM accountcompany WHERE account_id = % s',(session['id'],))
    company = cursor.fetchall()
    session["company"] = company
    cursor.execute('SELECT * FROM feedback')
    send = cursor.fetchall()
    return render_template("database.html",value= send, company = company,usertype=session['usertype'])

@app.route("/tablenegative", methods=["GET", "POST"])
def tablenegative():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM accountcompany WHERE account_id = % s',(session['id'],))
    company = cursor.fetchall()
    # sentiment = request.form["sentiment"]
    
    company  = request.form.get('company')
    item  = request.form.get('item')
    sentiment = request.form.get('type')

    if sentiment == "Positive" and item == "all":
        cursor.execute('SELECT * FROM feedback WHERE sentiment = % s and company_name = % s', (sentiment,company))
        send = cursor.fetchall()
        return render_template("table.html",name=session['username'],value= send, company = company)

    if sentiment == "Positive" or sentiment == "Negative" and item != "all":
        cursor.execute('SELECT * FROM feedback WHERE sentiment = % s and company_name = % s and item_name = % s', (sentiment,company,item,))
        send = cursor.fetchall()
        return render_template("table.html",name=session['username'],value= send, company = company)
    
    elif sentiment == "Positive" or sentiment == "Negative" and item == "all":
        cursor.execute('SELECT * FROM feedback WHERE sentiment = % s and company_name = % s', (sentiment,company))
        send = cursor.fetchall()
        return render_template("table.html",name=session['username'],value= send, company = company)
  
    elif sentiment == "all" and item != "all":
        cursor.execute('SELECT * FROM feedback WHERE company_name = % s and item_name = % s', (company,item,))
        send = cursor.fetchall()
        return render_template("table.html",name=session['username'],value= send, company = company)
    else:
        cursor.execute('SELECT * FROM feedback WHERE company_name = % s LIMIT 1000',(company,)) 
        send = cursor.fetchall()
        return render_template("table.html",name=session['username'],value= send, company = company)
    

@app.route("/mani", methods=["GET", "POST"])
def tablenegative1():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM accountcompany WHERE account_id = % s',(session['id'],))
    company = cursor.fetchall()
    # sentiment = request.form["sentiment"]
    sentiment = request.form.get('type')
       
    if sentiment == "Positive" or sentiment == "Negative":
        cursor.execute('SELECT * FROM feedback WHERE sentiment = % s', (sentiment,))
        send = cursor.fetchall()
        return render_template("database.html",name=session['username'],value= send, company = company)   
           
    else:
        cursor.execute('SELECT * FROM feedback') 
        send = cursor.fetchall()
        return render_template("database.html",name=session['username'],value= send, company = company,usertype =session['usertype'])

@app.route("/item",methods=["GET", "POST"])
def getcompanyname():
    name =session['username']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('SELECT * FROM feedback WHERE sentiment = % s',("Positive",))
    positive = cursor.rowcount
    cursor.execute('SELECT * FROM feedback WHERE sentiment = % s',("Negative",))
    negative = cursor.rowcount
    cursor.execute('SELECT * FROM feedback')
    total = cursor.rowcount
    cursor.execute('SELECT SUM(sentimentValue) As average FROM feedback')
    average = cursor.fetchone()
    average = average['average']
    if positive !=0 and negative !=0:
        average = positive/negative
    else:
        average = 0
    
    cursor.execute('SELECT MAX(id) As latestcomment FROM feedback')
    lastrow = cursor.fetchone()
    lastrow = lastrow['latestcomment']
    if lastrow is not None:
        cursor.execute('SELECT * FROM feedback WHERE id = % s',(lastrow,))
        latestc1 = cursor.fetchone()
        fb1 = latestc1['feedback']
        slice_object = slice(45) 
        fb1 = fb1[slice_object] + "..."
        cursor.execute('SELECT * FROM feedback WHERE id = % s',(lastrow - 1,))
        latestc2 = cursor.fetchone()
        fb2 = latestc2['feedback']
        fb2 = fb2[slice_object] + "..."
    else:
        fb1 = ""
        fb2 = ""
        latestc1 =""
        latestc2 =""


    
    slice_object = slice(45) 
    fb2 = fb2[slice_object] + "..."
    today = date.today()
    d3 = today.strftime("%m/%d/%Y")
    listdate = []
    listvalue = []
    listneg = []
    tdate = today - timedelta(days=6)
    for i in range(7):
        d = tdate + timedelta(days=i)
        listdate.append(d.strftime('%m/%d/%Y'))
    for i in listdate:
        cursor.execute('SELECT * FROM feedback WHERE date = % s and sentiment = % s',(i,"Positive"))
        line = cursor.rowcount
        listvalue.append(line)
    for i in listdate:
        cursor.execute('SELECT * FROM feedback WHERE date = % s and sentiment = % s',(i,"Negative"))
        line = cursor.rowcount
        listneg.append(line)
    companylist =[]
    cursor.execute('SELECT * FROM accountcompany WHERE account_id = % s',(session['id'],))
    company1 = cursor.fetchall()
    for row in company1:
        companylist.append(row['companyname'])
    itemlist =[]
    if not companylist:
        itemlist = ['Nan']
    else:
        cursor.execute('SELECT * FROM item WHERE company_name = % s', (companylist[0],))
        listitem = cursor.fetchall()
        for row in listitem:
            itemlist.append(row['item_name'])
         
    
    return render_template("item.html",positive = positive, negative = negative,name = name, total = total,average = str(round(average, 2)), lastrow = lastrow ,latestc1=latestc1, fb1= fb1, fb2= fb2,latestc2=latestc2,listdate=listdate,d3=d3,listvalue=listvalue,listneg=listneg,company1=company1,companylist=companylist,itemlist=itemlist,usertype=session['usertype'])


@app.route('/usersentiment', methods=['GET','POST'])
def usersentiment():
    return render_template("senti.html")

@app.route('/usergetresult', methods=['GET','POST'])
def predict():
    text = request.form['review']
    realtext = text
    text = clean_tokenize_stop(text)
    final_text = [text]
    output = model.predict(final_text)[0]
    
    if output == 0:
        out =  'Negative'
    else:
        out =  'Positive'

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO facebook(feeedback, sentiment) VALUES (%s, %s)", (text, out))
    mysql.connection.commit()
    cursor.close()    

    return render_template('senti.html', result = out ,realtext = realtext)


@app.route('/getitemmname', methods=['GET','POST'])
def getitemmname():
    vitem = request.form['selectedOption']
    return jsonify({'name': vitem})

@app.route('/changeitemlist', methods=['GET','POST'])
def getitemlist():
    val = request.form['feedbackType']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM item WHERE company_name = % s', (val,))
    listitem = cursor.fetchall()
    return jsonify(listitem)

@app.route('/itemtable', methods=['GET','POST'])
def itemtable():
    name =session['username']
    item = request.form['type'] 
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM feedback WHERE sentiment = % s and item_name = % s',("Positive",item,))
    positive = cursor.rowcount
    cursor.execute('SELECT * FROM feedback WHERE sentiment = % s and item_name = % s',("Negative",item))
    negative = cursor.rowcount
    cursor.execute('SELECT * FROM feedback')
    total = cursor.rowcount
    cursor.execute('SELECT SUM(sentimentValue) As average FROM feedback')
    average = cursor.fetchone()
    average = average['average']
    if positive !=0 and negative !=0:
        average = positive/negative
    else:
        average = 0
    cursor.execute('SELECT MAX(id) As latestcomment FROM feedback')
    lastrow = cursor.fetchone()
    if lastrow is not None:
        cursor.execute('SELECT * FROM feedback WHERE id = % s',(lastrow,))
        latestc1 = cursor.fetchone()
        fb1 = latestc1['feedback']
        slice_object = slice(45) 
        fb1 = fb1[slice_object] + "..."
        cursor.execute('SELECT * FROM feedback WHERE id = % s',(lastrow - 1,))
        latestc2 = cursor.fetchone()
        fb2 = latestc2['feedback']
        fb2 = fb2[slice_object] + "..."
    else:
        fb1 = ""
        fb2 = ""
        latestc1 =""
        latestc2 =""


    today = date.today()
    cursor.execute('SELECT * FROM accountcompany WHERE account_id = % s',(session['id'],))
    company = cursor.fetchall()
    d3 = today.strftime("%m/%d/%Y")
    listdate = []
    listvalue = []
    listneg = []
    tdate = today - timedelta(days=6)
    for i in range(7):
        d = tdate + timedelta(days=i)
        listdate.append(d.strftime('%m/%d/%Y'))
    for i in listdate:
        cursor.execute('SELECT * FROM feedback WHERE date = % s and sentiment = % s',(i,"Positive"))
        line = cursor.rowcount
        listvalue.append(line)
    for i in listdate:
        cursor.execute('SELECT * FROM feedback WHERE date = % s and sentiment = % s',(i,"Negative"))
        line = cursor.rowcount
        listneg.append(line)    
    
    return render_template("itemtable.html",positive = positive, negative = negative,name = name, total = total,average = str(round(average, 2)), lastrow = lastrow ,latestc1=latestc1, fb1= fb1, fb2= fb2,latestc2=latestc2,listdate=listdate,d3=d3,listvalue=listvalue,listneg=listneg,company=company)

@app.route('/itemtable1', methods=['GET','POST'])
def itemtable1():
    
    name =session['username']   
    item = request.form['type']
    company = request.form['company'] 

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM feedback WHERE sentiment = % s and item_name = % s and company_name = % s',("Positive",item,company,))
    positive = cursor.rowcount
    cursor.execute('SELECT * FROM feedback WHERE sentiment = % s and item_name = % s and company_name = % s',("Negative",item,company,))
    negative = cursor.rowcount
    cursor.execute('SELECT * FROM feedback WHERE item_name = % s and company_name = % s',(item,company,))
    total = cursor.rowcount
   
    if positive != 0 and total != 0 :
        totaltemp = positive/total
        totaltemp = totaltemp * 100
    else:
        totaltemp = 0
    total = positive + negative
    today = date.today()
    getdata = today.strftime('%m/%d/%Y')
    listdate = []
    listvalue = []
    listneg = []
    months = ['01/%','02/%','03/%','04/%','05/%']
    tdate = today - timedelta(days=6)
    cursor.execute('SELECT * FROM feedback WHERE date = % s and item_name = % s and company_name = % s',(getdata,item,company,))
    latestcomment = cursor.rowcount
    monthspositive = []
    monthsNegative = []

    for i in months:
          cursor.execute('SELECT * FROM feedback WHERE date LIKE %s and sentiment = %s and item_name = %s and company_name = %s',(i,"Positive",item,company,))
          results = cursor.fetchall()
          getpos = len(results)
          monthspositive.append(getpos)  

    for i in months:
          cursor.execute('SELECT * FROM feedback WHERE date LIKE %s and sentiment = %s and item_name = %s and company_name = %s',(i,"Negative",item,company,))
          results = cursor.fetchall()
          getpos = len(results)
          monthsNegative.append(getpos)  

    for i in range(7):
        d = tdate + timedelta(days=i)
        listdate.append(d.strftime('%m/%d/%Y'))
    for i in listdate:
        cursor.execute('SELECT * FROM feedback WHERE date = % s and sentiment = % s and item_name = % s and company_name = % s',(i,"Positive",item,company,))
        line = cursor.rowcount
        listvalue.append(line)
    for i in listdate:
        cursor.execute('SELECT * FROM feedback WHERE date = % s and sentiment = % s and item_name = % s and company_name = % s',(i,"Negative",item,company,))
        line = cursor.rowcount
        listneg.append(line)    

    return jsonify({'positive':positive, 'negative':negative,'total':total,'average': str(round(totaltemp,2))+"%",'listvalue': listvalue,'listneg':listneg,'latestcomment':latestcomment,'monthspositive':monthspositive,'monthsNegative':monthsNegative})


@app.route('/changeitem', methods=['GET','POST'])
def changeitemlistmaindb():
    val = request.form['feedbackType']

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM feedback WHERE company_name = %s ORDER BY id DESC LIMIT 1',(val,))
    last_record = cursor.fetchone()
    if not last_record:
        last_record = ""
    cursor.execute('SELECT * FROM feedback WHERE company_name = %s ORDER BY id DESC LIMIT 1 OFFSET 1',(val,))
    second_record = cursor.fetchone()
    if not second_record:
        second_record = ""
    cursor.execute('SELECT * FROM item WHERE company_name = % s', (val,))
    listitem = cursor.fetchall()
    countitem = cursor.rowcount
    cursor.execute('SELECT * FROM feedback WHERE sentiment = % s and company_name = % s',("Positive",val,))
    positive = cursor.rowcount
    cursor.execute('SELECT * FROM feedback WHERE sentiment = % s and company_name = % s',("Negative",val,))
    negative = cursor.rowcount
    cursor.execute('SELECT * FROM feedback WHERE company_name = % s', (val,))
    total = cursor.rowcount
    totaltemp = 1
    if positive != 0 and total != 0 :
        totaltemp = positive/total
        totaltemp = totaltemp * 100
    else:
        totaltemp = 0
    today = date.today()
    listdate = []
    listvalue = []
    listneg = []
    tdate = today - timedelta(days=6)
    for i in range(7):
        d = tdate + timedelta(days=i)
        listdate.append(d.strftime('%m/%d/%Y'))
    for i in listdate:
        cursor.execute('SELECT * FROM feedback WHERE date = % s and sentiment = % s and company_name = % s',(i,"Positive",val,))
        line = cursor.rowcount
        listvalue.append(line)
    for i in listdate:
        cursor.execute('SELECT * FROM feedback WHERE date = % s and sentiment = % s and company_name = % s',(i,"Negative",val,))
        line = cursor.rowcount
        listneg.append(line)

    return jsonify({'listitem':listitem,'positive':positive,'negative':negative,'total':total,'countitem':countitem,'totaltemp':str(round(totaltemp,2))+"%",'listvalue': listvalue,'listneg':listneg,'last_record':last_record,'second_record':second_record})

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        birthdate = request.form['birthdate']
        contact = request.form['contact']
        cursor = mysql.connection.cursor()

        # validate form data
        if not all([username, password, email, first_name, last_name, contact, birthdate]):
             return jsonify({'respo': username + password + email + first_name + last_name + contact + birthdate+"wewew"})
            # return jsonify({'respo': 'All fields are required'})
        elif len(username) < 5 or len(username) > 20:
            return jsonify({'respo': 'Username must be between 5 and 20 characters'})
        elif len(password) < 8 or len(password) > 30:
            return jsonify({'respo': 'Password must be between 8 and 30 characters'})
        elif '@' not in email or '.' not in email:
            return jsonify({'respo': 'Invalid email address'})
        elif not birthdate:
            return jsonify({'respo': 'Invalid birthdate'})
        else:
            cursor.execute('SELECT * FROM account WHERE username = %s', (username,))
            result = cursor.fetchone()
            if result:
                return jsonify({'respo': 'Username already exists'})
            else:
                cursor.execute('INSERT INTO account (fname, lname, username, password, email, birthdate, contact, acc_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',(first_name, last_name, username, password, email, birthdate, contact,"Standard"))
                mysql.connection.commit()
                return jsonify({'respo': 'Registration successful!'})

@app.route('/changeitem1', methods=['POST'])
def changeitemlistmaindb1():
    val = request.form['feedbackType']
    if val is not None:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT item_name FROM item WHERE company_name = % s', (val,))
        listitem = cursor.fetchall()
        listallitem =[]
        listallitemaverage = []
        for row in listitem:
            listallitem.append(row)
            cursor.execute('SELECT * FROM feedback WHERE sentiment = % s and item_name = % s and company_name = % s',("Positive",row,val,))
            positive = cursor.rowcount
            cursor.execute('SELECT * FROM feedback WHERE item_name = % s and company_name = % s', (row,val,))
            total = cursor.rowcount
            if positive != 0 and total != 0 :
                totaltemp = positive/total
                totaltemp = totaltemp * 100
            else:
                totaltemp = 0
            listallitemaverage.append(totaltemp)

        
        return jsonify({'listitem':listitem,'listallitem':listallitem,'listallitemaverage':listallitemaverage})


@app.route('/shoppe', methods=['GET', 'POST'])
def shoppeadd():
  
    
    random_number = random.randint(1000000000, 9999999999)
    randomkey=str(random_number)
    if session['usertype']  != 'Standard':
        url = request.form['urlshoppe']
        company = request.form['getcompany']
        item = request.form['modalgetitem']
        today = date.today()
        formatday = today.strftime('%m/%d/%Y')
        ctime = datetime.today()
        time = ctime.strftime("%H:%M:%S")
        if url != "":
            cursor = mysql.connection.cursor() 
            r = re.search(r"i\.(\d+)\.(\d+)", url)
            shop_id, item_id = r[1], r[2]
            ratings_url = "https://shopee.ph/api/v2/item/get_ratings?filter=0&flag=1&itemid={item_id}&limit=20&offset={offset}&shopid={shop_id}&type=0"
            insertdata = 0
            offset = 0
            d = {"username": [], "comment": []}
            while True:
                data = requests.get(
                    ratings_url.format(shop_id=shop_id, item_id=item_id, offset=offset)
                ).json()
                b=0
                i = 1
            
                below3word = 0
                if data["data"]["ratings"] is not None:
                
                    for i, rating in enumerate(data["data"]["ratings"], 1):
                        if rating["comment"] is not None:
                            val = len(rating["comment"].split())
                        if rating["comment"] == "":
                            b += 1
                        else:
                            
                            if val > 3:
                                text = clean_tokenize_stop(rating["comment"])
                                final_text = [text]
                                insertdata+=1
                                output = model.predict(final_text)[0]
                                if output == 0:
                                    out =  'Negative'
                                    output+=1
                                else:
                                    out =  'Positive'
                                    output+=1
                                name = rating["author_username"]
                                if name is None:
                                    name = "Unknown"
                                cursor.execute("INSERT INTO feedback(name, feedback, sentiment,date,time,sentimentValue,company_name,item_name,grp_name) VALUES (%s, %s,%s,%s, %s,%s, %s,%s,%s)", (name, rating["comment"],out,formatday,time,output,company,item,randomkey))
                                mysql.connection.commit()
                            else:
                                below3word+=1
                else:
                    print("No ratings data found for offset", offset)
                    break
  
                if i % 20:
                    break

                offset += 20
            
            cursor.execute('INSERT INTO history(company_name, item_name, inserted_data, insert_type, date,user_id,grp_name) VALUES (%s, %s, %s, %s, %s,%s,%s)',(company,item,insertdata,"Shopee Link",formatday,str(session['id']),randomkey))
            mysql.connection.commit()        
            cursor.close()
            flash('Successfully Inserted Data: {}'.format(insertdata))  
            return dblogin()
        else:
            flash("PLEASE INPUT URL")
            return dblogin()
    else:
        flash("This Feature is for Premium Users only.")
        return dblogin()

@app.route('/profile')
def profile():
    return render_template('profile.html',usertype=session['usertype'],name=session['username'])


@app.route('/profileupdate', methods=['POST','GET'])
def profileupdate():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM account WHERE id = %s",(str(session['id'])))
    details = cursor.fetchall()
    return jsonify(details)



@app.route('/profilechange', methods=['POST','GET'])
def profilechange():
    fname = request.form['firstname']
    lname = request.form['lname']
    password = request.form['password']
    email = request.form['email']

    if password =="":
        password = request.form['cpassword']
    else:
        password = request.form['password']

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE account SET fname = %s, lname = %s,password = %s,email = %s WHERE id = %s",(fname,lname,password,email,str(session['id']),))
    mysql.connection.commit()
   




    return jsonify({'password':password})

@app.route('/management')
def management():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM accountcompany WHERE account_id = % s',(session['id'],))
    company = cursor.fetchall()

    cursor.execute('SELECT * FROM history WHERE user_id = % s',(session['id'],))
    history = cursor.fetchall()
    return render_template('management.html',company=company,history=history,usertype=session['usertype'],name=session['username'])
   
@app.route('/getcompany', methods=['POST','GET'])
def getcompany():
    company = request.form['company']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM accountcompany WHERE companyname = % s',(company,))
    qweqwqwe = cursor.fetchone()

    itemlist =[]
    cursor.execute('SELECT * FROM item WHERE company_name = % s', (company,))
    listitem = cursor.fetchall()
    for row in listitem:
        itemlist.append(row[1])
    
    return render_template("company.html",company=qweqwqwe,itemlist=itemlist)


@app.route('/getallitemchange', methods=['POST','GET'])
def getallitemchange():
    company = request.form['company']
    cursor = mysql.connection.cursor()

    itemlist =[]
    cursor.execute('SELECT * FROM item WHERE company_name = % s', (company,))
    listitem = cursor.fetchall()
    for row in listitem:
        itemlist.append(row[1])
    
    return render_template("itemlisttable.html", itemlist=itemlist,company=company,enumerate=enumerate)


@app.route('/addcompany', methods=['POST','GET'])
def addcompany():
    get = request.form['additem']
    cursor = mysql.connection.cursor()

    cursor.execute('SELECT * FROM accountcompany WHERE account_id = %s',(session['id'],))
    rowcount=cursor.rowcount

    if session['usertype'] =='Standard':
        if rowcount >= 1:
            flash('Purchase Premium to create more Enterprise name.')
        else:
            cursor.execute('SELECT * FROM accountcompany WHERE companyname = %s', (get,))
            accountcompany = cursor.fetchone()
            if accountcompany:
                flash('Enterprise name already exists')
                return redirect(url_for('management'))
            else: 
                cursor.execute('INSERT INTO accountcompany(companyname , account_id) VALUES(%s,%s)',(get,session['id']))
                mysql.connection.commit()
                cursor.execute('INSERT INTO item(item_name , company_name) VALUES(%s,%s)',("Item"+str(get),get))
                mysql.connection.commit()
                flash('Succesfuly Created New Enterprise.')
    else:
        cursor.execute('SELECT * FROM accountcompany WHERE companyname = %s', (get,))
        accountcompany = cursor.fetchone()
        if accountcompany:
            flash('Enterprise name already exists')
            return redirect(url_for('management'))
        else: 
            cursor.execute('INSERT INTO accountcompany(companyname , account_id) VALUES(%s,%s)',(get,session['id']))
            mysql.connection.commit()
            cursor.execute('INSERT INTO item(item_name , company_name) VALUES(%s,%s)',("Item"+str(get),get))
            mysql.connection.commit()
            flash('Succesfuly Created New Enterprise.')
    return redirect(url_for('management'))


@app.route('/dropcompany', methods=['POST','GET'])
def dropcompany():

    company = request.form['company']

    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM accountcompany WHERE companyname = % s',(company,))
    mysql.connection.commit()
    cursor.execute('DELETE FROM feedback WHERE company_name = % s',(company,))
    mysql.connection.commit()
    cursor.execute('DELETE FROM item WHERE company_name = % s',(company,))
    mysql.connection.commit()
    cursor.execute('DELETE FROM history WHERE company_name = % s',(company,))
    mysql.connection.commit()
    flash('Succesfully Deleted all items in Entreprise See you again!')

    return redirect(url_for('management'))

@app.route('/companyupdate', methods=['POST','GET'])
def companyupdate():

    company = request.form['company']
    cvalue = request.form['cvalue']
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE accountcompany set companyname = %s WHERE companyname = %s',(company,cvalue))
    mysql.connection.commit()

    cursor.execute('UPDATE feedback set company_name = %s WHERE company_name = %s',(company,cvalue))
    mysql.connection.commit()

    cursor.execute('UPDATE item set company_name = %s WHERE company_name = %s',(company,cvalue))
    mysql.connection.commit()
    flash("SUCCCESSFULLY UPDATED "+cvalue+" To "+company)

    return redirect(url_for('management'))




@app.route('/additem', methods=['POST','GET'])
def additem():
    company = request.form['company']
    additem = request.form['newvalueitem']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM item WHERE company_name = %s', (company,))
    countcompany = cursor.rowcount
    if session['usertype'] =='Standard':
        if countcompany >= 2:
            flash('Purchase Premium to create more Item.')
        else:
            cursor.execute('SELECT * FROM item WHERE company_name = %s and item_name = %s', (company,additem))
            accountcompany = cursor.fetchone()
            if accountcompany:
                flash('Item name already exists')
                return redirect(url_for('management'))
            else:
                cursor.execute('INSERT INTO item(item_name , company_name) VALUES(%s,%s)',(additem,company))
                mysql.connection.commit()
                flash('Succesfuly Created New Item.')

    else:
        cursor.execute('SELECT * FROM item WHERE company_name = %s and item_name = %s', (company,additem))
        accountcompany = cursor.fetchone()
        if accountcompany:
            flash('Item name already exists')
            return redirect(url_for('management'))
        else:
            cursor.execute('INSERT INTO item(item_name , company_name) VALUES(%s,%s)',(additem,company))
            mysql.connection.commit()
            flash('Succesfuly Created New Item.')

    return redirect(url_for('management'))


@app.route('/edititem', methods=['POST','GET'])
def edititem():
    company = request.form['company']
    cvalue = request.form['item']
    newvalue = request.form['newvalue']
    cursor = mysql.connection.cursor()

    cursor.execute('SELECT * FROM item WHERE company_name = %s and item_name = %s', (company,cvalue))
    accountcompany = cursor.fetchone()

    if accountcompany:
        flash('Item Name Already Exists')
        return redirect(url_for('management'))
    else:
        cursor.execute('UPDATE item set item_name = %s WHERE item_name = %s and company_name = %s',(newvalue,cvalue,company))
        cursor.execute('UPDATE feedback set item_name = %s WHERE item_name = %s and company_name = %s',(newvalue,cvalue,company))
        mysql.connection.commit()
        flash('Name Has Successfully Change')
        return redirect(url_for('management'))
   

@app.route('/deleteitem', methods=['POST','GET'])
def deleteitem():
    company = request.form['company']
    cvalue = request.form['item']
    newvalue = request.form['newvalue']
    cursor = mysql.connection.cursor()

    cursor.execute('SELECT * FROM item WHERE company_name = %s',(company,))
    rowcount=cursor.rowcount
    if rowcount == 1:
        flash("HINDI PEDE MAG DELETE PAG ISA")
    else:
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM item WHERE item_name = %s and company_name = %s',(cvalue,company,))
        cursor.execute('DELETE FROM feedback WHERE item_name = %s and company_name = %s',(cvalue,company))
        cursor.execute('DELETE FROM history WHERE item_name = %s and company_name = %s',(cvalue,company))
        mysql.connection.commit()
        flash('SUCCESFULLY DELETED ITEM NAME: '+cvalue)
        
    return redirect(url_for('management'))



@app.route('/massdelete', methods=['POST','GET'])
def massdelete():
    getkey = request.form['getkey']
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM feedback WHERE grp_name = %s',(getkey,))
    cursor.execute('DELETE FROM history WHERE grp_name = %s',(getkey,))
    mysql.connection.commit()
    flash("Successfully deleted")
    return redirect(url_for('management'))
    




if __name__ == '__main__':
   app.run(port = 5000,debug= True)

