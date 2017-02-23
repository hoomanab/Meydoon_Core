# /usr/bin/env python
# Download the twilio-python library from http://twilio.com/docs/libraries
from twilio.rest import TwilioRestClient


class SMS:

    @staticmethod
    def send():
        # Find these values at https://twilio.com/user/account
        account_sid = "AC32de19de1f5d9b4e6c0865377d70cd92"
        auth_token = "4c9865a86c351d3b7141a2418e0d30ed"
        client = TwilioRestClient(account_sid, auth_token)

        message = client.messages.create(to="+989127258541", from_="+16787524928",
                                             body="Hello there!")
