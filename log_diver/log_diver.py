from flask import Flask, render_template, request, url_for, jsonify, stream_with_context, Response
from flask_socketio import send, emit, disconnect, SocketIO
from urllib.parse import urlparse, urljoin

import subprocess, logging, json, ipaddress, socket
import secrets


application = Flask(__name__)
application.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(application, ping_timeout=300, ping_interval=300)


@application.route('/')
def index():
    return render_template('index.html')


@application.route('/googlemap')
def googlemap():
    google_maps = request.args.get('google_maps')
    if google_maps is None:
        google_maps = [
           ['U', 37.3519, -121.952, 0, '0.0.0.0', 'US SANTACLARA'],
        ];
    
    return render_template('googlemap.html', maps=google_maps)


def percentinize_(progress):
    return '{}%'.format(progress)


@socketio.on('log_diver')
def log_diver(data):
    REQUEST_HEADER = 1
    RESPONSE_HEADER = 2
    LOG = 3
    IMAGE_LOG = 4

    url = data['url']
    server_ip = data['server_ip']

    url_obj = urlparse(url)
    hostname = url_obj.hostname

    if not hostname:
        emit('log_diver', json.dumps({
            'type': 'error',
            'message': 'Invalid URL or input http(s)://',
        }))
        disconnect();
        return

    try:
        ipaddress.ip_address(hostname)
        emit('log_diver', json.dumps({
            'type': 'error',
            'message': 'Cannot input IP in URL',
        }))
        disconnect();
        return
    except ValueError:
        pass
    
    if server_ip:
        try:
            # IP Check to [ValueError]
            ipaddress.ip_address(server_ip)
            # Akamaized IP Check to [socket.gaierror]
            socket.gethostbyname('a' + server_ip.replace('.','-') +'.deploy.akamaitechnologies.com') 
        except ValueError:
            try:
                server_ip = socket.gethostbyname(server_ip)
                socket.gethostbyname('a' + server_ip.replace('.','-') +'.deploy.akamaitechnologies.com')
            except socket.gaierror:
                emit('log_diver', json.dumps({
                    'type': 'error',
                    'message': 'This hostname or ip isn\'t akamaized.',
                }))
                disconnect();
                return
        except socket.gaierror:
            emit('log_diver', json.dumps({
                'type': 'error',
                'message': 'Invalid IP.',
            }))
            disconnect();
            return
               
        new_url = '{}://{}{}{}{}{}'.format(url_obj.scheme, server_ip, url_obj.path, url_obj.params, url_obj.query, url_obj.fragment)
        pipe = subprocess.Popen(secrets.LSG_COMMAND_WITH_HOST.format(new_url, hostname), \
            shell=True, stdout=subprocess.PIPE)
    else:
        try:
            socket.gethostbyname('a' + socket.gethostbyname(hostname).replace('.','-') +'.deploy.akamaitechnologies.com')
        except socket.gaierror:
            emit('log_diver', json.dumps({
                'type': 'error',
                'message': 'Your hostname isn\'t akamaized, you can input akamaized IP or Hostname in \"Server IP\" textbox',
            }))
            disconnect();
            return

        pipe = subprocess.Popen(secrets.LSG_COMMAND.format(url), \
            shell=True, stdout=subprocess.PIPE)

    status = 0
    progress = ''
    request_header = ''
    response_header = ''
    logs = ''
    others = ''
    summery = [['U', 37.3519, -121.952, 0, '0.0.0.0', 'US SANTACLARA'],]
    while pipe.poll() is None:
        line = pipe.stdout.readline().decode('utf-8')

        if line.startswith("[Request Header]"):
            status = REQUEST_HEADER
            continue
        elif line.startswith("[Response Header]"):
            status = RESPONSE_HEADER
            continue
        elif line.startswith("[Log]"):
            status = LOG
            edge_log = line.split('] [')[1]
            location_log = line.split('] [')[2][:-2].split('|')

            if edge_log.startswith('image_server'):
                edge = 'I'
                ip_address = edge_log.split(' ')[1]
                summery.append([edge, location_log[1], location_log[2], 0, ip_address, location_log[0]])
                status = IMAGE_LOG
                others = "Image Logs"
            continue
        elif line.startswith("[Console]"):
            emit('log_diver', json.dumps({
                    'type': 'console',
                    'content': line.split("|")[1]
                }))
            continue
        elif line.startswith("[Progress]"):
            emit('log_diver', json.dumps({
                'type': 'progress',
                'content': line.split(" ")[1]
            }))
            continue


        if status == REQUEST_HEADER:
            if line.startswith("[/Request Header]"):
                emit('log_diver', json.dumps({
                    'type': 'request',
                    'content': request_header
                }))
            request_header = request_header + line
        elif status == RESPONSE_HEADER:
            if line.startswith("[/Response Header]"):
                emit('log_diver', json.dumps({
                    'type': 'response',
                    'content': response_header
                }))
            response_header = response_header + line
        elif status == LOG:    
            if line.startswith("[/Log]"):
                pass
            elif line.strip() != '':
                edge = ''
                ip_address = ''
                if edge_log.startswith('parent'):
                    edge = 'P'
                    ip_address = edge_log.split(' ')[1]
                elif edge_log.startswith('icp'):
                    edge = 'G'
                    ip_address = edge_log.split(' ')[1]
                else: # child
                    edge = 'C'
                    ip_address = edge_log              
                
                summery.append([edge, location_log[1], location_log[2], 0, ip_address, location_log[0]])
                # TODO: Log Time
                # times = line.split(' ')
                # total = int(times[4]) + int(times[5]) + int(times[6])
                # google_maps.append([google_map[0], google_map[1], google_map[2], total])
            
                logs = logs + line
        elif status == IMAGE_LOG:
            if line.startswith("[/Log]"):
                pass
            else:
                others = others + line

    emit('log_diver', json.dumps({
        'type': 'log',
        'content': logs,
        'others': others,
        'summery': str(summery)
    }))

    disconnect();

# import re
# from jinja2 import evalcontextfilter, Markup, escape

# _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')


# @application.template_filter()
# @evalcontextfilter
# def nl2br(eval_ctx, value):
#     result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
#         for p in _paragraph_re.split(escape(value)))
#     if eval_ctx.autoescape:
#         result = Markup(result)
#     return result
#test

if __name__ == "__main__":
    # application.run(host='0.0.0.0')
    socketio.run(application)
