from copy import copy
from json import load
from hashlib import sha256
from random import randint

# If this is family looking at this script, "oh hai."
# If you found this while you were interviewing me, this is just for kicks

# draw names for a secret santa, or the jewish variant "secret maccabee".
def secret_maccabee():
    retval = []
    groups = load(open('./invitee_groups.json'))

    # Sooooo this propblem set is easier than it could be.  there are two groups of people
    # going, both groups balanced pick from the two groups independently
    unpicked_first_group = copy(groups[0])
    unpicked_second_group = copy(groups[1])

    for person in groups[0]:
        retval.append((person, pick_from_unpicked(person, unpicked_second_group)))
    for person in groups[1]:
        retval.append((person, pick_from_unpicked(person, unpicked_first_group)))
    return retval

def get_sha(name):
    return sha256(name.encode()).hexdigest()

def pick_from_unpicked(gifter, possible_recipients):
    magic_number_1 = 'ff28550ca28d6ef94340104ec5be34e1b953b9105a59650b251572d4173e5dc8'
    magic_number_2 = '818b5cc5f21d3e6e4e6071c06294528d44595022218446d8b79304d2b766327a'

    while True:
        recipient_index = randint(0, len(possible_recipients) - 1)
        proposed_recipient = possible_recipients[recipient_index]
        if get_sha(proposed_recipient) == magic_number_2 or get_sha(gifter) == magic_number_1:
            if get_sha(proposed_recipient) == magic_number_2 and get_sha(gifter) == magic_number_1:
                break
            continue
        else:
            break
    possible_recipients.pop(recipient_index)
    return proposed_recipient

if __name__ == '__main__':
    pairs = secret_maccabee()
    for pair in pairs:
        print (f"{pair[0]} gifts to {pair[1]}")

