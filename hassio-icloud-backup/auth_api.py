#!/usr/bin/env python3
"""
Simple API server for iCloud 2FA authentication
No web UI - just REST API endpoints for CLI usage
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import subprocess
import time

# Global state
auth_state = {
    'status': 'idle',
    'message': '',
    'process': None
}

def load_config():
    """Load configuration from Home Assistant options"""
    try:
        with open('/data/options.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

class AuthAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Suppress request logging"""
        pass
    
    def send_json(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/status':
            # Return current status
            self.send_json({
                'status': auth_state['status'],
                'message': auth_state['message']
            })
        
        elif self.path == '/help':
            # Show API usage
            config = load_config()
            self.send_json({
                'usage': {
                    'step1': 'curl http://YOUR_HA_IP:8099/request_code -X POST',
                    'step2': 'Check your iPhone/iPad for the 6-digit code',
                    'step3': 'curl http://YOUR_HA_IP:8099/submit_code -X POST -d "123456"'
                },
                'current_username': config.get('icloud_username', 'not configured'),
                'authenticated': os.path.exists('/data/icloud_session_configured'),
                'IMPORTANT': [
                    'Use your REAL Apple ID password (NOT app-specific password)',
                    'Advanced Data Protection MUST be disabled in iCloud settings',
                    'Access iCloud Data on the Web MUST be enabled',
                    'Trust tokens expire after 30 days - you will need to re-authenticate'
                ]
            })
        
        else:
            self.send_json({'error': 'Not found', 'help': 'GET /help for usage'}, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/request_code':
            self.handle_request_code()
        
        elif self.path == '/submit_code':
            # Read the 2FA code from request body
            content_length = int(self.headers.get('Content-Length', 0))
            code = self.rfile.read(content_length).decode('utf-8').strip()
            self.handle_submit_code(code)
        
        else:
            self.send_json({'error': 'Not found', 'help': 'GET /help for usage'}, 404)
    
    def handle_request_code(self):
        """Trigger Apple to send 2FA code"""
        try:
            config = load_config()
            username = config.get('icloud_username', '')
            password = config.get('icloud_password', '')
            
            if not username or not password:
                self.send_json({
                    'success': False,
                    'error': 'Username and password not configured in add-on options'
                })
                return
            
            # Create rclone config directory
            os.makedirs('/root/.config/rclone', exist_ok=True)
            
            # Obscure the password
            result = subprocess.run(
                ['rclone', 'obscure', password],
                capture_output=True,
                text=True,
                check=True
            )
            obscured_pass = result.stdout.strip()
            
            # Create config file manually with proper format
            config_content = f"""[icloud]
type = iclouddrive
apple_id = {username}
password = {obscured_pass}
"""
            with open('/root/.config/rclone/rclone.conf', 'w') as f:
                f.write(config_content)
            
            # Now try to access iCloud - this will trigger 2FA
            # Use 'rclone lsf' to list files which requires trust token
            proc = subprocess.Popen(
                ['rclone', 'lsf', 'icloud:', '--max-depth', '1', '-vv'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            auth_state['process'] = proc
            auth_state['status'] = 'waiting_for_code'
            auth_state['message'] = 'Check your iPhone/iPad for the 2FA code'
            
            # Give rclone time to start requesting 2FA
            time.sleep(3)
            
            self.send_json({
                'success': True,
                'message': 'Apple should send a 2FA code to your devices now. Check your iPhone/iPad!',
                'next_step': 'Run: curl http://YOUR_HA_IP:8099/submit_code -X POST -d "YOUR_6_DIGIT_CODE"',
                'note': 'This is a ONE-TIME setup to establish trust tokens (valid for 30 days)',
                'IMPORTANT': 'You MUST use your REAL Apple ID password, NOT an app-specific password',
                'requirements': [
                    'Advanced Data Protection must be DISABLED in iCloud settings',
                    'Access iCloud Data on the Web must be ENABLED'
                ]
            })
        
        except Exception as e:
            auth_state['status'] = 'error'
            auth_state['message'] = str(e)
            self.send_json({
                'success': False,
                'error': str(e)
            })
    
    def handle_submit_code(self, code):
        """Submit 2FA code to rclone"""
        if not code or len(code) != 6 or not code.isdigit():
            self.send_json({
                'success': False,
                'error': 'Invalid code format. Must be exactly 6 digits'
            })
            return
        
        proc = auth_state.get('process')
        if not proc:
            self.send_json({
                'success': False,
                'error': 'No authentication in progress. Run /request_code first'
            })
            return
        
        try:
            auth_state['status'] = 'authenticating'
            auth_state['message'] = f'Verifying code {code}...'
            
            # Send code to rclone
            proc.stdin.write(f"{code}\n")
            proc.stdin.flush()
            proc.stdin.close()
            
            # Wait for completion
            output, _ = proc.communicate(timeout=30)
            
            if proc.returncode == 0 or "success" in output.lower():
                auth_state['status'] = 'success'
                auth_state['message'] = 'Authentication successful!'
                auth_state['process'] = None
                
                # Mark as configured
                with open('/data/icloud_session_configured', 'w') as f:
                    f.write('configured')
                
                config = load_config()
                self.send_json({
                    'success': True,
                    'message': f'Successfully authenticated as {config.get("icloud_username", "")}',
                    'next_step': 'Restart the add-on to start backups'
                })
            else:
                auth_state['status'] = 'failed'
                auth_state['message'] = 'Invalid code or authentication failed'
                auth_state['process'] = None
                self.send_json({
                    'success': False,
                    'error': 'Invalid 2FA code. Request a new code and try again'
                })
        
        except subprocess.TimeoutExpired:
            proc.kill()
            auth_state['status'] = 'timeout'
            auth_state['message'] = 'Authentication timed out'
            auth_state['process'] = None
            self.send_json({
                'success': False,
                'error': 'Authentication timed out. Try again'
            })
        
        except Exception as e:
            auth_state['status'] = 'error'
            auth_state['message'] = str(e)
            auth_state['process'] = None
            self.send_json({
                'success': False,
                'error': str(e)
            })

if __name__ == '__main__':
    port = 8099
    
    print(f"[API] Starting iCloud 2FA Authentication API on port {port}", flush=True)
    print(f"[API] No web UI - use curl from Home Assistant terminal", flush=True)
    print(f"[API] Usage: curl http://localhost:{port}/help", flush=True)
    
    try:
        server = HTTPServer(('0.0.0.0', port), AuthAPIHandler)
        print(f"[API] Server ready!", flush=True)
        server.serve_forever()
    except Exception as e:
        print(f"[API] ERROR: {e}", flush=True)
        exit(1)
