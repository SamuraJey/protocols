from bottle import route, run, template,request

file_bucket='./files'

@route('/upload')
def get_upload():
    return '''
    <form action="/upload" method="post" enctype="multipart/form-data">
        Select a file: <input type="file" name="filecontrol" />
        <input type="submit" value="Start upload" />
    </form>
    '''
@route('/upload',method='POST')
def do_upload():
    file=request.files.get('filecontrol')
    file.save(file_bucket)
    return "OK"

run(host='localhost', port=8080, debug=True, reloader=True)