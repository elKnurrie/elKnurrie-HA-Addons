#!/usr/bin/env python3
"""
Test rclone iCloud authentication by simulating the interactive process
This shows what commands actually work to trigger 2FA
"""
import subprocess
import sys
import os
import time

print("=" * 60)
print("Testing rclone iCloud 2FA Process")
print("=" * 60)
print()

# Get credentials
username = input("Enter your Apple ID (email): ").strip()
password = input("Enter your app-specific password: ").strip()

if not username or not password:
    print("❌ Username and password required")
    sys.exit(1)

# Create config directory
config_dir = os.path.expanduser('~/.config/rclone')
os.makedirs(config_dir, exist_ok=True)

print("\n🔧 Method 1: Using rclone config create (non-interactive)")
print("-" * 60)

try:
    # Use rclone config create which is non-interactive
    result = subprocess.run(
        ['rclone', 'config', 'create', 'icloud', 'iclouddrive',
         f'user={username}',
         f'pass={password}'],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    print("Output:", result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    if result.returncode == 0:
        print("✅ Config created successfully")
    else:
        print(f"❌ Failed with exit code {result.returncode}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n🔧 Method 2: Testing connection (this should trigger 2FA)")
print("-" * 60)
print("Running: rclone lsf icloud: --max-depth 1")
print()

# Now try to list files - this should trigger 2FA
proc = subprocess.Popen(
    ['rclone', 'lsf', 'icloud:', '--max-depth', '1', '-vv'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

print("Waiting for output...")
print()

try:
    # Read output for 15 seconds
    start = time.time()
    output_lines = []
    
    while time.time() - start < 15:
        if proc.poll() is not None:
            break
            
        line = proc.stdout.readline()
        if line:
            output_lines.append(line)
            print(f"  {line.rstrip()}")
            
            # Look for 2FA prompts
            if any(word in line.lower() for word in ['2fa', 'verification', 'code', 'trust']):
                print("\n⚠️  2FA RELATED MESSAGE DETECTED!")
                print("Check your iPhone/iPad for a code!")
                print()
                
                # Ask for code
                code = input("Enter the 6-digit code (or press Enter to skip): ").strip()
                if code and len(code) == 6:
                    print(f"Sending code: {code}")
                    proc.stdin.write(f"{code}\n")
                    proc.stdin.flush()
    
    # Get remaining output
    remaining = proc.stdout.read()
    if remaining:
        print(remaining)
        output_lines.append(remaining)
    
    print()
    print("-" * 60)
    
    # Analyze
    full_output = ' '.join(output_lines).lower()
    
    if proc.returncode == 0 or 'success' in full_output:
        print("✅ SUCCESS!")
    elif '2fa' in full_output or 'verification' in full_output:
        print("ℹ️  2FA was triggered but may need the code")
    elif 'trust token' in full_output:
        print("⚠️  Trust token issue - need to use different rclone command")
    else:
        print(f"❌ Failed with exit code: {proc.returncode}")
    
    print("\nFull output analysis:")
    print("  - Contains '2fa':", '2fa' in full_output)
    print("  - Contains 'trust token':", 'trust token' in full_output)
    print("  - Contains 'verification':", 'verification' in full_output)
    print("  - Contains 'error':", 'error' in full_output)

except KeyboardInterrupt:
    print("\n⚠️  Interrupted")
    proc.kill()

print()
print("=" * 60)
print("Test complete")
print("=" * 60)
