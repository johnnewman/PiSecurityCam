import ByteWriter
import os


class DiskWriter(ByteWriter.ByteWriter):

    def __init__(self, full_path):
        super(DiskWriter, self).__init__(full_path)
        if not os.path.exists(os.path.dirname(full_path)):
            os.makedirs(os.path.dirname(full_path))
        self.file = open(full_path, 'a')

    def append_bytes(self, byte_string, close=False):
        if self.file is not None:
            self.file.write(byte_string)
            if close:
                self.file.close()
                # print('[DiskWriter] Closed file: \"%s\"' % self.full_path)
