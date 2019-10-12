from __future__ import print_function

import os
import sys
from os.path import basename, dirname
from time import sleep
from logbook import Logger, StreamHandler
from typing import Union
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, FileSystemEventHandler, FileCreatedEvent, DirCreatedEvent, \
    FileSystemEvent

stream_handler = StreamHandler(sys.stdout)
stream_handler.push_application()


class FileRelocateEventHandler(PatternMatchingEventHandler):
    """Event handler for new files, relocates the file to the defined sub-dir"""

    def __init__(self, dst_dir, patterns=None, ignore_patterns=None, ignore_directories=False, case_sensitive=False):
        sub_dir_pattern = '*{dst_dir}\\*'.format(dst_dir=dst_dir)
        if ignore_patterns:
            ignore_patterns.append(sub_dir_pattern)
        else:
            ignore_patterns = [sub_dir_pattern]
        super(FileRelocateEventHandler, self).__init__(patterns, ignore_patterns, ignore_directories, case_sensitive)
        self.dst_dir = dst_dir
        self.logger = Logger(self)

    def dispatch(self, event):
        # type: (FileSystemEvent) -> None
        if os.path.exists(event.src_path):
            super(FileRelocateEventHandler, self).dispatch(event)

    def on_created(self, event):
        # type: (Union[FileCreatedEvent, DirCreatedEvent]) -> None
        self.logger.info('Detected new matches file {}'.format(event.src_path))
        dir_path = os.path.join(dirname(event.src_path), self.dst_dir)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        dst_path = os.path.join(dir_path, basename(event.src_path))
        self.logger.info('Moved to {}'.format(dst_path))
        os.rename(event.src_path, dst_path)

    def __repr__(self):
        return '{cls}(dst_dir={dst_dir}, patterns={patterns})'.format(cls=self.__class__.__name__, dst_dir=self.dst_dir,
                                                                      patterns=self.patterns)


if __name__ == '__main__':
    event_handler = FileRelocateEventHandler(r'Images', patterns=['*.jpeg', '*.jpg'], ignore_directories=True)
    event_handler2 = FileRelocateEventHandler(r'Some', patterns=['*some*'], ignore_directories=True)
    observer = Observer()
    observer.schedule(event_handler, path=r'C:\temp\try')
    observer.schedule(event_handler2, path=r'C:\temp\try')
    observer.start()

    print('Ctrl+C for exiting...')
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print('Stopping...')
        observer.stop()
        print('Waiting for thread to terminate...')
        observer.join()
