# IMPORTS
import os
from datetime import datetime

from google.oauth2.credentials import Credentials

from db import ExpenseTableClient
from categorizer import Categorizer
from gmail import GmailClient

# CONSTANTS
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.modify']
UNLOGGED_LABEL = 'Label_8466755183052397706'
LOGGED_LABEL = 'Label_6979961476018667396'

date_mapping = {
    '1': '01',
    '2': '02',
    '3': '03',
    '4': '04',
    '5': '05',
    '6': '06',
    '7': '07',
    '8': '08',
    '9': '09',
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12',
}


class ExpenseClient:
    def __init__(self, local_creds=None):
        self.categorizer = Categorizer()
        self.mail_client = None
        self.expense_table_client = ExpenseTableClient(
            os.environ.get('DO_NOT_COMMIT_NOTION_TOKEN'),
            os.environ.get('NOTION_PAGE_URL'),
            os.environ.get('TABLE_URL')
        )

        if local_creds:
            creds = local_creds
        else:
            # SENSITIVE VARS
            token = os.environ.get('DO_NOT_COMMIT_GMAIL_TOKEN')
            refresh_token = os.environ.get('DO_NOT_COMMIT_GMAIL_REFRESH_TOKEN')
            token_uri = os.environ.get('DO_NOT_COMMIT_GMAIL_TOKEN_URI')
            client_id = os.environ.get('DO_NOT_COMMIT_GMAIL_CLIENT_ID')
            client_secret = os.environ.get('DO_NOT_COMMIT_GMAIL_CLIENT_SECRET')

            creds = Credentials(token, refresh_token=refresh_token, token_uri=token_uri,
                                client_id=client_id, client_secret=client_secret, scopes=GMAIL_SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                msg_to_send = self.create_message(
                    'Notion Expense Tracker',
                    os.environ.get('TARGET_EMAIL'),
                    'Notion expense tracker: need to refresh token',
                    'Your friendly Notion Expense Tracker'
                )

                self.send_message('me', msg_to_send)
        else:
            self.mail_client = GmailClient(creds)

    def get_messages_with_label(self, label_ids):
        return self.mail_client.list_messages_with_labels('me', label_ids=label_ids)

    def update_msg_label(self, msg_id):
        # updates labels from Venmo -> Unlogged to Venmo after processing
        to_remove = [UNLOGGED_LABEL]
        to_add = [LOGGED_LABEL]
        msg_labels = self.mail_client.create_msg_labels(to_remove, to_add)
        res = self.mail_client.modify_message('me', msg_id, msg_labels)

    def log_venmo_transactions(self, debug=False):
        # Call the Gmail API
        msgs = self.get_messages_with_label([UNLOGGED_LABEL])
        for msg in msgs:
            msg_id = msg['id']
            person, amt, descrip, charge_date = self.mail_client.get_critical_segments_from_message(
                msg_id, debug)
            if debug:
                print('person:', person)
                print('amt:', amt)
                print('descrip:', descrip)
                print('charge date:', charge_date)
                print('-------')

            if amt and descrip:

                date_arr = charge_date.replace(',', '').split(' ')
                if debug:
                    print(date_arr)

                assert len(date_arr) == 3
                month = date_mapping[date_arr[0]]
                optional_day = date_arr[1]
                day = date_mapping[optional_day] if optional_day in date_mapping else optional_day
                processed_charge_date = datetime.strptime(month + '-' + day + '-' +
                                                          date_arr[2], "%m-%d-%Y")

                category_label = self.categorizer.predict(descrip)  # TODO
                category = self.expense_table_client.categories[category_label]
                self.expense_table_client.add_expense(
                    [category], amt, 'Venmo', processed_charge_date, expense=descrip, additional=person)

            self.update_msg_label(msg_id)

            # reset values
            amt = 0
            descrip = ""

# first_msg = msgs[0]
# msg_id = first_msg['id']
# result = service.users().messages().get(userId='me', id=msg_id).execute()
# # print(result["payload"]["snippet"])
# # print(result["snippet"])

# subject = result["payload"]["headers"][16]['value']
# print(subject)

# for i, item in enumerate(result["payload"]["headers"]):
#     print(i, item)

# results = service.users().labels().list(userId='me').execute()
# labels = results.get('labels', [])

# if not labels:
#     print('No labels found.')
# else:
#     print('Labels:')
#     for label in labels:
#         print(label['name'])


# results = service.users().messages().list(userId='me', labelIds=[LOGGED_LABEL]).execute()
# # print(results)
# msgs = results.get('messages', [])
# # print(len(msgs))
# first_msg = msgs[0]


# if descrip:
#     descrip_arr = descrip.lower().split()
#     for token in descrip_arr:
#         if token not in bag_of_words:
#             bag_of_words[token] = 0
#         bag_of_words[token] += 1
# res = [(k, v)
#         for k, v in sorted(bag_of_words.items(), key=lambda item: item[1], reverse=True)]
# print(res)
