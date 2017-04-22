#!/usr/bin/env python

from flask import Flask
from flask import render_template
import urllib2, json
import utils
from utils import get_token, for_print
from redis import Redis

redis = Redis()
token = get_token()

class Issue(object):
    def __init__(self, id, title, body, repository):
        self.id=id
        self.title=title
        self.body=body
        self.repository=repository

def loadAllIssues():
    response = urllib2.urlopen('https://api.github.com/issues?access_token='+token)
    issues = json.loads(response.read())
    for issue in issues:
        redis.rpush("inbox", issue['id'])
        redis.hmset( issue['id'], 
                    {
                        'id': issue['id'],
                        'title': issue['title'],
                        'body': issue['body'],
                        'repository': issue['repository'],
                    }
                )
        
    
def getIssues(collumn):
    issues = []
    issue_ids = redis.lrange(collumn, 0, -1)

    for issue_id in issue_ids:
        issue = redis.hgetall(issue_id)
        issues.append(
            Issue(
                issue['id'], 
                issue['title'], 
                issue['body'], 
                issue['repository']
            ) 
        )

    return issues


#loadAllIssues()
app = Flask(__name__)

@app.route('/')
def index():
    inbox_issues = getIssues('inbox')

    board = (
        ("low-priority", []),
        ('inbox', inbox_issues),
        ('high-priority', []),
        ('inprogress', []),
        ('done', []),
    )

    return render_template('index.html', board=board)
