from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/')
def index():

    board = {
        "low-priority": ['item1', 'item2', 'item3'],
        'inbox': ['item1', 'item2', 'item3'],
        'high-priority': ['item1', 'item2', 'item3'],
        'inprogress': ['item1', 'item2', 'item3'],
        'done': ['item1', 'item2', 'item3']
    }

    return render_template('index.html', board=board)
