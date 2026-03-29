#!/usr/bin/python3

import yaml
import os
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


def report(args, status, info):

    try:
        content = {
            "service": args.monitoring_service_name,
	    	"status": status,
	    	"token": args.monitoring_server_token,
	    	"info": info
        }

        # check for auth params #
        if "monitoring_server_user" in args:
            auth = (args.monitoring_server_user, args.monitoring_server_pass)
        else:
            auth = (None, None)

        r = requests.post(args.monitoring_server, json=content, auth=auth)
        print(f"Report: {args.imap_target} [{status}] - {info}", file=sys.stderr)
        r.raise_for_status()

    except requests.RequestException as e:
        print(f"Warning: Report failed {e}", file=sys.stderr)

def send_and_check(args):

    if "imap_user" not in args:
        imap_user = args.receiver_email
    else:
        imap_user = args.imap_user

    challenge = {
        "time" : datetime.datetime.now().timestamp(),
        "token" : secrets.token_urlsafe(),
        "origin" : socket.gethostname(),
    }

    message = 'From: {}\nTo: {}\nSubject: Monitoring Challenge\n\n{}'.format(
                    args.smtp_sender_email, args.receiver_email, json.dumps(challenge))

    context = ssl.create_default_context()

    # send mail #
    server = smtplib.SMTP(args.smtp_sender_server, args.smtp_sender_server_port)
    server.starttls(context=context)
    if args.smtp_sender_pass:
        server.login(args.smtp_sender_email, args.smtp_sender_pass)

    test = server.sendmail(args.smtp_sender_email, args.receiver_email, message)

    # give server some time to deliver #
    time.sleep(5)

    # check imap #
    for x in range(0,5):

        imap_target = args.imap_target or args.target_server
        
        with imaplib.IMAP4_SSL(imap_target) as imap:

            imap.login(imap_user, args.imap_pass)
            imap.select('INBOX')
            status, messages = imap.search(None, 'ALL')

            # check search status #
            if not status == "OK":
                report_and_exit(args, "CRITICAL", "IMAP search failed")

            try:
                for message in messages[0].split(b' '):

                    if not message:
                        time.sleep(0.1)
                        continue

                    status, data = imap.fetch(message, '(RFC822)')

                    # check search status #
                    if not status == "OK":
                        report(args, "CRITICAL", "IMAP fetch failed")

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
                        report(args, "OK", "")
                        return
                    
                    # backoff and try again #
                    time.sleep(10)

            finally:
                imap.expunge()
                imap.logout()


    # if we didn't find anything #
    report(args, "CRITICAL", "Challenge not found via IMAP")
    return


if __name__ == "__main__":

    DEBUG = os.getenv("ENABLE_DEBUG") == 1

    with open("config.yaml") as f:

        config = yaml.safe_load(f)

        index = 0
        for element in config:

            element |= os.environ

            if type(element) != dict:
                print(f"Config at index {index} is not a valid config struct", file=sys.stderr)
                continue
            if "imap_target" not in element:
                print(f"Config struct at {index} is missing field 'imap_target'", file=sys.stderr)
                continue

            try:
                args = argparse.Namespace(**element)
                print(f"Checking: {args.imap_target}", file=sys.stderr)
                send_and_check(args)
            except AttributeError as e:
                print(f"Error during check for {args.imap_target}: {e}", file=sys.stderr)
                continue



