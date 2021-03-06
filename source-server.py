#!/usr/bin/python3
import valve.source.a2s
from valve.source import NoResponseError
import sys
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Monitor Source Server', 
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--host', '-H', default="127.0.0.1", help='Target Source-Server')
    parser.add_argument('--port', '-p', type=int, default=27015, help='Target Port')
    args = parser.parse_args()

    try:
        with valve.source.a2s.ServerQuerier((args.host, args.port)) as server:
            print("{} players".format(server.info()["player_count"]))
            sys.exit(0)
    except NoResponseError:
        print("No Response from Server")
    except Exception as e:
        print("Error: {}".format(e))
    
    sys.exit(1)
