#!/usr/bin/env python3
import sys
import subprocess
import platform
import json
import io
from urllib import request, error
from urllib.parse import urljoin

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BACKEND_BASE_URL = "http://localhost:8080"
RESCUE_ENDPOINT = "/api/v1/rescue"
MAX_LOG_LENGTH = 3000
REQUEST_TIMEOUT = 5

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def get_system_info():
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "python_version": platform.python_version()
    }

def send_error_report(error_log, command):
    payload = {
        "command": command,
        "error_log": error_log[-MAX_LOG_LENGTH:] if len(error_log) > MAX_LOG_LENGTH else error_log,
        "system_info": get_system_info(),
        "timestamp": __import__('time').time()
    }
    
    try:
        url = urljoin(BACKEND_BASE_URL, RESCUE_ENDPOINT)
        req = request.Request(url, method='POST')
        req.add_header('Content-Type', 'application/json')
        data = json.dumps(payload).encode('utf-8')
        
        with request.urlopen(req, data=data, timeout=REQUEST_TIMEOUT) as response:
            if response.getcode() == 200:
                print(f"{Colors.GREEN}[OK] FeiKnow 分析完成{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}[WARN] FeiKnow 后端响应异常{Colors.RESET}")
                
    except error.HTTPError as e:
        if e.code == 404:
            print(f"{Colors.YELLOW}[WARN] FeiKnow 后端接口尚未就绪{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}[WARN] FeiKnow 后端请求失败: {e.code}{Colors.RESET}")
    except error.URLError as e:
        print(f"{Colors.RED}[ERROR] FeiKnow 后端失联{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.YELLOW}[WARN] FeiKnow 上报失败: {str(e)}{Colors.RESET}")

def main():
    if len(sys.argv) < 2:
        print(f"{Colors.RED}用法: feiknow <command> [args...]{Colors.RESET}")
        sys.exit(1)
    
    command = sys.argv[1:]
    
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output, end='')
        
        stderr = process.stderr.read()
        return_code = process.returncode
        
        if return_code != 0:
            if stderr:
                print(stderr, file=sys.stderr)
            
            print(f"\n{Colors.BLUE}[INFO] FeiKnow 正在为您分析报错...{Colors.RESET}")
            send_error_report(stderr, ' '.join(command))
            
        sys.exit(return_code)
        
    except FileNotFoundError:
        print(f"{Colors.RED}[ERROR] 命令不存在: {command[0]}{Colors.RESET}")
        sys.exit(127)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[WARN] 用户中断执行{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}[ERROR] 执行异常: {str(e)}{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
