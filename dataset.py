import pandas as pd
import datetime
import os


class Dataset:
    def __init__(self):
        columns = ['timestamp','user', 'text', 'edits', 'error_idx', 'rating', 'error_obj', 'user_correction', 'correction_type']
        self.df = pd.DataFrame(columns=columns)       
        project_dir = os.getcwd()
        os.makedirs(os.path.join(project_dir, "data/"), exist_ok=True)
        print(project_dir+"/data", os.path.exists(project_dir+"/data"))
        self.filename = os.path.join(project_dir, "data", ("session-{date:%Y-%m-%d_%H%M%S}.csv".format(date=datetime.datetime.now())))
        print(self.filename)
       

    def add_row(self, timestamp, user, text, edits=None, error_idx=None, rating=None, error_obj=None, user_correction=None, correction_type=None):
        self.df.loc[len(self.df.index)] = [timestamp, user, text, edits, error_idx, rating, error_obj, user_correction, correction_type]
        

    def edit_rating(self, good):
        self.df.loc[self.df.index[-1], 'rating'] = good
        self.logs = self.save_csv()
        return self.logs


    def save_csv(self):
        dict_ = self.df.to_dict('index')
        return {str(k):v for k,v in dict_.items()}    


def dump_scenarios(_db, url):
    _df = pd.read_csv(url)
    _df = _df.astype(str)
    scenarios_list = _df.to_dict('records')
    _db.scenarios.delete_many({})
    _db.scenarios.insert_many(scenarios_list)
    return None


def dump_emails(_db):
    _df = pd.read_csv(os.getenv("ALLOWED_EMAILS_CSV"))
    _df = _df.astype(str)
    # make all the emails lowercase
    _df["email"] = _df["email"].str.lower()
    # make a list of email column
    emails_list = _df['email'].tolist()
    # put all 'email' and 'condition' in a tuple and make a list of tuples like [(email, condition), (email, condition)]
    email_condition_list = list(zip(_df['email'], _df['condition']))
    _df = _df.groupby('_id')['email'].apply(list).reset_index(name='emails')
    emails_dict = _df.to_dict('records')
    _db.emails_list.delete_many({})
    _db.emails_list.insert_many(emails_dict)
    return emails_list, email_condition_list

def get_emails(_db, classes):
    allowed_emails = []

    for c in classes:
        document = _db.emails_list.find_one({"_id": c})
        emails = document["emails"]
        allowed_emails.extend(emails)
    
    return allowed_emails

def get_starts_ends(scenarios):
    """
    Gets start and end date of each week  

    params: scenarios: dict
    returns: start_dates: list, end_dates: list
    """
    starts = []
    ends = []
    for scenario in scenarios:
        start = datetime.datetime.strptime(scenario["start_date"], "%y-%m-%d").date()
        end = datetime.datetime.strptime(scenario["end_date"], "%y-%m-%d").date()
        if start not in starts:
                starts.append(start)
        if end not in ends:
                ends.append(end)

    return starts, ends