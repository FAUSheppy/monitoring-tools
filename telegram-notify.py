#!/usr/bin/python3
import sys
import argparse
import requests

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send Notifications via Telegram HTTP-Gateway', 
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-4', '--ipv6', required=False, help="Address (v4)")
    parser.add_argument('-6', '--ipv4', required=False, help="Address (v6)")
    parser.add_argument('-b', '--author', required=False, help="Author")
    parser.add_argument('-c', '--comment', required=False, help="Comment")
    parser.add_argument('-d', '--date',         required=False, help="Date")
    parser.add_argument('-e', '--service-name', required=False, help="Service Name")
    parser.add_argument('-f', '--from',         required=False, help="From")
    parser.add_argument('-i', '--icingaweb-url', required=False, help="Icingaweb URL")
    parser.add_argument('-l', '--service-host',     required=False, help="Hostname")
    parser.add_argument('-n', '--service-host-alt', required=False, help="Hostdisplay Name")
    parser.add_argument('-o', '--service-output',   required=False, help="Service Output")
    parser.add_argument('-r', '--user-email',    required=False, help="User Email")
    parser.add_argument('-s', '--service-state', required=False, help="Service State")
    parser.add_argument('-t', '--service-type',  required=False, help="Type")
    parser.add_argument('-u', '--service-display-name', required=False, help="Service Display Name")

    parser.add_argument('-v', required=False, help="Deprecated. Compability only. Has no Effect.")
    parser.add_argument('--target-port', default=6000, help="Target port on which Telegram Gateway is running")
    args = parser.parse_args()

    # build message # 
    serviceName = args.service_name
    if args.service_display_name:
        serviceName = args.service_display_name

    # create and send request #
    url = "http://localhost:{port}/send-all-icinga".format(port=args.target_port)
    requests.post(url, json=vars(args))
