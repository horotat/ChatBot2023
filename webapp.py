# Info #

# to start: FLASK_APP=webapp.py FLASK_ENV=development flask run
# to check if mongo is running: service mongod status

# ------------------ #

# Imports #

import datetime
from distutils.log import debug
import logging
import os
import pandas as pd
import pymongo
from functools import wraps
from flask import Flask, render_template, request, session, jsonify, Response, redirect, stream_with_context, url_for
from transformers import T5ForConditionalGeneration, T5Tokenizer
from passlib.hash import pbkdf2_sha256
from ben_v2 import Ben
from dataset import Dataset
from dataset import dump_scenarios, get_starts_ends
from error_db import update_error_db, get_final_assessment_sentences
# ------------------ #

# Set up logging #

project_dir = os.getcwd()
os.makedirs(os.path.join(project_dir, "logs/"), exist_ok=True)

def setup_logger(name, filename=os.path.join(project_dir, "logs/chatbot.log"), level=logging.DEBUG):
    """
    This function is used to set up the logger.

    params: name: str, filenames: list, level: logging.INFO
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    fh = logging.FileHandler(filename)
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

logger = setup_logger("chatbot")

# ------------------ #

# App #


## Flask initialization  and DB connection ##

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client.chat_users

dump_scenarios(db, "https://docs.google.com/spreadsheets/d/e/2PACX-1vRrkBnC6bHeJHyN_hYFmwv4igWHiorOfuQpHV003UJqefBL3yAXoyQRnc3B-E9DeJVdol_bexLuGaZc/pub?gid=0&single=true&output=csv")


## Global variables ##

# # read the allowed emails from the online csv and put them in the database and store them in a variable as a list
# allowed_emails_old, email_condition_list = dump_emails(db)

# classes = ["A","B","C","D", "admin", "test"]
# allowed_emails_list = get_emails(db, classes)

# logger.info("allowed emails: %s", allowed_emails_list)

# get start and end date of the week from db.scenarios

scenarios_obj = db.scenarios.find()
start_dates, end_dates = get_starts_ends(scenarios_obj)

### Chat variables ###

chatbot_clients = {}

GLOBAL_CORRECTOR = T5ForConditionalGeneration.from_pretrained("Unbabel/gec-t5_small")
GLOBAL_TOKENIZER = T5Tokenizer.from_pretrained('t5-small')

# Turns per participant in each scenario, or character goal
turns = 5 # Not used currently
chargoal = 1000

# GPT model. Davinci is more advanced but takes longer time to respond and is way more expensive 
gpt_model = "text-davinci-003"
# gpt_model = "text-curie-001"

# bot's name
bot_name = "Alex"

# ------------------ #

# Decorators #

# check if user is logged in
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')
    return wrap

# check if route is accessed through redirect from another route
def redirect_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if request.referrer:
            return f(*args, **kwargs)
        else:
            return redirect('/dashboard/')
    return wrap


# ------------------ #

# Routes #

from user import routes    

@app.route('/')
def home():
    if 'logged_in' in session:
        return redirect('/dashboard')
    else:
        return render_template('home.html')

@app.route('/dashboard/')
@login_required
def dashboard():
    user = db.users.find_one({"_id": session['user']["_id"]})
    chats = user["chats"]
    todo = user["session_todo"]
    final_assess = False
    if "final_assessment" in user:
        final_assess = user["final_assessment"]
    chat_allowed = True
    # exclude session 0 (the pre-test) from the dashboard
    chats = {k: v for k, v in chats.items() if k != "session_0"}
    today = datetime.date.today()
    if todo != "":
        if chat_today(user):
            chat_allowed = False
    week_1 = {k: v for k, v in chats.items() if v['week']['number']==1}
    week_2 = {k: v for k, v in chats.items() if v['week']['number']==2}
    week_3 = {k: v for k, v in chats.items() if v['week']['number']==3}
    week_4 = {k: v for k, v in chats.items() if v['week']['number']==4}
    return render_template("dashboard.html", week_1=week_1, week_2=week_2, week_3=week_3, week_4=week_4, start_dates=start_dates, end_dates=end_dates,today=today, chat_allowed=chat_allowed, todo=todo, final_assess=final_assess)

@app.route("/profile/")
@login_required
def view_profile():
    user = db.users.find_one({"_id": session['user']["_id"]})
    return render_template("view_profile.html", user=user)

@app.route("/profile/edit")
@login_required
def profile():
    return render_template("profile.html", bot_name=bot_name)

@app.route("/start/")
@login_required
@redirect_required
def start_chat():
    # first, check if user has already done a chat today
    user = db.users.find_one({"_id":session['user']['_id']})
    if chat_today(user):
        return render_template("come_back_tomorrow.html", from_chat=True)
    chats = user['chats']
    session_id = user["session_todo"]
    user_id = user["_id"]
    condition = user["condition"]
    counter = 1
    if "attempt_"+str(counter) in chats[session_id]:
        counter = counter + 1
        attempt_id = "attempt_" + str(counter)
    else:
        attempt_id = "attempt_" + str(counter)
    start_time = datetime.datetime.now()
    file_handler = os.path.join(project_dir, "logs/chatbot_{user}.log".format(user=user_id))
    data = Dataset()

    if session_id == "session_0":
    # from the scenarios collection in db, get the prompt of the item with _id of "session_0"
        initial_prompt = (db.scenarios.find_one({"_id": session_id})["pre_scenario"] + "\nTeacher: " + db.scenarios.find_one({"_id": session_id})["scenario"] + "\n").format(botName = bot_name, studentName = user["name"])
    else:
    # in "session_id" id is an integer. split it and get the integer
        session_number = int(session_id.split("_")[1])
        previous_session = "session_" + str(session_number - 1)
    # we concatenate the previous session's summary with the prompt of the current session
        initial_prompt = chats[previous_session]["summary"] + ((db.scenarios.find_one({"_id": session_id})["pre_scenario"] + "\nTeacher: " + db.scenarios.find_one({"_id": session_id})["scenario"] + "\n").format(botName = bot_name, studentName = user["name"]))
    
    user_initial_message = db.scenarios.find_one({"_id": session_id})["scenario"].format(botName = bot_name, studentName = user["name"])

    ben = Ben(start_prompt=initial_prompt, dataset=data, furhat_on=False, furhat_IP=None, 
    turns=turns, gpt=gpt_model, corrector=GLOBAL_CORRECTOR, tokenizer=GLOBAL_TOKENIZER, chargoal=chargoal, condition=condition, errors={}, file_handler=file_handler) 
    chatbot_clients[session['user']['_id']] = [data, ben, user_id, session_id, attempt_id, start_time]
    logger.info("User %s started %s chat, %s", user_id, session_id, attempt_id)
    return render_template("chat.html", initial_message=user_initial_message, chargoal=chargoal) 

@app.route('/end/')
@login_required
def end_chat():
    counter = 0
    session_id = chatbot_clients[session['user']['_id']][3]
    attempt_id = chatbot_clients[session['user']['_id']][4]
    errors = db.users.find_one({"_id":session['user']['_id']})['chats'][session_id][attempt_id]['errors']
    dont_skip = {k:v for k,v in errors.items() if v["correction_type"] != "none"}
    corrective_fb = {k:v for k,v in errors.items() if v["correction_type"]=="corrective"}
    informative_fb = {k:v for k,v in errors.items() if v["correction_type"]=="informative"}
    combined_fb = {k:v for k,v in errors.items() if v["correction_type"]=="combined"}
    if session['user']['condition'] == "delayed":
        # make sure they can't see the report again
        counter = counter + 1
        if counter == 1:
            logger.info("User %s ended %s chat, showing report...", session['user']['_id'], session_id)
            return render_template("report.html", errors=dont_skip,corrective_fb=corrective_fb, informative_fb=informative_fb, combined_fb=combined_fb)
        else:
            logger.info("User %s tried to access report again, but was redirected to dashboard", session['user']['_id'])
            return redirect(("/dashboard"))
    else:
        logger.info("User %s ended %s chat, redirecting to dashboard", session['user']['_id'], session_id)
        return redirect("/dashboard")

# todo: restart chat button which restarts the same scenario

assessment_data = {}

@app.route("/final_assessment/", methods= ['GET', 'POST'])
@login_required
def final_assessment():
    if "final_assessment" not in db.users.find_one({"_id":session['user']['_id']}):
    # let's update the error db of the user 
        update_error_db(session['user'])
        final_assessment_sents = get_final_assessment_sentences(session['user'])
        assessment_data[session['user']['_id']] = {}
        assessment_data[session['user']['_id']]['start_time'] = datetime.datetime.now()
        assessment_data[session['user']['_id']]['counter'] = 0
        #sentences = ["I am a sentence", "cool, me too!"]
        for sentence in final_assessment_sents:
            assessment_data[session['user']['_id']][final_assessment_sents.index(sentence)] = {
                "sentence": sentence['sentence'],
            }
        print("Print from final_assessment: ")
        print(assessment_data)
        sentences = [x['sentence'] for x in final_assessment_sents]
        return render_template("final_assessment.html", sentences=sentences, tot=len(sentences))
    else:
        return render_template("come_back_tomorrow.html", from_final_assessment=True)

@app.route("/qualitative_assessment/")
@login_required
def qualitative_assessment():
    db.users.update_one({"_id": session['user']['_id']}, {"$set": {"final_assessment": True}})
    return render_template("qualitative_assessment.html")

@app.route("/goodbye/")
@login_required
def goodbye():
    change_password(session['user']['email'], "salvador")
    return redirect("/user/signout")


# ------------------ #

# Auxiliary routes #

@app.route('/dashboard/start/', methods=['POST'])
@login_required
def dashboard_chat():
    return redirect("/start/")

@app.route("/chat/get", methods=["GET", "POST"])
@login_required
def chatbot_response():
    msg = request.form["msg"]
    completed, turns, chars, errors, logs, response, correction = chatbot_clients[session['user']['_id']][1].send_and_recieve(str(msg), correct=True)
    user_id = chatbot_clients[session['user']['_id']][2]
    session_id = chatbot_clients[session['user']['_id']][3]
    attempt_id = chatbot_clients[session['user']['_id']][4]
    start_time = chatbot_clients[session['user']['_id']][5]
    end_time = datetime.datetime.now()
    duration = end_time - start_time 
    update_attempt(user_id=user_id, session_id=session_id, attempt_id=attempt_id, start_time = str(start_time), end_time=str(end_time), duration=str(duration), turns=turns, chars=chars, errors=errors, logs=logs, completed=completed)
    return {"data": response, "corr": str(correction)}

# later: todo: add waiting bot typing ...

@app.route('/chat/rate_good/')
@login_required
def rate_good():
    chatbot_clients[str(session['user']['_id'])][0].edit_rating(True)
    return ("nothing")

@app.route('/chat/rate_bad/')
@login_required
def rate_bad():
    chatbot_clients[str(session['user']['_id'])][0].edit_rating(False)
    return ("nothing")

@app.route('/final_assessment/get/<sentence>/<answer>/')
def go_to_next(sentence, answer):
    print(sentence)
    print(answer)
    final_assess_user = db.final_assessment.find_one({"_id": session['user']['_id']})
    final_assess_sents = final_assess_user["final_assessment_sentences"]
    final_assess_sents = [x['sentence'] for x in final_assess_sents]
    assessment_data[session['user']['_id']][final_assess_sents.index(sentence)]['answer'] = answer
    update_final_assessment(session['user']['_id'],sentence, answer)
    print("Print from finalassessment/get/sent/answ: ")
    print(assessment_data)
    #sentence = ""
    #answer = ""
    return ("nothing")

# ------------------ #

# Functions #

def chat_today(user):
    """ 
    This function checks if the user has already completed the chatbot today.

    params: user: the user object from the database
    """
    chats = user['chats']
    session_id = user["session_todo"]
    if session_id != "session_0":
    # check if previous session was completed in the same day
        previous_session = "session_" + str(int(session_id.split("_")[1]) - 1)
        if previous_session != "session_0":
            attempts = {k:v for k,v in chats[previous_session].items() if "attempt" in k}
            for v in attempts.values():
                if v["done"] == True and v["time"]["end"].split(" ")[0] == str(datetime.date.today()):
                    logger.info("User %s already completed %s chat today", user["_id"], previous_session)
                    return True


def session_done(user_id, session_id, turns, chars):
    """
    This function is used to update the user's chat completion status. 
    It is called when the user has finished a chat session and the chat attempt was successful.

    params: user_id: str, session_id: str, turns: int, chars: int
    """

    #if session.get("logged_in") == True: 
    filter = {"_id": user_id}
    if session_id != "session_12":
        session_todo = "session_" + str(int(session_id.split("_")[1])+1)
        newvalues = {
            "$set": {
                    "chats." + session_id + ".completion.status" : "done",
                    "chats." + session_id + ".completion.turns" : turns,
                    "chats." + session_id + ".completion.chars" : chars,
                    "session_todo": session_todo,
                    "chats." + session_todo + ".completion.status" : "todo"
            }
        }
    else: 
        session_todo = ""
        newvalues = {
                "$set": {
                    "chats." + session_id + ".completion.status" : "done",
                    "chats." + session_id + ".completion.turns" : turns,
                    "chats." + session_id + ".completion.chars" : chars,
                    "session_todo": session_todo,
                }
            }


    db.users.update_one(filter, newvalues)
    logger.info("User %s completed %s", user_id, session_id)
    return jsonify({"success": "Session updated successfully"}), 200
    # once session is saved, the user is redirected to the dashboard, which is updated [button with checkmark, and next session is yellow]

    
def update_attempt(user_id, session_id, attempt_id, logs, start_time, end_time, duration, turns, chars, completed, errors):
    """
    This function is used to save the user's chat attempt. 

    params: user_id: str, session_id: str, attempt_id: str, logs: dict, start_time: timestamp, end_time: timestamp, turns: int, chars: int, completed: bool, errors: dict
    """
    filter = {"_id": user_id}
    newvalues = {
            "$set": {
                "chats." + session_id + "." + attempt_id : {
                    "logs": logs,
                    "turns": turns,
                    "chars": chars,
                    "done": completed,
                    "errors": errors,
                    "time": {
                        "start": start_time,
                        "end": end_time,
                        "duration": duration
                    }
                }
            }
        }
    db.users.update_one(filter, newvalues)
        # if the attempt meets the criteria defined for completion (hence completed==True), update the completion status of the session
    if completed==True:
        session_done(user_id, session_id, turns, chars)
    logger.info("User %s: %s of %s saved successfully",user_id, attempt_id, session_id)
    return jsonify({"success": "Attempt saved successfully"}), 200

def update_final_assessment(user_id, sentence, answer):
    filter = {"_id": user_id}
    final_assessment_user = db.final_assessment.find_one(filter)
    final_assessment_sents = final_assessment_user["final_assessment_sentences"]
    for entry in final_assessment_sents:
        if entry['sentence'] == sentence:
            entry['final_assessment_answer'] = answer
            entry["time"] = str(datetime.datetime.now())
    db.final_assessment.update_one(filter, {"$set": {"final_assessment_sentences": final_assessment_sents}})

    return jsonify({"success": "Final assessment saved successfully"}), 200

def change_password(email, new_password):
    """
    Change the password of a user
    input: email, new_password
    output: None
    """
    # if there are more than one user with the same email, return "There are more than one user with this email: {}".format(email)
    # if there is no user with the email, return "There is no user with this email: {}".format(email)
    # if there is a user with the email, change the password to the new_password
    # return "Password changed successfully"

    if db.users.count_documents({"email": email}) > 1:
        return "There are more than one user with this email: {}".format(email)
    elif db.users.count_documents({"email": email}) == 0:
        return "There is no user with this email: {}".format(email)
    else:
        pass_hash = pbkdf2_sha256.hash(new_password)
        print(pass_hash)
        # update the password of the user with email, to pass_hash
        db.users.update_one({"email": email}, {"$set": {"password": pass_hash}})
        # print(db.users.find_one({"email": email}))
        return pass_hash, "Password changed successfully"
    
# ------------------ #
    
if __name__ == "__main__":
    app.run(port=5000)