import os
import yaml
from datetime import datetime
from pathlib import Path

class StorageStrategy:
    def __init__(self, context):
        self.context = context

    def save(self, file_name, dest_file_name, content):
        raise NotImplementedError("Subclasses must implement this method")

    def load(self, file_name):
        raise NotImplementedError("Subclasses must implement this method")

    def list(self):
        raise NotImplementedError("Subclasses must implement this method")

    def delete(self, file_name):
        raise NotImplementedError("Subclasses must implement this method")
    
    def format_file_name(self, file_name, format_string):
        return format_string.format(file_fullname=file_name,  # file_name with path
                                     file_name=Path(file_name).stem,  # file_name without path
                                     file_extension = Path(file_name).suffix,   # file extension
                                     Y=datetime.now().strftime('%Y'),
                                     mm=datetime.now().strftime('%m'),
                                     dd=datetime.now().strftime('%d'),
                                     HH=datetime.now().strftime('%H'),
                                     MM=datetime.now().strftime('%M'),
                                     SS=datetime.now().strftime('%S'))