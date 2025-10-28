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
            <strong>Setup Steps:</strong>
            <ol>
                <li><strong>Click "Request 2FA Code"</strong> below to trigger authentication</li>
                <li>Apple will send a 6-digit code to your iPhone/iPad</li>
                <li>Enter that code in the field below</li>
                <li>Click "Authenticate with iCloud"</li>
            </ol>
        </div>
        
        <div id="status"></div>
        
        <button id="requestCodeBtn" type="button" onclick="requestCode()">📱 Request 2FA Code from Apple</button>
        <br><br>
        
        <form id="setupForm" style="display:none">
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
        async function requestCode() {
            const statusDiv = document.getElementById('status');
            const requestBtn = document.getElementById('requestCodeBtn');
            
            requestBtn.disabled = true;
            requestBtn.textContent = '⏳ Requesting 2FA code from Apple...';
            statusDiv.innerHTML = '<div class="status info">⏳ Connecting to Apple iCloud...<br>Please wait, this may take 10-15 seconds...</div>';
            
            try {
                const response = await fetch('/request_code', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                
                const result = await response.json();
                
                if (result.success) {
                    statusDiv.innerHTML = '<div class="status success">✅ ' + result.message + 
                        '<br><br><strong>Check your iPhone/iPad for the 6-digit code!</strong></div>';
                    // Show the form
                    document.getElementById('setupForm').style.display = 'block';
                    document.getElementById('twofa_code').focus();
                    requestBtn.style.display = 'none';
                } else {
                    statusDiv.innerHTML = '<div class="status error">❌ ' + result.message + '</div>';
                    requestBtn.disabled = false;
                    requestBtn.textContent = '📱 Request 2FA Code from Apple';
                }
            } catch (error) {
                statusDiv.innerHTML = '<div class="status error">❌ Connection error: ' + error + '</div>';
                requestBtn.disabled = false;
                requestBtn.textContent = '📱 Request 2FA Code from Apple';
            }
        }
        
        document.getElementById('setupForm').onsubmit = async (e) => {
            e.preventDefault();
            const code = document.getElementById('twofa_code').value;
            const statusDiv = document.getElementById('status');
            const button = e.target.querySelector('button');
            
            button.disabled = true;
            button.textContent = 'Authenticating...';
            statusDiv.innerHTML = '<div class="status info">⏳ Verifying 2FA code with Apple...</div>';
            
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
                    button.style.display = 'none';
                } else {
                    statusDiv.innerHTML = '<div class="status error">❌ ' + result.message + 
                        '<br><br>Please try again with a new code.</div>';
                    button.disabled = false;
                    button.textContent = '✓ Authenticate with iCloud';
                }
            } catch (error) {
                statusDiv.innerHTML = '<div class="status error">❌ Connection error: ' + error + '</div>';
                button.disabled = false;
                button.textContent = '✓ Authenticate with iCloud';
            }
        };
        
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

@app.route('/request_code', methods=['POST'])
def request_code():
    """Trigger Apple to send 2FA code by initiating authentication"""
    try:
        config = load_config()
        username = config.get('icloud_username', '')
        password = config.get('icloud_password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password not configured'})
        
        print(f"[INFO] Triggering 2FA request for {username}")
        
        # Create rclone config directory
        os.makedirs('/root/.config/rclone', exist_ok=True)
        
        # Create initial config - use rclone obscure command properly
        try:
            obscure_result = subprocess.run(
                ['rclone', 'obscure', password],
                capture_output=True,
                text=True,
                check=True
            )
            obscured_pass = obscure_result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to obscure password: {e}")
            return jsonify({'success': False, 'message': 'Failed to prepare configuration'})
        
        config_content = f"""[icloud]
type = iclouddrive
user = {username}
pass = {obscured_pass}
"""
        
        with open('/root/.config/rclone/rclone.conf', 'w') as f:
            f.write(config_content)
        
        print("[INFO] Config created, initiating connection to trigger 2FA...")
        
        # Start rclone connection in background - this will trigger Apple to send 2FA
        # We don't wait for it to complete, just start it
        proc = subprocess.Popen(
            ['rclone', 'lsd', 'icloud:', '--verbose'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Store the process so we can send the code to it later
        auth_state['process'] = proc
        auth_state['status'] = 'waiting_for_code'
        auth_state['message'] = 'Waiting for 2FA code from user'
        
        # Wait a moment to ensure connection started
        time.sleep(3)
        
        print("[INFO] Connection initiated - Apple should send 2FA code now")
        
        return jsonify({
            'success': True,
            'message': '2FA request sent to Apple! Check your iPhone/iPad for the code.'
        })
        
    except Exception as e:
        print(f"[ERROR] Failed to request 2FA: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/setup', methods=['POST'])
def setup():
    data = request.json
    twofa_code = data.get('twofa_code', '')
    
    if not twofa_code or len(twofa_code) != 6:
        return jsonify({'success': False, 'message': 'Invalid 2FA code format. Must be 6 digits.'})
    
    # Check if we have a waiting process
    proc = auth_state.get('process')
    if not proc:
        return jsonify({'success': False, 'message': 'No authentication process waiting. Click "Request 2FA Code" first.'})
    
    try:
        print(f"[INFO] Sending 2FA code to rclone: {twofa_code}")
        auth_state['status'] = 'authenticating'
        auth_state['message'] = 'Verifying 2FA code...'
        
        # Send the 2FA code to the waiting rclone process
        proc.stdin.write(f"{twofa_code}\n")
        proc.stdin.flush()
        proc.stdin.close()
        
        # Wait for completion
        try:
            output, _ = proc.communicate(timeout=30)
            
            print(f"[DEBUG] rclone output:\n{output}")
            
            if proc.returncode == 0 or "success" in output.lower() or not ("error" in output.lower() or "failed" in output.lower()):
                print("[INFO] ✅ Authentication successful!")
                auth_state['status'] = 'success'
                auth_state['message'] = 'Authentication successful!'
                auth_state['process'] = None
                
                # Mark as configured
                with open('/data/icloud_session_configured', 'w') as f:
                    f.write('configured')
                
                config = load_config()
                return jsonify({
                    'success': True,
                    'message': f'Successfully authenticated! Session saved for {config.get("icloud_username", "")}.'
                })
            else:
                print(f"[ERROR] Authentication failed: {output}")
                auth_state['status'] = 'error'
                auth_state['message'] = 'Invalid 2FA code or authentication failed'
                auth_state['process'] = None
                return jsonify({
                    'success': False,
                    'message': 'Invalid 2FA code. Please request a new code and try again.'
                })
                
        except subprocess.TimeoutExpired:
            proc.kill()
            print("[ERROR] Authentication timed out")
            auth_state['status'] = 'error'
            auth_state['message'] = 'Authentication timed out'
            auth_state['process'] = None
            return jsonify({
                'success': False,
                'message': 'Authentication timed out. Please try again.'
            })
            
    except Exception as e:
        print(f"[ERROR] Exception during authentication: {e}")
        import traceback
        traceback.print_exc()
        auth_state['status'] = 'error'
        auth_state['message'] = f'Error: {str(e)}'
        auth_state['process'] = None
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
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
