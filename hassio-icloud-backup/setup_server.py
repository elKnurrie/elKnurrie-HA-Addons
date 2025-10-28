#!/usr/bin/env python3
"""
Web-based setup interface for iCloud 2FA authentication
Supports Home Assistant Ingress
"""
from flask import Flask, render_template_string, request, jsonify, abort
import json
import os

app = Flask(__name__)

# Get ingress path from environment (if running under HA ingress)
INGRESS_PATH = os.environ.get('INGRESS_PATH', '')

# Ingress security: Only allow connections from Home Assistant ingress gateway
ALLOWED_IP = '172.30.32.2'

@app.before_request
def limit_remote_addr():
    """Ensure requests only come from Home Assistant Ingress gateway"""
    if request.remote_addr != ALLOWED_IP:
        app.logger.warning(f"Rejected request from {request.remote_addr}")
        abort(403)  # Forbidden

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
    </script>
</body>
</html>
"""

def load_config():
    with open('/data/options.json', 'r') as f:
        return json.load(f)

@app.route('/')
def index():
    config = load_config()
    return render_template_string(
        HTML_TEMPLATE, 
        username=config.get('icloud_username', ''),
        ingress_path=''  # Ingress handles the path automatically
    )

@app.route('/setup', methods=['POST'])
def setup():
    data = request.json
    twofa_code = data.get('twofa_code', '')
    
    if not twofa_code or len(twofa_code) != 6:
        return jsonify({'success': False, 'message': 'Invalid 2FA code format. Must be 6 digits.'})
    
    config = load_config()
    username = config.get('icloud_username', '')
    
    # Save 2FA code to trigger authentication in run.sh
    with open('/data/icloud_2fa_code.txt', 'w') as f:
        f.write(twofa_code)
    
    return jsonify({
        'success': True,
        'message': f'Authentication code saved for {username}!'
    })

if __name__ == '__main__':
    port = int(os.environ.get('INGRESS_PORT', 8099))
    print(f"[INFO] Starting iCloud Setup Web Interface on port {port}")
    print(f"[INFO] Binding to 0.0.0.0:{port}")
    if INGRESS_PATH:
        print(f"[INFO] Running with Home Assistant Ingress support")
        print(f"[INFO] Ingress path: {INGRESS_PATH}")
    else:
        print(f"[INFO] Running in standalone mode")
    
    # Run with threaded=True for better Ingress support
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True, use_reloader=False)
