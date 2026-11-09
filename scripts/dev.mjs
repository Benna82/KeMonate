import {spawn} from 'node:child_process';
import {existsSync} from 'node:fs';
import path from 'node:path';
const root=process.cwd();
const candidates=[path.join(root,'.venv',process.platform==='win32'?'Scripts/python.exe':'bin/python'),path.resolve(root,'../.venv/bin/python')];
const python=process.env.KEMONATE_PYTHON||candidates.find(existsSync)||'python';
const backend=spawn(python,['backend/manage.py','runserver','127.0.0.1:8000','--noreload'],{stdio:'inherit'});
const frontend=spawn(process.execPath,['frontend/node_modules/vite/bin/vite.js','--config','frontend/vite.config.ts','frontend',...process.argv.slice(2)],{stdio:'inherit'});
function stop(){backend.kill();frontend.kill();}
process.on('SIGINT',stop);process.on('SIGTERM',stop);
backend.on('exit',code=>{if(code){frontend.kill();process.exitCode=code;}});
frontend.on('exit',()=>{backend.kill();});
