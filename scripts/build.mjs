import {mkdir,copyFile,cp} from "node:fs/promises";
await mkdir("dist",{recursive:true});
for(const file of ["index.html","menu.js","game.js","touch.js","polish.css"])await copyFile(file,`dist/${file}`);
await cp("assets","dist/assets",{recursive:true});
