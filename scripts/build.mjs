import {mkdir,copyFile,cp,rm} from "node:fs/promises";
await rm("dist",{recursive:true,force:true});
await mkdir("dist",{recursive:true});
for(const file of ["index.html","menu.js","polish.css","cards-v08.js","engine-v08.mjs","voyage-v08.js","voyage-v08.css","RULES-v0.8.txt"])await copyFile(file,`dist/${file}`);
await cp("assets","dist/assets",{recursive:true});
