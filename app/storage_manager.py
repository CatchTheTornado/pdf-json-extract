import os
import yaml
from storage_strategies.local_filesystem import LocalFilesystemStorageStrategy
from storage_strategies.google_drive import GoogleDriveStorageStrategy
from pathlib import Path

class StorageManager:
    def __init__(self, profile_name):
        profile_path = os.path.join(os.getenv('STORAGE_PROFILE_PATH', '/storage_profiles'), f'{profile_name}.yaml')
        with open(profile_path, 'r') as file:
            self.profile = yaml.safe_load(file)
        
        strategy = self.profile['strategy']
        if strategy == 'local_filesystem':
            self.strategy = LocalFilesystemStorageStrategy(self.profile)
        elif strategy == 'google_drive':
            self.strategy = GoogleDriveStorageStrategy(self.profile)
        else:
            raise ValueError(f"Unknown storage strategy '{strategy}'")

    def save(self, file_name, dest_file_name, content):
        self.strategy.save(file_name, dest_file_name, content)

    def load(self, file_name):
        return self.strategy.load(file_name)

    def list(self):
        return self.strategy.list()

    def delete(self, file_name):
        self.strategy.delete(file_name)