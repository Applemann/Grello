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


def getColumns():
    columns = []
    for key, value in Columns.__dict__.iteritems():
        if key[0] != '_':
            columns.append(value)
    return columns


PROJECTS=('erp', 'docker', 'bwt', 'backend', 'TeamZeus-Ansible', 'soap-bridge', 'teamzeus_frontend_django', 'gridhub', 'draq', 'grello')
BACKGROUND_COLORS=('#6fd6ed', '#69e571', '#f453e7', '#f4383b', '#f7c53d', '#c95afc', '#d2f243', '#49f4b3', '#083887')
COLORS=('#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#ffffff')

IssueFields = ('id', 'title', 'body', 'repository', 'html_url', 'repository_url')
class Issue(object):
    def __init__(self, issues):
        for k, v in issues.iteritems():
            self.__dict__[k] = v
        self.set_repository()
        self.set_colors()

    def set_repository(self):
        self.repository = self.repository_url.split('/')[-1]

    def set_colors(self):
        for i in range(len(PROJECTS)):
            if PROJECTS[i] == self.repository:
                self.background_color = BACKGROUND_COLORS[i]
                self.color = COLORS[i]
                


def loadAllIssues():
    response = urllib2.urlopen('https://api.github.com/issues?access_token='+token)
    issues = json.loads(response.read())

    redis_issues = []
    for column in getColumns():
        redis_issues += redis.lrange(column, 0, -1)

    for issue in issues:
        if not str(issue['id']) in redis_issues:
            redis.rpush(Columns.INBOX, issue['id'])
            redis.hmset( issue['id'], {k: issue[k] for k in IssueFields} )
        
    
def getIssues(column):
    issues = []
    issue_ids = redis.lrange(column, 0, -1)

    for issue_id in issue_ids:
        issue = redis.hgetall(issue_id)
        issues.append( Issue(issue) )

    return issues



#redis.flushdb()
loadAllIssues()
app = Flask(__name__)

@app.route('/')
def index():
    column = lambda x: (x, getIssues(x))
    board = (
        column(Columns.LOW_PRIORITY),
        column(Columns.INBOX),
        column(Columns.HIGH_PRIORITY),
        column(Columns.IN_PROGRESS),
        column(Columns.DONE),
    )

    return render_template('index.html', board=board)


@app.route('/move_issue', methods=['GET', 'POST'])
def move_issue():
    from_column = request.form['from_column']
    to_column = request.form['to_column']
    issue = request.form['issue']
    position_before = request.form['position_before']

    redis.lrem(from_column, issue)
    if position_before != '': 
        redis.linsert(to_column, 'before', position_before, issue)
    else: 
        redis.rpush(to_column, issue)

    return from_column + ' ' + to_column
