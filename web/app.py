from flask_restful import Api , Resource
import pymongo
from flask import Flask , jsonify , request
import hashlib
from bson.json_util import dumps
app = Flask(__name__)
api = Api(app)

# connecting to the database ( mongo )
client = pymongo.MongoClient('mongodb://localhost:27017/' , username='root' , password='password'   )  ## mongo auth ##
db = client.bank_database #### data base name ###
collection=db["Users"] #### collection name ### 



def UserExit (username) : 
  
    x= db.posts.find_one({'username': username}) 
    

    if x !=  None : 
        return False

    else:
     return True

class Register(Resource) :
    def post(self) : 
        posteData = request.json
        username = posteData["username"]
        password = posteData["password"]
        if not UserExit(username) : 
            retJson ={
                "status" : "301"  , 
                "msg" : "Invalid Username"
            }
            return jsonify(retJson)
        hashed_pw=  hashlib.sha256(str(password).encode('utf-8')).hexdigest()
        post = {
            "username" : username
            , "password" : hashed_pw , 
            "own": 0 ,
            "debt":0
           
        }
        posts = db.posts 
        post_id = posts.insert_one(post).inserted_id

    
        retjson={
            "status":200 , 
            "msg" : " you successfully signed up to the bank "
        }
        return jsonify(retjson)
def verifyPw ( username , password) : 
    if not UserExit(username) : 
        return False
    user_record = db.posts.find_one({'username': username}) 
    pw = dumps(user_record['password'])
    pw=str(pw)
    pass_test=  hashlib.sha256(str(password).encode('utf-8')).hexdigest()  ## hashing the given password ##
    pass_test = f'"{pass_test}"'   # " password  "
    if pass_test == pw:
        print(True )
        return True 
    else : 
      print(False)
      print( pass_test  )
      False
def cashWithuser(username) : 
    user_record = db.posts.find_one({'username': username}) 
    cash = dumps(user_record['own'])
    return cash 
def debtWithuser(username) : 
    user_record = db.posts.find_one({'username': username}) 
    debt = dumps(user_record['debt'])
    return debt

def generateReturnDict(staus , msg) : 
    retJson = {
        "status" : staus , 
        "msg" : msg 
    }
    return retJson 
def verifyCredentials(username , password ) : 
    if  not UserExit(username) : 
        return generateReturnDict(301 , "invalid username") , True 
    correct_pw = verifyPw(username , password)
    if not correct_pw : 
        return generateReturnDict(302 , "inavalid password") , True 
    return None , False 
def updateAccount (username, balance) : 
       db.posts.update_one({ "username" : username } , {
            '$set' :{
                "own":balance , 
               
                }  } )
def updateDept (username, balance) : 
       db.posts.update_one({ "username" : username } , {
            '$set' :{
                "debt":balance , 
               
                }  } )
class Add ( Resource) :
    def post(self) : 
        posteData =  request.json
        username = posteData["username"]
        password = posteData["password"]
        money = posteData["amount"] 
       
     
        if money <= 0 : 
            return jsonify(generateReturnDict(304 , " No money to add  !! "))
        cash = cashWithuser(username) 
        money-=1  #with every transaction the user do the bank get 1 dt
        bank_cash = cashWithuser("BANK")
        bank_cash = int(bank_cash)
        updateAccount("BANK" , bank_cash + 1 )
        money = int(money)
        cash = int(cash)
        updateAccount(username , cash + money)
        return jsonify(generateReturnDict(200 , ' transaction DONE  '))

class Transfer(Resource) : 
    def post(self) : 
        posteData =  request.json
        username = posteData["username"]
        password = posteData["password"]
        money = posteData["amount"] 
        to = posteData["to"] 
        
        
        cash = int(cashWithuser(username) )
        if cash <= 0 : 
            return jsonify(generateReturnDict(304 , " No money to send !! "))
      
        cash_from = int(cashWithuser(username))
        cash_to = int(cashWithuser(to))
        cash_bank = int(cashWithuser("BANK"))
        updateAccount ("BANK" , cash_bank+1)
        updateAccount (to , cash_to + money -1 )
        updateAccount (username , cash_from - money - 1 )
        return jsonify(generateReturnDict(200 , "amount transfered"))


class Balance(Resource) : 
    def post (self ) : 
        posteData =  request.json
        username = posteData["username"]
        password = posteData["password"]
   
        user_record = db.posts.find_one({'username': username}) 
        name = dumps(user_record['username'])
        own= dumps(user_record['own'])
        dept = dumps(user_record['debt'])
        retjson = { "name" : name , 
        "own" : own , 
        "dept" :  dept }
        return jsonify(retjson)


class   TakeLoan (Resource) : 
    def post(self) : 
        posteData =  request.json
        username = posteData["username"]
        password = posteData["password"]        
        money = posteData["amount"] 
   
        cash = int(cashWithuser(username) )
        dept = int(debtWithuser(username)) 
        updateAccount(username , cash+money ) 
        updateDept(username , dept+money)
        return jsonify(generateReturnDict(200 , "Loan added to your account"))

class PayLoan (Resource) : 
    def post(self) : 

        posteData =  request.json
        username = posteData["username"]
        password = posteData["password"]
        money = posteData["amount"]
     
        cash = int(cashWithuser(username) ) 
        if cash < money : 
            return jsonify(generateReturnDict(303 , " not enough money in your account "))
        debt = int(debtWithuser(username))
        updateAccount(username , cash-money)
        updateDept(username, debt-money)
        return jsonify(generateReturnDict(200 , "you ve succesfully paid your loan"))


api.add_resource(Register, '/register')
api.add_resource(Add , '/add')

api.add_resource(Transfer , '/transfer')
api.add_resource(Balance , '/balance') 

api.add_resource(TakeLoan , '/takeloan')
api.add_resource(PayLoan , '/payloan')

if __name__ == "__main__" : 
    app.run(debug=True)

