# New YouTube (untitled)

## Buggy version
### You need to install:
1. Flask 
2. Flask Forms 
3. SQLAlchemy 
4. Bcrypt 
5. Flask Login 
6. Flask-Mail

### What's New (from v0.1)
1. Route for new password (reset_pass) [Not to be confused with the forgot password route]

### Known Bugs
[x] ~~Updating profile picture changes every user's profile picture.~~ (Fixed)
[x] ~~Can't save the updated profile picture in static/profile_pics and thus the changed PFP doesn't show up.~~ (Fixed)
[ ] Database doesn't update the password when the form in reset_pass(not to be confused with reset_password) route is validated.

### How to Run
-> Move these files to the directory where your virtual environment is located.

        *e.g. If you have a dir, 'nyt' with your venv installed IN IT, paste these files into 'nyt'.*
  
-> Boot up your virtual environment and type "python run.py" to run in debug mode.

-> Boot up your web browser and type the URL, "localhost:5000/"

