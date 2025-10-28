#!/usr/bin/env python3
"""
Web-based setup interface for iCloud 2FA authentication
Supports Home Assistant Ingress
"""
from flask import Flask, render_template_string, request, jsonify, abort
import json
import os
import subprocess
import threading
import time

app = Flask(__name__)

# Get ingress path from environment (if running under HA ingress)
INGRESS_PATH = os.environ.get('INGRESS_PATH', '')

# Ingress security: Only allow connections from Home Assistant ingress gateway
# when running under Ingress (INGRESS_PATH is set)
INGRESS_GATEWAY_IP = '172.30.32.2'

# Global state for authentication process
auth_state = {
    'status': 'waiting',  # waiting, authenticating, success, error
    'message': '',
    'process': None
}

@app.before_request
def limit_remote_addr():
    """Ensure requests only come from Home Assistant Ingress gateway when using Ingress"""
    # Only enforce IP restriction if running under Ingress
    if INGRESS_PATH:
        if request.remote_addr != INGRESS_GATEWAY_IP:
            app.logger.warning(f"Rejected request from {request.remote_addr} (expected {INGRESS_GATEWAY_IP})")
            abort(403)  # Forbidden
    # Allow all IPs in standalone mode (no INGRESS_PATH)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>iCloud Drive Setup</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            max-width: 600px; 
            margin: 0 auto; 
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { 
            color: #333; 
            margin-top: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status { 
            padding: 15px; 
            margin: 20px 0; 
            border-radius: 5px;
            font-size: 14px;
        }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        button { 
            width: 100%;
            padding: 12px 20px; 
            background: #03a9f4; 
            color: white; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
        }
        button:hover { background: #0288d1; }
        button:active { background: #0277bd; }
        input { 
            width: 100%; 
            padding: 12px; 
            margin: 10px 0; 
            border: 1px solid #ddd; 
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        label { 
            font-weight: 600; 
            display: block; 
            margin-top: 15px;
            color: #555;
        }
        .readonly-field {
            background: #f9f9f9;
            color: #666;
        }
        .steps {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .steps ol {
            margin: 10px 0;
            padding-left: 20px;
        }
        .steps li {
            margin: 8px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🍎 iCloud Drive Setup</h1>
        
        <div class="status info">
            <strong>First-time setup required!</strong><br>
            To connect to iCloud Drive, you need to verify your identity with a 2FA code.
        </div>
        
        <div class="steps">
            <strong>How to get your 2FA code:</strong>
            <ol>
                <li>Check your trusted Apple device (iPhone, iPad, Mac)</li>
                <li>You should receive a 6-digit verification code</li>
                <li>Enter that code below</li>
            </ol>
        </div>
        
        <div id="status"></div>
        
        <form id="setupForm">
            <label>Apple ID:</label>
            <input type="text" class="readonly-field" value="{{ username }}" readonly>
            
            <label>2FA Verification Code:</label>
            <input 
                type="text" 
                id="twofa_code" 
                placeholder="123456" 
                maxlength="6" 
                pattern="[0-9]{6}" 
                autocomplete="off"
                required
                autofocus>
            
            <br><br>
            <button type="submit">✓ Authenticate with iCloud</button>
        </form>
    </div>
    
    <script>
        document.getElementById('setupForm').onsubmit = async (e) => {
            e.preventDefault();
            const code = document.getElementById('twofa_code').value;
            const statusDiv = document.getElementById('status');
            const button = e.target.querySelector('button');
            
            button.disabled = true;
            button.textContent = 'Authenticating...';
            statusDiv.innerHTML = '<div class="status info">⏳ Connecting to iCloud...</div>';
            
            try {
                const response = await fetch('/setup', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({twofa_code: code})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    statusDiv.innerHTML = '<div class="status success">✅ ' + result.message + 
                        '<br><br><strong>Next step:</strong> Go back to the add-on page and click RESTART.</div>';
                    document.getElementById('twofa_code').value = '';
                } else {
                    statusDiv.innerHTML = '<div class="status error">❌ ' + result.message + '</div>';
                    button.disabled = false;
                    button.textContent = '✓ Authenticate with iCloud';
                }
            } catch (error) {
                statusDiv.innerHTML = '<div class="status error">❌ Connection error: ' + error + '</div>';
                button.disabled = false;
                button.textContent = '✓ Authenticate with iCloud';
            }
        };
        
        // Auto-focus the input field
        document.getElementById('twofa_code').focus();
        
        // Poll for status updates during authentication
        setInterval(async () => {
            try {
                const response = await fetch('/status');
                const result = await response.json();
                if (result.authenticating) {
                    document.getElementById('status').innerHTML = 
                        '<div class="status info">⏳ ' + result.message + '</div>';
                }
            } catch (e) {}
        }, 2000);
    </script>
</body>
</html>
"""

def load_config():
    with open('/data/options.json', 'r') as f:
        return json.load(f)

def authenticate_with_rclone(username, password, twofa_code):
    """Actually run rclone authentication with 2FA code"""
    try:
        print(f"[INFO] Starting rclone authentication for {username}")
        auth_state['status'] = 'authenticating'
        auth_state['message'] = 'Initializing rclone...'
        
        # Create rclone config directory
        os.makedirs('/root/.config/rclone', exist_ok=True)
        
        # Create initial config
        obscured_pass = subprocess.check_output(['rclone', 'obscure', password]).decode().strip()
        
        config_content = f"""[icloud]
type = iclouddrive
user = {username}
pass = {obscured_pass}
"""
        
        with open('/root/.config/rclone/rclone.conf', 'w') as f:
            f.write(config_content)
        
        print(f"[INFO] Config created, attempting connection...")
        auth_state['message'] = 'Connecting to iCloud (Apple will send 2FA now)...'
        
        # Try to list iCloud Drive - this will trigger 2FA
        # We pass the code via stdin when rclone prompts
        proc = subprocess.Popen(
            ['rclone', 'lsd', 'icloud:', '--verbose'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Send the 2FA code immediately
        print(f"[INFO] Sending 2FA code: {twofa_code}")
        proc.stdin.write(f"{twofa_code}\n")
        proc.stdin.flush()
        proc.stdin.close()
        
        # Wait for completion (with timeout)
        try:
            output, _ = proc.communicate(timeout=45)
            
            print(f"[DEBUG] rclone output:\n{output}")
            
            if proc.returncode == 0 or "trust token" in output.lower():
                print("[INFO] ✅ Authentication successful!")
                auth_state['status'] = 'success'
                auth_state['message'] = 'Authentication successful!'
                
                # Mark as configured
                with open('/data/icloud_session_configured', 'w') as f:
                    f.write('configured')
                
                return True
            else:
                print(f"[ERROR] Authentication failed: {output}")
                auth_state['status'] = 'error'
                auth_state['message'] = f'Authentication failed. Check your credentials and 2FA code.'
                return False
                
        except subprocess.TimeoutExpired:
            proc.kill()
            print("[ERROR] Authentication timed out")
            auth_state['status'] = 'error'
            auth_state['message'] = 'Authentication timed out - Apple may not have sent 2FA'
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception during authentication: {e}")
        import traceback
        traceback.print_exc()
        auth_state['status'] = 'error'
        auth_state['message'] = f'Error: {str(e)}'
        return False

@app.route('/')
def index():
    config = load_config()
    return render_template_string(
        HTML_TEMPLATE, 
        username=config.get('icloud_username', ''),
        ingress_path=''  # Ingress handles the path automatically
    )

@app.route('/status')
def status():
    """Return current authentication status"""
    return jsonify({
        'authenticating': auth_state['status'] == 'authenticating',
        'message': auth_state['message'],
        'status': auth_state['status']
    })

@app.route('/setup', methods=['POST'])
def setup():
    data = request.json
    twofa_code = data.get('twofa_code', '')
    
    if not twofa_code or len(twofa_code) != 6:
        return jsonify({'success': False, 'message': 'Invalid 2FA code format. Must be 6 digits.'})
    
    config = load_config()
    username = config.get('icloud_username', '')
    password = config.get('icloud_password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password not configured'})
    
    # Start authentication in background thread
    def auth_thread():
        authenticate_with_rclone(username, password, twofa_code)
    
    thread = threading.Thread(target=auth_thread)
    thread.start()
    
    # Wait for authentication to complete (with timeout)
    thread.join(timeout=50)
    
    if auth_state['status'] == 'success':
        return jsonify({
            'success': True,
            'message': f'Successfully authenticated! Session saved for {username}.'
        })
    else:
        return jsonify({
            'success': False,
            'message': auth_state.get('message', 'Authentication failed')
        })

if __name__ == '__main__':
    port = int(os.environ.get('INGRESS_PORT', 8099))
    print(f"[INFO] Starting iCloud Setup Web Interface on port {port}")
    print(f"[INFO] Binding to 0.0.0.0:{port}")
    if INGRESS_PATH:
        print(f"[INFO] Running with Home Assistant Ingress support")
        print(f"[INFO] Ingress path: {INGRESS_PATH}")
        print(f"[INFO] IP restriction: Only {INGRESS_GATEWAY_IP} allowed")
    else:
        print(f"[INFO] Running in standalone mode")
        print(f"[INFO] All IPs allowed (no Ingress)")
    
    # Run with threaded=True for better Ingress support
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True, use_reloader=False)
