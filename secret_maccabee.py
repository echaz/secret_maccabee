from copy import copy
from traceback import print_exc
from os import getenv
from random import shuffle
import smtplib
from invitee_groups import groups

# If this is family looking at this script, "oh hai."
# If you found this while you were interviewing me, this is just for kicks

# I dont have time to send personalized emails, plus I would screw it up
gmail_user = getenv("GMAILUSER")
gmail_password = getenv("GMAILPASSWORD")

def send_email(to_email, secret_maccabee_person, physical_address=None):
    from_line = f"From: {gmail_user}"
    to_line = f"To: {to_email}"
    subject_line = 'Subject: Your Secret Maccabee information'
    blank_line = '\n'
    body = f"Your Secret Macabee is: {secret_maccabee_person}"
    if physical_address:
        body += f"\nThis year they are not in person, their mailing address is:\n{physical_address}"

    email_text = '\n'.join([from_line, to_line, subject_line, blank_line, body])

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, to_email, email_text)
        server.close()

        print ('Email sent!')
    except:
        print ('oh noes!')
        print_exc()

# draw names for a secret santa, or the jewish variant "secret maccabee".
# TODO: gift recommendation
def validate_input():
    # input validation
    assert len(groups) == 2
    for group in groups:
        for person in group:
            assert len(person) == 3  # name, email, remote boolean
        for value in group:
            # consider these todos:
            assert value != "UNKNOWN"

    return shuffle_groups(groups[0], groups[1])


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
            if gifters[person_index][0] == recipients[person_index][0]:
                continue
            valid = True
            break
    if not valid:
        raise Exception("Unable to find a matching user set")
    return gifters, recipients

# since this guy is going to send emails, I'm going to not call main until I either have solid tests or have run this for a few years.
# consider this an example of how I'm calling this from ipython
if __name__ == '__main__':
    gifters, recipients = validate_input()

    # TODO: I think zip or something works better here
    for person_index in range(len(gifters)):
        print (f"# {gifters[person_index][0]} gifts to {recipients[person_index][0]}")
        print(f"send_email('{gifters[person_index][1]}','{recipients[person_index][0]}','{recipients[person_index][2]}')")

