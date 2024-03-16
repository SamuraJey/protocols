class hexdump:
    def __init__(self, buf, off=0):
        self.buffer = buf
        self.offset = off

    def __iter__(self) -> iter:
        last_byte_string, last_line = None, None
        yield "          " + " ".join(f"{i:02X}" for i in range(8)) + "  " + " ".join(f"{i:02X}" for i in range(8, 16))
        for i in range(0, len(self.buffer), 16):
            byte_string = bytearray(self.buffer[i:i+16])
            line = "{:08x}  {:23}  {:23}  |{:16}|".format(
                self.offset + i,
                " ".join(("{:02x}".format(x) for x in byte_string[:8])),
                " ".join(("{:02x}".format(x) for x in byte_string[8:])),
                "".join((chr(x) if 32 <= x < 255 else "." for x in byte_string)),
            )
            if byte_string == last_byte_string:
                line = "*"
            if byte_string != last_byte_string or line != last_line:
                yield line
            last_byte_string, last_line = byte_string, line
        yield "{:08x}".format(self.offset + len(self.buffer))

    def __str__(self) -> str:
        return "\n".join(self)


message = b"Seven troubles - one answer\n\
A crutch and a bicycle\n\
Seven troubles- one answer\n\
Put in a crutch, reinvent the wheel\n"
print(hexdump(message))
