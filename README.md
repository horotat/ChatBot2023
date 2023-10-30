# Adaptive Chatbot for English Conversation Practice

| Alireza M. Kamelabad | |
| [alimk@kth.se](mailto:alimk@kth.se) | [alimk@ieee.org](mailto:alimk@ieee.org) |
| [ali.mk](https://ali.mk) | | 

<img src="https://ali.mk/assets/images/new-kth-logo.png" alt="KTH Logo" style="max-height: 150px; width: auto; margin-right: 10px;">
<img src="https://ali.mk/assets/images/eLADDA_logo.png" alt="e-LADDA Logo" style="max-height: 150px; width: auto;">

> If you got problems anywhere in the process, please [contact me](https://ali.mk/call).
{: .prompt}

## Repository

Access the code here: [`/horotat/ChatBot2023`](https://github.com/horotat/ChatBot2023)

or

```bash
git clone https://github.com/horotat/ChatBot2023.git
```

## Installation

To run the program properly you need an installation of [`conda`](https://www.anaconda.com/) (`anaconda` is suggested over `miniconda`). Once you have `conda` installed on your machine, follow the steps below.

### Requirements

First, you need to create a conda virtual environment. The packages and their dependecies are checked and are functional in `Ubuntu 22.04`, `Windows 11`, and `macOS ventura 13.0 arm64`.

Create a conda virtual environment and install packages from the `alice_env.yml` file.

```bash
conda env create -f env.yml
```

After the installation

#### **[Spacy](https://spacy.io/) Language Model**

We need to [download the `en` language model](https://spacy.io/api/cli#download) for [spacy](https://spacy.io/). To do so, run the following command in the terminal.

```bash
python -m spacy download en
```

#### Set Environmental Variables

In order for the system to work properly, you need to set the following environemnt variables in the system.

- `$OPENAI_API_KEY`: OpenAI API Key
    - Used in `webapp.py`
- `$FLASK_SECRET_KEY`: A random [Flask Secret Key](https://flask.palletsprojects.com/en/2.2.x/api/?highlight=secret%20key#flask.Flask.secret_key) to run the application.
    - Used in `webapp.py`
- `$ALLOWED_EMAILS_CSV`: Link to a CSV file that contains list of allowed emails to signup coupled with the class and condition. (e.g. `group, email, condition`)
    - Used in `dataset.py`

### Database

We used `mongodb` as our database. You can install it from [here](https://www.mongodb.com/try/download/community). After installation make sure that the `mongod` service is running.

### Server Configurations

Deployment of the application is done using `gunicorn` and `nginx`.

We used [these instructions](https://www.digitalocean.com/community/tutorials/how-to-set-up-password-authentication-with-nginx-on-ubuntu-22-04) to set a Password Authentication for the `nginx` server.

## Running the Chatbot

To run the chatbot, first activate the conda virtual environment by:

```bash
conda activate alice_env
```

Then, run the `webapp.py` file with the following terminal command:

```bash
FLASK_APP=webapp.py FLASK_ENV=development flask run
```

### Scenarios

The scenarios are feched from an online CSV. There is no automatic update for the scenarios. To update the scenarios, you need to run the `scenarios_update.py` file. To do so, run the following command in the terminal.

```bash
python scenarios_update.py
```
