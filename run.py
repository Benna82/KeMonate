#!/usr/bin/env python3
"""First-run setup and a localhost-only server. Python 3.10+ required."""
import os,sys,subprocess,venv,webbrowser,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser(description='Run KeMonate on localhost')
    parser.add_argument('--port',type=int,default=8000)
    parser.add_argument('--no-browser',action='store_true')
    args=parser.parse_args()
    if not 1024<=args.port<=65535: parser.error('Choose a port from 1024 to 65535.')
    if sys.version_info<(3,10): raise SystemExit('Please install Python 3.10 or newer.')
    if (ROOT/'.env').exists():
        for line in (ROOT/'.env').read_text().splitlines():
            if line.strip() and not line.lstrip().startswith('#') and '=' in line:
                k,v=line.split('=',1);os.environ.setdefault(k.strip(),v.strip().strip('"\''))
    env=ROOT/'.venv'
    python=env/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
    if not python.exists():
        print('Creating a private Python environment…',flush=True);venv.create(env,with_pip=True)
    marker=env/'.requirements-installed'
    wanted=(ROOT/'requirements.txt').read_text()
    if not marker.exists() or marker.read_text()!=wanted:
        subprocess.run([str(python),'-m','pip','install','-r',str(ROOT/'requirements.txt')],check=True)
        marker.write_text(wanted)
    if not (ROOT/'frontend/dist/index.html').exists(): raise SystemExit('Frontend build missing. Run npm ci and npm run build inside frontend/.')
    manage=ROOT/'backend/manage.py'
    subprocess.run([str(python),str(manage),'migrate','--noinput'],check=True)
    url=f'http://127.0.0.1:{args.port}'
    print(f'\nKeMonate is starting at {url}\nPress Ctrl+C to stop.\n',flush=True)
    if not args.no_browser:
        import threading
        threading.Timer(2,lambda:webbrowser.open(url)).start()
    try: subprocess.run([str(python),str(manage),'runserver',f'127.0.0.1:{args.port}','--noreload'],check=True)
    except KeyboardInterrupt: print('\nKeMonate stopped.')

if __name__=='__main__': main()
