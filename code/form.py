import os
import io
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# SCOPES: Read-only for Sheets, full access for Drive files
SCOPES = ['https://www.googleapis.com/auth/drive.readonly',
          'https://www.googleapis.com/auth/spreadsheets.readonly']

# Path to your downloaded OAuth credentials
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'
DOWNLOAD_FOLDER = 'downloads'  # Change as needed

# Google Sheet ID and range
SHEET_ID = '1RjT5SNngJoktfgVkSPmaYCDw-5PlecHj6tAUyqkmZRI'
RANGE = 'Form Responses 1!A1:Z'  # Adjust if your tab/range differs


def authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds

def download_file(drive_service, file_id, filename):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(os.path.join(DOWNLOAD_FOLDER, filename), 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

def main():
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    creds = authenticate()
    sheets_service = build('sheets', 'v4', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    # Get file upload URLs from the form response sheet
    sheet = sheets_service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE).execute()
    rows = result.get('values', [])

    if not rows:
        print("No data found.")
        return

    headers = rows[0]
    file_col_index = -1
    for i, h in enumerate(headers):
        if 'upload photo here!' in h.lower():
            file_col_index = i
            break

    if file_col_index == -1:
        print("File upload column not found.")
        return

    # Process each row
    for row in rows[1:]:
        if len(row) <= file_col_index:
            continue
        file_urls = row[file_col_index].split(", ")
        for url in file_urls:
            match = None
            import re
            match = re.search(r'[-\w]{25,}', url)
            if match:
                file_id = match.group(0)
                try:
                    metadata = drive_service.files().get(fileId=file_id).execute()
                    filename = metadata['name']
                    if filename not in os.listdir(DOWNLOAD_FOLDER):
                        print(f"Downloading {filename}...")
                        download_file(drive_service, file_id, filename)
                except Exception as e:
                    print(f"Error downloading file: {e}")

if __name__ == '__main__':
    main()
