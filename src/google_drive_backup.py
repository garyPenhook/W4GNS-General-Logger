"""
Google Drive Backup Module
Automatic backup of database and configuration to Google Drive
"""

import os
import shutil
import json
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    from googleapiclient.errors import HttpError
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False


class GoogleDriveBackup:
    """Manages automatic backups to Google Drive"""

    # OAuth 2.0 scopes
    SCOPES = ['https://www.googleapis.com/auth/drive.file']

    # Backup folder name in Google Drive
    BACKUP_FOLDER_NAME = 'W4GNS-Logger-Backups'

    def __init__(self, config, database_path=None):
        """
        Initialize Google Drive backup manager

        Args:
            config: Config object for storing settings
            database_path: Path to database file (default: logger.db in project root)
        """
        self.config = config
        self.service = None
        self.backup_folder_id = None
        self.is_authenticated = False
        self.auto_backup_thread = None
        self.stop_auto_backup = False

        # Get project root directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(script_dir)

        # Set database path
        if database_path is None:
            self.database_path = os.path.join(self.project_root, "logger.db")
        else:
            self.database_path = database_path

        # Paths for credentials
        self.token_path = os.path.join(self.project_root, 'gdrive_token.json')
        self.credentials_path = os.path.join(self.project_root, 'gdrive_credentials.json')

        # Initialize if credentials exist
        if os.path.exists(self.token_path):
            self.authenticate()

    @staticmethod
    def is_available():
        """Check if Google Drive API libraries are available"""
        return GOOGLE_DRIVE_AVAILABLE

    def authenticate(self):
        """Authenticate with Google Drive using OAuth 2.0"""
        if not GOOGLE_DRIVE_AVAILABLE:
            raise ImportError("Google Drive API libraries not installed. Run: pip install -r requirements.txt")

        creds = None

        # Load existing token
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            except Exception as e:
                print(f"Error loading token: {e}")

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    creds = None

            if not creds:
                # Need new authentication
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}\n"
                        "Please download OAuth credentials from Google Cloud Console"
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        # Build service
        self.service = build('drive', 'v3', credentials=creds)
        self.is_authenticated = True

        # Find or create backup folder
        self._ensure_backup_folder()

        return True

    def _ensure_backup_folder(self):
        """Ensure backup folder exists in Google Drive"""
        if not self.service:
            return None

        try:
            # Search for existing backup folder
            query = f"name='{self.BACKUP_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            folders = results.get('files', [])

            if folders:
                self.backup_folder_id = folders[0]['id']
            else:
                # Create new folder
                folder_metadata = {
                    'name': self.BACKUP_FOLDER_NAME,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = self.service.files().create(
                    body=folder_metadata,
                    fields='id'
                ).execute()
                self.backup_folder_id = folder.get('id')

            return self.backup_folder_id

        except HttpError as error:
            print(f"Error ensuring backup folder: {error}")
            return None

    def create_backup(self, include_config=True):
        """
        Create a backup and upload to Google Drive

        Args:
            include_config: Whether to include config.json in backup

        Returns:
            dict: Backup result with status and details
        """
        if not self.is_authenticated:
            return {
                'success': False,
                'error': 'Not authenticated with Google Drive'
            }

        if not os.path.exists(self.database_path):
            return {
                'success': False,
                'error': f'Database file not found: {self.database_path}'
            }

        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Create temporary backup directory
            temp_backup_dir = os.path.join(self.project_root, 'temp_backup')
            os.makedirs(temp_backup_dir, exist_ok=True)

            # Copy database
            db_backup_name = f'logger_{timestamp}.db'
            db_backup_path = os.path.join(temp_backup_dir, db_backup_name)
            shutil.copy2(self.database_path, db_backup_path)

            # Upload database
            db_result = self._upload_file(db_backup_path, db_backup_name)

            results = {
                'success': db_result['success'],
                'timestamp': timestamp,
                'database': db_result
            }

            # Optionally backup config
            if include_config:
                config_path = os.path.join(self.project_root, 'config.json')
                if os.path.exists(config_path):
                    config_backup_name = f'config_{timestamp}.json'
                    config_backup_path = os.path.join(temp_backup_dir, config_backup_name)
                    shutil.copy2(config_path, config_backup_path)

                    config_result = self._upload_file(config_backup_path, config_backup_name)
                    results['config'] = config_result

            # Cleanup
            shutil.rmtree(temp_backup_dir, ignore_errors=True)

            # Rotate old backups
            self._rotate_backups()

            # Update last backup time in config
            self.config.set('google_drive.last_backup', datetime.now().isoformat())

            return results

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _upload_file(self, file_path, file_name):
        """Upload a file to Google Drive backup folder"""
        try:
            file_metadata = {
                'name': file_name,
                'parents': [self.backup_folder_id]
            }

            media = MediaFileUpload(file_path, resumable=True)

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, size, createdTime'
            ).execute()

            return {
                'success': True,
                'file_id': file.get('id'),
                'name': file.get('name'),
                'size': file.get('size'),
                'created': file.get('createdTime')
            }

        except HttpError as error:
            return {
                'success': False,
                'error': str(error)
            }

    def list_backups(self):
        """List all backups in Google Drive"""
        if not self.is_authenticated or not self.backup_folder_id:
            return []

        try:
            query = f"'{self.backup_folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, size, createdTime, modifiedTime)',
                orderBy='createdTime desc'
            ).execute()

            return results.get('files', [])

        except HttpError as error:
            print(f"Error listing backups: {error}")
            return []

    def _rotate_backups(self):
        """Delete old backups based on retention policy"""
        max_backups = self.config.get('google_drive.max_backups', 30)

        if max_backups <= 0:
            return  # No rotation

        backups = self.list_backups()

        # Filter to database backups only
        db_backups = [b for b in backups if b['name'].startswith('logger_') and b['name'].endswith('.db')]

        # Delete oldest backups beyond max_backups
        if len(db_backups) > max_backups:
            to_delete = db_backups[max_backups:]

            for backup in to_delete:
                try:
                    self.service.files().delete(fileId=backup['id']).execute()
                    print(f"Deleted old backup: {backup['name']}")
                except HttpError as error:
                    print(f"Error deleting backup {backup['name']}: {error}")

    def download_backup(self, file_id, destination_path):
        """Download a backup from Google Drive"""
        if not self.is_authenticated:
            return False

        try:
            request = self.service.files().get_media(fileId=file_id)

            with open(destination_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()

            return True

        except HttpError as error:
            print(f"Error downloading backup: {error}")
            return False

    def start_auto_backup(self):
        """Start automatic backup thread"""
        if self.auto_backup_thread and self.auto_backup_thread.is_alive():
            return  # Already running

        if not self.config.get('google_drive.enabled', False):
            return  # Auto backup not enabled

        self.stop_auto_backup = False
        self.auto_backup_thread = threading.Thread(target=self._auto_backup_loop, daemon=True)
        self.auto_backup_thread.start()

    def stop_auto_backup_thread(self):
        """Stop automatic backup thread"""
        self.stop_auto_backup = True
        if self.auto_backup_thread:
            self.auto_backup_thread.join(timeout=5)

    def _auto_backup_loop(self):
        """Background thread for automatic backups"""
        # Get backup interval in hours (default 24 hours)
        interval_hours = self.config.get('google_drive.backup_interval_hours', 24)
        interval_seconds = interval_hours * 3600

        while not self.stop_auto_backup:
            # Check if it's time for a backup
            last_backup_str = self.config.get('google_drive.last_backup')

            should_backup = False
            if not last_backup_str:
                should_backup = True
            else:
                try:
                    last_backup = datetime.fromisoformat(last_backup_str)
                    if datetime.now() - last_backup > timedelta(seconds=interval_seconds):
                        should_backup = True
                except (ValueError, TypeError) as e:
                    print(f"Warning: Invalid last backup timestamp: {e}")
                    should_backup = True

            if should_backup and self.is_authenticated:
                print(f"[Auto Backup] Creating scheduled backup...")
                result = self.create_backup()
                if result['success']:
                    print(f"[Auto Backup] Backup completed successfully")
                else:
                    print(f"[Auto Backup] Backup failed: {result.get('error', 'Unknown error')}")

            # Sleep for 1 hour, check stop flag frequently
            for _ in range(60):
                if self.stop_auto_backup:
                    break
                time.sleep(60)  # Check every minute

    def disconnect(self):
        """Disconnect and clear authentication"""
        self.stop_auto_backup_thread()
        self.service = None
        self.is_authenticated = False
        self.backup_folder_id = None

        # Optionally remove token
        if os.path.exists(self.token_path):
            try:
                os.remove(self.token_path)
            except (OSError, PermissionError) as e:
                print(f"Warning: Could not remove token file: {e}")


def format_file_size(size_bytes):
    """Format file size in human-readable format"""
    try:
        size_bytes = int(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    except (ValueError, TypeError):
        return "Unknown"


def format_timestamp(iso_timestamp):
    """Format ISO timestamp to readable format"""
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError, AttributeError):
        return iso_timestamp
