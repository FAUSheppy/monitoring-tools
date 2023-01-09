#!/usr/bin/python3

import smtplib, ssl
import requests
import sys
import secrets
import datetime
import argparse
import socket
import time
import imaplib
import json

args = None

def exit(status, info):

    content = { "service" : args.monitoring_service_name,
				"status" : status,
				"token" : args.monitoring_token,
				"info" : info }

    r = requests.post(args.monitoring_server, json=content)
    print(r.content)
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Email STMP/IMAP Monitor',
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--target",    required=True, help="Target Server to check")
    parser.add_argument("--sender",    required=True, help="Sender Email to use")
    parser.add_argument("--receiver",  required=True, help="Receiver Mail (must exits on target)")
    parser.add_argument("--imap-user",                help="IMAP User for receiver Mail")
    parser.add_argument("--imap-pass", required=True, help="IMAP Password for receiver Mail")
    parser.add_argument("--port",      default=587,   help="Target (START_TLS) port")
    parser.add_argument("--monitoring-server", required=True)
    parser.add_argument("--monitoring-token", required=True)
    parser.add_argument("--monitoring-service-name", required=True)

    args = parser.parse_args()

    imap_user = args.imap_user
    if not imap_user:
        imap_user = args.receiver

    challenge = {
        "time" : datetime.datetime.now().timestamp(),
        "token" : secrets.token_urlsafe(),
        "origin" : socket.gethostname(),
    }

    message = message = 'Subject: Monitoring Challenge\n\n{}'.format(json.dumps(challenge))

    context = ssl.create_default_context()

    # send mail #
    server = smtplib.SMTP(args.target, args.port)
    server.starttls(context=context)
    server.sendmail(args.sender, args.receiver, message)

    # give server some time to deliver #
    time.sleep(5)

    # check imap #
    for x in range(0,5):

        with imaplib.IMAP4_SSL(args.target) as imap:
            imap.login(imap_user, args.imap_pass)
            imap.select('INBOX')
            status, messages = imap.search(None, 'ALL')

            # check search status #
            if not status == "OK":
                exit("CRITICAL", "IMAP search failed")

            for message in messages[0].split(b' '):

                status, data = imap.fetch(message, '(RFC822)')

                # check search status #
                if not status == "OK":
                    exit("CRITICAL", "IMAP fetch failed")

                # parse mail
                info = None
                body = None

                # ignore badly formated messages #
                try:
                    body = data[0][1].decode("utf-8").split("\r\n")[-2]
                except IndexError:
                    continue

                # ignore badly formated messages (json-body) #
                try:
                    info = json.loads(body)
                except json.decoder.JSONDecodeError:
                    continue

                # ignore mail if it's not ours otherwise cleanup #
                if info["origin"] != challenge["origin"]:
                    continue
                else:
                    imap.store(message, '+FLAGS', '\\Deleted')

                if info["token"] == challenge["token"]:
                    exit("OK", "")

            imap.logout()

        # backoff and try again #
        time.sleep(10)

    # if we didn't find anything #
    exit("CRITICAL", "Challange not found via IMAP")
