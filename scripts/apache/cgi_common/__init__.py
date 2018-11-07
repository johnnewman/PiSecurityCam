from __future__ import print_function
import config
import controller
import datetime
import json
import os
import sys

CONFIG_LOCATION = '/etc/piseccam/proxy_config.json'

cgi_config = config.CGIConfig(CONFIG_LOCATION)
controller = controller.CameraController(CONFIG_LOCATION)


def std(*args):
    """
    Writes ``args`` back to the client.
    """
    print(*args, sep=' ', end='', file=sys.stdout)


def err(*args):
    """
    Sends ``args`` to the server's error logs.
    """
    print('[{}] [{}]'.format(str(datetime.datetime.now()), __name__), *args, sep=' ', end='\n', file=sys.stderr)


def stop_with_error(error_string, code=500, code_title='Internal Server Error'):
    """
    Sends the error code to the client. Wraps the ``error_string`` in a JSON
    object. Stops executing the CGI script.
    """
    send_response(dict(error_message=error_string), code, code_title)
    sys.exit()


def send_response(json_dict, code=200, code_title='OK'):
    std('Status: {} {}\r\n'.format(str(code), code_title))
    if json_dict is not None:
        std('Content-Type: application/json\r\n\r\n')
        std(json.dumps(json_dict))


def parse_api_key():
    """
    Searches all headers for the the api key defined in the config json.
    :return: The header value or None if nothing was found.
    """
    for header_name, header_value in os.environ.iteritems():
        if header_name == cgi_config.api_key_header_name:
            return header_value
    return None


def verify_api_key():
    api_key = parse_api_key()
    if api_key is None:
        err('Accessed without an API key.')
        send_response('Unauthorized', 403, 'Forbidden')

    elif cgi_config.api_key is None or len(cgi_config.api_key) == 0:
        err('No API key defined in the config file!')
        send_response('Unauthorized', 403, 'Forbidden')

    elif not cgi_config.api_key == api_key:
        err('Accessed with a bad API key.')
        send_response('Unauthorized', 403, 'Forbidden')

    else:
        return True
    return False
