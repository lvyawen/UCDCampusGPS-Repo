from flask import Flask, request
import Classifier
import numpy as np

app = Flask(__name__)

#Creating the end point for the app
@app.route('/', methods=['GET', 'POST'])
def index():
    req_json = request.get_json();
    predict_loc = Classifier.predict_classifier(req_json);
    return (predict_loc)


if __name__ == "__main__":
    app.run(debug=True)





