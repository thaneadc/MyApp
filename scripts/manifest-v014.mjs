import {readdirSync,readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const files=readdirSync('dist',{recursive:true,withFileTypes:true}).filter(x=>x.isFile()).map(x=>(x.parentPath+'/'+x.name).replace(/^dist\//,'')).sort();
writeFileSync('release-manifest.json',JSON.stringify(files.map(path=>({path,sha256:createHash('sha256').update(readFileSync('dist/'+path)).digest('hex')})),null,2)+'\n');
console.log('Release manifest:',files.length,'files');
