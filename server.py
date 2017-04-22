#!/usr/bin/env python

from flask import Flask
from flask import render_template
import urllib2, json
import utils
from utils import get_token, for_print


class Issue(object):
    def __init__(self, title, body, repository):
        self.title=title
        self.body=body
        self.repository=repository

    
def getAllIssues(token):
    response = urllib2.urlopen('https://api.github.com/issues?access_token='+token)
    issues = json.loads(response.read())
    retIssues = []
    for issue in issues:
        retIssues.append(
            Issue(
                issue['title'], 
                issue['body'], 
                issue['repository']
            ) 
        )

    return retIssues

app = Flask(__name__)

@app.route('/')
def index():
    
    inbox_col = []
    all_issues = getAllIssues(utils.get_token())
    for issue in all_issues:
        inbox_col.append(issue.title)


    board = (
        ("low-priority", ['item1', 'item2', 'item3']),
        ('inbox', inbox_col),
        ('high-priority', ['item1', 'item2', 'item3']),
        ('inprogress', ['item1', 'item2', 'item3']),
        ('done', ['item1', 'item2', 'item3']),
    )

    return render_template('index.html', board=board)
