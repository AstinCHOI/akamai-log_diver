from flask import Flask, render_template, request, url_for, jsonify, stream_with_context, Response
from flask_socketio import send, emit, SocketIO
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
           ['E', 37.3519, -121.952, 0, '0.0.0.0', 'US SANTACLARA'],
        ];
    
    return render_template('googlemap.html', maps=google_maps)


# TODO: Code refactoring
# TODO: change + to .format
@socketio.on('log_diver')
def log_diver(data):
    REQUEST_HEADER = 1
    RESPONSE_HEADER = 2
    LOG = 3
    IMAGE_LOG = 4
    
    url_obj = urlparse(data['url'])
    hostname = url_obj.hostname
    if not hostname:
        # TODO: EMIT with error message / submit button enable / socket close
        return

    server_ip = data['server_ip']
    if server_ip:
        try:
            ipaddress.ip_address(server_ip)
            socket.gethostbyname('a' + server_ip.replace('.','-') +'.deploy.akamaitechnologies.com')
        except ValueError:
            try:
                socket.gethostbyname('a' + socket.gethostbyname(server_ip).replace('.','-') +'.deploy.akamaitechnologies.com')
            except socket.gaierror:
                # TODO: EMIT with error message / submit button enable / socket close
                return
        except socket.gaierror:
            # TODO: EMIT with error message / submit button enable / socket close
            return
               
        new_url = '{}://{}{}{}{}{}'.format(url_obj.scheme, server_ip, url_obj.path, url_obj.params, url_obj.query, url_obj.fragment)
        pipe = subprocess.Popen(secrets.LSG_COMMAND_WITH_HOST.format(new_url, hostname), \
            shell=True, stdout=subprocess.PIPE)
    else:
        pipe = subprocess.Popen(secrets.LSG_COMMAND.format(data['url']), \
            shell=True, stdout=subprocess.PIPE)


    status = 0
    progress = ''
    request_header = ''
    response_header = ''
    logs = ''
    summery = [['E', 37.3519, -121.952, 0, '0.0.0.0', 'US SANTACLARA'],]
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
            continue
        elif line.startswith("\rProgress:"):
            progress = line.split(' ')[1]
            emit('log_diver', json.dumps({
                'type': 'progress',
                'progress': progress,
            }))
            continue

        if status == REQUEST_HEADER:
            if line.startswith("[/Request Header]"):
                emit('log_diver', json.dumps({
                    'type': 'request',
                    'progress': '30%',
                    'content': request_header
                }))
            request_header = request_header + line
        elif status == RESPONSE_HEADER:
            if line.startswith("[/Response Header]"):
                emit('log_diver', json.dumps({
                    'type': 'response',
                    'progress': '40%',
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
                logs = logs + line

    emit('log_diver', json.dumps({
        'type': 'log',
        'progress': '100%',
        'content': logs,
        'summery': str(summery)
    }))

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
#test1


if __name__ == "__main__":
    # application.run(host='0.0.0.0')
    socketio.run(application)
