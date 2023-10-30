from dataset import dump_scenarios, dump_emails
import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client.chat_users


def main():
    dump_scenarios(db, "https://docs.google.com/spreadsheets/d/e/2PACX-1vRrkBnC6bHeJHyN_hYFmwv4igWHiorOfuQpHV003UJqefBL3yAXoyQRnc3B-E9DeJVdol_bexLuGaZc/pub?gid=0&single=true&output=csv")

    dump_emails(db)


# the main function
if __name__ == "__main__":
    main()