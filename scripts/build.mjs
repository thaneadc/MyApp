import {mkdir,copyFile,cp,rm} from "node:fs/promises";
await rm("dist",{recursive:true,force:true});
await mkdir("dist",{recursive:true});
for(const file of ["index.html","menu.js","polish.css","cards-v014.js","engine-v014.mjs","voyage-v014.js","voyage-v08.css","voyage-v014.css","voyage-flair.js","voyage-feedback.css","voyage-table.css"])await copyFile(file,`dist/${file}`);
await cp("assets","dist/assets",{recursive:true});
