#!/usr/bin/python3
import sys
import argparse
import requests

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send Notifications via Telegram HTTP-Gateway', 
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-4', required=False, help="Address (v4)")
    parser.add_argument('-6', required=False, help="Address (v6)")
    parser.add_argument('-b', required=False, help="Author")
    parser.add_argument('-c', required=False, help="Comment")
    parser.add_argument('-d', required=False, help="Date")
    parser.add_argument('-e', required=False, help="Service Name")
    parser.add_argument('-f', required=False, help="From")
    parser.add_argument('-i', required=False, help="Icingaweb URL")
    parser.add_argument('-l', required=False, help="Hostname")
    parser.add_argument('-n', required=False, help="Hostdisplay Name")
    parser.add_argument('-o', required=False, help="Service Output")
    parser.add_argument('-r', required=False, help="User Email")
    parser.add_argument('-s', required=False, help="Service State")
    parser.add_argument('-t', required=False, help="Type")
    parser.add_argument('-u', required=False, help="Service Display Name")
    parser.add_argument('-v', required=False, help="Deprecated. Compability only. Has no Effect.")
    parser.add_argument('--target-port', default=6000, help="Target port on which Telegram Gateway is running")
    args = parser.parse_args()

    # build message # 
    serviceName = args.e
    if args.u:
        serviceName = args.u
    message = "*{service} {state} on {host}*\n{output}\Icingaweb: {url}".format(
                    service=serviceName, state=args.s, host=args.l, output=args.o, url=args.i)

    # create and send request #
    jsonPayload = { 'message'      : message           }
    headers     = { 'Content-Type' : 'application/json'}
    url = "http://localhost:{port}/send-all".format(port=args.target_port)
    requests.post(url, data=jsonPayload, headers=headers)
