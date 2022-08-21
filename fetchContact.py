from __future__ import print_function
import os.path
from typing_extensions import final
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
# SCOPES = 'https://www.googleapis.com/auth/calendar'
SCOPES = 'https://www.googleapis.com/auth/contacts.readonly'
CLIENT_SECRET_FILE = 'keys3.json'
APPLICATION_NAME = 'Birthday Wishing App'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    # credential_dir = os.path.join(home_dir, '.credentials4')
    credential_dir = os.path.join(os.getcwd(), 'credentials')

    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


# If modifying these scopes, delete the file
#  token.json.
# SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']

# def main():
def importContacts():
    """Shows basic usage of the People API.
    Prints the name of the first 10 connections.
    """

    creds = get_credentials()
    http = creds.authorize(httplib2.Http())
    # service = discovery.build('calendar', 'v3', http=http)

    service = build('people', 'v1', credentials=creds)

    # Call the People API
    # print('List of Connection :')
    results = service.people().connections().list(
        resourceName='people/me',
        pageSize=1000,
        personFields='names,emailAddresses,birthdays,phoneNumbers').execute()
    connections = results.get('connections', [])

    finalpeople = []

    for person in connections:
        birthdays = person.get('birthdays', [])
        if birthdays:
            finalpeople.append(person)

    return finalpeople
