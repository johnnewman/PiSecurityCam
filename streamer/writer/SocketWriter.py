import socket
from streamer.writer import ByteWriter


BOUNDARY = 'FRAME'


class SocketWriter(ByteWriter.ByteWriter):

    def __init__(self, comm_socket):
        super(SocketWriter, self).__init__(None)
        self.__socket = comm_socket

    def append_bytes(self, byte_string, close=False):
        try:
            total_sent = 0
            while total_sent < len(byte_string) and len(byte_string) > 0:
                sent = self.__socket.send(byte_string[total_sent:])
                if sent == 0:
                    raise RuntimeError('Socket connection is broken.')
                total_sent += sent
            if close:
                self.__socket.shutdown(socket.SHUT_RDWR)
                self.__socket.close()
        except Exception as e:
            self.__socket.shutdown(socket.SHUT_RDWR)
            self.__socket.close()


class MJPEGSocketWriter(SocketWriter):

    def __init__(self, comm_socket):
        super(MJPEGSocketWriter, self).__init__(comm_socket)
        self.__has_sent_header = False

    def append_bytes(self, byte_string, close=False):
        header_content = ''
        if not self.__has_sent_header:
            header_content = 'HTTP/1.1 200 OK\r\n' + \
                             'Content-Type: multipart/x-mixed-replace; boundary=' + BOUNDARY + '\r\n' + \
                             'Connection: keep-alive\r\n\r\n'
            self.__has_sent_header = True

        byte_string = header_content + '--' + BOUNDARY + '\r\n' + \
            'Content-Type: image/jpeg\r\n' + \
            'Content-Length: ' + str(len(byte_string)) + '\r\n\r\n' + \
            byte_string + \
            '\r\n\r\n'
        super(MJPEGSocketWriter, self).append_bytes(byte_string, close)
