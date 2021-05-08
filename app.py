from flask import Flask, render_template, request, redirect, url_for, session
import requests, json, os
from ibm_watson import VisualRecognitionV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'a'
app.config['MYSQL_HOST'] = "remotemysql.com" 
app.config["MYSQL_PORT"] = 3306
app.config['MYSQL_USER'] = "lypD47Dxuh" 
app.config['MYSQL_PASSWORD'] = "EATLsr4rTp"
app.config['MYSQL_DB'] = "lypD47Dxuh" 
mysql = MySQL(app)


@app.route('/')
def index():
    return  render_template('index.html')

@app.route('/login', methods = ["POST", "GET"])
def login():
    """
    Login page with username and password
    """
    return render_template("login.html")

    
@app.route('/submission', methods=["POST", "GET"])
def submission():
    if request.method == "POST":
        name = request.form["username"]
        password = request.form["password"]
        session['name'] = name
        session['password'] = password
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO user_details VALUES(NULL,% s, % s)',(name, password))
        mysql.connection.commit()
        a = session['name']
        cursor.execute("SELECT * FROM `user_details` WHERE `username` = %s",[a])
        account = cursor.fetchone()
        return render_template("submission.html", account = account[1])
    else:
        return redirect(request.url)
    
    
@app.route('/display', methods = ["POST", "GET"])
def display():
    """
    Display page that displays nutritional value of input image of food name
    """
    if request.method == "POST":
        image = request.files["food"] 
        authenticator = IAMAuthenticator('2A6BucKErMHbNpKGwdyGMBTsAZYxRYmm8Rxr0chzTvfm')
        visual_recognition = VisualRecognitionV3(
        version='2018-03-19',
        authenticator=authenticator)
        visual_recognition.set_service_url('https://api.us-south.visual-recognition.watson.cloud.ibm.com/instances/80c78105-880f-4bb7-b79c-93764795ee73') 
        classes = visual_recognition.classify(images_filename=image.filename, 
                                              images_file=image ,classifier_ids='food').get_result() 
        data=json.loads(json.dumps(classes,indent=4))

        foodName=data["images"][0]['classifiers'][0]["classes"][0]["class"]
        nutrients = {}
        USDAapiKey = '9f8yGs19GGo5ExPpBj7fqjKOFlXXxkJdMyJKXwG3'
        response = requests.get('https://api.nal.usda.gov/fdc/v1/foods/search?api_key={}&query={}&requireAllWords={}'.format(USDAapiKey, foodName, True))

        data = json.loads(response.text)
        concepts = data['foods'][0]['foodNutrients']
        arr = ["Sugars","Energy", "Vitamin A","Vitamin D","Vitamin B", "Vitamin C", "Protein","Fiber","Iron","Magnesium",
               "Phosphorus","Cholestrol","Carbohydrate","Total lipid (fat)", "Sodium", "Calcium",]
        for x in concepts:
            if x['nutrientName'].split(',')[0] in arr:
                if(x['nutrientName'].split(',')[0]=="Total lipid (fat)"):
                    nutrients['Fat'] = str(x['value'])+" " + x['unitName']
                else:    
                    nutrients[x['nutrientName'].split(',')[0]] = str(x['value'])+" " +x['unitName']
                    
        return render_template('display.html', x = foodName, data = nutrients, account = session['name'])
    else:
        return redirect(request.url)       

if __name__ == '__main__':
   app.run(host='0.0.0.0',debug = True, port = 8080)
    
