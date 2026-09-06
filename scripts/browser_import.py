import hashlib
import json
import os
import pathlib
import time
import urllib.request

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

SHARE=os.environ['SHARE_URL']
NAME='Captains_Dash_Full_Game_v0.7.2_PRODUCTION.html'
EXPECTED=os.environ['EXPECTED_SHA']
OUT=pathlib.Path(os.environ.get('OUT','index.html')).resolve()
DL=pathlib.Path('downloads').resolve(); DL.mkdir(exist_ok=True)


def verify(raw, source):
    if len(raw) < 4_000_000 or b"Captain's Dash" not in raw:
        return False
    sha=hashlib.sha256(raw).hexdigest()
    print('candidate',source,'bytes',len(raw),'sha',sha)
    if sha != EXPECTED:
        return False
    OUT.write_bytes(raw)
    print('SUCCESS wrote',OUT)
    return True


def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'*/*'})
    with urllib.request.urlopen(req,timeout=30) as r:return r.read()

opt=Options()
opt.add_argument('--headless=new'); opt.add_argument('--no-sandbox'); opt.add_argument('--disable-gpu'); opt.add_argument('--disable-dev-shm-usage')
opt.add_experimental_option('prefs',{'download.default_directory':str(DL),'download.prompt_for_download':False,'download.directory_upgrade':True,'safebrowsing.enabled':True})
opt.set_capability('goog:loggingPrefs', {'performance':'ALL','browser':'ALL'})
d=webdriver.Chrome(options=opt)
d.execute_cdp_cmd('Page.setDownloadBehavior', {'behavior':'allow','downloadPath':str(DL)})

try:
    d.get(SHARE); time.sleep(4)
    print('initial url',d.current_url)
    print('initial body',d.find_element(By.TAG_NAME,'body').text[:5000])

    # Click the file row/card first. Prefer the smallest element containing the filename.
    found=d.find_elements(By.XPATH, f"//*[contains(normalize-space(.), '{NAME}')]")
    found=sorted(found,key=lambda e: len(e.text or ''))
    for e in found[:10]:
        try:
            target=e
            ancestors=e.find_elements(By.XPATH,'ancestor-or-self::a | ancestor-or-self::button')
            if ancestors: target=ancestors[-1]
            d.execute_script('arguments[0].scrollIntoView({block:"center"})',target)
            d.execute_script('arguments[0].click()',target)
            print('clicked filename element',target.tag_name,(target.text or '')[:200])
            time.sleep(3); break
        except Exception as ex: print('filename click err',repr(ex))

    labels=['Download','DOWNLOAD','ダウンロード','ファイルをダウンロード','ダウンロードする','保存','次へ','続ける','開く']
    for roundno in range(12):
        # Check browser downloads.
        for p in DL.glob('*'):
            if p.is_file() and not p.name.endswith('.crdownload'):
                raw=p.read_bytes()
                if verify(raw,'download:'+str(p)): raise SystemExit(0)

        # A click may navigate to a signed/public file URL. Fetch it raw.
        cur=d.current_url
        if cur != SHARE and '/f/' not in cur:
            try:
                raw=fetch(cur)
                if verify(raw,'current-url:'+cur): raise SystemExit(0)
            except Exception as ex: print('current url fetch err',repr(ex))

        # Inspect performance resources for a signed/download URL.
        try:
            resources=d.execute_script("return performance.getEntriesByType('resource').map(x=>x.name)")
            for u in resources[-100:]:
                if any(k in u.lower() for k in ['download','storage','amazonaws','r2.cloudflarestorage','blob.core','signed']):
                    try:
                        raw=fetch(u)
                        if verify(raw,'resource:'+u): raise SystemExit(0)
                    except Exception: pass
        except Exception: pass

        clicked=False
        for label in labels:
            xpath=f"//*[self::button or self::a or @role='button'][contains(normalize-space(.), '{label}')]"
            for e in d.find_elements(By.XPATH,xpath):
                try:
                    if not e.is_displayed(): continue
                    txt=(e.text or '').strip()
                    if len(txt)>160: continue
                    d.execute_script('arguments[0].scrollIntoView({block:"center"})',e)
                    d.execute_script('arguments[0].click()',e)
                    print('round',roundno,'clicked',repr(txt),'url',d.current_url)
                    clicked=True; time.sleep(3); break
                except Exception: pass
            if clicked: break
        if not clicked:
            print('round',roundno,'no obvious button; body:',d.find_element(By.TAG_NAME,'body').text[:5000])
            time.sleep(2)

    print('FINAL URL',d.current_url)
    print('FINAL BODY',d.find_element(By.TAG_NAME,'body').text[:10000])
    print('BROWSER LOG',d.get_log('browser')[-50:])
    raise SystemExit(2)
finally:
    d.quit()
