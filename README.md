# AP-Project
Automated Birthday wishing app using python with features to schedule B'day wishes using SMS and Email service.Insert,update and delete custom message and schedule birthday wish with an option to get import from google contacts.      

## Setting Up:
1. Install `virtualenv`:
```
$ pip3 install virtualenv
```

2. Open a terminal in the project root directory and run:
```
$ virtualenv env
```

3. Then run the command:
```
$ source env/bin/activate
```
In windows,
```
$ source env\Scripts\activate
```

4. Then install the dependencies:
```
$ (env) pip3 install -r requirements.txt
```

5. Finally start the web server:
```
$ (env) python3 app.py
```

This server will start on port 5000 by default. You can change this in `app.py` by changing the following line to this:

```python
if __name__ == "__main__":
    app.run(debug=False, port=<desired port>)
```
