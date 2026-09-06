import hashlib
import json
import os
import re
import sys
import urllib.parse
import urllib.request

SHARE_URL=os.environ['SHARE_URL']
FILE_ID=os.environ.get('FILE_ID','')
EXPECTED_SHA=os.environ.get('EXPECTED_SHA','')
MIN_SIZE=int(os.environ.get('MIN_SIZE','4000000'))
OUT=os.environ.get('OUT','index.html')
UA='Mozilla/5.0 AppleWebKit/605.1.15 Safari/605.1.15'


def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'*/*'})
    with urllib.request.urlopen(req,timeout=15) as r:
        return r.read(),r.geturl(),dict(r.headers)


def save(body,src):
    if len(body)<MIN_SIZE or b"Captain's Dash" not in body:return False
    got=hashlib.sha256(body).hexdigest()
    if EXPECTED_SHA and got!=EXPECTED_SHA:
        print('SHA mismatch',got,src);return False
    open(OUT,'wb').write(body)
    print('SUCCESS imported',len(body),'bytes from',src,'sha256',got)
    return True

share_id=urllib.parse.urlparse(SHARE_URL).path.rstrip('/').split('/')[-1]

# First ask the public share API for the exact file metadata.
for env in ['prod','dev']:
    api=f'https://api.firestorage.ai/{env}/file/shares/{share_id}/files?maxResults=1000'
    try:
        body,url,h=fetch(api)
        print('LIST',env,body.decode('utf-8','ignore'))
        data=json.loads(body)
        # Use returned fileId if available rather than assuming upload metadata.
        def walk(o):
            if isinstance(o,dict):
                if o.get('fileId'): yield o
                for v in o.values(): yield from walk(v)
            elif isinstance(o,list):
                for v in o: yield from walk(v)
        rows=list(walk(data))
        ids=[str(r.get('fileId')) for r in rows if r.get('fileId')]
        if FILE_ID and FILE_ID not in ids: ids.insert(0,FILE_ID)
        for fid in ids:
            base=f'https://api.firestorage.ai/{env}/file/shares/{share_id}'
            paths=[
                f'{base}/files/{fid}/download',
                f'{base}/files/{fid}/download-url',
                f'{base}/files/{fid}/downloadUrl',
                f'{base}/files/{fid}/signed-url',
                f'{base}/files/{fid}/signedUrl',
                f'{base}/download/{fid}',
                f'{base}/download?fileId={urllib.parse.quote(fid)}',
                f'https://api.firestorage.ai/{env}/file/download/{share_id}/{fid}',
                f'https://api.firestorage.ai/{env}/file/download?shareId={urllib.parse.quote(share_id)}&fileId={urllib.parse.quote(fid)}',
            ]
            for u in paths:
                try:
                    b,res,hdr=fetch(u)
                    print('TRY',u,'->',len(b),'bytes',hdr.get('Content-Type'),hdr.get('Content-Disposition'))
                    if save(b,res):sys.exit(0)
                    # Some endpoints return a signed URL as JSON.
                    try:
                        obj=json.loads(b)
                        strings=[]
                        def s(o):
                            if isinstance(o,dict):
                                for k,v in o.items():
                                    if isinstance(v,str):strings.append((k,v))
                                    s(v)
                            elif isinstance(o,list):
                                for v in o:s(v)
                        s(obj)
                        for k,v in strings:
                            if v.startswith('http'):
                                try:
                                    fb,furl,fh=fetch(v)
                                    print('SIGNED',k,v[:160],'->',len(fb),'bytes')
                                    if save(fb,furl):sys.exit(0)
                                except Exception as e: print('SIGNED ERR',repr(e))
                    except Exception: pass
                except Exception as e:
                    print('ERR',u,repr(e))
    except Exception as e:print('LIST ERR',env,repr(e))

# Inspect the public web-client route for the exact API path if guesses fail.
route='https://firestorage.ai/_next/static/chunks/app/(files)/ja/f/page-4d19ae0a4ce39d79.js'
try:
    js,_,_=fetch(route); txt=js.decode('utf-8','ignore')
    for key in ['download','fileId','shares/','signed','presign']:
        print('JS EXCERPTS',key)
        for m in list(re.finditer(key,txt,re.I))[:20]:
            a=max(0,m.start()-350);z=min(len(txt),m.end()+500)
            print(txt[a:z].replace('\n',' ')[:900])
except Exception as e:print('JS ERR',repr(e))

print('FAILED to resolve full build download')
sys.exit(2)
