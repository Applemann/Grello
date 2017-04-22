#!/usr/bin/env python

def for_print(prom):
    if (str(type(prom)) == '<type \'dict\'>'):
        for i, j in prom.iteritems():
            print str(i) +': '+ str(j)
    elif (str(type(prom)) == '<type \'list\'>'):
        for i in prom:
            print str(i)
    elif (str(type(prom)) == '<type \'unicode\'>'):
        print prom
    else:
        print 'Promenna je typu: ' + str(type(prom))


def get_token():
    f=open('token')
    token=f.read()
    f.close()
    return token


