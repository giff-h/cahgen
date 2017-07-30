import struct
import imghdr


def get_image_size(filename):
    """Determine the image type of file_handle and return its size.
    source: http://bit.ly/29JRtdY

    :param filename: string to relative file path"""

    with open(filename, 'rb') as file_handle:
        head = file_handle.read(24)
        if len(head) != 24:
            return
        if imghdr.what(filename) == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                return
            width, height = struct.unpack('>ii', head[16:24])
        elif imghdr.what(filename) == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
        elif imghdr.what(filename) == 'jpeg':
            try:
                file_handle.seek(0)  # Read 0xff next
                size = 2
                file_type = 0
                while not 0xc0 <= file_type <= 0xcf:
                    file_handle.seek(size, 1)
                    byte = file_handle.read(1)
                    while ord(byte) == 0xff:
                        byte = file_handle.read(1)
                    file_type = ord(byte)
                    size = struct.unpack('>H', file_handle.read(2))[0] - 2
                # We are at a SOFn block
                file_handle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', file_handle.read(4))
            except Exception:  # IGNORE:W0703
                return
        else:
            return
        return width, height
