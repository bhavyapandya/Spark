import traceback

from flask import *
import datetime
import sqlite3
app = Flask(__name__)
app.secret_key = 'some secret key'
class User_Error(Exception):
   # Constructor method
   def __init__(self, value):
      self.value = value
   # __str__ display function
   def __str__(self):
      return(repr(self.value))
@app.route('/',methods=['GET','POST'])
def home():
    return render_template("home.html")
@app.route('/customer',methods=['GET','POST'])
def customer(call=None):
    try:
        with sqlite3.connect('spark.db') as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute('select * from customer')
            rows = cur.fetchall()
    except:
        return "error"
    return render_template("customer.html", rows=rows,call=call)
@app.route('/transfer',methods=['GET','POST'])
def transfer():
    if request.method == 'POST' or request.method=='GET':
        try:
            fnm = request.form['from']
            tnm = request.form['to']
            amt=request.form['amount']
            with sqlite3.connect('spark.db') as con:
                con.row_factory = sqlite3.Row
                cur = con.cursor()
                cur.execute('select * from customer where id=?',(fnm))
                row = cur.fetchone()
                day=datetime.datetime.now()
            bal=int(row['balance'])-int(amt)
            if bal<0:
                raise User_Error("Unsuccessful due to insufficient money")
            with sqlite3.connect('spark.db') as con:
                con.row_factory = sqlite3.Row
                cur = con.cursor()
                cur.execute('update customer set balance=? where id=?',(bal,fnm))
                cur.execute('update customer set balance=balance+? where id=?', (amt, tnm))
            with sqlite3.connect('spark.db') as con:
                con.row_factory = sqlite3.Row
                cur = con.cursor()
                cur.execute('insert into tran values (?,?,?,?,?)',(fnm,tnm,int(amt),day.strftime("%d-%m-%Y"),day.strftime("%H-%M")))
        except User_Error:
            return customer("Unsuccessful due to insufficient money")
        except:
            return traceback.print_exc()
        return customer('successful')
if __name__ == '__main__':
    app.run(debug=True)

