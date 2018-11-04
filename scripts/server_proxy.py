#!/usr/bin/python

from __future__ import print_function
import cgi
import datetime
import json
import os
import re
import socket
import ssl
import sys
import time


FILE_NAME = 'server_proxy.py'
CONF_LOCATION = '/etc/piseccam/proxy_config.json'
READ_CHUNK_SIZE = 4096
NO_DATA_SLEEP_TIME = 0.1


def print_std(*args):
    """
    Writes ``args`` back to the client.
    """
    print(*args, sep=' ', end='', file=sys.stdout)


def print_err(*args):
    """
    Sends ``args`` to the server's error logs.
    """
    print('[{}] [{}]'.format(str(datetime.datetime.now()), FILE_NAME), *args, sep=' ', end='\n', file=sys.stderr)


def stop_with_error(error_string, code=500, code_tile='Internal Server Error'):
    """
    Sends the error code to the client. Wraps the ``error_string`` in a JSON
    object. Stops executing the CGI script.
    """
    print_std('Status: {} {}\r\n'.format(str(code), code_tile))
    print_std('Content-Type: application/json\r\n\r\n')
    print_std(json.dumps(dict(error_message=error_string)))
    sys.exit()


def parse_api_key():
    """
    Searches all headers for the the api key defined in the config json.
    :return: The header value or None if nothing was found.
    """
    for header_name, header_value in os.environ.iteritems():
        if header_name == config_json['api_key_header_name']:
            return header_value
    return None


def strip_status_code(buf):
    """
    Used to remove the HTTP status code returned from the MJPEG streamer. Since
    this is a CGI script, the host server will not like this being sent to the
    client.
    :param buf: The buffer to search.
    :return: A tuple with a flag indicating if the string was removed and the
             new buffer.
    """
    status_code_str = 'HTTP/1.1 200 OK\r\n'
    if buf.startswith(status_code_str):
        return True, buf[len(status_code_str):]
    return False, buf


def send_next_chunk(buf):
    """
    Finds the next Content-Length key and sends the next content chunk to the
    client, assuming buffer fully contains the length.
    :param buf: The buffer to search.
    :return: The buffer with any leading read portion removed.
    """
    result = re.search('\r\nContent-Length: (?P<length>\d+)\r\n\r\n', buf)
    if result:
        end_index = result.end() + int(result.group('length'))
        if len(buf) >= end_index:
            print_std(buf[:end_index])
            sys.stdout.flush()
            return buf[end_index:]
    return buf


def extract_fps():
    fps = cgi.FieldStorage().getvalue('fps', default=float(config_json['camera']['default_fps']))
    try:
        fps = float(fps)
    except Exception:
        print_err('Exception turning FPS into float. Falling back to config file default.')
        fps = float(config_json['camera']['default_fps'])
    return fps


def stream_camera():
    """
    Creates a socket connection to the camera address and port defined in the
    config file. Reads the data from this server and proxy's it to the client
    in chunks separated by the boundary.
    """
    conn = None
    try:
        fps = extract_fps()
        conn = ssl.wrap_socket(socket.socket(socket.AF_INET),
                               ca_certs=config_json['camera']['cert_location'],
                               cert_reqs=ssl.CERT_REQUIRED)
        conn.connect((config_json['camera']['network_address'], config_json['camera']['port']))
        conn.send('GET /stream?fps={} HTTP/1.1\r\n'.format(str(fps)) +
                  '{}: {}\r\n\r\n'.format(config_json['camera']['api_key_header_name'],
                                          config_json['camera']['api_key']))

    except Exception as e:
        print_err('Exception connecting to socket.', repr(e), e.message)
        stop_with_error('Failed to load stream.')

    try:
        buf = ''
        stripped_code = False
        no_data_time = None
        while True:
            received_data = conn.recv(READ_CHUNK_SIZE)
            if len(received_data) == 0:
                if no_data_time is None:
                    no_data_time = time.time()
                if time.time() - no_data_time > 1.0/fps + 1:
                    break
                time.sleep(NO_DATA_SLEEP_TIME)
            else:
                buf += received_data
                if not stripped_code:
                    stripped_code, buf = strip_status_code(buf)
                else:
                    no_data_time = None
                    buf = send_next_chunk(buf)
    except Exception as e:
        print_err('Exception reading from socket.', repr(e), e.message)


def main():
    api_key = parse_api_key()
    if api_key is None:
        print_err('Accessed without an API key.')
        stop_with_error('Unauthorized', 403, 'Forbidden')

    elif config_json['api_key'] is None or len(config_json['api_key']) == 0:
        print_err('No API key defined in the config file!')
        stop_with_error('Unauthorized', 403, 'Forbidden')

    elif not config_json['api_key'] == api_key:
        print_err('Accessed with a bad API key.')
        stop_with_error('Unauthorized', 403, 'Forbidden')

    else:
        stream_camera()


with open(CONF_LOCATION, 'r') as config_file:
    config_json = json.load(config_file)
    main()
