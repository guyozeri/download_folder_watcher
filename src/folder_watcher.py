import os
from os.path import basename, dirname
from typing import Union
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, FileCreatedEvent, DirCreatedEvent


class FileRelocateEventHandler(PatternMatchingEventHandler):
    """Event handler for new files, relocates the file to the defined sub-dir"""

    def __init__(self, dst_dir, patterns=None, ignore_patterns=None, ignore_directories=False, case_sensitive=False):
        super(FileRelocateEventHandler, self).__init__(patterns, ignore_patterns, ignore_directories, case_sensitive)
        self.dst_dir = dst_dir

    def on_created(self, event):
        # type: (Union[FileCreatedEvent, DirCreatedEvent]) -> None
        dir_path = os.path.join(dirname(event.src_path), self.dst_dir)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        dst_path = os.path.join(dir_path, basename(event.src_path))
        os.rename(event.src_path, dst_path)


if __name__ == '__main__':
    event_handler = FileRelocateEventHandler(r'Images', patterns=['*.jpeg', '*.jpg'])
    observer = Observer()
    observer.schedule(event_handler, path=r'C:\temp\try')
    observer.start()

    raw_input('[Enter] for exiting...')
