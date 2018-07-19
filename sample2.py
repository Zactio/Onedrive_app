#Python Onedrive application
#Done by: Zachary and Brandnon

import base64
import mimetypes
import os
import pprint
import uuid
import flask
import re
from flask_oauthlib.client import OAuth
from flask import request, jsonify,send_file,render_template,Flask, flash, request, redirect, url_for, send_from_directory, after_this_request
from flask_uploads import UploadSet, configure_uploads, ALL
from jinja2 import Template
from werkzeug.utils import secure_filename
import config

#<name>_<version>.txt
#fileA_1.txt
#fileB_1.txt
#fileA_2.txt
#fileA_3.txt

#upload
#find current latest version of file if exists
#save as 1 version later.
#e.g. if fileA_2.txt exists on onedrive, and the user uploads fileA.txt, save it as fileA_3.txt
#assume that when the user uploads the file, it is versionless. e.g. only fileA.txt

#search
#show only the latest version per file. e.g. based on the files above, show the user fileA_3.txt and fileB_1.txt

#python functions sort(), 


UPLOAD_FOLDER = 'static/templates/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'pdf'])

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
    return flask.render_template('homepage.html')

@APP.route('/login')
def login():
    flask.session['state'] = str(uuid.uuid4())
    return MSGRAPH.authorize(callback=config.REDIRECT_URI, state=flask.session['state'])

@APP.route('/login/authorized')
def authorized():
    if str(flask.session['state']) != str(flask.request.args['state']):
        raise Exception('state returned to redirect URL does not match!')
    response = MSGRAPH.authorized_response()
    flask.session['access_token'] = response['access_token']
    return flask.redirect('/options')



@APP.route('/options/')
def options():
    return flask.render_template('options.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@APP.route('/search', methods=['GET', 'POST'] )
def upload_search():
    if request.methods == 'POST':
        search_name = request.form['html_search']
        search_path = MSGRAPH.get("me/drive/root/search(q='%s')?select=weburl" % search_name, headers=request_headers()).data
        path_list = []
        for x in search_path["value"]:
            if x["name"]:
                path_list.append(x["webUrl"][(x["webUrl"].index("Documents")):])
                print (x["webUrl"][(x["webUrl"].index("Documents")):])
        return jsonify(path_list)

    return render_template("upload_search.html")


##############################################################

# def getVersion(string):
#     if ([x for x in re.split('(\d+)',string) if x.isdigit()] == []):
#         return []
#     else:
#         return [x for x in re.split('(\d+)',string) if x.isdigit()]
# # File_name_1.txt
# # f_i_l_e_1.txt
# def getFileName(string):
#     match = re.search('([A-Za-z_\d]+?)(_?[\d]*?)\.(\w{3})',string)
#     if match:
#         return (match.group(1), match.group(3))
#     else:
#         return "None"

# def makeFullFileName(filename, version, extension):
#     if version == "None":
#         entirefilename = filename+"_1"+"."+extension
#     else:
#         entirefilename = filename+"_"+str(int(version)+1)+"."+extension
#     return entirefilename

# def getHighestVersion(listOfStrings):       
#         return max(listOfStrings)
######################################################
def isForm(string):
    if string[0:1] == "f" or string[0:1] == "F":
        return True
    else:
        return False

def isRecord(string):
    if string[0:1] == "r" or string[0:1] == "R":
        return True
    else:
        return False

def getPartsOfFile(string):
    match = re.search('([f|F|R|r]\d*)([A-Za-z_]+?)(\d+)([A-Za-z_]+?)\.(\w+)',string)
    if match:
        # print("Yes - getPartsOfFile")
        return (match.group(1), match.group(2), match.group(3), match.group(4) , match.group(5))
    else:
        # print("None - getPartsOfFile")
        return ("None", "None", "None", "None", "None")

def makeNextFormString(initialFormString, LatestVersion):
    # print "Latest Version----------------> %s" % LatestVersion
    return "F"+ makeFormNumericId(getPartsOfFile(initialFormString)[0][1:])+getPartsOfFile(initialFormString)[1]+LatestVersion+getPartsOfFile(initialFormString)[3]+"."+getPartsOfFile(initialFormString)[4]

def makeNextRecordString(initialFormString, LatestVersion):
    return "R"+ makeFormNumericId(getPartsOfFile(initialFormString)[0][1:])+getPartsOfFile(initialFormString)[1]+LatestVersion+getPartsOfFile(initialFormString)[3]+"."+getPartsOfFile(initialFormString)[4]

def makeFormNumericId(integer):
    if len(str(integer)) == 1:
        return "00"+integer
    elif len(str(integer)) == 2:
        return "0"+integer
    else:
        return integer

def getLatestVersion(fn):
    search_path = MSGRAPH.get("me/drive/root/search(q='%s')?select=name" % getPartsOfFile(fn)[0], headers=request_headers()).data
    searched_File_ID = getPartsOfFile(fn)[0][1:]
    File_ext = getPartsOfFile(fn)[4]
    print("File_ext - %s"% File_ext)
    print ("searched_File_ID - %s" % searched_File_ID)
    file_version = []
    print ("search_path - %s" % search_path)
    for x in search_path["value"]:
        print ("Onedrive file ext - %s "% x['name'][x['name'].rfind(".")+1:])
        print ("Onedrive file name ------------------------> %s"% getPartsOfFile(x['name'])[0][1:])
        print ("-------------------------------------------------")
        try:
            if ((File_ext == x['name'][x['name'].rfind(".")+1:]) and (getPartsOfFile(x['name'])[0][1:] == searched_File_ID)):#if ext and filename is the same
                file_version.append(getPartsOfFile(x['name'])[2])
            else: continue 
        except Exception as e:
            print("Continue")
            continue
        else: continue 
    print ("file_version(list) - %s" % file_version)
    if (file_version == []):
        print("None - getLatestVersion")
        version = "None"
        return "1"
    else:
        version = str(int(max(file_version))+1)
        print ("File-version(list2--------------)%s"% file_version)
        return version 

def getLatestVersionReport(filename):
    #diff part
    print("YAY2 - getLatestVersionReport")
    LatestVersion = getLatestVersion(filename)
    return LatestVersion
    #diff part

def getLatestVersionForm(filename):
    print("YAY2 - getLatestVersionForm")
    # asdjsaodaoidjas = getLatestVersion(formNumericIdn, filename)
    LatestVersion = getLatestVersion(filename)
    return LatestVersion



# def getLatestVersion(searchString):
#     results = onedrive.getItems(searchString)
#     version = sort(results).getFirst()
#     newversion+=1

######################################################
@APP.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        fn = file.filename
        if file and allowed_file(file.filename):
            @after_this_request
            def remove_file(response):
                os.remove((APP.config['UPLOAD_FOLDER']+filename))
                return response
############################################################################
            fn = file.filename
            # fn = secure_filename(file.filename)
            # if fn.find("_") == True:
            #     search_path = MSGRAPH.get("me/drive/root/search(q='%s')?select=name" % (fn[0:fn.rfind(".")]), headers=request_headers()).data

            # search_path = MSGRAPH.get("me/drive/root/search(q='%s')?select=name" % getPartsOfFile(fn)[0], headers=request_headers()).data

            # file_version = []
            # file_named = getFileName(fn)[0]
            # file_ext = getFileName(fn)[1]
            # for x in search_path["value"]:
            #     if ((File_ext == x['name'][x['name'].rfind(".")+1:]) and (getPartsOfFile(x['name'])[0][1:] == File_NumericId)):#if ext and filename is the same
            #         try:
            #             file_version = file_version +getPartsOfFile(x['name'])[2]
            #         except Exception as e:
            #             continue
            #     else: continue                    
            # if (file_version == []):
            #     version = "None"
            # else:
            #     version = getHighestVersion(file_version)
            if isForm(fn) == True:
                LatestVersion = getLatestVersionForm(fn)
                filename = makeNextFormString(fn, LatestVersion)
            elif isRecord(fn) == True:
                LatestVersion = getLatestVersionReport(fn)
                filename = makeNextRecordString(fn, LatestVersion)
            else:
                return "<h1>Error</h1><p>File is not a form or record.</p>"

            file.save(os.path.join(APP.config['UPLOAD_FOLDER'], filename))
            user_profile = MSGRAPH.get('me', headers=request_headers()).data
            user_name = user_profile['displayName']
            profile_pic = UPLOAD_FOLDER + filename
            upload_response = upload_file(client=MSGRAPH, filename=profile_pic)
            if str(upload_response.status).startswith('2'):
                link_url = sharing_link(client=MSGRAPH, item_id=upload_response.data['id'])
            else:
                link_url = ''
            return "<h1>Succesful</h1><p>Your item has been uploaded into your personal onedrive documents.</p>"
                    

    return render_template("upload_page.html")

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
def download_function(searched_name):
    search_path = MSGRAPH.get("me/drive/root/search(q='%s')?select=weburl" % searched_name, headers=request_headers()).data
    path_list = []
    for x in search_path["value"]:
        if x["webUrl"]:
            path_list.append(x["webUrl"][(x["webUrl"].index("Documents"))+10:])

    if path_list == []:
        return "<h1>Error 404</h1><p>File not found in Onedrive.</p>"

    if request.method == 'POST':
        route = request.form['html_path']
        # namesz = request.form['html_name']

        photo,filename = profile_photo(route=route,client=MSGRAPH, user_id='me', save_as= "Placeholder")
        return return_files_tut(filename)
    return render_template('download_page.html', path = path_list, name = searched_name)


def profile_photo(*, route, client=MSGRAPH, user_id='me', save_as=None):

    endpoint = 'me/drive/root:/'+route+':/content' if user_id == 'me' else f'users/{user_id}/$value'
    photo_response = client.get(endpoint)
    photo = photo_response.raw_data
    filename = save_as + '.' + 'txt'
    print(filename)
    print("raw data", photo)
    with open(filename, 'wb') as fhandle:fhandle.write(photo)
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


def return_files_tut(path):
    try:
        @after_this_request
        def remove_path(response):
            os.remove(path)
            print (path)
            return response        
        return send_file(path,attachment_filename="Placeholder")

    except Exception as e:
        return str(e)

def sharing_link(*, client, item_id, link_type='view'):
    endpoint = f'me/drive/items/{item_id}/createLink'
    response = client.post(endpoint,
                           headers=request_headers(),
                           data={'type': link_type},
                           format='json')

    if str(response.status).startswith('2'):
        return response.data['link']['webUrl']

def upload_file(*, client, filename, folder=None):
    fname_only = os.path.basename(filename)
    if folder:
        endpoint = f'me/drive/root:/{folder}/{fname_only}:/content'
    else:
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


