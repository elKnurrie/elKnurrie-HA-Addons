#!/usr/bin/env python3
"""
Home Assistant iCloud Backup Add-on
Uploads Home Assistant backups to iCloud Drive using PyiCloud-ipd (maintained fork)
"""
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

try:
    from pyicloud import PyiCloudService
    from pyicloud.exceptions import PyiCloudFailedLoginException, PyiCloud2SARequiredError
except ImportError:
    # Try alternative import
    from pyicloud_ipd import PyiCloudService
    from pyicloud_ipd.exceptions import PyiCloudFailedLoginException, PyiCloud2SARequiredError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from /data/options.json"""
    config_file = Path('/data/options.json')
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)

def authenticate_icloud(username, password):
    """Authenticate with iCloud"""
    logger.info("Authenticating with iCloud...")
    logger.info(f"Using Apple ID: {username}")
    
    try:
        # Use a persistent cookie directory
        cookie_dir = '/data'
        
        # Try to authenticate
        api = PyiCloudService(
            username, 
            password,
            cookie_directory=cookie_dir,
            verify=True
        )
        
        # Check if 2FA is required
        if api.requires_2fa:
            logger.error("Two-factor authentication code is required!")
            logger.error("")
            logger.error("This add-on cannot handle interactive 2FA prompts.")
            logger.error("")
            logger.error("IMPORTANT: You must use an app-specific password!")
            logger.error("Regular Apple ID passwords won't work.")
            logger.error("")
            logger.error("Steps to generate app-specific password:")
            logger.error("1. Go to: https://appleid.apple.com/account/manage")
            logger.error("2. Click 'Security'")
            logger.error("3. Under 'App-Specific Passwords', click 'Generate Password'")
            logger.error("4. Label it 'Home Assistant'")
            logger.error("5. Copy the password (format: xxxx-xxxx-xxxx-xxxx)")
            logger.error("6. Use that in this add-on (not your regular password)")
            logger.error("")
            sys.exit(1)
        
        # Verify we can access drive
        try:
            _ = api.drive
            logger.info("Successfully authenticated and accessed iCloud Drive!")
        except Exception as drive_error:
            logger.error(f"Authenticated but cannot access iCloud Drive: {drive_error}")
            logger.error("Make sure iCloud Drive is enabled in your iCloud settings")
            sys.exit(1)
            
        return api
        
    except PyiCloud2SARequiredError:
        logger.error("Two-Step Authentication is required but cannot be completed automatically")
        logger.error("You MUST use an app-specific password instead of your regular password")
        logger.error("Generate one at: https://appleid.apple.com/account/manage")
        sys.exit(1)
        
    except PyiCloudFailedLoginException as e:
        logger.error(f"Failed to login to iCloud: {e}")
        logger.error("")
        logger.error("Troubleshooting:")
        logger.error("")
        logger.error("1. VERIFY you're using an APP-SPECIFIC password")
        logger.error("   (NOT your regular Apple ID password)")
        logger.error("")
        logger.error("2. Check if your app-specific password is still valid")
        logger.error("   (They can expire or be revoked)")
        logger.error("")
        logger.error("3. Generate a NEW app-specific password:")
        logger.error("   - Go to https://appleid.apple.com/account/manage")
        logger.error("   - Security → App-Specific Passwords")
        logger.error("   - Generate new password")
        logger.error("   - Use format: xxxx-xxxx-xxxx-xxxx (with dashes)")
        logger.error("")
        logger.error("4. Verify your Apple ID email is correct")
        logger.error(f"   Currently using: {username}")
        logger.error("")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"iCloud authentication error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

def get_or_create_folder(drive, folder_name):
    """Get or create a folder in iCloud Drive"""
    try:
        # Try to find existing folder
        for item in drive.dir():
            if item.name == folder_name and item.type == 'folder':
                logger.info(f"Found existing folder: {folder_name}")
                return item
        
        # Create new folder
        logger.info(f"Creating folder: {folder_name}")
        drive.mkdir(folder_name)
        
        # Return the newly created folder
        for item in drive.dir():
            if item.name == folder_name:
                return item
                
    except Exception as e:
        logger.error(f"Failed to access/create folder: {e}")
        sys.exit(1)

def upload_backup(drive, folder, backup_file):
    """Upload a backup file to iCloud Drive"""
    try:
        filename = os.path.basename(backup_file)
        logger.info(f"Uploading {filename} to iCloud...")
        
        with open(backup_file, 'rb') as f:
            folder.upload(f, filename)
        
        logger.info(f"Successfully uploaded {filename}")
        return True
    except Exception as e:
        logger.error(f"Failed to upload {backup_file}: {e}")
        return False

def delete_old_backups(folder, retention_days):
    """Delete backups older than retention_days"""
    if retention_days <= 0:
        return
    
    try:
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        logger.info(f"Removing backups older than {retention_days} days...")
        
        deleted_count = 0
        for item in folder.dir():
            if item.type == 'file':
                # Get file modification date
                file_date = item.date_modified
                if file_date and file_date < cutoff_date:
                    logger.info(f"Deleting old backup: {item.name}")
                    item.delete()
                    deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"Deleted {deleted_count} old backup(s)")
        else:
            logger.info("No old backups to delete")
            
    except Exception as e:
        logger.error(f"Error cleaning up old backups: {e}")

def main():
    """Main function"""
    logger.info("Starting Home Assistant iCloud Backup...")
    
    # Load configuration
    config = load_config()
    username = config.get('icloud_username', '')
    password = config.get('icloud_password', '')
    backup_source = config.get('backup_source', '/backup')
    icloud_folder = config.get('icloud_folder', 'HomeAssistantBackups')
    retention_days = config.get('retention_days', 14)
    
    # Validate configuration
    if not username or not password:
        logger.error("iCloud username and password are required!")
        sys.exit(1)
    
    # Authenticate with iCloud
    api = authenticate_icloud(username, password)
    
    # Access iCloud Drive
    logger.info("Accessing iCloud Drive...")
    drive = api.drive
    
    # Get or create backup folder
    backup_folder = get_or_create_folder(drive, icloud_folder)
    
    # Find backup files
    backup_path = Path(backup_source)
    if not backup_path.exists():
        logger.error(f"Backup directory not found: {backup_source}")
        sys.exit(1)
    
    backup_files = list(backup_path.glob('*.tar'))
    if not backup_files:
        logger.warning(f"No backup files found in {backup_source}")
    else:
        logger.info(f"Found {len(backup_files)} backup file(s)")
        
        # Upload each backup
        uploaded = 0
        for backup_file in backup_files:
            if upload_backup(drive, backup_folder, str(backup_file)):
                uploaded += 1
        
        logger.info(f"Successfully uploaded {uploaded}/{len(backup_files)} backup(s)")
    
    # Clean up old backups
    delete_old_backups(backup_folder, retention_days)
    
    logger.info("Backup sync complete!")
    logger.info("Add-on will continue running until stopped.")

if __name__ == '__main__':
    try:
        main()
        # Keep the container running
        import time
        while True:
            time.sleep(3600)  # Sleep for 1 hour
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
