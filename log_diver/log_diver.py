from flask import Flask, render_template, request, url_for, jsonify, stream_with_context, Response
# from flask.ext.aiohttp import async

import subprocess
import logging
import secrets


REQUEST_HEADER = 1
RESPONSE_HEADER = 2
LOGS = 3

application = Flask(__name__)


@application.route('/')
def index():
    return render_template('index.html')


@application.route('/googlemap')
def googlemap():
    google_maps = request.args.get('google_maps')
    if google_maps is None:
        google_maps = [
           ['US CA SANTACLARA', 37.3519, -121.952],
        ];
     
    return render_template('googlemap.html', maps=google_maps)


@application.route('/log_diver')
def log_diver():
    url = request.args.get('url')
    
    pipe = subprocess.Popen(secrets.LSG_COMMAND.format(url), \
        shell=True, stdout=subprocess.PIPE)

    status = 0
    request_header = ''
    response_header = ''
    logs = ''
    google_map = ''
    google_maps = [['US SANTACLARA', 37.3519, -121.952],]
    while pipe.poll() is None:
        line = pipe.stdout.readline().decode('utf-8')

        if line.startswith("[Request Header]"):
            status = REQUEST_HEADER
            continue
        elif line.startswith("[Response Header]"):
            status = RESPONSE_HEADER
            continue
        elif line.startswith("[LOGS]"):
            status = LOGS
            google_map = line.split('] [')[2][:-2].split('|')
            continue

        if status == REQUEST_HEADER:
            request_header = request_header + line
        elif status == RESPONSE_HEADER:
            response_header = response_header + line
        elif status == LOGS:
            if len(line) > 1:
                times = line.split(' ')
                total = int(times[4]) + int(times[5]) + int(times[6])
                google_maps.append([google_map[0], google_map[1], google_map[2], total])
            logs = logs + line

    return jsonify(request_header=request_header, response_header=response_header, logs=logs, google_maps=str(google_maps))


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


if __name__ == "__main__":
    application.run(host='0.0.0.0')