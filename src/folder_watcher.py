from __future__ import print_function

import json
import os
import sys
from os.path import basename, dirname
from time import sleep
from logbook import Logger, StreamHandler
from typing import Union
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, FileCreatedEvent, DirCreatedEvent, FileSystemEvent

DEFAULT_CONF_PATH = r'C:\folder_watcher\conf.json'

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


class ObserverManager(object):

    def __init__(self):
        self.observer = Observer()

    def load_conf_from_path(self, path=DEFAULT_CONF_PATH):
        with open(path, 'rb') as conf_file:
            conf = json.load(conf_file)
        for path, rules in conf.items():
            self._add_rules_to_dir(path, rules)

    def _add_rules_to_dir(self, path, rules):
        assert os.path.isdir(path), "Path must be a directory."
        for rule in rules:
            event_handler = FileRelocateEventHandler(**rule)
            self.observer.schedule(event_handler, path)

    def start(self):
        self.observer.start()

    def stop(self):
        self.observer.stop()

    def join(self):
        self.observer.join()


if __name__ == '__main__':
    observer_manager = ObserverManager()
    observer_manager.load_conf_from_path()
    observer_manager.start()

    print('Ctrl+C for exiting...')
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print('Stopping...')
        observer_manager.stop()
        print('Waiting for thread to terminate...')
        observer_manager.join()
