
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
from multiprocessing import Queue

class FileWatcher(object):


    def __init__(self,collector_path,supported_files):
        self._initialize_members(collector_path,supported_files)

    def _initialize_members(self,collector_path,supported_files):        

        self._logger = logging.getLogger('ONI.INGEST.WATCHER')        
        self._logger.info("Creating File watcher")

        # initializing observer.
        event_handler = NewFileEvent(self)
        self._observer = Observer()
        self._observer.schedule(event_handler,collector_path)

        self._collector_path = collector_path
        self._files_queue =Queue()
        self._supported_files = supported_files

    def start(self):       
        
        self._logger.info("Watching: {0}".format(self._collector_path))        
        self._observer.start()

    def new_file_detected(self,file):

        self._logger.info("-------------------------------------- New File detected --------------------------------------")
        self._logger.info("File: {0}".format(file))

        # Validate the file is supported.        
        if file.endswith(tuple(self._supported_files)):                   
            self._files_queue.put(file)
            self._logger.info("File {0} added to process queue".format(file))                        
        else:
            self._logger.warning("File extension not supported: {0}".format(file))
            self._logger.warning("File won't be ingested")  

    def stop(self):
        self._logger.info("Stopping File Watcher")
        self._files_queue.close()
        self._observer.stop()
        self._observer.join()

    def GetNextFile(self):
        return self._files_queue.get()      
    
    @property
    def HasFiles(self):
        return not self._files_queue.empty()

class NewFileEvent(FileSystemEventHandler):
        
    def __init__(self,watcher_instance):
        self.watcher_instance = watcher_instance

    def on_moved(self,event):        
        if not event.is_directory:            
            self.watcher_instance.new_file_detected(event.dest_path)

    def on_created(self,event):
        if not event.is_directory:            
            self.watcher_instance.new_file_detected(event.src_path)