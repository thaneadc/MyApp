import {readFile, mkdir, writeFile} from 'node:fs/promises';
import {dirname} from 'node:path';
import {createHash} from 'node:crypto';
const revision=process.argv[2];
if(!/^[a-f0-9]{40}$/.test(revision||''))throw new Error('A full immutable release commit SHA is required');
const manifest=JSON.parse(await readFile('release-manifest.json','utf8'));
for(let i=0;i<manifest.length;i+=6){
 await Promise.all(manifest.slice(i,i+6).map(async item=>{
  if(!/^(assets\/[\w.-]+|index\.html|game\.js|menu\.js|touch\.js|polish\.css)$/.test(item.path))throw new Error('Unexpected asset path');
  const response=await fetch(`https://raw.githubusercontent.com/thaneadc/MyApp/${revision}/${item.path}`,{signal:AbortSignal.timeout(60000)});
  if(!response.ok)throw new Error(`${item.path}: HTTP ${response.status}`);
  const bytes=Buffer.from(await response.arrayBuffer());
  if(createHash('sha256').update(bytes).digest('hex')!==item.sha256)throw new Error(`Integrity mismatch: ${item.path}`);
  await mkdir(dirname(`dist/${item.path}`),{recursive:true});
  await writeFile(`dist/${item.path}`,bytes);
 }));
}
console.log(`Published ${manifest.length} verified files from ${revision}`);
