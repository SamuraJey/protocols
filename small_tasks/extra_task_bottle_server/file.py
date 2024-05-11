#!/usr/bin/python3
# Made by: Sergey Zaremba MO-201

import os
from bottle import route, request, run, static_file

file_bucket = './files'


@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='./static')


@route('/upload')
def get_upload():
    return '''
    <head>
        <link rel="stylesheet" type="text/css" href="/static/styles.css">
    </head>
    <body>
        <form action="/upload" method="post" enctype="multipart/form-data">
            Select a file: <input type="file" name="filecontrol" />
            <input type="submit" value="Start upload" />
        </form>
    </body>
    '''


@route('/upload', method='POST')
def do_upload():
    file = request.files.get('filecontrol')
    filename = file.filename
    save_path = file_bucket + '/' + filename
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    try:
        file.save(save_path)
    except IOError as e:
        return "Can't save file. IOError: " + str(e)
    except Exception as e:
        return "Error: " + str(e)
    return "OK"


run(host='localhost', port=8080, debug=True, reloader=True)
