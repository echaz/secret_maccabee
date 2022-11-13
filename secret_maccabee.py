from argparse import ArgumentParser
from copy import copy
from csv import reader
from io import StringIO
from os import getenv
from random import shuffle
from smtplib import SMTP_SSL
from traceback import print_exc

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials


# If this is family looking at this script, "oh hai."
# If you found this while you were interviewing me, this is just for kicks

# I dont have time to send personalized emails, plus I would screw it up
# TODO: I think I should be able to use the oauth creds to send email
gmail_user = getenv("GOOGLE_USER")
gmail_password = getenv("GOOGLE_PASSWORD")
google_sheet_id = getenv("GOOGLE_SHEET_ID")
google_oauth_file = getenv("GOOGLE_OAUTH_CREDS")

class Participant:
    def __init__(self, name, email, in_person, physical_address):
        self.name = name
        self.email = email
        self.in_person = in_person
        self.physical_address = physical_address

    def __repr__(self):
        return self.name

def send_email(to_email, secret_maccabee_person):
    from_line = f"From: {gmail_user}"
    to_line = f"To: {to_email}"
    subject_line = 'Subject: Your Secret Maccabee information'
    blank_line = '\n'
    body = f"Your Secret Macabee is: {secret_maccabee_person.name}"
    if not secret_maccabee_person.in_person:
        body += f"\nThis year they are not in person, their mailing address is:\n{secret_maccabee_person.address}"

    email_text = '\n'.join([from_line, to_line, subject_line, blank_line, body])

    try:
        server = SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, to_email, email_text)
        server.close()

        print ('Email sent!')
    except:
        print ('oh noes!')
        print_exc()

def download_sheet_as_csv(drive_file_id=google_sheet_id, creds=google_oauth_file):
    ''' download the google spreadsheet as a csv, and return the csv_string '''
    credentials = Credentials.from_service_account_file(creds)
    drive_service = build('drive', 'v3', credentials=credentials)
    csv_string = drive_service.files().export_media(fileId=drive_file_id, mimeType='text/csv').execute()
    return csv_string.decode('utf-8')


def parse_input():
    csv_string = download_sheet_as_csv()

    buff = StringIO(csv_string)

    csv_reader = reader(buff)
    headers = next(csv_reader)
    header_row = ['Name', 'email address', 'Will attend this year', 'Participating', 'Bender?', 'Address']

    # header validation:
    for index, col in enumerate(headers):
        assert col.strip().lower() == header_row[index].strip().lower()

    print('the file seems valid')

    group_1_list = []
    group_2_list = []
    for row in csv_reader:
        participating = row[3]

        if participating.lower() == "yes":
            # name, email, in_person, physical_address
            person = Participant(row[0], row[1], row[2], row[5])
            group_val = row[4]
            group_1 = group_val.strip().lower() == 'true'

            if group_1:
                group_1_list.append(person)
            else:
                group_2_list.append(person)

    return group_1_list, group_2_list


def shuffle_groups(group_1, group_2):
    # shuffle the groups, so we can do index matching:
    shuffle(group_1)
    shuffle(group_2)

    gifters = copy(group_1)
    gifters.extend(group_2)
    valid = False

    for _ in range(100):
        shuffle(group_1)
        shuffle(group_2)

        recipients = copy(group_2)
        recipients.extend(group_1)

        for person_index in range(len(gifters)):
            if gifters[person_index].name == recipients[person_index].name:
                continue
            valid = True
            break
    if not valid:
        raise Exception("Unable to find a matching user set")
    return gifters, recipients

# since this guy is going to send emails, I'm going to not call main until I either have solid tests or have run this for a few years.
# consider this an example of how I'm calling this from ipython
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--dry-run", type=bool, required=False, default=True,
                        help="build a little, test a little, learn alot")
    parser.add_argument("--pause", type=bool, required=False, default=True,
                        help='human in the loop incase mistakes are made')
    gifters, recipients = parse_input()

    args = parser.parse_args()
    groups = parse_input()
    gifters, recipients = shuffle_groups(*groups)

    if args.dry_run:
        for person_index in range(len(gifters)):
            print (f"# {gifters[person_index].name} gifts to {recipients[person_index]}")
            print(f"send_email('{gifters[person_index].email}','{recipients[person_index]}')")
    else:
        raise Exception(f"pause is {args.pause}")
