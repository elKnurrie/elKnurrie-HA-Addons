#!/usr/bin/env python3
"""
Web-based setup interface for iCloud 2FA authentication
"""
from flask import Flask, render_template_string, request, jsonify
import json
import subprocess
import os
from pathlib import Path

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>iCloud Drive Setup</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .status { padding: 15px; margin: 20px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        input { width: 100%; padding: 8px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
        label { font-weight: bold; display: block; margin-top: 15px; }
    </style>
</head>
<body>
    <h1>🍎 iCloud Drive Setup</h1>
    
    <div class="status info">
        <strong>First-time setup required!</strong><br>
        Enter your 2FA code to authenticate with iCloud Drive.
    </div>
    
    <div id="status"></div>
    
    <form id="setupForm">
        <label>Apple ID:</label>
        <input type="text" id="username" value="{{ username }}" readonly>
        
        <label>2FA Code (6 digits):</label>
        <input type="text" id="twofa_code" placeholder="123456" maxlength="6" pattern="[0-9]{6}" required>
        
        <br><br>
        <button type="submit">Authenticate with iCloud</button>
    </form>
    
    <script>
        document.getElementById('setupForm').onsubmit = async (e) => {
            e.preventDefault();
            const code = document.getElementById('twofa_code').value;
            const statusDiv = document.getElementById('status');
            
            statusDiv.innerHTML = '<div class="status info">Authenticating...</div>';
            
            try {
                const response = await fetch('/setup', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({twofa_code: code})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    statusDiv.innerHTML = '<div class="status success">✅ ' + result.message + '</div>';
                } else {
                    statusDiv.innerHTML = '<div class="status error">❌ ' + result.message + '</div>';
                }
            } catch (error) {
                statusDiv.innerHTML = '<div class="status error">❌ Connection error: ' + error + '</div>';
            }
        };
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
    return render_template_string(HTML_TEMPLATE, username=config.get('icloud_username', ''))

@app.route('/setup', methods=['POST'])
def setup():
    data = request.json
    twofa_code = data.get('twofa_code', '')
    
    if not twofa_code or len(twofa_code) != 6:
        return jsonify({'success': False, 'message': 'Invalid 2FA code format'})
    
    config = load_config()
    username = config.get('icloud_username', '')
    password = config.get('icloud_password', '')
    
    # Save 2FA code to trigger authentication in run.sh
    with open('/data/icloud_2fa_code.txt', 'w') as f:
        f.write(twofa_code)
    
    return jsonify({
        'success': True,
        'message': 'Authentication code saved! Please restart the add-on to complete setup.'
    })

if __name__ == '__main__':
    print("[INFO] Starting iCloud Setup Web Interface on port 8099")
    print("[INFO] Open this in your browser to complete 2FA setup")
    app.run(host='0.0.0.0', port=8099, debug=False)
