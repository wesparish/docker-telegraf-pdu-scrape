#!/usr/bin/env python3
from __future__ import print_function

from __future__ import absolute_import

import argparse, gc, json, logging, os, sys, re, getpass, time
import pexpect

try:
    raw_input
except NameError:
    raw_input = input

COMMAND_PROMPT = 'cli>'
TERMINAL_PROMPT = r'(?i)terminal type\?'
TERMINAL_TYPE = 'vt100'
SSH_NEWKEY = '(?i)are you sure you want to continue connecting'

def sendline_delay(child, text_to_send, delay=0.005):
    child.send(text_to_send)
    child.send("\r\n")

def main():
    global COMMAND_PROMPT, TERMINAL_PROMPT, TERMINAL_TYPE, SSH_NEWKEY

    parser = argparse.ArgumentParser(description='Collect information from a Dell Smart PDU via SSH')
    parser.add_argument('host', nargs='*', default=os.getenv('PDU_SCRAPE_HOSTS', '').split(','),
                        help='PDU host/IP with SSH enabled')
    parser.add_argument('--user', default='admin',
                        help='SSH username, default: admin')
    parser.add_argument('--password', default='admin',
                        help='SSH password, default: admin')
    parser.add_argument('--verbose', default=False, action="store_true",
                        help='Toggle verbose output')

    args = parser.parse_args()

    if args.verbose:
      logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                          stream=sys.stdout,
                          level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')))
    else:
      logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                          filename="%s.log" % (os.path.basename(__file__)),
                          level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')))

    logging.info("Host list: %s" % (args.host))
    logging.info("SSH User: %s" % (args.user))
    logging.info("SSH Password: %s" % (args.password))

    user = args.user
    password = args.password
    for host in args.host:
        try:
            child = pexpect.spawn('ssh -l %s %s'%(user, host), timeout=2)
            i = child.expect([pexpect.TIMEOUT, SSH_NEWKEY, COMMAND_PROMPT, 'password'])
            if i == 0:
                logging.info('ERROR! could not login with SSH. Here is what SSH said:')
                logging.info(child.before, child.after)
                logging.info(str(child))
                sys.exit (1)
            if i == 1:
                sendline_delay (child, 'yes')
                child.expect ('password')
            if i == 2:
                pass
            if i == 3:
                child.sendline(password)
    
            readings = {'host': host, 'data': {}}
        
            sendline_delay (child, 'devReading power')
            i = child.expect ('Success\\r\\n([\d.]*)\s+kW')
            if i != 0:
              logging.info("Timed out, child.before: %s\nchild.after:%s" % (child.before, child.after))
              sys._exit(1)
            readings['data']['dev_reading_power'] = float(child.match.group(1).decode('utf-8'))
            logging.info("readings: %s" % readings)
    
            sendline_delay (child, 'devReading energy')
            i = child.expect ('Success\\r\\n([\d.]*)\s+kWh')
            if i != 0:
              logging.info("Timed out, child.before: %s\nchild.after:%s" % (child.before, child.after))
              sys._exit(1)
              sys._exit(1)
            readings['data']['dev_reading_energy'] = float(child.match.group(1).decode('utf-8'))
            logging.info("readings: %s" % readings)
        
            sendline_delay (child, 'phReading all current')
            i = child.expect ('Success\\r\\n1:\s+(\d.*) A')
            if i != 0:
              logging.info("Timed out, child.before: %s\nchild.after:%s" % (child.before, child.after))
              sys._exit(1)
              sys._exit(1)
            readings['data']['phreading_all_current'] = float(child.match.group(1).decode('utf-8'))
            logging.info("readings: %s" % readings)
        
            sendline_delay (child, 'phReading all voltage')
            i = child.expect ('Success\\r\\n1:\s+(\d.*) V')
            if i != 0:
              logging.info("Timed out, child.before: %s\nchild.after:%s" % (child.before, child.after))
              sys._exit(1)
              sys._exit(1)
            readings['data']['phreading_all_voltage'] = float(child.match.group(1).decode('utf-8'))
            logging.info("readings: %s" % readings)
    
            sendline_delay (child, 'phReading all power')
            i = child.expect ('Success\\r\\n1:\s+(\d.*) kW')
            if i != 0:
              logging.info("Timed out, child.before: %s\nchild.after:%s" % (child.before, child.after))
              sys._exit(1)
              sys._exit(1)
            readings['data']['phreading_all_power'] = float(child.match.group(1).decode('utf-8'))
            logging.info("readings: %s" % readings)
    
            sendline_delay (child, 'exit')
            index = child.expect([pexpect.EOF, "(?i)there are stopped jobs"])
            if index==1:
                child.sendline("exit")
                child.expect(EOF)
    
            print(json.dumps(readings))
        except Exception as ex:
            logging.error("caught exception: %s" % ex)
        finally:
            del child
            gc.collect()

if __name__ == "__main__":
    main()
