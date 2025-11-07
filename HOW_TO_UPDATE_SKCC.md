# How to Update SKCC Contacts from ADIF

## Quick Start

After fixing the SKCC import bugs, you need to update your existing contacts with the corrected SKCC data.

## Prerequisites

1. Your SKCC Logger ADIF export file
2. The W4GNS Logger database file (logger.db)

## Where to Find Your SKCC Logger ADIF File

### Windows
- `C:\Users\<YourName>\Documents\SKCC Logger\`
- `C:\Users\<YourName>\AppData\Roaming\SKCC Logger\`

### Mac/Linux
- `~/Documents/SKCC Logger/`
- `~/.skcc_logger/`

### Export from SKCC Logger
If you don't have an ADIF file:
1. Open SKCC Logger
2. File → Export → ADIF
3. Save as `skcc_log.adi`

## Update Your Contacts

### Method 1: Update Existing Contacts (Recommended)

This updates your contacts without deleting anything:

```bash
cd /home/user/W4GNS-General-Logger
python3 update_skcc_from_adif.py /path/to/skcc_log.adi
```

**Example:**
```bash
# If ADIF file is in home directory
python3 update_skcc_from_adif.py ~/skcc_log.adi

# If ADIF file is in Downloads
python3 update_skcc_from_adif.py ~/Downloads/skcc_log.adi

# Specify database location
python3 update_skcc_from_adif.py ~/skcc_log.adi ./logger.db
```

### Method 2: Delete and Re-import (Alternative)

**⚠️ WARNING: This deletes contacts! Have a backup!**

```bash
# Step 1: Delete SKCC contacts (asks for confirmation)
python3 delete_skcc_contacts.py

# Step 2: Use the GUI to re-import
# Run the app, then: File → Import Log (ADIF)...
```

## What Gets Updated

The update script will:
- ✅ Add missing SKCC numbers from `<SKCC:...>` field
- ✅ Add missing key types from `<APP_SKCCLOGGER_KEYTYPE:...>` field
- ✅ Translate key codes: BG→BUG, SK/ST→STRAIGHT, SS→SIDESWIPER
- ✅ Match contacts by: callsign + date + time
- ✅ Preserve all other contact data

## After Updating

1. Run the W4GNS Logger application
2. Go to the "SKCC Awards" tab
3. Your contacts should now appear correctly
4. Tribune award should show your progress

## Troubleshooting

### "Database not found"
The logger.db file doesn't exist yet. Run the W4GNS Logger app first to create it.

### "No contacts found in ADIF"
Check your ADIF file path. Make sure it's the correct file from SKCC Logger.

### "Contacts not found in DB"
These contacts exist in your ADIF but not in your database. They might be new contacts that need importing via the GUI.

### "Still showing 0 contacts in awards"
Make sure:
1. The SKCC numbers were imported (check the script output)
2. The key_type field was set (should show BUG, STRAIGHT, or SIDESWIPER)
3. Your user configuration has SKCC join date and centurion date set
4. The contacts are in CW mode

## Bugs Fixed

This update addresses three bugs:
1. ✅ Key type validation now requires mechanical keys
2. ✅ SKCC Logger key codes (BG, SK, ST, SS) now translated
3. ✅ SKCC field `<SKCC:...>` now recognized (was only looking for APP_SKCCLOGGER_NUMBER)

## Need Help?

If you encounter issues, run the diagnostic:
```bash
python3 skcc_diagnostic.py
```
