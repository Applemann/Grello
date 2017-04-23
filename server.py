#!/usr/bin/env python

from flask import Flask
from flask import render_template, request
import urllib2, json
import utils
from utils import get_token, for_print
from redis import Redis

redis = Redis()
token = get_token()

class Columns(object):
    LOW_PRIORITY = "low-priority"
    HIGH_PRIORITY = "high-priority"
    INBOX = "inbox"
    IN_PROGRESS = "inprogress"
    DONE = "done"

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
        
    
def getIssues(column):
    issues = []
    issue_ids = redis.lrange(column, 0, -1)

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
    board = (
        (Columns.LOW_PRIORITY, getIssues(Columns.LOW_PRIORITY)),
        (Columns.INBOX, getIssues(Columns.INBOX)),
        (Columns.HIGH_PRIORITY, getIssues(Columns.HIGH_PRIORITY)),
        (Columns.IN_PROGRESS, getIssues(Columns.IN_PROGRESS)),
        (Columns.DONE, getIssues(Columns.DONE)),
    )

    return render_template('index.html', board=board)


@app.route('/move_issue', methods=['GET', 'POST'])
def move_issue():
    from_column = request.form['from_column']
    to_column = request.form['to_column']
    issue = request.form['issue']
    position_before = request.form['position_before']
    redis.lrem(from_column, issue)
    if (position_before != ''): 
        redis.linsert(to_column, 'before', position_before, issue)
    else: 
        redis.rpush(to_column, issue)

    return from_column + ' ' + to_column
