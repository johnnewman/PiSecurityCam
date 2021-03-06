import os
from . import byte_writer


class DiskWriter(byte_writer.ByteWriter):
    """
    A simple class that writes all supplied bytes to a file.  Will close the
    file when finished.
    """

    def __init__(self, full_path):
        super(DiskWriter, self).__init__(full_path)
        if not os.path.exists(os.path.dirname(full_path)):
            os.makedirs(os.path.dirname(full_path))
        self.file = open(full_path, 'ab')

    def append_bytes(self, bts, close=False):
        if self.file is not None:
            self.file.write(bts) if len(bts) > 0 else None
            if close:
                self.file.close()
