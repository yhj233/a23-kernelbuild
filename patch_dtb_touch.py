#!/usr/bin/env python3
"""Force the Silead touchscreen node in a compiled DTB to sane values.

The stock sun8i-q8-common.dtsi declares the panel as 1024x600 with a single
finger.  The GSL1680 firmware on this tablet reports 0..969 / 0..627, so with
a 1024x600 axis range libinput scales the touch down and the last ~40 px on
the right/bottom of the 800x480 panel can never be reached.

This walks the flattened device tree in place (no dtc needed) and rewrites:
    touchscreen-size-x  -> 970
    touchscreen-size-y  -> 628
    silead,max-fingers  -> 5
"""
import struct
import sys

FDT_MAGIC = 0xD00DFEED
FDT_BEGIN_NODE = 1
FDT_END_NODE = 2
FDT_PROP = 3
FDT_NOP = 4
FDT_END = 9

TARGETS = {
    'touchscreen-size-x': 970,
    'touchscreen-size-y': 628,
    'silead,max-fingers': 5,
}


def patch(path):
    d = bytearray(open(path, 'rb').read())
    magic, total, off_s, off_str, _, ver, _, _, sstr, _ = struct.unpack('>10I', d[:40])
    if magic != FDT_MAGIC:
        raise SystemExit('%s: not a DTB (magic %#x)' % (path, magic))
    strings = bytes(d[off_str:off_str + sstr])

    def name_at(off):
        end = strings.find(b'\0', off)
        return strings[off:end].decode('latin1')

    p = off_s
    done = set()
    while True:
        tok = struct.unpack('>I', d[p:p + 4])[0]
        p += 4
        if tok == FDT_BEGIN_NODE:
            end = d.find(b'\0', p)
            p = (end + 4) & ~3
        elif tok == FDT_END_NODE:
            pass
        elif tok == FDT_PROP:
            length, nameoff = struct.unpack('>II', d[p:p + 8])
            p += 8
            name = name_at(nameoff)
            if name in TARGETS and length == 4:
                old = struct.unpack('>I', bytes(d[p:p + 4]))[0]
                new = TARGETS[name]
                if old != new:
                    d[p:p + 4] = struct.pack('>I', new)
                    print('  %-22s %6d -> %d' % (name, old, new))
                else:
                    print('  %-22s already %d' % (name, old))
                done.add(name)
            p = (p + length + 3) & ~3
        elif tok == FDT_NOP:
            pass
        elif tok == FDT_END:
            break
        else:
            raise SystemExit('%s: bad FDT token %#x at %d' % (path, tok, p - 4))

    missing = set(TARGETS) - done
    if missing:
        print('  WARNING: node(s) not found: %s' % ', '.join(sorted(missing)))
    open(path, 'wb').write(d)
    print('  wrote %s (%d bytes)' % (path, len(d)))


if __name__ == '__main__':
    for f in sys.argv[1:]:
        print(f)
        patch(f)
