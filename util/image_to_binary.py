import getopt, sys

def convert_image_to_bytearray(path: str, invert=True) -> bytearray:
    """
    Extract the byte stream from a .PBM image file. Optionally, 
    invert the byte stream for OLED displays.
    """
    with open(path, "rb") as f:
        f.readline() # magic number
        f.readline() # creator comment
        f.readline() # image dimensions
        buffer = bytearray(f.read())
    
    # XOR bits for OLED displays
    if invert:
        for i in range(len(buffer)):
            buffer[i] ^= 0xFF

    return buffer 

def write_to_file(buffer: bytes, file_name: str):
    """
    Write a bytearray/buffer to a binary file.
    """
    with open(file_name, "wb") as f:
        f.write(buffer)

args_list = sys.argv[1:]
options = "hi:o:"
long_options = ["help", "input=", "output="]
try:
    # parse arguments
    args, value = getopt.getopt(args_list, options, long_options)
    # check for each argument
    for current_arg, current_value in args:
        if current_arg in ("-h", "--help"):
            print("help")
        if current_arg in ("-i", "--input"):
            buffer = convert_image_to_bytearray(current_value)
        if current_arg in ("-o", "--output"):
            write_to_file(buffer, current_value)

except getopt.error as err:
    print(str(err))