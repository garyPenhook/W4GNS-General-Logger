# Google Drive Auto-Backup Setup Guide

The W4GNS General Logger now supports automatic backups to Google Drive! This guide will walk you through setting up the feature.

## Features

- 🔄 **Automatic Scheduled Backups** - Set custom intervals (1-168 hours)
- 📦 **Database & Config Backup** - Backs up both logger.db and config.json
- 🔐 **Secure OAuth Authentication** - Uses Google's official OAuth 2.0
- 🗂️ **Organized Storage** - Creates dedicated "W4GNS-Logger-Backups" folder
- ♻️ **Automatic Rotation** - Keeps only recent backups (configurable 5-100)
- 📊 **Backup Management** - View, manage, and restore backups from the app

## Prerequisites

1. **Python 3.12+** (already required for the logger)
2. **Google Account** with Google Drive access
3. **Google Cloud Project** (free tier is sufficient)

## Step 1: Install Required Dependencies

```bash
# Navigate to the logger directory
cd /path/to/W4GNS-General-Logger

# Install Google Drive API libraries
pip install -r requirements.txt
```

This installs:
- `google-auth` - Authentication library
- `google-auth-oauthlib` - OAuth flow handling
- `google-auth-httplib2` - HTTP transport
- `google-api-python-client` - Google Drive API client

## Step 2: Create Google Cloud Project

### 2.1 Create a Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a Project" → "New Project"
3. Name it: `W4GNS Logger Backup` (or any name you prefer)
4. Click "Create"

### 2.2 Enable Google Drive API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Drive API"
3. Click on it and press "Enable"

### 2.3 Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "+ CREATE CREDENTIALS" → "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: **External** (unless you have a Google Workspace)
   - App name: `W4GNS General Logger`
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Skip (we'll set this in code)
   - Test users: Add your Google email
   - Click "Save and Continue" through the rest

4. Back to "Create OAuth Client ID":
   - Application type: **Desktop app**
   - Name: `W4GNS Logger Desktop`
   - Click "Create"

5. **Download Credentials**:
   - Click the download icon (⬇️) next to your OAuth client
   - Save the JSON file

### 2.4 Rename and Place Credentials File

1. Rename the downloaded file to: **`gdrive_credentials.json`**
2. Place it in your logger project root directory:

```
W4GNS-General-Logger/
├── gdrive_credentials.json  ← Place here
├── main.py
├── src/
├── config.json
└── ...
```

## Step 3: Configure in the Logger

1. **Launch the logger**: `python main.py`
2. Go to the **Settings** tab
3. Scroll down to **"Google Drive Auto-Backup"** section

### 3.1 First-Time Authentication

1. Click **"Connect to Google Drive"**
2. Your browser will open to Google's OAuth consent screen
3. **Sign in** to your Google account
4. **Review permissions** - The app requests:
   - See and download files created by this app in Google Drive
   - Upload files to Google Drive
5. Click **"Continue"** or **"Allow"**
6. You'll see "Authentication successful" - close the browser tab
7. Return to the logger - you should see **"✓ Connected"**

## Step 4: Configure Backup Settings

In the Google Drive Auto-Backup section:

### Basic Settings

- ☑️ **Enable automatic Google Drive backups** - Check this box
- **Backup interval**: Set how often to backup (default: 24 hours)
- **Keep last**: Number of backups to retain (default: 30)
  - Older backups are automatically deleted
- ☑️ **Include configuration file** - Backs up config.json too

### Backup Controls

- **Backup Now** - Perform immediate manual backup
- **View Backups** - See list of all backups with sizes and dates
- **Open Google Drive Folder** - Opens backup folder in your browser

## Step 5: Verify It Works

### Test Manual Backup

1. Click **"Backup Now"**
2. Wait for the success message
3. Click **"View Backups"** to see your backup
4. Or click **"Open Google Drive Folder"** to view in browser

### Check Automatic Backup

- The logger will now backup automatically based on your interval
- Check **"Last backup:"** timestamp to verify
- Backups continue even if you close and reopen the app

## Backup File Naming

Backups are named with timestamps for easy identification:

```
logger_20250310_143022.db      # Database backup (YYYYMMDD_HHMMSS)
config_20250310_143022.json    # Config backup (if enabled)
```

## Security & Privacy

### What Data is Backed Up?

- **logger.db**: All your contact logs and awards data
- **config.json**: Your settings (callsign, preferences, etc.)

### Data Security

- ✅ Encrypted in transit (HTTPS)
- ✅ Encrypted at rest (Google Drive encryption)
- ✅ OAuth tokens stored locally in `gdrive_token.json`
- ✅ Only accessible by you through your Google account
- ✅ App can only access files it creates (not your entire Drive)

### Permissions

The app requests **limited scope** (`.../auth/drive.file`):
- ✅ Can create and manage files in its own folder
- ❌ Cannot access other files in your Google Drive
- ❌ Cannot see your personal documents

## Troubleshooting

### "Credentials file not found"

**Solution**: Ensure `gdrive_credentials.json` is in the project root directory:
```bash
ls -la gdrive_credentials.json  # Should exist
```

### "Authentication failed"

**Solutions**:
1. Check if your Google Cloud project is still active
2. Verify Google Drive API is enabled
3. Try disconnecting and reconnecting
4. Delete `gdrive_token.json` and re-authenticate

### "Backup failed" Errors

**Solutions**:
1. Check your internet connection
2. Verify you have Google Drive storage space
3. Check if you're still authenticated (status should show "✓ Connected")
4. Try disconnecting and reconnecting

### "Google Drive API not installed"

**Solution**: Install dependencies:
```bash
pip install --upgrade -r requirements.txt
```

### OAuth Consent Screen Warnings

If you see "Google hasn't verified this app":
1. Click **"Advanced"**
2. Click **"Go to W4GNS General Logger (unsafe)"**
3. This is normal for personal apps in testing mode

## Restoring from Backup

### Option 1: Via Google Drive Web Interface

1. Go to your Google Drive
2. Navigate to `W4GNS-Logger-Backups` folder
3. Download the desired `logger_YYYYMMDD_HHMMSS.db` file
4. Rename it to `logger.db`
5. Replace the file in your logger directory

### Option 2: Local Restore

1. In the logger, go to **Settings** → **Backup & Auto-Save**
2. Click **"Restore Database"**
3. Browse to downloaded backup file
4. Confirm the restore

**⚠️ Warning**: Restoring will overwrite your current database!

## Cost

**Free Tier**: Google Drive offers 15 GB free storage, shared across:
- Gmail
- Google Photos
- Google Drive files

**Typical Usage**:
- Database backup: ~100 KB - 10 MB (depends on contacts)
- Config backup: ~1 KB
- 30 backups: Usually under 1 MB total

You'll likely never hit the free tier limit with logger backups!

## Advanced Configuration

### Multiple Google Accounts

To switch accounts:
1. Click **"Disconnect"** in Settings
2. Delete `gdrive_token.json` from project root
3. Click **"Connect to Google Drive"** again
4. Authenticate with different account

### Sharing Backups

The backup folder is private by default. To share:
1. Click **"Open Google Drive Folder"**
2. Right-click the folder → "Share"
3. Add collaborators

### Backup to Multiple Drives

Currently supports one Google account. To backup to multiple:
- Use the built-in local backup feature alongside Google Drive
- Set different external backup paths

## Uninstalling / Disabling

### Temporarily Disable

1. Uncheck **"Enable automatic Google Drive backups"** in Settings
2. Backups stop, but connection remains

### Fully Disconnect

1. Click **"Disconnect"** in Settings
2. Optionally delete these files from project root:
   - `gdrive_token.json`
   - `gdrive_credentials.json`

3. Your backups remain in Google Drive unless you delete them

## Support

Having issues? Check:

1. **Logger Console Output**: Look for error messages
2. **Google Cloud Console**: Verify project status and API quota
3. **Google Drive**: Ensure you have storage space
4. **Network**: Check firewall isn't blocking Google APIs

## Privacy Policy

This feature:
- Only stores data in YOUR Google Drive
- Does NOT send data to third parties
- Does NOT collect analytics
- Uses Google's official APIs
- Source code is open for inspection

## Summary

✅ Automatic scheduled backups
✅ Secure OAuth authentication
✅ Configurable retention policy
✅ Easy restore process
✅ Free (within Google's limits)
✅ Privacy-focused

Your ham radio logs are now safely backed up to the cloud!

---

**Note**: This is an optional feature. The logger works perfectly fine with local backups only if you prefer not to use Google Drive.
