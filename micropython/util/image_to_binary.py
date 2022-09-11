from PIL import Image

def convert_image_to_bytearray(path: str) -> bytearray:
    """
    Ported from this online post:
    https://forum.micropython.org/viewtopic.php?f=16&t=2974
    """
    image = Image.open(path)
    buffer = bytearray((image.height // 8) * image.width)
    i = 0
    for y in range(image.height // 8):
        for x in range(image.width):
            byte = 0
            for bit in range(8):
                pixel = image.getpixel((x, y * 8 + bit))
                if pixel == 255:
                    byte |= (1 << bit)
            buffer[i] = byte
            i += 1
    
    return buffer

def write_to_file(buffer: bytes, file_name: str):
    """
    Write buffer to a binary file.
    """
    with open(file_name, "wb") as f:
        f.write(buffer)