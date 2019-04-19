from PIL import Image, ExifTags
from io import BytesIO
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from pkg_resources import resource_filename

import argparse
import json
import os
import pickle
import sys
import urllib.request

## Oauth vals
SCOPE = 'https://www.googleapis.com/auth/devstorage.read_only'
CLIENT_SECRET = resource_filename(__name__, 'auth/client_secret_imagemeta.json')
OAUTH_CREDS = resource_filename(__name__, 'auth/credentials.p')
IMAGEMETA_ACCESS_TOKEN = None

def get_auth( request_func ):
    """
        decorator for OAuth2 for functions that
        need to make requests to Google APIs
    """
    client_secrets_path = CLIENT_SECRET
    scopes = [SCOPE]

    def auth_decorator( url ):
        #check if env var already set
        if os.getenv("IMAGEMETA_ACCESS_TOKEN"):
            return request_func(url)

        #attempt to read local Oauth pickle file
        if os.path.exists(OAUTH_CREDS):
            try:
                oauth_creds = pickle.load( open( OAUTH_CREDS, "rb" ) )
            except (IOError, EOFError):
                print("Could not open local oauth file")

            ##if expiry in local Oauth creds is later than now()
            if datetime.utcnow() < oauth_creds.expiry:
                os.environ["IMAGEMETA_ACCESS_TOKEN"] = oauth_creds.token

        # if IMAGEMETA_ACCESS_TOKEN env var not set, use Oauth flow
        if os.getenv("IMAGEMETA_ACCESS_TOKEN") == None:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_path, scopes=scopes)
            if sys.platform == "darwin":
                flow.run_local_server()
            else:
                #running from docker shell
                flow.run_console()
            os.environ["IMAGEMETA_ACCESS_TOKEN"] = flow.credentials.token
            pickle.dump( flow.credentials, open( OAUTH_CREDS, "wb" ) )

        return request_func(url)

    return auth_decorator

@get_auth
def request_gc_api ( api_url ):
    """
        makes requests to the Google Cloud API
    """
    IMAGEMETA_ACCESS_TOKEN = os.environ["IMAGEMETA_ACCESS_TOKEN"]
    req = urllib.request.Request(api_url,
                            headers={'Authorization': 'Bearer ' + IMAGEMETA_ACCESS_TOKEN})
    try:
        response = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        raise e

    return response

def list_bucket ( bucket ):
    """
        given a bucket, returns of list of files in bucket
    """
    # list-bucket api-url
    api_url = "https://www.googleapis.com/storage/v1/b/%s/o" % (bucket)

    try:
        list_bucket_response = request_gc_api( api_url )
    except urllib.error.HTTPError as e:
        print("Could not access bucket: %s" % bucket)
        return []

    list_bucket_dict = json.loads(list_bucket_response.read())
    bucket_objects = [i['name'] for i in list_bucket_dict['items'] ]
    return bucket_objects

def get_image_meta( bucket, image ):
    """
        returns json for image metadata of the format:
        { 'image' : [bucket]/[image name],
           'exif_metadata' : { exif_metadata...}
        }
    """
    print("Getting metadata for /%s/%s" % (bucket, image))

    api_url = "https://storage.googleapis.com/%s/%s" % (bucket, image)
    try:
        imgdata = request_gc_api(api_url)
    except urllib.error.HTTPError as e:
        print("Could not access file - /%s/%s" % (bucket, image))
        return None

    img = Image.open(BytesIO(imgdata.read()))
    img_data = { 'image' : bucket+"/"+image,
                 'exif_metadata' : {}
                }

    #no exif metadata on image
    if img._getexif() == None:
        return img_data

    img_data['exif_metadata'] = { ExifTags.TAGS.get(k, k): v \
                                    for k, v in img._getexif().items() \
                                    if not isinstance(v, (bytes, bytearray)) }
    # recast tuples (bytes type) as lists for json encoding
    for k, val in img_data['exif_metadata'].items():
        if k == 'GPSInfo':
            gps_data = {}
            for t in val:
                sub_decoded = ExifTags.GPSTAGS.get(t, t)
                gps_data[sub_decoded] = val[t].decode()
            img_data['exif_metadata'][k] = gps_data
        if isinstance( val , (tuple)):
            img_data['exif_metadata'][k] = str(val)

    return img_data

def get_bucket_meta_json( bucket_name, out_path = None ):
    bucket_files = list_bucket(bucket_name)
    meta_list = []
    for f in bucket_files:
        img_meta = get_image_meta(bucket_name, f)
        if img_meta: meta_list.append(img_meta)

    print(meta_list)

    if out_path:
        with open(out_path, 'w') as outfile:
            json.dump(meta_list, outfile)
    return

def get_image_meta_json ( file_name, out_path = None):
    bucket_name = file_name.lstrip('/').split('/')[0]
    f = file_name.split('/')[-1]

    meta_list = []
    img_meta = get_image_meta(bucket_name, f)
    if img_meta: meta_list.append(img_meta)

    print(meta_list)

    if out_path:
        with open(out_path, 'w') as outfile:
            json.dump(meta_list, outfile)
    return
