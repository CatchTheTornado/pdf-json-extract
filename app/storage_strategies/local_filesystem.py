import os
from storage_strategies.storage_strategy import StorageStrategy
from datetime import datetime
from pathlib import Path

def resolve_path(path):
    # Expand `~` to the home directory
    expanded_path = os.path.expanduser(path)
    # Convert to absolute path, resolving any `..` or `.`
    absolute_path = os.path.abspath(expanded_path)
    return absolute_path

class LocalFilesystemStorageStrategy(StorageStrategy):
    def __init__(self, context):
        super().__init__(context)
        self.base_directory = resolve_path(self.context['settings']['root_path'])
        print("Storage base directory: ", self.base_directory)
        self.create_subfolders = self.context['settings'].get('create_subfolders', False)
        self.subfolder_names_format = self.context['settings'].get('subfolder_names_format', '')
        os.makedirs(self.base_directory, exist_ok=True)

    def _get_subfolder_path(self, file_name):
        if not self.subfolder_names_format:
            return self.base_directory
        
        now = datetime.now()
        subfolder_path = self.format_file_name(file_name, self.subfolder_names_format)
        return os.path.join(self.base_directory, subfolder_path)

    def save(self, file_name, dest_file_name, content):
        file_name = self.format_file_name(file_name, dest_file_name)
        subfolder_path = self._get_subfolder_path(file_name)
        full_path = os.path.join(subfolder_path, file_name)
        full_directory = os.path.dirname(full_path)
        os.makedirs(full_directory, exist_ok=True)
        with open(full_path, 'w') as file:
            file.write(content)

    def load(self, file_name):
        subfolder_path = self._get_subfolder_path(file_name)
        file_path = os.path.join(subfolder_path, file_name)
        with open(file_path, 'r') as file:
            return file.read()

    def list(self):
        all_files = []
        for root, dirs, files in os.walk(self.base_directory):
            for file in files:
                all_files.append(os.path.join(root, file))
        return all_files

    def delete(self, file_name):
        subfolder_path = self._get_subfolder_path(file_name)
        file_path = os.path.join(subfolder_path, file_name)
        os.remove(file_path)