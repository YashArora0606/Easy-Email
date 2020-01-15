# RecruiterEmailBot

1. Clone this repo.
2. Go to the Google Sheets template (link below) and go to `File-> Make a copy`
3. Add names of recruiters, emails and company name to this new copied csv!
4. Download the Google Sheet as a `.csv` and then RENAME it to `recruiter_raw_data.csv` and place into the repo folder.
5. run `python send_message.py` and the emails will be sent. (When you run it for the first time, a browser window will open asking you to login into your Gmail account)

# IMPORTANT
DELETE the csv file after running the python command! Don't run the `python send_message.py` command more than once for same csv or else it'll send multiple emails to the recruiter! Copy the template Google Sheets and start fresh each time!

https://docs.google.com/spreadsheets/d/1kBouZ-j4ytpQXi93KuPst8DfyONpV8irhwCCSukvdjM/edit?usp=sharing

# Client JSON
![Instruction](https://i.stack.imgur.com/ICIXt.png)

https://console.developers.google.com/start/api?id=gmail
