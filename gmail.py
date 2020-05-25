import os
import re
from datetime import date

from apiclient import errors
from googleapiclient.discovery import build

import base64
from email.mime.text import MIMEText

# REGEX
IN_PAID_DESCRIPTION_RE = r"paid You (.*) Transfer Date and Amount: ([\w]* [0-9]*, [0-9]*) PDT"
OUT_PAID_DESCRIPTION_RE = r"You paid (.*) Transfer Date and Amount: ([\w]* [0-9]*, [0-9]*) PDT"
OUT_CHARGE_DESCRIPTION_RE = r"charged You (.*) Transfer Date and Amount: ([\w]* [0-9]*, [0-9]*) PDT"
IN_CHARGE_DESCRIPTION_RE = r"You charged (.*) Transfer Date and Amount: ([\w]* [0-9]*, [0-9]*) PDT"

OUT_COMPLETED_REQUEST_EMAIL_SUBJECT_RE = r"You completed (.*)'s \$(.*) charge request"
IN_REQUEST_EMAIL_SUBJECT_RE = r"(.*) completed your \$([0-9]*.[0-9]*) charge request"
IN_PAID_EMAIL_SUBJECT_RE = r"(.*) paid you \$([0-9]*.[0-9]*)"
OUT_PAID_EMAIL_SUBJECT_RE = r"You paid(.*) \$([0-9]*.[0-9]*)"


class GmailClient:
    def __init__(self, creds):
        self.service = build('gmail', 'v1', credentials=creds)
        self.in_description_res = [
            IN_PAID_DESCRIPTION_RE, IN_CHARGE_DESCRIPTION_RE]
        self.in_subject_res = [
            IN_PAID_EMAIL_SUBJECT_RE, IN_REQUEST_EMAIL_SUBJECT_RE]
        self.out_description_res = [
            OUT_PAID_DESCRIPTION_RE, OUT_CHARGE_DESCRIPTION_RE]
        self.out_subject_res = [
            OUT_COMPLETED_REQUEST_EMAIL_SUBJECT_RE, OUT_PAID_EMAIL_SUBJECT_RE]

    def send_message(self, user_id, message):
        """Send an email message.

        Args:
            service: Authorized Gmail API service instance.
            user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
            message: Message to be sent.

        Returns:
            Sent Message.
        """
        try:
            message = (self.service.users().messages().send(userId=user_id, body=message)
                       .execute())
            print('Message Id: %s' % message['id'])
            return message
        except errors.HttpError:
            print('An error occurred')

    def create_message(self, sender, to, subject, message_text):
        """Create a message for an email.

        Args:
            sender: Email address of the sender.
            to: Email address of the receiver.
            subject: The subject of the email message.
            message_text: The text of the email message.

        Returns:
            An object containing a base64url encoded email object.
        """
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

    def create_msg_labels(self, to_remove, to_add):
        """Create object to update labels.

        Returns:
            A label update object.
        """
        return {'removeLabelIds': to_remove, 'addLabelIds': to_add}

    def modify_message(self, user_id, msg_id, msg_labels):
        """Modify the Labels on the given Message.

        Args:
            service: Authorized Gmail API service instance.
            user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
            msg_id: The id of the message required.
            msg_labels: The change in labels.

        Returns:
            Modified message, containing updated labelIds, id and threadId.
        """
        #   try:
        message = self.service.users().messages().modify(userId=user_id, id=msg_id,
                                                         body=msg_labels).execute()

        label_ids = message['labelIds']

        print('Message ID: %s - With Label IDs %s' % (msg_id, label_ids))
        return message
        #   except errors.HttpError e:
        #     print('An error occurred')
        #     return None

    def list_messages_with_labels(self, user_id, label_ids=[]):
        """List all Messages of the user's mailbox with label_ids applied.

        Args:
            service: Authorized Gmail API service instance.
            user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
            label_ids: Only return Messages with these labelIds applied.

        Returns:
            List of Messages that have all required Labels applied. Note that the
            returned list contains Message IDs, you must use get with the
            appropriate id to get the details of a Message.
        """
        try:
            response = self.service.users().messages().list(userId=user_id,
                                                            labelIds=label_ids).execute()
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.service.users().messages().list(userId=user_id,
                                                                labelIds=label_ids,
                                                                pageToken=page_token).execute()
                messages.extend(response['messages'])

            return messages

        except errors.HttpError:
            print('An error occurred')
            return None

    def get_message_by_id(self, msg_id):
        return self.service.users().messages().get(userId='me', id=msg_id).execute()

    def get_critical_segments_from_message(self, msg_id, debug=False):
        result = self.get_message_by_id(msg_id)
        subject = result["payload"]["headers"][16]['value']
        snippet = result["snippet"]
        if debug:
            print("subject:", subject)
            print("snippet:", snippet)

        person = ""
        amt = 0
        descrip = ""
        charge_date = ""

        # extract outgoing $
        for pattern in self.out_subject_res:
            subject_match = re.search(pattern, subject)
            if subject_match:
                person = 'To: ' + subject_match.group(1)
                amt_string = subject_match.group(2)
                amt = float(amt_string.replace(',', ''))
                break

        for pattern in self.out_description_res:
            descrip_match = re.search(pattern, snippet)
            if descrip_match:
                descrip = descrip_match.group(1)
                charge_date = descrip_match.group(2)
                break

        # extract incoming $, recorded as a -amount
        for pattern in self.in_subject_res:
            subject_match = re.search(pattern, subject)
            if subject_match:
                person = 'From: ' + subject_match.group(1)
                amt_string = subject_match.group(2)
                amt = -float(amt_string.replace(',', ''))
                break

        for pattern in self.in_description_res:
            descrip_match = re.search(pattern, snippet)
            if descrip_match:
                descrip = descrip_match.group(1)
                charge_date = descrip_match.group(2)
                break

        return person, amt, descrip, charge_date
