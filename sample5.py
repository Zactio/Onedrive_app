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


#########################################################################################################################

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
        return (match.group(1), match.group(2), match.group(3), match.group(4) , match.group(5))
    else:
        return ("None", "None", "None", "None", "None")


class ISODocumentFactory():
    @staticmethod
    def createDocument(input_string):
        if isRecord(input_string) == True:
            # return ISORecord(*getPartsOfFile(input_string))
            return ISODocument(getPartsOfFile(input_string)[0],getPartsOfFile(input_string)[1],getPartsOfFile(input_string)[2],getPartsOfFile(input_string)[3],getPartsOfFile(input_string)[4])
            

        elif isForm(input_string) == True: 
            # return getPartsOfFile(input_string)
            return ISODocument(getPartsOfFile(input_string)[0],getPartsOfFile(input_string)[1],getPartsOfFile(input_string)[2],getPartsOfFile(input_string)[3],getPartsOfFile(input_string)[4])
        else:
            raise ValueError('Document is not a record or string.')

    @staticmethod
    def CreateDocParts(input_string):
        if isRecord(input_string) == True:
            return (getPartsOfFile(input_string))
        elif isForm(input_string) == True: 
            return (getPartsOfFile(input_string))
        else:
            pass

    @staticmethod
    def NoExisting(input_string):
        if isRecord(input_string) == True or isForm(input_string) == True:
            return
        else:
            return RaiseError()
        
class ISODocument():
    # [FormNumericId][FormStringId][FormVersion][StringDescription][Extension]
    def __init__(self, numericId, stringId, version, description, extension):
        self.numericId = numericId
        self.stringId = stringId
        self.version = version
        self.description = description
        self.extension = extension

    def file_name(self):
        return self.numericId+self.stringId+str(int(self.version)+1)+self.description+ '.' + self.extension

        # raise ValueError('A very specific bad thing happened.')

    # def isForm(self):
    #     if self.numericId[:1] == "f" or self.numericId[:1] == "F":
    #         return True
    #     else:
    #         return False

    # def isRecord(self):
    #     if self.numericId[:1] == "r" or self.numericId[:1] == "R":
    #         return True
    #     else:
    #         return False

    def sameFile(self, fn):
        if ((getPartsOfFile(self)[0][0:1] == 'F' or getPartsOfFile(self)[0][0:1] == 'R') and (getPartsOfFile(self)[4] == "docx" or getPartsOfFile(self)[4] == "txt")):
            if getPartsOfFile(self)[0] == getPartsOfFile(fn)[0] and self[self.rfind("."):] == fn[fn.rfind("."):]:
                return True
            else:
                return False
        else:
            RaiseError()

    # def makeNextFormString(self):
    #     return self.filename#self would be the latest document 

    # def makeNextRecordString(self):
    #     return self.filename

# class ISOForm(ISODocument):
#     def makeNextDoumentString(self):
#         #"F"+ self.numericId + self.stringId + str(int(Latestversion)+1) + self.description + '.' + self.extension
#         pass
#         #implement this
#         #returns the filename of the next version

# class ISORecord(ISODocument):
#     def makeNextDocumentString(self):
#         pass
#         #implement this
def RaiseError():
    return "<h1>Error</h1><p>Selected file is not a record or form.</p>"
    # pass#raise error for when error needs to be raised; replaces all the hardcoded return errors

############<class = "??">




#################################################################


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
                if match:
                # try:
                    print ("Matches")
                    print(response)
                    print(type(response))
                    os.remove((APP.config['UPLOAD_FOLDER']+filename))
                    return response
                else:
                    return response
                # except Exception as e:
                #     print ("No file to delete")
            match = re.search('([f|F|R|r]\d*)([A-Za-z_]+?)(\d+)([A-Za-z_]+?)\.(\w+)',fn)
            if not match:
                print("Test")
                return "<h1>Error</h1><p>Selected file is not a record or form.</p>"
            else:
                results = MSGRAPH.get("me/drive/root/search(q='%s')?select=name" % match.group(1), headers=request_headers()).data
                InitialDocument = ISODocument(getPartsOfFile(fn)[0], getPartsOfFile(fn)[1], getPartsOfFile(fn)[2], getPartsOfFile(fn)[3], getPartsOfFile(fn)[4])
                documents = [ISODocumentFactory.CreateDocParts(result['name']) for result in results['value'] if ISODocument.sameFile(result['name'],fn) == True]# documents = [ISODocumentFactory.returnVersion(result['name']) for result in results['value'] if ((File_ext == result['name'][result['name'].rfind(".")+1:]) and (getPartsOfFile(result['name'])[0] == getPartsOfFile(searched_File_ID)[0]))]
                print (documents)
                if not documents:
                    #verify that filename is a record or form first DONE
                    ISODocumentFactory.NoExisting(fn)
                    filename = fn
                    # do something -- create documents with that name and version DO NOT RAISE ERROR DONE
                else:
                    sortedDocuments = sorted(documents, reverse = True, key=lambda doc:doc[2])
                    # print (sortedDocuments)
                    Latest_Doc_version = sortedDocuments[0][2]
                    # if (int(Latest_Doc_version) < int(getPartsOfFile(fn)[2])):
                    #     filename = fn
                    # else:
                    if sortedDocuments[0][2]< getPartsOfFile(fn)[2]:
                        filename = fn
                    else:
                        InitialDocument.version = Latest_Doc_version 
                        filename = InitialDocument.file_name()

                print (filename)
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


