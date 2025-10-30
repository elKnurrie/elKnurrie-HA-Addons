#!/usr/bin/env python3
"""
Simple HTTP server for iCloud 2FA setup
Uses Python's built-in http.server - no external dependencies
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import subprocess
import time

# Global state for authentication process
auth_state = {
    'status': 'waiting',  # waiting, authenticating, success, error
    'message': '',
    'process': None
}

def load_config():
    """Load configuration from Home Assistant options"""
    config_file = '/data/options.json'
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

class SetupHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Override to suppress request logging"""
        pass
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def send_html_response(self, html, status=200):
        """Send HTML response"""
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/' or self.path.startswith('/?'):
            # Serve main page
            config = load_config()
            html = HTML_TEMPLATE.replace('{{username}}', config.get('icloud_username', ''))
            self.send_html_response(html)
        
        elif self.path == '/status':
            # Return authentication status
            self.send_json_response({
                'authenticating': auth_state['status'] == 'authenticating',
                'message': auth_state['message'],
                'status': auth_state['status']
            })
        
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_json_response({'success': False, 'message': 'Invalid JSON'}, 400)
            return
        
        if self.path == '/request_code':
            self.handle_request_code()
        
        elif self.path == '/setup':
            self.handle_setup(data)
        
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')
    
    def handle_request_code(self):
        """Trigger Apple to send 2FA code"""
        try:
            config = load_config()
            username = config.get('icloud_username', '')
            password = config.get('icloud_password', '')
            
            if not username or not password:
                self.send_json_response({
                    'success': False,
                    'message': 'Username and password not configured'
                })
                return
            
            # Create rclone config directory
            os.makedirs('/root/.config/rclone', exist_ok=True)
            
            # Obscure password
            result = subprocess.run(
                ['rclone', 'obscure', password],
                capture_output=True,
                text=True,
                check=True
            )
            obscured_pass = result.stdout.strip()
            
            # Create rclone config
            config_content = f"""[icloud]
type = iclouddrive
user = {username}
pass = {obscured_pass}
"""
            with open('/root/.config/rclone/rclone.conf', 'w') as f:
                f.write(config_content)
            
            # Start rclone to trigger 2FA
            proc = subprocess.Popen(
                ['rclone', 'lsd', 'icloud:', '--verbose'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            auth_state['process'] = proc
            auth_state['status'] = 'waiting_for_code'
            auth_state['message'] = 'Waiting for 2FA code from user'
            
            time.sleep(3)
            
            self.send_json_response({
                'success': True,
                'message': '2FA request sent to Apple! Check your iPhone/iPad for the code.'
            })
        
        except Exception as e:
            self.send_json_response({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    def handle_setup(self, data):
        """Handle 2FA code submission"""
        twofa_code = data.get('twofa_code', '')
        
        if not twofa_code or len(twofa_code) != 6:
            self.send_json_response({
                'success': False,
                'message': 'Invalid 2FA code format. Must be 6 digits.'
            })
            return
        
        proc = auth_state.get('process')
        if not proc:
            self.send_json_response({
                'success': False,
                'message': 'No authentication process waiting. Click "Request 2FA Code" first.'
            })
            return
        
        try:
            auth_state['status'] = 'authenticating'
            auth_state['message'] = 'Verifying 2FA code...'
            
            # Send code to rclone
            proc.stdin.write(f"{twofa_code}\n")
            proc.stdin.flush()
            proc.stdin.close()
            
            # Wait for completion
            try:
                output, _ = proc.communicate(timeout=30)
                
                if proc.returncode == 0 or "success" in output.lower():
                    auth_state['status'] = 'success'
                    auth_state['message'] = 'Authentication successful!'
                    auth_state['process'] = None
                    
                    # Mark as configured
                    with open('/data/icloud_session_configured', 'w') as f:
                        f.write('configured')
                    
                    config = load_config()
                    self.send_json_response({
                        'success': True,
                        'message': f'Successfully authenticated! Session saved for {config.get("icloud_username", "")}.'
                    })
                else:
                    auth_state['status'] = 'error'
                    auth_state['message'] = 'Invalid 2FA code'
                    auth_state['process'] = None
                    self.send_json_response({
                        'success': False,
                        'message': 'Invalid 2FA code. Please request a new code and try again.'
                    })
            
            except subprocess.TimeoutExpired:
                proc.kill()
                auth_state['status'] = 'error'
                auth_state['message'] = 'Authentication timed out'
                auth_state['process'] = None
                self.send_json_response({
                    'success': False,
                    'message': 'Authentication timed out. Please try again.'
                })
        
        except Exception as e:
            auth_state['status'] = 'error'
            auth_state['message'] = f'Error: {str(e)}'
            auth_state['process'] = None
            self.send_json_response({
                'success': False,
                'message': f'Error: {str(e)}'
            })

# HTML template (same as before)
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>iCloud Drive Setup</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; margin-top: 0; }
        .alert { padding: 15px; margin-bottom: 20px; border-radius: 4px; }
        .alert-info { background-color: #d1ecf1; color: #0c5460; border-left: 4px solid #0099ff; }
        .alert-success { background-color: #d4edda; color: #155724; border-left: 4px solid #28a745; }
        .alert-danger { background-color: #f8d7da; color: #721c24; border-left: 4px solid #dc3545; }
        button { background-color: #0099ff; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; width: 100%; margin-top: 10px; }
        button:hover { background-color: #0077cc; }
        button:disabled { background-color: #ccc; cursor: not-allowed; }
        input { width: 100%; padding: 10px; margin: 5px 0; box-sizing: border-box; border: 1px solid #ddd; border-radius: 4px; }
        .form-group { margin-bottom: 15px; }
        label { font-weight: bold; display: block; margin-bottom: 5px; }
        #status { margin-top: 20px; }
        .step { margin: 10px 0; padding: 15px; background: #f8f9fa; border-left: 3px solid #0099ff; border-radius: 4px; }
        ol { margin: 10px 0; padding-left: 20px; }
        ol li { margin: 8px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🍎 iCloud Drive Setup</h1>
        
        <div class="alert alert-info">
            <strong>First-time setup required!</strong><br>
            To connect to iCloud Drive, you need to verify your identity with a 2FA code.
        </div>

        <div class="step">
            <h3>Setup Steps:</h3>
            <ol>
                <li>Click "<strong>Request 2FA Code</strong>" below</li>
                <li>Apple will send a 6-digit code to your iPhone/iPad</li>
                <li>Enter the code in the field below</li>
                <li>Click "Authenticate with iCloud"</li>
            </ol>
        </div>

        <div id="status"></div>

        <button onclick="requestCode()" id="requestBtn">📱 Request 2FA Code from Apple</button>

        <div id="authForm" style="display: none; margin-top: 20px;">
            <div class="form-group">
                <label for="apple_id">Apple ID:</label>
                <input type="email" id="apple_id" value="{{username}}" readonly>
            </div>
            
            <div class="form-group">
                <label for="code">2FA Verification Code:</label>
                <input type="text" id="code" placeholder="123456" maxlength="6" pattern="[0-9]{6}">
            </div>
            
            <button onclick="authenticate()" id="authBtn">✓ Authenticate with iCloud</button>
        </div>
    </div>

    <script>
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.innerHTML = '<div class="alert alert-' + type + '">' + message + '</div>';
        }

        async function requestCode() {
            const btn = document.getElementById('requestBtn');
            btn.disabled = true;
            showStatus('🔄 Requesting 2FA code from Apple...', 'info');
            
            try {
                const response = await fetch('/request_code', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showStatus('✅ ' + data.message + '<br><br>Enter the code below when you receive it.', 'success');
                    document.getElementById('authForm').style.display = 'block';
                } else {
                    showStatus('❌ ' + data.message, 'danger');
                    btn.disabled = false;
                }
            } catch (error) {
                showStatus('❌ Connection error: ' + error.message, 'danger');
                btn.disabled = false;
            }
        }

        async function authenticate() {
            const code = document.getElementById('code').value;
            
            if (!code || code.length !== 6) {
                showStatus('❌ Please enter a valid 6-digit code', 'danger');
                return;
            }
            
            const btn = document.getElementById('authBtn');
            btn.disabled = true;
            showStatus('🔄 Authenticating with iCloud...', 'info');
            
            try {
                const response = await fetch('/setup', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({twofa_code: code})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showStatus('✅ ' + data.message + '<br><br>Please restart the add-on to start backups!', 'success');
                } else {
                    showStatus('❌ ' + data.message, 'danger');
                    btn.disabled = false;
                }
            } catch (error) {
                showStatus('❌ Connection error: ' + error.message, 'danger');
                btn.disabled = false;
            }
        }
    </script>
</body>
</html>"""

if __name__ == '__main__':
    port = int(os.environ.get('INGRESS_PORT', 8099))
    
    print(f"[HTTP] Starting iCloud Setup Web Interface on 0.0.0.0:{port}", flush=True)
    print(f"[HTTP] Using Python's built-in http.server (no Flask required)", flush=True)
    
    try:
        server = HTTPServer(('0.0.0.0', port), SetupHandler)
        print(f"[HTTP] Server started successfully!", flush=True)
        print(f"[HTTP] Listening on http://0.0.0.0:{port}", flush=True)
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"[HTTP] Server stopped by user", flush=True)
    except Exception as e:
        print(f"[HTTP] FATAL ERROR: {type(e).__name__}: {e}", flush=True)
        import traceback
        traceback.print_exc()
        exit(1)
