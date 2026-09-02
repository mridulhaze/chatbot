import subprocess
import os
import base64
import fitz

with open('docs/HindSiliguri-Regular.ttf', 'rb') as f:
    regular_b64 = base64.b64encode(f.read()).decode('utf-8')

with open('docs/HindSiliguri-Bold.ttf', 'rb') as f:
    bold_b64 = base64.b64encode(f.read()).decode('utf-8')

with open('docs/HindSiliguri-SemiBold.ttf', 'rb') as f:
    semibold_b64 = base64.b64encode(f.read()).decode('utf-8')

html_content = f"""<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="UTF-8">
<title>বাংলা টেস্ট</title>
<style>
  @font-face {{
    font-family: 'HindSiliguriCustom';
    src: url('data:font/truetype;charset=utf-8;base64,{regular_b64}') format('truetype');
    font-weight: normal;
    font-style: normal;
  }}
  @font-face {{
    font-family: 'HindSiliguriCustom';
    src: url('data:font/truetype;charset=utf-8;base64,{semibold_b64}') format('truetype');
    font-weight: 600;
    font-style: normal;
  }}
  @font-face {{
    font-family: 'HindSiliguriCustom';
    src: url('data:font/truetype;charset=utf-8;base64,{bold_b64}') format('truetype');
    font-weight: bold;
    font-style: normal;
  }}

  body {{ 
    font-family: 'HindSiliguriCustom', sans-serif; 
    padding: 40px; 
    font-size: 16px;
    color: #1e293b;
    line-height: 1.6;
  }}
  h1 {{ color: #0369a1; font-weight: bold; font-size: 24px; margin-bottom: 8px; }}
  h2 {{ color: #0f172a; font-weight: 600; font-size: 18px; margin-top: 16px; }}
  .badge {{ background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 4px; font-weight: 600; font-size: 13px; }}
</style>
</head>
<body>
  <span class="badge">জাতীয় বিশ্ববিদ্যালয় এআই অ্যাসিস্ট্যান্ট</span>
  <h1>জাতীয় বিশ্ববিদ্যালয় AI অ্যাসিস্ট্যান্ট ও সাপোর্ট প্ল্যাটফর্ম</h1>
  <h2>সিস্টেম পর্যালোচনা ও সম্পূর্ণ ব্যবহারকারী এবং ডেভেলপার নির্দেশিকা</h2>
  <p><b>সফলভাবে বাংলা ফন্ট রেন্ডার হয়েছে।</b> যুক্তবর্ণ ও কার-চিহ্ন পরীক্ষা: জাতীয় বিশ্ববিদ্যালয়, পরীক্ষা নিয়ন্ত্রণ দপ্তর, প্রকৌশল ও স্থাপত্য, তথ্য ও যোগাযোগ প্রযুক্তি (ICT), শিক্ষার্থী সেবা পোর্টাল, টোকেন সাপোর্ট সেন্টার।</p>
  <p>এই নির্দেশিকায় প্রতিটি সিস্টেম কম্পোনেন্ট, ওয়ার্কফ্লো, ডাটাবেস আর্কিটেকচার এবং ব্যবহারবিধি বিস্তারিতভাবে লিপিবদ্ধ করা হয়েছে।</p>
</body>
</html>"""

with open('docs/test_bn.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
cmd = [
    chrome_path,
    '--headless=new',
    '--disable-gpu',
    '--no-pdf-header-footer',
    '--print-to-pdf=docs/test_bn.pdf',
    os.path.abspath('docs/test_bn.html')
]
res = subprocess.run(cmd, capture_output=True, text=True)

doc = fitz.open('docs/test_bn.pdf')
doc[0].get_pixmap(dpi=150).save('docs/test_bn_page.png')
print('Rendered to PNG successfully with base64 HindSiliguri')
