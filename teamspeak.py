#!/usr/bin/python3
import ts3.query
import argparse
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Monitor Source Server', 
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--host', '-H', default="127.0.0.1", help='Target Teamspeak 3 Server')
    parser.add_argument('--port', '-p', type=int, default=10011, help='Target Port')
    parser.add_argument('--user', '-u', help='User to connect as')
    parser.add_argument('--password', '-P', help='Password for user')
    parser.add_argument('--use-ssh', action='store_const', default="telnet", const="ssh", 
                            help='Use SSH instead of telnet')
    args = parser.parse_args()

    userPassString = ""
    if args.user:
        if args.password:
            userPassString = "{}:{}@".format(args.user, args.password)
        else:
            userPassString = "{}@".format(args.user)

    connectionString = "{protocol}://{userPassString}@{server}:{port}".format(protocol=args.use_ssh,
                                                                                userPassString=userPassString,
                                                                                server=args.host,
                                                                                port=args.port)
    print(connectionString)
    try:
        with ts3.query.TS3ServerConnection(connectionString) as ts3conn:
            ts3conn.exec_("use", sid=1)
            clients = ts3conn.query("clientlist", "away", "uid").all()
    except ts3.query.TS3QueryError:
        print("error id 2568: insufficient client permissions", file=sys.stderr)
        sys.exit(1)
