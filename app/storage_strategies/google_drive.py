import os
import io
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2.service_account import Credentials
from storage_strategies.storage_strategy import StorageStrategy

## Note - this code is using Service Accounts for authentication which are separate accounts other than
## your Google account. You can create a service account and download the JSON key file to use it for
## how to enable GDrive API: https://developers.google.com/drive/api/quickstart/python?hl=pl
class GoogleDriveStorageStrategy(StorageStrategy):
    def __init__(self, context):
        super().__init__(context)
        self.credentials = Credentials.from_service_account_file(
            context['settings']['service_account_file'],
            scopes=['https://www.googleapis.com/auth/drive']
        )
        self.service = build('drive', 'v3', credentials=self.credentials)
        self.folder_id = context['settings']['folder_id']

    def save(self, file_name, dest_file_name, content):
        # Save content to a temporary file
        with open(file_name, 'wb') as temp_file:
            temp_file.write(content.encode('utf-8'))  # Encode the string to bytes
        
        file_metadata = {
            'name': self.format_file_name(file_name, dest_file_name),
        }
        if self.folder_id:
            file_metadata['parents'] = [self.folder_id]

        print(file_metadata)
        media = MediaFileUpload(file_name, resumable=True)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"File ID: {file.get('id')}")
        
        # Remove the temporary file
        os.remove(file_name)

    def load(self, file_name):
        query = f"name = '{file_name}'"
        if self.folder_id:
            query += f" and '{self.folder_id}' in parents"
        results = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
            return None
        file_id = items[0]['id']
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
        fh.seek(0)
        return fh.read()

    def list(self):
        query = "" #"mimeType='application/vnd.google-apps.file'"
        if self.folder_id:
            query = f"'{self.folder_id}' in parents"
        results = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        return [item['name'] for item in items]

    def delete(self, file_name):
        query = f"name = '{file_name}'"
        if self.folder_id:
            query += f" and '{self.folder_id}' in parents"
        results = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
            return
        file_id = items[0]['id']
        self.service.files().delete(fileId=file_id).execute()
        print(f"File {file_name} deleted.")