#!/usr/bin/env python

from flask import Flask
from flask import render_template, request
import urllib2, json
import utils
from utils import get_token, for_print
from redis import Redis

redis = Redis(host='localhost', port=6379, db=0)
token = get_token()


class Project(object):
    def __init__(self, id, label, background_color, border_color):
        self.id = id
        self.label = label
        self.border_color = border_color
        self.background_color = background_color

PROJECTS = (
    Project('erp', 'ERP', '#97c3ef', '#0653a0'),
    Project('docker', 'Docker', '#b7e589', '#195908'),
    Project('bwt', 'BWT', '#faa4fc', '#a657a8'),
    Project('backend', 'TZ-Backend', '#000000', '#ffffff'),
    Project('TeamZeus-Ansible', 'Ansible', '#ef8686', '#aa210d'),
    Project('soap-bridge', 'Soap-Bridge', '#000000', '#ffffff'),
    Project('teamzeus_frontend_django', 'TZ-Frontend', '#71ede6', '#349691'),
    Project('gridhub', 'Gridhub', '#000000', '#ffffff'),
    Project('draq', 'Draq', '#000000', '#ffffff'),
    Project('grello', 'Grello', '#000000', '#ffffff'),
)


class Column(object):
    def __init__(self, id, label, color, background_color):
        self.id = id
        self.label = label
        self.color = color
        self.background_color = background_color
	

class Columns(object):
    LOW_PRIORITY = Column("low-priority", "Low priority", "#000000", "#f7f57e")
    HIGH_PRIORITY = Column("high-priority", "High priority", "#000000", "#e03731")
    INBOX = Column("inbox", "Inbox", "#000000", "#ffffff")
    IN_PROGRESS = Column("inprogress", "In progress", "#000000", "#5b85e5")
    DONE = Column("done", "Done", "#000000", "#6eea60")
    DOCKER = Column("docker", "Docker", "#000000", "#0d7720")
    LATER = Column("later", "Later", "#000000", "#e2a809")



def getColumns():
    columns = []
    for key, value in Columns.__dict__.iteritems():
        if key[0] != '_':
            columns.append(value)
    return columns



IssueFields = ('id', 'title', 'body', 'repository', 'html_url', 'repository_url', 'state')
class Issue(object):
    def __init__(self, values):
        for k, v in values.iteritems():
            self.__dict__[k] = v
        self.set_repository()
        self.set_project()

    def set_repository(self):
        self.repository = self.repository_url.split('/')[-1]

    def set_project(self):
        for project in PROJECTS:
            if project.id == self.repository:
                self.project = project
                


def loadAllIssues():
    response = urllib2.urlopen('https://api.github.com/issues?access_token='+token)
    issues = json.loads(response.read())

    redis_issues = []
    for column in getColumns():
        redis_issues += redis.lrange(column.id, 0, -1)

    for issue in issues:
        if not str(issue['id']) in redis_issues:
            redis.rpush(Columns.INBOX.id, str(issue['id']))
            redis.hmset( str(issue['id']), {k: issue[k] for k in IssueFields} )

        
    
def getIssues(columnId):
    issues = []
    issue_ids = redis.lrange(columnId, 0, -1)

    for issue_id in issue_ids:
        issue = redis.hgetall(issue_id)
        issues.append( Issue(issue) )

    return issues


def removeClosedIssues():
    issues = []
    for column in getColumns():
        issues = getIssues(column.id)
        for issue in issues:
            if issue.state == 'close':
                redis.lrem(column, issue)



#redis.flushdb()
removeClosedIssues()
loadAllIssues()
app = Flask(__name__)

@app.route('/')
def index():
    column = lambda x: (x, getIssues(x.id))
    board = (
        column(Columns.INBOX),
        column(Columns.LOW_PRIORITY),
        column(Columns.LATER),
        column(Columns.DOCKER),
        column(Columns.HIGH_PRIORITY),
        column(Columns.IN_PROGRESS),
        column(Columns.DONE),
    )

    projects = {}

    return render_template('index.html', board=board, projects=PROJECTS)


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
