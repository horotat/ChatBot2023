# Adaptive Chatbot for English Conversation Practice

<img src="https://ali.mk/assets/images/new-kth-logo.png" alt="KTH Logo" style="max-height: 120px; width: auto; margin-right: 10px;">
<img src="https://ali.mk/assets/images/eLADDA_logo.png" alt="e-LADDA Logo" style="max-height: 120px; width: auto;">

| Alireza M. Kamelabad | |
| --- | --- |
| [ali.mk](https://ali.mk) | [alimk@kth.se](mailto:alimk@kth.se) |
| +46 8 790 9269 | [alimk@ieee.org](mailto:alimk@ieee.org) | 

> If you got problems anywhere in the process, please [contact me](https://ali.mk/call).

## Publication

The paper describing this work is published in **Frontiers in Education**:

> **Personalized Language Learning with an LLM Chatbot: Effects of Immediate vs. Delayed Corrective Feedback**
>
> Alireza M. Kamelabad, Beatrice Turano, Mattias Lundin, Gabriel Skantze
>
> *Frontiers in Education*, vol. 11, p. 1703664, Feb. 2026. Frontiers Media S.A.
>
> 🔗 DOI: [10.3389/feduc.2026.1703664](https://doi.org/10.3389/feduc.2026.1703664)

<details>
<summary><b>Abstract</b></summary>

The emergence of Large Language Models (LLMs) has opened new possibilities for language learning through conversational interaction with chatbots. Yet, little empirical evidence exists on how students experience such interactions and how corrective feedback should be provided. Research suggests that immediate corrective feedback is generally more effective than delayed feedback. Nevertheless, learners' perception of this effectiveness and their preferences for feedback timing, particularly in the domain of Computer-Assisted Language Learning (CALL), remain underexplored. This study investigates the feasibility of providing immediate feedback and examines the impact of feedback timing on user experience and grammar learning gains in English. An in-the-wild experiment was conducted with 66 L2 English learners, who integrated chatbot sessions into their English course as an extracurricular activity over one semester. Participants were randomly assigned to two groups receiving feedback either during or after the conversation. Findings reveal no significant difference in learning gains, but immediate feedback enhanced user experience, leading to overall positive perceptions of the chatbot. Additionally, we explore users' perceptions of the chatbot's social role and personality, offering a roadmap for future enhancements. These results provide valuable insights into the potential of LLMs and chatbots for language learning.

</details>

## Citation

If you use this work, please cite the paper using one of the formats below.

<details>
<summary><b>BibTeX</b></summary>

```bibtex
@article{m.kamelabad2026-PersonalizedLanguageLearning,
  title = {Personalized Language Learning with an {{LLM}} Chatbot: Effects of Immediate vs. Delayed Corrective Feedback},
  shorttitle = {Personalized Language Learning with an {{LLM}} Chatbot},
  author = {M. Kamelabad, Alireza and Turano, Beatrice and Lundin, Mattias and Skantze, Gabriel},
  year = 2026,
  month = feb,
  journal = {Frontiers in Education},
  volume = {11},
  pages = {1703664},
  publisher = {Frontiers Media S.A.},
  issn = {2504-284X},
  doi = {10.3389/feduc.2026.1703664},
  url = {https://www.frontiersin.org/articles/10.3389/feduc.2026.1703664/full},
  abstract = {The emergence of Large Language Models (LLMs) has opened new possibilities for language learning through conversational interaction with chatbots. Yet, little empirical evidence exists on how students experience such interactions and how corrective feedback should be provided. Research suggests that immediate corrective feedback is generally more effective than delayed feedback. Nevertheless, learners' perception of this effectiveness and their preferences for feedback timing, particularly in the domain of Computer-Assisted Language Learning (CALL), remain underexplored. This study investigates the feasibility of providing immediate feedback and examines the impact of feedback timing on user experience and grammar learning gains in English. An in-the-wild experiment was conducted with 66 L2 English learners, who integrated chatbot sessions into their English course as an extracurricular activity over one semester. Participants were randomly assigned to two groups receiving feedback either during or after the conversation. Findings reveal no significant difference in learning gains, but immediate feedback enhanced user experience, leading to overall positive perceptions of the chatbot. Additionally, we explore users' perceptions of the chatbot's social role and personality, offering a roadmap for future enhancements. These results provide valuable insights into the potential of LLMs and chatbots for language learning.},
  copyright = {Creative Commons Attribution 4.0 International},
  langid = {english},
}
```

</details>

<details>
<summary><b>APA 7</b></summary>

M. Kamelabad, A., Turano, B., Lundin, M., & Skantze, G. (2026). Personalized language learning with an LLM chatbot: Effects of immediate vs. delayed corrective feedback. *Frontiers in Education*, *11*, 1703664. https://doi.org/10.3389/feduc.2026.1703664

</details>

<details>
<summary><b>IEEE</b></summary>

A. M. Kamelabad, B. Turano, M. Lundin, and G. Skantze, "Personalized Language Learning with an LLM Chatbot: Effects of Immediate vs. Delayed Corrective Feedback," *Frontiers in Education*, vol. 11, p. 1703664, Feb. 2026, doi: 10.3389/feduc.2026.1703664.

</details>

<details>
<summary><b>ACM</b></summary>

Alireza M. Kamelabad, Beatrice Turano, Mattias Lundin, and Gabriel Skantze. 2026. Personalized Language Learning with an LLM Chatbot: Effects of Immediate vs. Delayed Corrective Feedback. *Frontiers in Education* 11 (Feb. 2026), 1703664. https://doi.org/10.3389/feduc.2026.1703664

</details>


## Repository

Access the code here: [`github.com/horotat/ChatBot2023`](https://github.com/horotat/ChatBot2023)

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
