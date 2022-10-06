# Application_Programming
## How to run project:
- install poetry and dependencies:
```
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
poetry add flask
```
- start the server
    in command line:
```
curl -v -XGET http://localhost:8080/api/v1/hello-world-11
```
   or open link in the browser:  
```
http://localhost:8080/api/v1/hello-world-11
```

