#!/usr/bin/env python3
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from copy import deepcopy
from csv import DictReader
from io import StringIO
from os import getenv
from random import shuffle
from smtplib import SMTP_SSL
from traceback import print_exc
from types import SimpleNamespace

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# If this is family looking at this script, "oh hai."
# If you found this while you were interviewing me, this is just for kicks
gmail_user = getenv("GOOGLE_USER")
gmail_password = getenv("GOOGLE_PASSWORD")
google_sheet_id = getenv("GOOGLE_SHEET_ID")
google_oauth_file = getenv("GOOGLE_OAUTH_CREDS", './google_oauth.json')

if gmail_user is None or gmail_password is None or google_sheet_id is None or google_oauth_file is None:
    raise Exception("check your environmental variables and try again")

def send_email(gifter, giftee):
    from_line = f"From: {gmail_user}"
    to_line = f"To: {gifter.Email}"
    subject_line = 'Subject: Your Secret Maccabee information'
    blank_line = '\n'
    body = f"Hi {gifter.Name}!  Your Secret Macabee person is: {giftee.Name}"
    if not giftee.Attending:
        body += f"\nThis year they are not in person, their mailing address is:\n{giftee.Address}"

    body += '\nIf you have any problems questions, please let me know.'

    email_text = '\n'.join([from_line, to_line, subject_line, blank_line, body])

    try:
        server = SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, gifter.Email, email_text)
        server.quit()

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
    persons = []

    headers = ['Index', 'Name', 'Email', 'Attending', 'Participating', 'Address', 'Exclusions']
    reader = DictReader(buff, fieldnames=headers)

    # header validation:
    for index, col in enumerate(headers):
        assert col.strip().lower() == headers[index].strip().lower()


    for row in list(reader)[1:]:
        print(row)
        row_object = SimpleNamespace(**row)
        if row_object.Participating == 'YES':
            row_object.Index = int(row_object.Index)
            row_object.Exclusions = [int(val) for val in row_object.Exclusions.split(',')]
            row_object.Exclusions.append(row_object.Index)
            persons.append(row_object)
    return persons

def shuffle_groups(persons: list[SimpleNamespace]):
    for _ in range(1000):
        print(f"\niterating on index {_}")
        receivers = deepcopy(persons)
        givers = deepcopy(persons)
        shuffle(receivers)
        shuffle(givers)

        random_pairs = tuple(zip(receivers, givers))

        # Check every pair: not gifting to themselves and not in exclusion
        all_good = True
        for giver, receiver in random_pairs:
            print(f"giver: {giver.Name}, exclusions: {giver.Exclusions}, receiver: {receiver.Name}, {receiver.Index}")
            if receiver.Index in giver.Exclusions:
                all_good = False
                break

        if all_good:
            return random_pairs

if __name__ == '__main__':
    parser = ArgumentParser(description=f'''
    Secret Maccabee Shuffler and email sender.  Required environment variables:
    GOOGLE_USER - the username of the email sender
    GOOGLE_PASSWORD - password
    GOOGLE_SHEET_ID - the id of the secret maccabee google sheet
    GOOGLE_OAUTH_CREDS - service account credentials (they should probably replace the user/pass)
    ''',
    formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("--live", required=False, default=False, action='store_true',
                        help="build a little, test a little, learn alot")
    parser.add_argument("--nopause", required=False, default=False, action='store_true',
                        help='human in the loop incase mistakes are made')
    args = parser.parse_args()
    print(f"{args.__dict__}")

    persons = parse_input()
    random_pairs = shuffle_groups(persons)

    # for giver, receiver in random_pairs:
    #    print (f"# {giver.Name} gifts to {receiver.Name}")

    if args.live:
        if not args.nopause:
            input('Pausing for confirmation')

        for giver, receiver in random_pairs:
            send_email(giver, receiver)

    else:
        print("this was just a dry run!")

