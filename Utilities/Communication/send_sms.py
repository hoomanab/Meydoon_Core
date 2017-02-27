# -*- coding: utf8 -*-

import requests
import urllib

class SMS:

    @staticmethod
    def send(phone_number, ver_code):
        message = "کاربر عزیز میدون،" + "\n"\
                  + "این کد برای تایید شماره تلفن شما است:" + "\n" + str(ver_code)
        message = urllib.urlencode(message)

        request = requests.post("https://api.kavenegar.com/v1/"
                                + "2B2F762F45696A3043654478734C4A4D4F4E4E4138773D3D"
                                + "/sms/send.json"
                                + "?receptor=" + str(phone_number)
                                + "&message=" + message
                                )
        print(str(request.text))
