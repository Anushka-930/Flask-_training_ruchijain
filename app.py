from flask import Flask,render_template,request,redirect,url_for


app=Flask(__name__)
@app.route('/')
def home():
    return "<h1>Hello I am Anushka Mewada</h1>"



@app.route("/welcome")
def welcome():
    return "<h1>welcome to flask training class</h1>"

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/success/<int:a>")
def success(a):
    return "the person is pass and the score is"+str(a)

@app.route("/fail/<int:a>")
def fail(a):
    return "the person is fail and the score is"+str(a)


@app.route('/calculate',methods=['POST','GET'])
def calculate():
    if request.method=='GET':
        return render_template('calculate.html')
    else:
        maths=float(request.form['m'])
        Science=float(request.form['S'])
        DataScience=float(request.form['DS'])
        avg=(maths+Science+DataScience)/3
        result=""
        if avg>=80:
            result="success"
        else:
            result="fail"
        return redirect(url_for(result,a=avg))

if __name__=='__main__':
    app.run(debug=True)

