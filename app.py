# app.py – Govt Job Tools: 100% Client-Side (Fast & Free Tier Friendly)
import os
from flask import Flask, render_template_string

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'govt-tools-secret')

# No file size limit needed because files are processed in the browser!
# We only serve the HTML/JS.

INDEX_HTML = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GovtJob Image Tools - Fast & Secure</title>
  
  <script src="https://cdn.tailwindcss.com"></script>
  
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>

  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    body { font-family: 'Inter', sans-serif; }
    
    .tab { display: none; animation: fadeIn 0.3s ease-in-out; }
    .tab.active { display: block; }
    
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

    .preview-box {
      border: 2px dashed #cbd5e1;
      border-radius: 0.5rem;
      padding: 1.5rem;
      text-align: center;
      background: #f8fafc;
      cursor: pointer;
      transition: all 0.2s;
    }
    .preview-box:hover { border-color: #2563eb; background: #eff6ff; }
    
    .btn-primary {
      background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
      transition: transform 0.1s, box-shadow 0.2s;
    }
    .btn-primary:active { transform: scale(0.98); }
    
    .tab-btn.active {
      border-bottom: 2px solid #2563eb;
      color: #2563eb;
      background-color: #eff6ff;
      font-weight: 600;
    }
    
    .preset-card {
        cursor: pointer;
        border: 1px solid #e2e8f0;
        transition: all 0.2s;
    }
    .preset-card:hover { border-color: #2563eb; background-color: #eff6ff; }
    .preset-card.selected { border-color: #2563eb; background-color: #dbeafe; ring: 2px solid #2563eb; }

    .loader {
      border: 3px solid #f3f4f6;
      border-top: 3px solid #2563eb;
      border-radius: 50%;
      width: 24px;
      height: 24px;
      animation: spin 1s linear infinite;
      display: inline-block;
    }
    @keyframes spin{ 0%{transform: rotate(0deg);} 100%{transform: rotate(360deg);} }
  </style>
</head>
<body class="bg-slate-50 min-h-screen p-3 md:p-6">
  <div class="max-w-5xl mx-auto">
    
    <div class="bg-white p-6 rounded-2xl shadow-sm mb-6 border border-slate-200 flex flex-col md:flex-row justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <i class="fas fa-id-card text-blue-600"></i> GovtJob Tools
        </h1>
        <p class="text-slate-500 text-sm">Resize, Date Stamp & Convert for SSC, UPSC, IBPS</p>
      </div>
      <span class="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-bold">
        <i class="fas fa-bolt"></i> Client-Side Processing (Fast)
      </span>
    </div>

    <div class="bg-white rounded-xl shadow-sm mb-6 overflow-x-auto border border-slate-200">
      <div class="flex min-w-max">
        <button onclick="switchTab('tab-photo')" class="tab-btn active flex-1 px-6 py-4 text-slate-600 flex items-center gap-2 justify-center hover:bg-slate-50">
          <i class="fas fa-user-tie"></i> Photo Resizer
        </button>
        <button onclick="switchTab('tab-sig')" class="tab-btn flex-1 px-6 py-4 text-slate-600 flex items-center gap-2 justify-center hover:bg-slate-50">
          <i class="fas fa-signature"></i> Signature
        </button>
        <button onclick="switchTab('tab-date')" class="tab-btn flex-1 px-6 py-4 text-slate-600 flex items-center gap-2 justify-center hover:bg-slate-50">
          <i class="fas fa-calendar-plus"></i> Date on Photo
        </button>
        <button onclick="switchTab('tab-pdf')" class="tab-btn flex-1 px-6 py-4 text-slate-600 flex items-center gap-2 justify-center hover:bg-slate-50">
          <i class="fas fa-file-pdf"></i> Images to PDF
        </button>
      </div>
    </div>

    <div class="bg-white p-6 rounded-2xl shadow-lg min-h-[500px]">

      <div id="tab-photo" class="tab active">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="md:col-span-1 space-y-3">
             <h3 class="font-bold text-slate-700 text-sm uppercase tracking-wide">Select Exam</h3>
             <div id="photo-presets" class="space-y-2 h-64 overflow-y-auto pr-1 custom-scrollbar">
                </div>
          </div>
          
          <div class="md:col-span-2">
            <div class="preview-box mb-4 relative group">
              <input type="file" id="p-input" accept="image/*" class="absolute inset-0 opacity-0 cursor-pointer z-10" onchange="loadImage(this, 'p-preview', 'p-stats')">
              <div id="p-preview" class="min-h-[200px] flex items-center justify-center text-slate-400 flex-col">
                 <i class="fas fa-cloud-upload-alt text-4xl mb-2"></i>
                 <p>Click to Upload Photo</p>
              </div>
              <p id="p-stats" class="text-xs text-slate-500 mt-2 hidden"></p>
            </div>

            <div class="bg-slate-50 p-4 rounded-lg border border-slate-200 grid grid-cols-2 md:grid-cols-3 gap-4">
               <div>
                 <label class="block text-xs font-bold text-slate-500 mb-1">Width (px)</label>
                 <input type="number" id="p-w" class="w-full p-2 border rounded text-sm">
               </div>
               <div>
                 <label class="block text-xs font-bold text-slate-500 mb-1">Height (px)</label>
                 <input type="number" id="p-h" class="w-full p-2 border rounded text-sm">
               </div>
               <div>
                 <label class="block text-xs font-bold text-slate-500 mb-1">Max Size (KB)</label>
                 <input type="number" id="p-kb" class="w-full p-2 border rounded text-sm">
               </div>
            </div>
            
            <button onclick="processImage('photo')" class="btn-primary w-full text-white mt-4 py-3 rounded-lg font-bold shadow-lg flex justify-center items-center gap-2">
              <span id="p-btn-text">Process & Download</span>
              <div id="p-loader" class="loader hidden" style="border-color: #ffffff; border-top-color: transparent; width: 20px; height: 20px;"></div>
            </button>
            
            <div id="p-msg" class="mt-3 text-center text-sm font-medium"></div>
          </div>
        </div>
      </div>

      <div id="tab-sig" class="tab">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
           <div class="md:col-span-1 space-y-3">
             <h3 class="font-bold text-slate-700 text-sm uppercase tracking-wide">Signature Presets</h3>
             <div id="sig-presets" class="space-y-2">
                </div>
          </div>
          
          <div class="md:col-span-2">
             <div class="preview-box mb-4 relative">
              <input type="file" id="s-input" accept="image/*" class="absolute inset-0 opacity-0 cursor-pointer z-10" onchange="loadImage(this, 's-preview', 's-stats')">
              <div id="s-preview" class="min-h-[150px] flex items-center justify-center text-slate-400 flex-col">
                 <i class="fas fa-pen-nib text-4xl mb-2"></i>
                 <p>Upload Signature</p>
              </div>
              <p id="s-stats" class="text-xs text-slate-500 mt-2 hidden"></p>
            </div>
            
            <div class="bg-slate-50 p-4 rounded-lg border border-slate-200 grid grid-cols-3 gap-4">
               <input type="number" id="s-w" placeholder="Width" class="p-2 border rounded text-sm">
               <input type="number" id="s-h" placeholder="Height" class="p-2 border rounded text-sm">
               <input type="number" id="s-kb" placeholder="Max KB" class="p-2 border rounded text-sm">
            </div>

            <button onclick="processImage('sig')" class="btn-primary w-full text-white mt-4 py-3 rounded-lg font-bold shadow-lg flex justify-center items-center gap-2">
              <span id="s-btn-text">Process Signature</span>
              <div id="s-loader" class="loader hidden" style="border-color: #ffffff; border-top-color: transparent; width: 20px; height: 20px;"></div>
            </button>
            <div id="s-msg" class="mt-3 text-center text-sm font-medium"></div>
          </div>
        </div>
      </div>

      <div id="tab-date" class="tab">
        <div class="flex flex-col md:flex-row gap-8">
          <div class="flex-1">
            <div class="preview-box relative h-full flex flex-col justify-center">
              <input type="file" id="d-input" accept="image/*" class="absolute inset-0 opacity-0 cursor-pointer z-10" onchange="loadDatePreview(this)">
              <canvas id="d-canvas" class="max-w-full max-h-[400px] mx-auto shadow-md hidden"></canvas>
              <div id="d-placeholder" class="text-slate-400">
                 <i class="fas fa-camera text-4xl mb-2"></i>
                 <p>Upload Photo</p>
              </div>
            </div>
          </div>
          
          <div class="flex-1 space-y-5">
            <div class="bg-yellow-50 border border-yellow-200 p-4 rounded-lg text-sm text-yellow-800">
              <i class="fas fa-info-circle mr-1"></i> Adds a standard white strip with name/date at the bottom (SSC format).
            </div>
            
            <div>
              <label class="block text-sm font-bold text-slate-700 mb-2">Name (Optional)</label>
              <input type="text" id="d-name" placeholder="RAHUL KUMAR" class="w-full p-3 border border-slate-300 rounded-lg" oninput="updateDatePreview()">
            </div>
            
            <div>
              <label class="block text-sm font-bold text-slate-700 mb-2">Date of Photo (DOP)</label>
              <input type="date" id="d-date" class="w-full p-3 border border-slate-300 rounded-lg" oninput="updateDatePreview()">
            </div>

            <button onclick="downloadDatePhoto()" class="btn-primary w-full text-white py-3 rounded-lg font-bold shadow-lg">
              <i class="fas fa-download mr-2"></i> Download Photo
            </button>
          </div>
        </div>
      </div>

      <div id="tab-pdf" class="tab">
        <div class="text-center max-w-2xl mx-auto">
           <div class="preview-box mb-6 relative bg-blue-50 border-blue-200">
              <input type="file" id="pdf-input" accept="image/*" multiple class="absolute inset-0 opacity-0 cursor-pointer z-10" onchange="handlePdfFiles(this)">
              <div class="py-8">
                 <i class="fas fa-images text-5xl text-blue-400 mb-3"></i>
                 <h3 class="text-lg font-bold text-slate-700">Select Images</h3>
                 <p class="text-slate-500 text-sm">JPG, PNG supported</p>
              </div>
           </div>
           
           <div id="pdf-list" class="grid grid-cols-3 sm:grid-cols-4 gap-3 mb-6"></div>
           
           <button onclick="generatePDF()" class="btn-primary px-10 py-3 rounded-lg text-white font-bold shadow-lg disabled:opacity-50 disabled:cursor-not-allowed" id="pdf-btn" disabled>
             <i class="fas fa-file-pdf mr-2"></i> Create PDF
           </button>
           <div id="pdf-msg" class="mt-3 text-sm"></div>
        </div>
      </div>

    </div>
    
    <div class="text-center mt-8 text-slate-400 text-xs">
        <p>&copy; 2024 GovtJob Tools. Privacy: Files processed locally.</p>
    </div>
  </div>

<script>
// --- Constants & Presets ---
const PRESETS_PHOTO = [
    { name: "SSC (CGL, CHSL, MTS)", w: 350, h: 450, kb: 50, desc: "3.5 x 4.5 cm" },
    { name: "UPSC Civil Services", w: 350, h: 350, kb: 300, desc: "350 x 350 px" },
    { name: "IBPS / SBI PO", w: 450, h: 350, kb: 50, desc: "4.5 x 3.5 cm" },
    { name: "Railways (RRB)", w: 350, h: 450, kb: 40, desc: "15-40 KB" },
    { name: "GATE 2025", w: 480, h: 640, kb: 500, desc: "Aspect 0.75" },
    { name: "Custom Size", w: 0, h: 0, kb: 0, desc: "Manual Entry" }
];

const PRESETS_SIG = [
    { name: "SSC Signature", w: 400, h: 200, kb: 20, desc: "4.0 x 2.0 cm" },
    { name: "UPSC Signature", w: 350, h: 115, kb: 20, desc: "350 x 115 px" },
    { name: "IBPS Signature", w: 240, h: 120, kb: 20, desc: "10-20 KB" },
    { name: "Custom Size", w: 0, h: 0, kb: 0, desc: "Manual Entry" }
];

// --- Init ---
window.onload = () => {
    renderPresets('photo-presets', PRESETS_PHOTO, 'p');
    renderPresets('sig-presets', PRESETS_SIG, 's');
};

function switchTab(id) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    // Highlight button logic simplified
    event.currentTarget.classList.add('active');
}

function renderPresets(containerId, data, prefix) {
    const container = document.getElementById(containerId);
    container.innerHTML = data.map((p, idx) => `
        <div class="preset-card p-3 rounded-lg bg-slate-50 flex justify-between items-center" 
             onclick="applyPreset(this, '${prefix}', ${p.w}, ${p.h}, ${p.kb})">
            <div>
                <div class="font-bold text-slate-700 text-sm">${p.name}</div>
                <div class="text-xs text-slate-500">${p.desc} • Max ${p.kb ? p.kb+'KB' : 'N/A'}</div>
            </div>
            ${idx === 0 ? '<i class="fas fa-check-circle text-blue-500"></i>' : ''}
        </div>
    `).join('');
    
    // Select first by default
    if(data.length > 0) applyPreset(container.firstElementChild, prefix, data[0].w, data[0].h, data[0].kb);
}

function applyPreset(el, prefix, w, h, kb) {
    // Visual selection
    el.parentElement.querySelectorAll('.preset-card').forEach(c => {
        c.classList.remove('selected');
        const icon = c.querySelector('.fa-check-circle');
        if(icon) icon.remove();
    });
    el.classList.add('selected');
    el.insertAdjacentHTML('beforeend', '<i class="fas fa-check-circle text-blue-500"></i>');

    // Set values
    if(w) document.getElementById(prefix+'-w').value = w;
    if(h) document.getElementById(prefix+'-h').value = h;
    if(kb) document.getElementById(prefix+'-kb').value = kb;
}

// --- Core Image Processing ---

let currentFile = { p: null, s: null };
let dateFile = null;

function loadImage(input, previewId, statsId) {
    const file = input.files[0];
    if (!file) return;
    
    const type = previewId[0]; // 'p' or 's'
    currentFile[type] = file;

    const reader = new FileReader();
    reader.onload = (e) => {
        const img = document.createElement('img');
        img.src = e.target.result;
        img.className = "max-h-[200px] rounded shadow object-contain";
        
        const container = document.getElementById(previewId);
        container.innerHTML = '';
        container.appendChild(img);
        
        // Show stats
        const stats = document.getElementById(statsId);
        stats.textContent = `Original: ${file.name} (${(file.size/1024).toFixed(1)} KB)`;
        stats.classList.remove('hidden');
    };
    reader.readAsDataURL(file);
}

async function processImage(type) {
    const prefix = type === 'photo' ? 'p' : 's';
    const file = currentFile[prefix];
    const w = parseInt(document.getElementById(prefix+'-w').value);
    const h = parseInt(document.getElementById(prefix+'-h').value);
    const maxKb = parseInt(document.getElementById(prefix+'-kb').value);
    const msgDiv = document.getElementById(prefix+'-msg');
    const loader = document.getElementById(prefix+'-loader');
    const btnText = document.getElementById(prefix+'-btn-text');

    if (!file) {
        msgDiv.innerHTML = "<span class='text-red-500'>Please upload an image first.</span>";
        return;
    }

    // UI Loading State
    loader.classList.remove('hidden');
    btnText.textContent = "Processing...";
    msgDiv.innerHTML = "";

    try {
        // 1. Load Image to Canvas
        const imgBitmap = await createImageBitmap(file);
        const canvas = document.createElement('canvas');
        canvas.width = w || imgBitmap.width;
        canvas.height = h || imgBitmap.height;
        const ctx = canvas.getContext('2d');
        
        // Smooth resizing
        ctx.imageSmoothingEnabled = true;
        ctx.imageSmoothingQuality = 'high';
        ctx.drawImage(imgBitmap, 0, 0, canvas.width, canvas.height);

        // 2. Compression Loop (Binary Search for Quality)
        let blob = await new Promise(r => canvas.toBlob(r, 'image/jpeg', 0.95));
        
        if (maxKb && maxKb > 0) {
            let minQ = 0.1, maxQ = 1.0;
            let bestBlob = blob;
            
            // If initial is already small enough, good. If not, compress.
            if (blob.size / 1024 > maxKb) {
                for (let i = 0; i < 6; i++) { // Max 6 iterations
                    let midQ = (minQ + maxQ) / 2;
                    const tempBlob = await new Promise(r => canvas.toBlob(r, 'image/jpeg', midQ));
                    
                    if (tempBlob.size / 1024 > maxKb) {
                        maxQ = midQ; // Too big, lower quality
                    } else {
                        minQ = midQ; // Fits, try higher quality
                        bestBlob = tempBlob;
                    }
                }
                blob = bestBlob;
            }
        }

        // 3. Download
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `processed_${type}_${Date.now()}.jpg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        const finalSize = (blob.size / 1024).toFixed(1);
        msgDiv.innerHTML = `<span class='text-green-600'><i class='fas fa-check'></i> Done! Size: ${finalSize} KB</span>`;

    } catch (err) {
        console.error(err);
        msgDiv.innerHTML = "<span class='text-red-500'>Error processing image.</span>";
    } finally {
        loader.classList.add('hidden');
        btnText.textContent = type === 'photo' ? "Process & Download" : "Process Signature";
    }
}

// --- Date Stamp Logic ---
let dateImgObj = null;

function loadDatePreview(input) {
    const file = input.files[0];
    if(!file) return;
    dateFile = file;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        dateImgObj = new Image();
        dateImgObj.onload = updateDatePreview;
        dateImgObj.src = e.target.result;
        
        document.getElementById('d-placeholder').classList.add('hidden');
        document.getElementById('d-canvas').classList.remove('hidden');
    };
    reader.readAsDataURL(file);
}

function updateDatePreview() {
    if(!dateImgObj) return;
    
    const canvas = document.getElementById('d-canvas');
    const ctx = canvas.getContext('2d');
    
    // Set canvas size to original image size
    canvas.width = dateImgObj.width;
    canvas.height = dateImgObj.height;
    
    // Draw original
    ctx.drawImage(dateImgObj, 0, 0);
    
    const name = document.getElementById('d-name').value.toUpperCase();
    const date = document.getElementById('d-date').value;
    
    if(!name && !date) return; // Nothing to draw
    
    // Constants for styling
    const W = canvas.width;
    const H = canvas.height;
    const stripH = H * 0.15; // Strip is 15% of height
    const fontSize = stripH * 0.40; // Font is 40% of strip
    
    // Draw White Strip
    ctx.fillStyle = 'white';
    ctx.fillRect(0, H - stripH, W, stripH);
    
    // Text Settings
    ctx.fillStyle = 'black';
    ctx.textAlign = 'center';
    ctx.font = `bold ${fontSize}px Arial, sans-serif`;
    
    // Logic: if name exists, two lines. Else one line.
    const centerY = H - (stripH / 2);
    
    if (name) {
        ctx.fillText(name, W/2, centerY - (fontSize * 0.6));
        ctx.fillText(`DOP: ${formatDate(date)}`, W/2, centerY + (fontSize * 0.6));
    } else {
        ctx.fillText(`DOP: ${formatDate(date)}`, W/2, centerY + (fontSize * 0.3));
    }
}

function formatDate(dateStr) {
    if(!dateStr) return "DD-MM-YYYY";
    const d = new Date(dateStr);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    return `${day}-${month}-${d.getFullYear()}`;
}

function downloadDatePhoto() {
    const canvas = document.getElementById('d-canvas');
    if(canvas.classList.contains('hidden')) {
        alert("Please upload an image first");
        return;
    }
    
    const link = document.createElement('a');
    link.download = 'photo_with_date.jpg';
    link.href = canvas.toDataURL('image/jpeg', 0.95);
    link.click();
}

// --- PDF Logic ---
let pdfFilesList = [];

function handlePdfFiles(input) {
    pdfFilesList = Array.from(input.files);
    const grid = document.getElementById('pdf-list');
    const btn = document.getElementById('pdf-btn');
    
    grid.innerHTML = '';
    
    if(pdfFilesList.length > 0) {
        btn.disabled = false;
        pdfFilesList.forEach(f => {
            const div = document.createElement('div');
            div.className = "bg-slate-50 p-2 border rounded text-center";
            div.innerHTML = `<div class="text-xs truncate text-slate-600"><i class="fas fa-image mr-1"></i>${f.name.substring(0,10)}...</div>`;
            grid.appendChild(div);
        });
    } else {
        btn.disabled = true;
    }
}

async function generatePDF() {
    const btn = document.getElementById('pdf-btn');
    const msg = document.getElementById('pdf-msg');
    
    btn.disabled = true;
    btn.innerHTML = '<div class="loader" style="width:20px;height:20px;border-width:2px"></div> Generating...';
    
    try {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        for (let i = 0; i < pdfFilesList.length; i++) {
            if (i > 0) doc.addPage();
            
            const file = pdfFilesList[i];
            const imgData = await readFileAsDataURL(file);
            const imgProps = doc.getImageProperties(imgData);
            
            const pdfWidth = doc.internal.pageSize.getWidth();
            const pdfHeight = doc.internal.pageSize.getHeight();
            
            // Scale to fit page
            const ratio = Math.min(pdfWidth / imgProps.width, pdfHeight / imgProps.height);
            const w = imgProps.width * ratio;
            const h = imgProps.height * ratio;
            const x = (pdfWidth - w) / 2;
            const y = (pdfHeight - h) / 2;
            
            doc.addImage(imgData, 'JPEG', x, y, w, h);
        }
        
        doc.save(`combined_images_${Date.now()}.pdf`);
        msg.innerHTML = "<span class='text-green-600'>PDF Downloaded!</span>";
        
    } catch (e) {
        console.error(e);
        msg.innerHTML = "<span class='text-red-600'>Error generating PDF</span>";
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-file-pdf mr-2"></i> Create PDF';
    }
}

function readFileAsDataURL(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
