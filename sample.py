#Python Onedrive application
#Done by: Zachary and Brandon
import base64
import mimetypes
import os
import pprint
import uuid
import flask
from flask_oauthlib.client import OAuth
from flask import request, jsonify,send_file,render_template,Flask, flash, request, redirect, url_for, send_from_directory
from flask_uploads import UploadSet, configure_uploads, ALL
from jinja2 import Template
from werkzeug.utils import secure_filename
import config

UPLOAD_FOLDER = 'static/templates/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

APP = flask.Flask(__name__, template_folder='static/templates')
APP.debug = True
APP.secret_key = 'development'
OAUTH = OAuth(APP)
MSGRAPH = OAUTH.remote_app(
    'microsoft',
    consumer_key=config.CLIENT_ID,
    consumer_secret=config.CLIENT_SECRET,
    request_token_params={'scope': config.SCOPES},
    base_url=config.RESOURCE + config.API_VERSION + '/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url=config.AUTHORITY_URL + config.TOKEN_ENDPOINT,
    authorize_url=config.AUTHORITY_URL + config.AUTH_ENDPOINT)


APP.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@APP.route('/')
def homepage():
    """Render the home page."""
    return flask.render_template('homepage.html')

@APP.route('/login')
def login():
    """Prompt user to authenticate."""
    flask.session['state'] = str(uuid.uuid4())
    return MSGRAPH.authorize(callback=config.REDIRECT_URI, state=flask.session['state'])

@APP.route('/login/authorized')
def authorized():
    """Handler for the application's Redirect Uri."""
    if str(flask.session['state']) != str(flask.request.args['state']):
        raise Exception('state returned to redirect URL does not match!')
    response = MSGRAPH.authorized_response()
    flask.session['access_token'] = response['access_token']
    return flask.redirect('/options')



@APP.route('/options/')
def options():
    """this is to render the options page"""
    return flask.render_template('options.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@APP.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(APP.config['UPLOAD_FOLDER'], filename))
                # """Sample form for sending email via Microsoft Graph."""

            # # read user profile data
            user_profile = MSGRAPH.get('me', headers=request_headers()).data
            user_name = user_profile['displayName']

            profile_pic = UPLOAD_FOLDER + filename
            print (profile_pic)
            print (type(profile_pic))
            # upload profile photo to OneDrive
            upload_response = upload_file(client=MSGRAPH, filename=profile_pic)
            if str(upload_response.status).startswith('2'):
                # create a sharing link for the uploaded photo
                link_url = sharing_link(client=MSGRAPH, item_id=upload_response.data['id'])
            else:
                link_url = ''

            # body = flask.render_template('email.html', name=user_name, link_url=link_url)
            return "<h1>Succesful</h1><p>Your item has been uploaded into your personal onedrive documents.</p>"
                    

                    # return redirect(url_for('uploaded_file',filename=filename))

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''



@APP.route('/search/<string:search_name>', methods=['GET'] )
def searches(search_name):
    search_path = MSGRAPH.get("me/drive/root/search(q='%s')?select=weburl" % search_name, headers=request_headers()).data
    path_list = []
    for x in search_path["value"]:
        if x["webUrl"]:
            path_list.append(x["webUrl"][(x["webUrl"].index("Documents")):])
            print (x["webUrl"][(x["webUrl"].index("Documents")):])
    return jsonify(path_list)

@APP.route('/download/', methods=['GET','POST']) 
def down_search():
    if request.method == 'POST':
        name_searched = request.form['search_file']
        return flask.redirect("/download/%s"%name_searched)

    return render_template("download.html")

@APP.route('/download/<string:searched_name>', methods=['GET','POST']) 
def downloadz(searched_name):
    search_path = MSGRAPH.get("me/drive/root/search(q='%s')?select=weburl" % searched_name, headers=request_headers()).data
    path_list = []
    for x in search_path["value"]:
        if x["webUrl"]:
            path_list.append(x["webUrl"][(x["webUrl"].index("Documents"))+10:])
            # print (x["webUrl"][(x["webUrl"].index("Documents"))+10:])

    if path_list == []:
        return "<h1>Error 404</h1><p>File not found in Onedrive.</p>"

    if request.method == 'POST':
        pathsz = request.form['html_path']
        namesz = request.form['html_name']
        #local = request.form['html_local']

        photo,filename = profile_photo(pathsz=pathsz,client=MSGRAPH, user_id='me', save_as = namesz)
        return return_files_tut(filename,namesz)
    return render_template('download_page.html', path = path_list, name = searched_name)

    # return flask.redirect('/download/')


def profile_photo(*, client=MSGRAPH, user_id='me', save_as=None, pathsz):

    endpoint = 'me/drive/root:/'+pathsz+':/content' if user_id == 'me' else f'users/{user_id}/$value'
    photo_response = client.get(endpoint)
    photo = photo_response.raw_data
    filename = save_as + '.' + 'txt'
    print(filename)
    print("raw data", photo)
    with open(filename, 'wb') as fhandle:
            fhandle.write(photo)
    return (photo,filename)

@MSGRAPH.tokengetter
def get_token():
    return (flask.session.get('access_token'), '')

def request_headers(headers=None):
    default_headers = {'SdkVersion': 'sample-python-flask',
                       'x-client-SKU': 'sample-python-flask',
                       'client-request-id': str(uuid.uuid4()),
                       'return-client-request-id': 'true'}
    if headers:
        default_headers.update(headers)
    return default_headers


def return_files_tut(path, name):
    try:
        return send_file(path.replace("/","\\"),attachment_filename=name)
    except Exception as e:
        return str(e)




def sharing_link(*, client, item_id, link_type='view'):
    endpoint = f'me/drive/items/{item_id}/createLink'
    response = client.post(endpoint,
                           headers=request_headers(),
                           data={'type': link_type},
                           format='json')

    if str(response.status).startswith('2'):
        # status 201 = link created, status 200 = existing link returned
        return response.data['link']['webUrl']

def upload_file(*, client, filename, folder=None):
    """Upload a file to OneDrive for Business.

    client  = user-authenticated flask-oauthlib client instance
    filename = local filename; may include a path
    folder = destination subfolder/path in OneDrive for Business
             None (default) = root folder

    File is uploaded and the response object is returned.
    If file already exists, it is overwritten.
    If folder does not exist, it is created.

    API documentation:
    https://developer.microsoft.com/en-us/graph/docs/api-reference/v1.0/api/driveitem_put_content
    """
    fname_only = os.path.basename(filename)

    # create the Graph endpoint to be used
    if folder:
        # create endpoint for upload to a subfoldero
        endpoint = f'me/drive/root:/{folder}/{fname_only}:/content'
    else:
        # create endpoint for upload to drive root folder
        endpoint = f'me/drive/root/children/{fname_only}/content'

    content_type, _ = mimetypes.guess_type(fname_only)
    with open(filename, 'rb') as fhandle:
        file_content = fhandle.read()

    return client.put(endpoint,
                      headers=request_headers({'content-type': content_type}),
                      data=file_content,
                      content_type=content_type)


ssl_dir: str = os.path.dirname(__file__).replace('src', 'ssl')
key_path: str = os.path.join(ssl_dir, 'ssl/server.key')
crt_path: str = os.path.join(ssl_dir, 'ssl/server.crt')
ssl_context: tuple = (crt_path, key_path)

if __name__ == "__main__":
	APP.run('0.0.0.0', 8000, debug=True, ssl_context=ssl_context)

