#!/usr/bin/env python3
import argparse, json, re, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_FOLDER_ID = "1bknLSlpI2qJnQfAod7N1GujfJ4p1gTAy"
FOLDER_URL = "https://drive.google.com/drive/folders/{id}"
DOWNLOAD_URL = "https://drive.google.com/uc?export=download&id={id}"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
TIMEOUT=45
FOLDER_MIME="application/vnd.google-apps.folder"
ENTRY_HEAD=r'\[null,"([A-Za-z0-9_-]{25,44})"\](?:(?!\[null,"[A-Za-z0-9_-]{25,44}"\]).{0,400}?)'
FOLDER_ENTRY_RE=re.compile(ENTRY_HEAD+re.escape(FOLDER_MIME),re.S)
FILE_ENTRY_RE=re.compile(ENTRY_HEAD+r'"image/(?:png|jpeg|webp)"',re.S)
LABEL_RE=re.compile(r'\[\[\["(qsl\d+)"')
FILENAME_RE=re.compile(r'"([^"]+\.(?:png|jpg|jpeg|webp))"')
ACTIVITY_TITLES={f"qsl{i}":f"Actividad {i}" for i in range(1,20)}
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':USER_AGENT})
    try:
        with urllib.request.urlopen(req,timeout=TIMEOUT) as r:
            return r.read().decode('utf-8','replace')
    except Exception as e:
        raise SystemExit(e)

def split_blocks(html,entry_re):
    m=list(entry_re.finditer(html)); b=[]
    for i,x in enumerate(m):
        end=m[i+1].start() if i+1<len(m) else len(html); b.append((x.group(1),x.start(),end))
    return b

def parse_folders(html):
    pairs=[]
    seen_id=set()
    for fid,s,e in split_blocks(html,FOLDER_ENTRY_RE):
        if fid in seen_id: continue
        seen_id.add(fid)
        lab=LABEL_RE.search(html[s:e])
        if lab:
            pairs.append((lab.group(1).lower(),fid))
    pairs.sort(key=lambda x:(int(x[0][3:]) if x[0].startswith('qsl') and x[0][3:].isdigit() else 999,x[0]))
    return pairs

def parse_files(html):
    files=[]; seen=set()
    for fid,s,e in split_blocks(html,FILE_ENTRY_RE):
        if fid in seen: continue
        nm=FILENAME_RE.search(html[s:e])
        if not nm: continue
        seen.add(fid); files.append({'id':fid,'name':nm.group(1)})
    return files

def fsize(fid):
    try:
        req=urllib.request.Request(DOWNLOAD_URL.format(id=fid),headers={'User-Agent':USER_AGENT},method='GET')
        with urllib.request.urlopen(req,timeout=TIMEOUT) as r:
            return int(r.headers.get('Content-Length') or 0)
    except: return 0

def calln(nm):
    return nm.rsplit('.',1)[0].split('_',1)[0].upper() or '?'

def main():
    html=fetch(FOLDER_URL.format(id=DEFAULT_FOLDER_ID))
    folders=parse_folders(html)  # solo qsl1..qsl7 correctos ahora
    # si hay extras no deseados, los filtramos? ya solo los 7 correctos
    entries=[]; counts={}; acts={}
    for act,fid in folders:
        try: sh=fetch(FOLDER_URL.format(id=fid))
        except Exception as ex: print('ERR',act,ex); continue
        fl=parse_files(sh)
        counts[act]=len(fl); acts[act]={'id':fid,'title':ACTIVITY_TITLES.get(act,act)}
        for ff in fl:
            entries.append({'call':calln(ff['name']),'act':act,'name':ff['name'],'id':ff['id'],'size':fsize(ff['id'])})
    entries.sort(key=lambda e:(e['call'],e['act'],e['name']))
    idx={'version':1,'generated_at':datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
         'folder_id':DEFAULT_FOLDER_ID,'folder_url':FOLDER_URL.format(id=DEFAULT_FOLDER_ID),
         'activities':acts,'counts':counts,'total':len(entries),'entries':entries}
    Path('qsl_index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
    print(idx['total']); [print(k,v) for k,v in counts.items()]

if __name__=='__main__': main()
