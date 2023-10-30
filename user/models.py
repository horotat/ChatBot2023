from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
from webapp import db, project_dir
from dataset import dump_emails
import random
import uuid
import logging
import os

user_logger = logging.getLogger('chatbot.user')

def condition_assign(email):
    """ 
    Function to assign immediate/delayed feedback conditions to users 
    """

    allowed_emails_list, email_condition_list = dump_emails(db)

    for em_con in email_condition_list:
        if email == em_con[0]:
            return em_con[1]
    


def get_class(email):

    class_A = db.emails_list.find_one({"_id": "A"})
    class_B = db.emails_list.find_one({"_id": "B"})
    class_C = db.emails_list.find_one({"_id": "C"})
    class_D = db.emails_list.find_one({"_id": "D"})
    admins = db.emails_list.find_one({"_id": "admin"})
    test = db.emails_list.find_one({"_id": "test"})

    # check if email is in each class
    if email in class_A["emails"]:
        return "A"
    elif email in class_B["emails"]:
        return "B"
    elif email in class_C["emails"]:
        return "C"
    elif email in class_D["emails"]:
        return "D"
    elif email in admins["emails"]:
        return "admin"
    elif email in test["emails"]:
        return "test"


class User:


    def start_session(self, user):
        del user["password"]
        # make cookie less heavy by removing chat history
        del user["chats"]
        session['logged_in'] = True
        session['user'] = user
        user_logger.info("User %s logged in successfully", user["email"])
        return jsonify(user), 200

    def signup(self):

        # Create the user object
        user = {
            "_id": uuid.uuid4().hex,
            "name": request.form.get("name"),
            "email": request.form.get("email").lower(),
            "password": request.form.get("password"),
            "class": get_class(request.form.get("email")),
            "condition": condition_assign(request.form.get("email").lower()),
            "session_todo": "session_0",
            "demographics" : {},
            "chats": {
                "session_0": {
                    "completion": {
                        "status": "todo",
                        "turns": 0,
                        "chars": 0,
                    },
                    "summary": "",
                    "week": {
                        "number": 1,
                        "start": "2022-11-21",
                        "end": "2022-11-27"
                    }
                },
                "session_1": {
                    "completion": {
                        "status": "locked",
                        "turns": 0,
                        "chars": 0,
                    },
                    "summary": "",
                    "week": {
                        "number": 1,
                        "start": "2022-11-21",
                        "end": "2022-11-27"
                    }
                },
                "session_2": {
                    "completion": {
                        "status": "locked",
                        "turns": 0,
                        "chars": 0,
                    },
                    "summary": "",
                    "week": {
                        "number": 1,
                        "start": "2022-11-21",
                        "end": "2022-11-27"
                    }
                },
                "session_3": {
                    "completion": {
                        "status": "locked",
                        "turns": 0,
                        "chars": 0,
                    },
                    "summary": "",
                    "week": {
                        "number": 1,
                        "start": "2022-11-21",
                        "end": "2022-11-27"
                    }
                },
                "session_4": {
                    "completion": {
                        "status": "locked",
                        "turns": 0,
                        "chars": 0,
                    },
                    "summary": "",
                    "week": {
                        "number": 2,
                        "start": "2022-11-28",
                        "end": "2022-12-04"
                    }
                },
                "session_5": {
                    "completion": {
                        "status": "locked",
                        "turns": 0,
                        "chars": 0,
                    },
                    "summary": "",
                    "week": {
                        "number": 2,
                        "start": "2022-11-28",
                        "end": "2022-12-04"
                    }
                },
                "session_6": {
                    "completion": {
                        "status": "locked",
                        "turns": 0,
                        "chars": 0,
                    },
                    "summary": "",
                    "week": {
                        "number": 2,
                        "start": "2022-11-28",
                        "end": "2022-12-04"
                    }
                },
                "session_7": {
                    "completion": {
                        "status": "locked",
                        "turns": 0,
                        "chars": 0
                    },
                    "summary": "",
                    "week": {
                        "number": 3,
                        "start": "2022-12-05",
                        "end": "2022-12-11"
                    }
                },
                "session_8": {
                    "completion": {
                        "status": "locked",
                        "turns": 0,
                        "chars": 0
                    },
                    "summary": "",
                    "week": {
                        "number": 3,
                        "start": "2022-12-05",
                        "end": "2022-12-11"
                    }
                },
                "session_9": {
                    "completion": {
                        "status": "locked",
                        "turns": 0,
                        "chars": 0,
                    },
                    "summary": "",
                    "week": {
                        "number": 3,
                        "start": "2022-12-05",
                        "end": "2022-12-11"
                    }
                },
                "session_10": {
                    "completion": {
                        "status": "locked",
                        "turns": 0,
                        "chars": 0,
                    },
                    "summary": "",
                    "week": {
                        "number": 4,
                        "start": "2022-12-12",
                        "end": "2022-12-18"
                    }
                },
                "session_11": {
                    "completion": {
                        "status": "locked",
                        "turns": 0,
                        "chars": 0,
                    },
                    "summary": "",
                    "week": {
                        "number": 4,
                        "start": "2022-12-12",
                        "end": "2022-12-18"
                    }
                },
                "session_12": {
                    "completion": {
                        "status": "locked",
                        "turns": 0,
                        "chars": 0,
                    },
                    "summary": "",
                    "week": {
                        "number": 4,
                        "start": "2022-12-12",
                        "end": "2022-12-18"
                    }
                }
            }
        }
        # Encrypt the password
        user["password"] = pbkdf2_sha256.hash(user["password"])

        # Check for existing email address. If it exists, return an error message

        if db.users.find_one({"email": user["email"]}):
            return jsonify({"error": "Email address already in use"}), 400
        
        allowed_emails_list, email_condition_list = dump_emails(db)
        # Check email is in allowed mailing list
        if user["email"] not in allowed_emails_list:
            return jsonify({"error": "Email address not allowed"}), 400
        
        # If email does not exist, insert new user into database

        if db.users.insert_one(user):
            # add file handler for user logger
            user_file = os.path.join(project_dir, "logs/chatbot_{user}.log".format(user=user["_id"]))
            user_handler = logging.FileHandler(user_file)
            formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
            user_handler.setFormatter(formatter)
            user_logger.addHandler(user_handler)
            user_logger.info("User %s signed up successfully", user["email"])
            return self.start_session(user) # success!

        return jsonify({"error": "Signup failed :( "}), 400 # failure as default
    
    def signout(self):
        user_logger.info("User %s signed out", session['user']['email'])
        session.clear()
        return redirect('/')
    
    def login(self):

        user = db.users.find_one({
            "email": request.form.get("email").lower()
        })

        if user and pbkdf2_sha256.verify(request.form.get("password"), user["password"]):
            return self.start_session(user)
        
        return jsonify({"error": "Invalid login credentials"}), 401

    def manage_profile(self):

        # This function is used to update the user's profile information 

        if session.get("logged_in") == True:
            
            filter = {"_id": session["user"]["_id"]}

            newvalues = {
                "$set": {
                    "demographics" : {
                        "gender" : request.form.get("gender"),
                        "age" : request.form.get("age"),
                        "level" : request.form.get("level"),
                        "native" : request.form.get("native"),
                        "education" : request.form.get("education"),
                        "study_field" : request.form.get("study_field")
                    }
                }
            }

            db.users.update_one(filter, newvalues)
            user_logger.info("User profile information updated successfully")
            return jsonify({"success": "Profile updated successfully"}), 200

        return jsonify({"error": "Update failed"}), 400 
    
    