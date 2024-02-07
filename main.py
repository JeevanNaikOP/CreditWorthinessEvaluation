import os
import json
import requests
import tornado.web
import tornado.ioloop
import tornado.autoreload
import sys
import asyncio
#import psycopg2
import time
#import matplotlib.pyplot as plt

# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))
#port=8000
class landingPage(tornado.web.RequestHandler):
    def get(self):
        self.render("static/index.html")
        
class HomePage(tornado.web.RequestHandler):
    def get(self):
        self.render("static/index.html")

class Login(tornado.web.RequestHandler):
    def post(self):

        print("inside login")
        username = str(self.get_body_argument("uname"))
        print(username)
        pwd = str(self.get_body_argument("pass"))
        print(pwd)

        print("json")
        if username =="admin" and pwd == "adminpass":
            print("success")
            self.render("static/indexx.html")
        else:
            print("no")
            self.render("static/trial.html")



class basicRevHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/reversal.html")

class predictScore(tornado.web.RequestHandler):
    def post(self):
        header = {
            'Content-Type': 'application/json',
            'Control': 'no-cache',
        }

        json_data = {
            'username' : os.getenv("USERNAME"),
            'password' : os.getenv("PASSWORD"),
        }

        response = requests.post('https://192.86.32.113:9888/auth/generateToken', json=json_data, headers=header,verify=False)

        token = json.loads(response.text)['token']

        base_url = 'http://192.86.32.113:5001/iml/v2/scoring/online/0a2443f6-e896-450d-8be1-af2108a69ba6'

        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
        
        amt=str(self.get_body_argument("amt"))
        cnt_children=str(self.get_body_argument("cnt_children"))
        gender=str(self.get_body_argument("gender"))
        birth=str(self.get_body_argument("birth"))
        ext_source_1=str(self.get_body_argument("ext_source_1"))
        ext_source_2=str(self.get_body_argument("ext_source_2"))
        graduate=str(self.get_body_argument("graduate"))
        postgraduate=str(self.get_body_argument("postgraduate"))
        income_type=str(self.get_body_argument("income_type"))
        occupation_type=str(self.get_body_argument("occupation_type"))

        payload_scoring = [{"EXT_SOURCE_2":ext_source_1,"EXT_SOURCE_3":ext_source_2,"DAYS_BIRTH":birth,"CODE_GENDER_M":gender,"NAME_EDUCATION_TYPE_Higher education":graduate,"NAME_EDUCATION_TYPE_Secondary / secondary special":postgraduate,"NAME_INCOME_TYPE_Working":income_type,"AMT_CREDIT":amt,"CNT_CHILDREN":cnt_children,"OCCUPATION_TYPE_Sales staff":occupation_type}]
        print(payload_scoring)
        response_scoring = requests.post('http://192.86.32.113:5001/iml/v2/scoring/online/0a2443f6-e896-450d-8be1-af2108a69ba6', json=payload_scoring, headers=header,verify=False)

        json_out = (json.loads(response_scoring.text))

        print("before")
        #print(json_out)
        jsonstruct=json_out
        #print(jsonstruct)
        jsonstruct=json.dumps(jsonstruct)
        json_load=json.loads(jsonstruct)

        print("df")
        print(json_load)
        val1=json_load[0]['probability(0)']
        val2=json_load[0]['probability(1)']
        #print(val1)
        val1=round(val1,16)
        val2=round(val2,16)
        #print (val1)
        val1=round((val1*100),2)
        val2=round((val2*100),2)

        print(val1,val2)
        labels= ['Risk for transfer', 'Non-risk for transfer']
        colors=['#14213d','#e63946']
        sizes= [val1,val2]

        # if json_load[0]['prediction']:
        #     outVal = 'No'
        # else:
        #     outVal = 'Yes'

        x1x = round(json_load[0]['probability(1)'],12)*100
        x0x = round(json_load[0]['probability(0)'],12)*100

        self.render("static/result.html",label=labels,color=colors,size=sizes,x1x=x1x,xox=x0x,bloc="predictScore", jsonstruct=jsonstruct,
                    amt=amt,
                    cnt_children=cnt_children,
                    gender=gender,birth=birth,
                    ext_source_1=ext_source_1,
                    ext_source_2=ext_source_2,graduate=graduate,
                    postgraduate=postgraduate,
                    income_type=income_type,
                    occupation_type=occupation_type)
                   # outVal=outVal)
        



if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/", landingPage),
        (r"/predictScore", predictScore),

    ])
    print("commit")
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    app.listen(port)
    # TODO remove in prod
    #print("inside win")
    #server=HTTPServer(app)
    tornado.autoreload.start()
    print("I'm listening on port specified")
    print(port)
    tornado.ioloop.IOLoop.current().start()
