import dropbox
import ByteWriter


class DropboxUploader(ByteWriter.ByteWriter):

    def __init__(self, full_path, dropbox_token):
        super(DropboxUploader, self).__init__(full_path)
        self.__dropbox_token = dropbox_token
        self.__dbx = dropbox.Dropbox(dropbox_token)
        self.__cursor = None
        self.__commit = None

    def append_bytes(self, byte_string, close=False):
        if self.__cursor is None:
            session_start_result = self.__dbx.files_upload_session_start(byte_string)
            self.__cursor = dropbox.files.UploadSessionCursor(session_start_result.session_id, offset=len(byte_string))
            self.__commit = dropbox.files.CommitInfo(self.full_path, mode=dropbox.files.WriteMode.add)
            # print('[DropboxUploader] Started upload task with path \"%s\"' % self.full_path)
            return

        if close:
            self.__dbx.files_upload_session_finish(byte_string, self.__cursor, self.__commit)
            # print('[DropboxUploader] Closed Dropbox file: \"%s\"' % self.full_path)
        else:
            self.__dbx.files_upload_session_append_v2(byte_string, self.__cursor)
            self.__cursor.offset = self.__cursor.offset + len(byte_string)
