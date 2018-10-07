Webapp
------
How to Setup
-------------
sudo docker build -t webapp .
sudo docker run --name webapp -p 5000:5000 webapp

How to Test
-----------

1) http://localhost:5000/upload

2) http://localhost:5000/retrieve_file

3) http://localhost:5000/delete
