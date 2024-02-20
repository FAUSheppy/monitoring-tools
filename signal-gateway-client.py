#!/usr/bin/python3
import sys
import argparse
import requests
import os

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Send Notifications via Atlantis Dispatcher', 
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # incident information #
    parser.add_argument('-4', '--ipv6',                 required=False, help="Address (v4)")
    parser.add_argument('-6', '--ipv4',                 required=False, help="Address (v6)")
    parser.add_argument('-b', '--author',               required=False, help="Author")
    parser.add_argument('-c', '--comment',              required=False, help="Comment")
    parser.add_argument('-d', '--date',                 required=False, help="Date")
    parser.add_argument('-e', '--service-name',         required=False, help="Service Name")
    parser.add_argument('-f', '--from',                 required=False, help="From")
    parser.add_argument('-i', '--icingaweb-url',        required=False, help="Icingaweb URL")
    parser.add_argument('-l', '--service-host',         required=False, help="Hostname")
    parser.add_argument('-n', '--service-host-alt',     required=False, help="Hostdisplay Name")
    parser.add_argument('-o', '--service-output',       required=False, help="Service Output")
    parser.add_argument('-r', '--user-email',           required=False, help="User Email")
    parser.add_argument('-s', '--service-state',        required=False, help="Service State")
    parser.add_argument('-t', '--service-type',         required=False, help="Type")
    parser.add_argument('-u', '--service-display-name', required=False, help="Service Display Name")

    # connection configuration #
    parser.add_argument('-w', '--target-port',  default=6000,        help="Signal Gateway Port")
    parser.add_argument('-x', '--target-host',  default="localhost", help="Signal Gateway Address")
    parser.add_argument('-y', '--target-proto', default="http",      help="Signal proto")

    # deprecated compability options FIXME: remove after Q1/2024 #
    parser.add_argument('-v', required=False, help="Deprecated. Compatibility only. Has no Effect.")

    # owners and groups to pass to smart send #
    parser.add_argument('--owners', nargs='+', required=False)
    parser.add_argument('--owner-groups', nargs='+', required=False)
    parser.add_argument('--legacy-gateway', default=False, required=False)
    parser.add_argument('--type', default="icinga", required=False)

    parser.add_argument('--dispatcher-pass-file', default="/etc/icinga2/dispatcher-pass-file.txt")

    args = parser.parse_args()

    # check pass file #
    user, password = (None, None)
    if os.path.isfile(args.dispatcher_pass_file) or os.path.islink(args.dispatcher_pass_file):
        with open(args.dispatcher_pass_file) as f:
            user, password = f.read().split()
            access_token = password # new style auth

    # build message # 
    serviceName = args.service_name
    if args.service_display_name:
        serviceName = args.service_display_name

    # create and send request #
    base_url = "{proto}://{host}:{port}/".format(host=args.target_host,
                    port=args.target_port,
                    proto=args.target_proto)

    if args.legacy_gateway:
        url = base_url + "/send-all-icinga"
        requests.post(url, json=vars(args))
    else:
        url = base_url + "/smart-send?dispatch-access-token={}".format(access_token)
        struct = {
            "users" : args.owners,
            "groups" : args.owner_groups,
            "data" : vars(args)
        }
        requests.post(url, json=struct, auth=(user, password))
