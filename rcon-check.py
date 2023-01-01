#!/usr/bin/python3
import sys
import argparse
import subprocess
import os

PW_FILE="/etc/rcon.pass"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Monitor Source Server', 
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--host', '-H', default="127.0.0.1", help='Target Source-Server')
    parser.add_argument('--port', '-p', type=int, default=27015, help='Target Port')
    args = parser.parse_args()

    password = None
    try:
        with open(PW_FILE) as f:
            password = f.read().strip()
    except PermissionError as e:
        print("Insurgency CRITICAL - Permission Error on /etc/rcon.pass")
        sys.exit(1)
    except FileNotFoundError as e:
        print("Insurgency CRITICAL - Missing /etc/rcon.pass")
        sys.exit(1)

    cmd = [ "/usr/local/bin/rcon", "-P{}".format(password), "-a{}".format(args.host),
            "-p{}".format(args.port), "sm plugins info Skillbird" ]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
    if p.returncode != 0:
        print("Insurgency CRITICAL - {}".format(p.stdout))
        sys.exit(1)
    elif "not loaded" in p.stdout:
        print("Insurgency WARNING - {}".format(out))
        sys.exit(2)
    else:
        print("Insurgency OK")
        sys.exit(0)
