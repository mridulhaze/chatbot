import subprocess
import os
import fitz

html_content = """<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;600;700&display=swap');
  body {
    font-family: 'Hind Siliguri', 'Segoe UI', sans-serif;
    padding: 40px;
    color: #1e293b;
  }
  h1 { color: #065f46; }
</style>
</head>
<body>
  <h1>জাতীয় বিশ্ববিদ্যালয় AI অ্যাসিস্ট্যান্ট ও স্মার্ট সাপোর্ট প্ল্যাটফর্ম</h1>
  <p>বিশ্ববিদ্যালয়, শিক্ষার্থী, ভর্তি, পরীক্ষার রুটিন, ফরম পূরণ (EMS), ফলাফল, মার্কশিট ও সনদ উত্তোলন।</p>
</body>
</html>"""

with open('E:/projects/AI_CHAT_BOT/docs/test_render.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
cmd = [
    edge_exe,
    '--headless',
    '--disable-gpu',
    '--no-pdf-header-footer',
    '--print-to-pdf=E:/projects/AI_CHAT_BOT/docs/test_render.pdf',
    'file:///E:/projects/AI_CHAT_BOT/docs/test_render.html'
]
res = subprocess.run(cmd, capture_output=True)
print('PDF generated, returncode:', res.returncode)

doc = fitz.open('E:/projects/AI_CHAT_BOT/docs/test_render.pdf')
pix = doc[0].get_pixmap(dpi=150)
pix.save('E:/projects/AI_CHAT_BOT/docs/test_render_preview.png')
print('Preview image saved to E:/projects/AI_CHAT_BOT/docs/test_render_preview.png')
