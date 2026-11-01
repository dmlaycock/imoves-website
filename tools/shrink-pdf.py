import pikepdf, io, sys
from pikepdf import PdfImage, Name
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
pdf = pikepdf.open(src)
done = set(); n=0; saved=0
for raw in list(pdf.objects):
    if isinstance(raw, pikepdf.Stream) and raw.get('/Subtype') == Name('/Image'):
        name = str(raw.objgen)
        try:
            pim = PdfImage(raw); img = pim.as_pil_image()
        except Exception as e:
            cs = raw.get('/ColorSpace'); bpc = int(raw.get('/BitsPerComponent', 0) or 0)
            modes = {'/DeviceCMYK': 'CMYK', '/DeviceRGB': 'RGB', '/DeviceGray': 'L'}
            if bpc != 8 or str(cs) not in modes or '/Decode' in raw:
                print('skip', name, cs, bpc, e); continue
            try:
                img = Image.frombytes(modes[str(cs)], (int(raw['/Width']), int(raw['/Height'])), raw.read_bytes())
            except Exception as e2:
                print('skip', name, 'raw decode', e2); continue
        before = int(raw.get('/Length', 0))
        if before < 150000: continue
        if '/Decode' in raw or '/Mask' in raw: print('skip decode/mask', name); continue
        if img.mode == 'CMYK':
            img = img.convert('RGB')
        elif img.mode == 'L':
            pass
        elif img.mode not in ('RGB',):
            img = img.convert('RGB')
        # cap long side at 1600px: the brochure is viewed on screen
        w, h = img.size; m = max(w, h)
        if m > 1600:
            img = img.resize((round(w*1600/m), round(h*1600/m)), Image.LANCZOS)
        buf = io.BytesIO(); img.save(buf, 'JPEG', quality=82, optimize=True, progressive=True)
        data = buf.getvalue()
        if len(data) >= before: continue
        raw.write(data, filter=Name('/DCTDecode'))
        raw['/ColorSpace'] = Name('/DeviceRGB') if img.mode == 'RGB' else Name('/DeviceGray')
        raw['/BitsPerComponent'] = 8; raw['/Width'], raw['/Height'] = img.size
        for k in ('/Decode', '/DecodeParms'):
            if k in raw: del raw[k]
        n += 1; saved += before - len(data)
pdf.remove_unreferenced_resources()
pdf.save(dst, compress_streams=True, object_stream_mode=pikepdf.ObjectStreamMode.generate, linearize=True)
print('recompressed', n, 'images, saved', round(saved/1e6,1), 'MB')
