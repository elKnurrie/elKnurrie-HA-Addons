#!/usr/bin/env python3
"""
Local test script for iCloud authentication
This will help debug why 2FA codes aren't being received
"""
import subprocess
import sys
import os
import time

print("=" * 60)
print("iCloud Authentication Debug Tool")
print("=" * 60)
print()

# Get credentials
username = input("Enter your Apple ID (email): ").strip()
password = input("Enter your Apple ID password: ").strip()

if not username or not password:
    print("❌ Username and password are required")
    sys.exit(1)

print()
print("Testing rclone connection to iCloud...")
print("-" * 60)

# Create rclone config directory
os.makedirs(os.path.expanduser('~/.config/rclone'), exist_ok=True)

# Obscure the password using rclone
print("\n1. Obscuring password with rclone...")
try:
    result = subprocess.run(
        ['rclone', 'obscure', password],
        capture_output=True,
        text=True,
        check=True,
        timeout=10
    )
    obscured_pass = result.stdout.strip()
    print(f"   ✅ Password obscured: {obscured_pass[:20]}...")
except subprocess.TimeoutExpired:
    print("   ❌ rclone obscure timed out")
    sys.exit(1)
except subprocess.CalledProcessError as e:
    print(f"   ❌ rclone obscure failed: {e}")
    sys.exit(1)
except FileNotFoundError:
    print("   ❌ rclone not found. Please install rclone first:")
    print("      https://rclone.org/downloads/")
    sys.exit(1)

# Create rclone config
print("\n2. Creating rclone config...")
config_content = f"""[icloud]
type = iclouddrive
user = {username}
pass = {obscured_pass}
"""

config_path = os.path.expanduser('~/.config/rclone/rclone.conf')
with open(config_path, 'w') as f:
    f.write(config_content)
print(f"   ✅ Config written to {config_path}")

# Try to connect to iCloud
print("\n3. Attempting to connect to iCloud Drive...")
print("   This should trigger Apple to send a 2FA code to your devices")
print("   Watch your iPhone/iPad for a notification!")
print()
print("   Starting rclone connection in verbose mode...")
print("   " + "=" * 56)

try:
    # Start rclone with verbose output
    proc = subprocess.Popen(
        ['rclone', 'lsd', 'icloud:', '--verbose'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    print("\n   Waiting for output from rclone...")
    print("   If you see a 2FA prompt, Apple will send the code to your devices")
    print()
    
    # Read output in real-time
    output_lines = []
    start_time = time.time()
    
    while True:
        line = proc.stdout.readline()
        if line:
            output_lines.append(line)
            print(f"   [rclone] {line.rstrip()}")
            
            # Check for 2FA-related messages
            if '2fa' in line.lower() or 'verification' in line.lower() or 'code' in line.lower():
                print("\n   ⚠️  2FA code required! Check your iPhone/iPad!")
                
        # Check if process ended
        if proc.poll() is not None:
            break
            
        # Timeout after 30 seconds if no activity
        if time.time() - start_time > 30:
            print("\n   ⏱️  Timeout after 30 seconds")
            print("   If you didn't see any 2FA prompts, there might be an issue")
            proc.kill()
            break
    
    # Get any remaining output
    remaining = proc.stdout.read()
    if remaining:
        output_lines.append(remaining)
        print(f"   [rclone] {remaining.rstrip()}")
    
    print()
    print("   " + "=" * 56)
    print()
    
    # Analyze the output
    full_output = ''.join(output_lines).lower()
    
    if '2fa' in full_output or 'verification code' in full_output:
        print("✅ 2FA code should have been sent!")
        print()
        print("Now enter the 6-digit code you received:")
        code = input("2FA Code: ").strip()
        
        if code and len(code) == 6:
            print(f"\nSending code '{code}' to rclone...")
            try:
                proc.stdin.write(f"{code}\n")
                proc.stdin.flush()
                proc.stdin.close()
                
                output, _ = proc.communicate(timeout=30)
                print(output)
                
                if proc.returncode == 0:
                    print("\n✅ SUCCESS! Authentication completed!")
                    print("Your rclone config is now authenticated with iCloud")
                else:
                    print("\n❌ Authentication failed")
                    print(f"Exit code: {proc.returncode}")
            except Exception as e:
                print(f"\n❌ Error submitting code: {e}")
        else:
            print("Invalid code format")
            proc.kill()
    
    elif 'error' in full_output or 'failed' in full_output:
        print("❌ Errors detected in rclone output:")
        print()
        for line in output_lines:
            if 'error' in line.lower() or 'failed' in line.lower():
                print(f"   {line.rstrip()}")
        print()
        print("Common issues:")
        print("  - Incorrect Apple ID or password")
        print("  - App-specific password required (if 2FA already enabled)")
        print("  - Account locked or security issues")
        
    else:
        print("⚠️  No 2FA prompts detected in the output")
        print()
        print("This could mean:")
        print("  1. You might need an app-specific password instead")
        print("     (Create one at: https://appleid.apple.com/account/manage)")
        print("  2. Your account doesn't have 2FA enabled yet")
        print("  3. rclone couldn't connect to Apple's servers")
        print("  4. The credentials are incorrect")

except KeyboardInterrupt:
    print("\n\n⚠️  Interrupted by user")
    proc.kill()
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("Debug session complete")
print("=" * 60)
