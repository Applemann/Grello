# Grello
Grello is simple web application for visualization github issues.


## Local setup:

  Fork project from github and clone it:
  
  ```
  git clone <git-repository>
  ```

  
  go to repository:
  ```
  cd grello
  ```
  
  create virtualenv:
```
mkdir grello-dev
virtualenv grello-dev
source ./grello-dev/bin/activate

pip install -r requirements.txt
```

setup your token:
```
echo "{{ your gitHub auth token }}" > token
```


run server:
```
export FLASK_APP=server.py && flask run --host=0.0.0.0
```


## Special thanks:

 - [Redis](https://redis.io/): In-memory data storage.
 - [Flask](http://flask.pocoo.org/): Python microframework.



## Authors:

 - Martin Jablečník

