FROM python:2.7
# clone application
COPY git-repo /opt/project
WORKDIR /opt/project

# install application
RUN pip install -r requirements.txt

ENV FLASK_APP=server.py 
EXPOSE 5000

ENTRYPOINT flask run --host=0.0.0.0
    
