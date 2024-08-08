#!/usr/bin/env python3
import io
import struct
import sys

"""
From scripts/dtc/libfdt/fdt.h
#define FDT_MAGIC	0xd00dfeed
"""
FDT_MAGIC = 0xEDFE0DD0


def dump_file(io: io.FileIO, head: bytearray, len: int):
    return io.write(head[:len])


def split(kernel_image: str):
    dtb_count = 1
    complete = False
    _len = 0

    fdt_magic = struct.pack("<I", FDT_MAGIC)

    with open(kernel_image, "rb") as fp:
        kernel_size = fp.seek(0, io.SEEK_END)
        fp.seek(0, io.SEEK_SET)

        kernel = fp.read()

        dtb_head_p = kernel.find(fdt_magic)
        if dtb_head_p < 0:
            print("ERROR: Appended Device Tree Blob not found!")
            return -1

        _len = dtb_head_p
        with open("kernel", "wb") as kfp:
            dump_file(kfp, kernel, _len)

        while not complete:
            # Find the next dtbs
            _len = kernel_size - dtb_head_p - len(fdt_magic)
            dtb_next_p = kernel.find(fdt_magic, dtb_head_p + len(fdt_magic))
            if dtb_next_p < 0:
                _len = kernel_size - dtb_head_p
                complete = True
            else:
                _len = dtb_next_p - dtb_head_p

            # Dump found dtbs
            outfile = f"dtbdump_{dtb_count}.dtb"
            dtb_count += 1

            with open(outfile, "wb") as dfp:
                dump_file(dfp, kernel[dtb_head_p:], _len)

            dtb_head_p = dtb_next_p

        print("Found %d appended dtbs, please check the output." % (dtb_count - 1))

        return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:\n\t%s Image-dtb" %sys.argv[0])
        sys.exit(0)
    
    image = sys.argv[1]
    rc = split(image)

    sys.exit(rc)