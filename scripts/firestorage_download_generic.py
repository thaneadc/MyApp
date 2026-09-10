import hashlib
import os
import pathlib
import time
import urllib.request

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

SHARE = os.environ['SHARE_URL']
NAME = os.environ['FILE_NAME']
EXPECTED = os.environ['EXPECTED_SHA']
OUT = pathlib.Path(os.environ['OUT']).resolve()
MIN_BYTES = int(os.environ.get('MIN_BYTES', '1'))
DL = pathlib.Path('downloads-v018').resolve()
DL.mkdir(exist_ok=True)


def verify(raw, source):
    if len(raw) < MIN_BYTES:
        return False
    sha = hashlib.sha256(raw).hexdigest()
    print('candidate', source, 'bytes', len(raw), 'sha', sha)
    if sha != EXPECTED:
        return False
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(raw)
    print('SUCCESS wrote', OUT)
    return True


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


opt = Options()
opt.add_argument('--headless=new')
opt.add_argument('--no-sandbox')
opt.add_argument('--disable-gpu')
opt.add_argument('--disable-dev-shm-usage')
opt.add_experimental_option('prefs', {
    'download.default_directory': str(DL),
    'download.prompt_for_download': False,
    'download.directory_upgrade': True,
    'safebrowsing.enabled': True,
})
opt.set_capability('goog:loggingPrefs', {'performance': 'ALL', 'browser': 'ALL'})
d = webdriver.Chrome(options=opt)
d.execute_cdp_cmd('Page.setDownloadBehavior', {'behavior': 'allow', 'downloadPath': str(DL)})

try:
    d.get(SHARE)
    time.sleep(4)
    print('initial url', d.current_url)
    print('initial body', d.find_element(By.TAG_NAME, 'body').text[:3000])

    found = d.find_elements(By.XPATH, f"//*[contains(normalize-space(.), '{NAME}')]")
    found = sorted(found, key=lambda e: len(e.text or ''))
    for e in found[:10]:
        try:
            target = e
            ancestors = e.find_elements(By.XPATH, 'ancestor-or-self::a | ancestor-or-self::button')
            if ancestors:
                target = ancestors[-1]
            d.execute_script('arguments[0].scrollIntoView({block:"center"})', target)
            d.execute_script('arguments[0].click()', target)
            print('clicked filename', (target.text or '')[:160])
            time.sleep(3)
            break
        except Exception as ex:
            print('filename click err', repr(ex))

    labels = ['Download', 'DOWNLOAD', 'ダウンロード', 'ファイルをダウンロード', 'ダウンロードする', '保存', '次へ', '続ける', '開く']
    for roundno in range(14):
        for p in DL.glob('*'):
            if p.is_file() and not p.name.endswith('.crdownload'):
                if verify(p.read_bytes(), 'download:' + str(p)):
                    raise SystemExit(0)

        cur = d.current_url
        if cur != SHARE and '/f/' not in cur:
            try:
                if verify(fetch(cur), 'current-url:' + cur):
                    raise SystemExit(0)
            except Exception as ex:
                print('current url fetch err', repr(ex))

        try:
            resources = d.execute_script("return performance.getEntriesByType('resource').map(x=>x.name)")
            for u in resources[-120:]:
                if any(k in u.lower() for k in ['download', 'storage', 'amazonaws', 'cloudflarestorage', 'blob.core', 'signed']):
                    try:
                        if verify(fetch(u), 'resource:' + u):
                            raise SystemExit(0)
                    except Exception:
                        pass
        except Exception:
            pass

        clicked = False
        for label in labels:
            xpath = f"//*[self::button or self::a or @role='button'][contains(normalize-space(.), '{label}')]"
            for e in d.find_elements(By.XPATH, xpath):
                try:
                    if not e.is_displayed():
                        continue
                    txt = (e.text or '').strip()
                    if len(txt) > 160:
                        continue
                    d.execute_script('arguments[0].scrollIntoView({block:"center"})', e)
                    d.execute_script('arguments[0].click()', e)
                    print('round', roundno, 'clicked', repr(txt), 'url', d.current_url)
                    clicked = True
                    time.sleep(3)
                    break
                except Exception:
                    pass
            if clicked:
                break
        if not clicked:
            print('round', roundno, 'no obvious button')
            time.sleep(2)

    raise SystemExit('Could not download verified file from Firestorage')
finally:
    d.quit()
