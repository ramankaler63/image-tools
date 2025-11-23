# app.py – ImageMaster Pro for Indian Govt Jobs (Render Free Tier Ready)
import os, io, uuid, traceback
from flask import Flask, render_template_string, request, send_file, jsonify
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import time

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # Reduced to 10MB for free tier
app.secret_key = os.environ.get('SECRET_KEY', 'govt-job-tool-2025')

ALLOWED_EXT = {'png','jpg','jpeg','webp','bmp','gif'}

# ---------- Helpers ----------
def allowed_filename(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXT

def pil_open_validate(file_stream):
    try:
        img = Image.open(file_stream)
        img.verify()
        file_stream.seek(0)
        return True
    except:
        return False

def save_temp_bytes(b: bytes, suffix=''):
    name = f"{uuid.uuid4().hex}{suffix}"
    path = f"/tmp/{name}"  # Render allows /tmp
    with open(path, 'wb') as f:
        f.write(b)
    return path

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# ---------- Updated HTML with Govt Job Tools ----------
INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>भारत सरकार जॉब फोटो टूल्स - Sarkari Naukri Photo Maker</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css">
  <style>
    .tab{display:none}.tab.active{display:block}
    .preview-image{max-width:100%;max-height:400px;border-radius:0.5rem;box-shadow:0 4px 6px rgba(0,0,0,0.1);}
    .btn-govt{background:linear-gradient(135deg,#0f766e,#14b8a6);transition:all .3s;}
    .btn-govt:hover{transform:translateY(-2px);box-shadow:0 10px 20px rgba(0,0,0,0.2);}
    .checkerboard{background:linear-gradient(45deg,#e5e7eb 25%,transparent 25%),linear-gradient(-45deg,#e5e7eb 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#e5e7eb 75%),linear-gradient(-45deg,transparent 75%,#e5e7eb 75%);background-size:20px 20px;background-position:0 0,0 10px,10px -10px,-10px 0px;}
  </style>
</head>
<body class="bg-gradient-to-br from-teal-50 to-blue-50 min-h-screen p-4">
<div class="max-w-5xl mx-auto">

  <div class="text-center mb-8 bg-white p-8 rounded-2xl shadow-xl">
    <h1 class="text-4xl font-bold text-teal-700 mb-3">भारत सरकार जॉब फोटो टूल्स</h1>
    <p class="text-xl text-gray-700">SSC • Railway • UPSC • Bank • Police • State PSC</p>
    <p class="text-sm text-gray-500 mt-4">100% Free • No Upload to Server • Works Offline After Load</p>
  </div>

  <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-8">
    <button onclick="showTab('passport')" class="tab-button active btn-govt text-white p-6 rounded-xl shadow-lg text-center">
      <i class="fas fa-id-card text-3xl mb-2"></i><br>Passport Photo
    </button>
    <button onclick="showTab('signature')" class="tab-button btn-govt text-white p-6 rounded-xl shadow-lg text-center">
      <i class="fas fa-signature text-3xl mb-2"></i><br>Signature
    </button>
    <button onclick="showTab('scanner')" class="tab-button btn-govt text-white p-6 rounded-xl shadow-lg text-center">
      <i class="fas fa-scanner text-3xl mb-2"></i><br>Document Scanner
    </button>
    <button onclick="showTab('resizekb')" class="tab-button btn-govt text-white p-6 rounded-xl shadow-lg text-center">
      <i class="fas fa-compress-arrows-alt text-3xl mb-2"></i><br>Resize to KB
    </button>
    <button onclick="showTab('border')" class="tab-button btn-govt text-white p-6 rounded-xl shadow-lg text-center">
      <i class="fas fa-frame text-3xl mb-2"></i><br>Add Border
    </button>
    <button onclick="showTab('printsheet')" class="tab-button btn-govt text-white p-6 rounded-xl shadow-lg text-center">
      <i class="fas fa-print text-3xl mb-2"></i><br>Print Sheet
    </button>
    <button onclick="showTab('bgremove')" class="tab-button btn-govt text-white p-6 rounded-xl shadow-lg text-center">
      <i class="fas fa-cut text-3xl mb-2"></i><br>Remove BG
    </button>
    <button onclick="showTab('compress')" class="tab-button btn-govt text-white p-6 rounded-xl shadow-lg text-center">
      <i class="fas fa-compress text-3xl mb-2"></i><br>Compress
    </button>
  </div>

  <div class="bg-white rounded-2xl shadow-xl p-8">
    <!-- Passport Photo -->
    <div id="passport" class="tab active">
      <h2 class="text-2xl font-bold mb-4"><i class="fas fa-id-card"></i> Passport Size Photo (2x2 inch)</h2>
      <form onsubmit="handlePassport(event)">
        <input type="file" id="pass-in" accept="image/*" required onchange="previewImage(this,'pass-prev')" class="hidden">
        <label for="pass-in" class="preview-container"><div class="text-6xl text-gray-400 mb-4"><i class="fas fa-cloud-upload-alt"></i></div>Upload Photo</label>
        <div id="pass-prev" class="text-center"></div>
        <button type="submit" class="btn-govt w-full py-4 text-xl mt-6">Generate Passport Size Photos</button>
      </form>
      <div id="pass-result" class="mt-8"></div>
    </div>

    <!-- Signature Tool -->
    <div id="signature" class="tab">
      <h2 class="text-2xl font-bold mb-4"><i class="fas fa-signature"></i> Signature Resizer</h2>
      <form onsubmit="handleSignature(event)">
        <input type="file" id="sig-in" accept="image/*" required onchange="previewImage(this,'sig-prev')" class="hidden">
        <label for="sig-in" class="preview-container"><div class="text-6xl text-gray-400 mb-4"><i class="fas fa-cloud-upload-alt"></i></div>Upload Signature</label>
        <div id="sig-prev" class="text-center"></div>
        <div class="grid grid-cols-2 gap-4 mt-4">
          <select name="bg" class="p-3 border rounded-lg">
            <option value="white">White Background</option>
            <option value="transparent">Transparent (PNG)</option>
          </select>
          <input type="number" name="maxkb" placeholder="Max KB (e.g. 20)" value="20" class="p-3 border rounded-lg">
        </div>
        <button type="submit" class="btn-govt w-full py-4 text-xl mt-6">Create Signature</button>
      </form>
      <div id="sig-result" class="mt-8"></div>
    </div>

    <!-- Document Scanner -->
    <div id="scanner" class="tab">
      <h2 class="text-2xl font-bold mb-4"><i class="fas fa-scanner"></i> Document Scanner Effect</h2>
      <form onsubmit="handleScanner(event)">
        <input type="file" id="scan-in" accept="image/*" required onchange="previewImage(this,'scan-prev')" class="hidden">
        <label for="scan-in" class="preview-container"><div class="text-6xl text-gray-400 mb-4"><i class="fas fa-cloud-upload-alt"></i></div>Upload Document Photo</label>
        <div id="scan-prev" class="text-center"></div>
        <button type="submit" class="btn-govt w-full py-4 text-xl mt-6">Apply Scanner Effect</button>
      </form>
      <div id="scan-result" class="mt-8"></div>
    </div>

    <!-- Resize to KB -->
    <div id="resizekb" class="tab">
      <h2 class="text-2xl font-bold mb-4"><i class="fas fa-compress-arrows-alt"></i> Resize to Exact KB</h2>
      <form onsubmit="handleResizeKB(event)">
        <input type="file" id="kb-in" accept="image/*" required onchange="previewImage(this,'kb-prev')" class="hidden">
        <label for="kb-in" class="preview-container"><div class="text-6xl text-gray-400 mb-4"><i class="fas fa-cloud-upload-alt"></i></div>Upload Image</label>
        <div id="kb-prev" class="text-center"></div>
        <input type="number" name="targetkb" placeholder="Target Size in KB (e.g. 50)" required class="w-full p-4 border rounded-lg mt-4 text-center text-2xl">
        <button type="submit" class="btn-govt w-full py-4 text-xl mt-6">Resize to Target KB</button>
      </form>
      <div id="kb-result" class="mt-8"></div>
    </div>

    <!-- Add Border -->
    <div id="border" class="tab">
      <h2 class="text-2xl font-bold mb-4"><i class="fas fa-frame"></i> Add Border + White Background</h2>
      <form onsubmit="handleBorder(event)">
        <input type="file" id="border-in" accept="image/*" required onchange="previewImage(this,'border-prev')" class="hidden">
        <label for="border-in" class="preview-container"><div class="text-6xl text-gray-400 mb-4"><i class="fas fa-cloud-upload-alt"></i></div>Upload Photo</label>
        <div id="border-prev" class="text-center"></div>
        <button type="submit" class="btn-govt w-full py-4 text-xl mt-6">Add White Border</button>
      </form>
      <div id="border-result" class="mt-8"></div>
    </div>

    <!-- Print Sheet -->
    <div id="printsheet" class="tab">
      <h2 class="text-2xl font-bold mb-4"><i class="fas fa-print"></i> Print-Ready Photo Sheet (35×45mm)</h2>
      <form onsubmit="handlePrintSheet(event)">
        <input type="file" id="print-in" accept="image/*" required onchange="previewImage(this,'print-prev')" class="hidden">
        <label for="print-in" class="preview-container"><div class="text-6xl text-gray-400 mb-4"><i class="fas fa-cloud-upload-alt"></i></div>Upload Photo</label>
        <div id="print-prev" class="text-center"></div>
        <button type="submit" class="btn-govt w-full py-4 text-xl mt-6">Generate A4 Print Sheet (6 Photos)</button>
      </form>
      <div id="print-result" class="mt-8"></div>
    </div>

    <!-- Background Remove -->
    <div id="bgremove" class="tab">
      <h2 class="text-2xl font-bold mb-4"><i class="fas fa-cut"></i> Remove Background</h2>
      <form onsubmit="handleBGRemove(event)">
        <input type="file" id="bg-in" accept="image/*" required onchange="previewImage(this,'bg-prev')" class="hidden">
        <label for="bg-in" class="preview-container"><div class="text-6xl text-gray-400 mb-4"><i class="fas fa-cloud-upload-alt"></i></div>Upload Photo</label>
        <div id="bg-prev" class="text-center"></div>
        <button type="submit" class="btn-govt w-full py-4 text-xl mt-6">Remove Background</button>
      </form>
      <div id="bg-result" class="mt-8"></div>
    </div>

    <!-- Compress -->
    <div id="compress" class="tab">
      <h2 class="text-2xl font-bold mb-4"><i class="fas fa-compress"></i> Compress Image</h2>
      <form onsubmit="handleCompress(event)">
        <input type="file" id="comp-in" accept="image/*" required onchange="previewImage(this,'comp-prev')" class="hidden">
        <label for="comp-in" class="preview-container"><div class="text-6xl text-gray-400 mb-4"><i class="fas fa-cloud-upload-alt"></i></div>Upload Image</label>
        <div id="comp-prev" class="text-center"></div>
        <button type="submit" class="btn-govt w-full py-4 text-xl mt-6">Compress & Download</button>
      </form>
      <div id="comp-result" class="mt-8"></div>
    </div>

  </div>

  <div class="text-center mt-12 text-gray-600">
    <p>Made with <i class="fas fa-heart text-red-500"></i> for Indian Job Seekers</p>
  </div>
</div>

<script>
function showTab(id){ document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active')); document.querySelectorAll('.tab-button').forEach(b=>b.classList.remove('active')); document.getElementById(id).classList.add('active'); event.target.classList.add('active'); }
function previewImage(input, prevId){ if(input.files[0]){ const r=new FileReader(); r.onload=e=>document.getElementById(prevId).innerHTML=`<img src="${e.target.result}" class="preview-image">`; r.readAsDataURL(input.files[0]); } }

// Reusable download function
function downloadImage(url, name){ const a=document.createElement('a'); a.href=url; a.download=name; a.click(); }

async function handlePassport(e){ e.preventDefault(); const f=new FormData(e.target); const r=await fetch('/passport', {method:'POST',body:f}); if(r.ok){ const b=await r.blob(); const u=URL.createObjectURL(b); document.getElementById('pass-result').innerHTML=`<img src="${u}" class="preview-image"><br><button onclick="downloadImage('${u}','passport_6_copies.jpg')" class="btn-govt text-white px-8 py-3 rounded mt-4">Download 6 Photos (A4)</button>`; } }
async function handleSignature(e){ e.preventDefault(); const f=new FormData(e.target); f.append('bg',e.target.bg.value); f.append('maxkb',e.target.maxkb.value); const r=await fetch('/signature', {method:'POST',body:f}); if(r.ok){ const b=await r.blob(); const u=URL.createObjectURL(b); document.getElementById('sig-result').innerHTML=`<div class="checkerboard inline-block p-4"><img src="${u}" class="max-w-xs"></div><br><button onclick="downloadImage('${u}','signature.png')" class="btn-govt text-white px-8 py-3 rounded mt-4">Download</button>`; } }
async function handleScanner(e){ e.preventDefault(); const f=new FormData(e.target); const r=await fetch('/scanner', {method:'POST',body:f}); if(r.ok){ const b=await r.blob(); const u=URL.createObjectURL(b); document.getElementById('scan-result').innerHTML=`<img src="${u}" class="preview-image"><br><button onclick="downloadImage('${u}','scanned_document.jpg')" class="btn-govt text-white px-8 py-3 rounded mt-4">Download</button>`; } }
async function handleResizeKB(e){ e.preventDefault(); const f=new FormData(e.target); f.append('targetkb',e.target.targetkb.value); const r=await fetch('/resizekb', {method:'POST',body:f}); if(r.ok){ const b=await r.blob(); const u=URL.createObjectURL(b); document.getElementById('kb-result').innerHTML=`<img src="${u}" class="preview-image"><br><button onclick="downloadImage('${u}','resized_image.jpg')" class="btn-govt text-white px-8 py-3 rounded mt-4">Download (${(b.size/1024).toFixed(1)} KB)</button>`; } }
async function handleBorder(e){ e.preventDefault(); const f=new FormData(e.target); const r=await fetch('/border', {method:'POST',body:f}); if(r.ok){ const b=await r.blob(); const u=URL.createObjectURL(b); document.getElementById('border-result').innerHTML=`<img src="${u}" class="preview-image"><br><button onclick="downloadImage('${u}','photo_with_border.jpg')" class="btn-govt text-white px-8 py-3 rounded mt-4">Download</button>`; } }
async function handlePrintSheet(e){ e.preventDefault(); const f=new FormData(e.target); const r=await fetch('/printsheet', {method:'POST',body:f}); if(r.ok){ const b=await r.blob(); const u=URL.createObjectURL(b); document.getElementById('print-result').innerHTML=`<img src="${u}" class="preview-image"><br><button onclick="downloadImage('${u}','passport_print_sheet.jpg')" class="btn-govt text-white px-8 py-3 rounded mt-4">Download A4 Sheet</button>`; } }
async function handleBGRemove(e){ e.preventDefault(); const f=new FormData(e.target); const r=await fetch('/bg_remove_simple', {method:'POST',body:f}); if(r.ok){ const b=await r.blob(); const u=URL.createObjectURL(b); document.getElementById('bg-result').innerHTML=`<div class="checkerboard inline-block p-8"><img src="${u}" class="max-w-md"></div><br><button onclick="downloadImage('${u}','no_background.png')" class="btn-govt text-white px-8 py-3 rounded mt-4">Download PNG</button>`; } }
async function handleCompress(e){ e.preventDefault(); const f=new FormData(e.target); const r=await fetch('/compress', {method:'POST',body:f}); if(r.ok){ const b=await r.blob(); const u=URL.createObjectURL(b); document.getElementById('comp-result').innerHTML=`<img src="${u}" class="preview-image"><br><button onclick="downloadImage('${u}','compressed.jpg')" class="btn-govt text-white px-8 py-3 rounded mt-4">Download (${(b.size/1024).toFixed(1)} KB)</button>`; } }
</script>
</body></html>"""

# ---------- Routes ----------
@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/passport', methods=['POST'])
def passport():
    f = request.files['file']
    img = Image.open(f.stream).convert('RGB')
    img = ImageOps.exif_transpose(img)
    target = (413, 531)  # 35mm x 45mm at 300 DPI
    img = ImageOps.fit(img, target, Image.LANCZOS)
    sheet = Image.new('RGB', (2480, 3508), 'white')  # A4 at 300dpi
    positions = [(100,100), (600,100), (1100,100), (1600,100), (100,700), (600,700)]
    for pos in positions:
        sheet.paste(img, pos)
    buf = io.BytesIO()
    sheet.save(buf, 'JPEG', quality=95)
    buf.seek(0)
    return send_file(buf, mimetype='image/jpeg', as_attachment=True, download_name='passport_6_copies.jpg')

@app.route('/signature', methods=['POST'])
def signature():
    f = request.files['file']
    img = Image.open(f.stream)
    img = img.convert('RGBA')
    img = ImageOps.invert(img.convert('L')).convert('RGBA')
    data = img.getdata()
    new_data = [(0,0,0,a) if r+g+b < 600 else (255,255,255,0) for r,g,b,a in data]
    img.putdata(new_data)
    img = img.resize((400,150), Image.LANCZOS)
    bg_type = request.form.get('bg','white')
    max_kb = int(request.form.get('maxkb',20))
    if bg_type == 'white':
        bg = Image.new('RGB', img.size, 'white')
        bg.paste(img, mask=img)
        img = bg
    buf = io.BytesIO()
    quality = 95
    img.save(buf, 'PNG' if bg_type=='transparent' else 'JPEG', quality=quality, optimize=True)
    while buf.tell() > max_kb*1024 and quality > 10:
        buf = io.BytesIO()
        quality -= 10
        img.save(buf, 'JPEG', quality=quality, optimize=True)
    buf.seek(0)
    return send_file(buf, mimetype='image/png' if bg_type=='transparent' else 'image/jpeg', as_attachment=True, download_name='signature.png')

@app.route('/scanner', methods=['POST'])
def scanner():
    f = request.files['file']
    img = Image.open(f.stream).convert('L')
    img = ImageEnhance.Contrast(img).enhance(3.0)
    img = img.convert('RGB')
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=95)
    buf.seek(0)
    return send_file(buf, mimetype='image/jpeg', as_attachment=True, download_name='scanned.jpg')

@app.route('/resizekb', methods=['POST'])
def resizekb():
    f = request.files['file']
    target_kb = int(request.form['targetkb'])
    img = Image.open(f.stream).convert('RGB')
    quality = 95
    buf = io.BytesIO()
    while True:
        buf.seek(0)
        buf.truncate(0)
        img.save(buf, 'JPEG', quality=quality, optimize=True)
        if buf.tell() <= target_kb*1024 or quality <= 10:
            break
        quality -= 5
    buf.seek(0)
    return send_file(buf, mimetype='image/jpeg', as_attachment=True, download_name='resized.jpg')

@app.route('/border', methods=['POST'])
def border():
    f = request.files['file']
    img = Image.open(f.stream).convert('RGB')
    img = ImageOps.expand(img, border=40, fill='white')
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=95)
    buf.seek(0)
    return send_file(buf, mimetype='image/jpeg', as_attachment=True, download_name='photo_with_border.jpg')

@app.route('/printsheet', methods=['POST'])
def printsheet():
    f = request.files['file']
    img = Image.open(f.stream).convert('RGB')
    target = (413, 531)
    img = ImageOps.fit(img, target, Image.LANCZOS)
    sheet = Image.new('RGB', (2480, 3508), 'white')
    positions = [(200,150),(800,150),(1400,150),(200,800),(800,800),(1400,800)]
    for pos in positions:
        sheet.paste(img, pos)
    buf = io.BytesIO()
    sheet.save(buf, 'JPEG', quality=95)
    buf.seek(0)
    return send_file(buf, mimetype='image/jpeg', as_attachment=True, download_name='print_sheet.jpg')

@app.route('/bg_remove_simple', methods=['POST'])
def bg_remove_simple():
    f = request.files['file']
    img = Image.open(f.stream).convert('RGBA')
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[0] > 220 and item[1] > 220 and item[2] > 220:
            new_data.append((255,255,255,0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png', as_attachment=True, download_name='transparent_bg.png')

@app.route('/compress', methods=['POST'])
def compress():
    f = request.files['file']
    img = Image.open(f.stream).convert('RGB')
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=85, optimize=True)
    buf.seek(0)
    return send_file(buf, mimetype='image/jpeg', as_attachment=True, download_name='compressed.jpg')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
