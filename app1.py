from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():

    answer = ""

    if request.method == "POST":

        num1 = float(request.form["num1"])
        num2 = float(request.form["num2"])
        operation = request.form["operation"]

        if operation == "add":
            answer = num1 + num2

        elif operation == "sub":
            answer = num1 - num2

        elif operation == "mul":
            answer = num1 * num2

        elif operation == "div":
            if num2 != 0:
                answer = num1 / num2
            else:
                answer = "Cannot divide by zero"

    return render_template("calculator.html", answer=answer)


if __name__ == "__main__":
    app.run(debug=True)