#!/bin/bash

# LUKS device and keyfile info
LUKS_DEV="/dev/nvme1n1p3"  # Partition holding root LUKS
LUKS_MAPPER="/dev/mapper/ubuntu--vg-ubuntu--lv"  # LVM root
CRYPTTAB_NAME="dm_crypt-0"  # Name in /etc/crypttab (may need adjustment)
KEYFILE_SRC="/media/phantomojo/datacrypt/keyfile.luks"
CRYPTTAB="/etc/crypttab"

# Get the real user (not root when script is run with sudo)
REAL_USER=${SUDO_USER:-$USER}
REAL_HOME=$(eval echo ~$REAL_USER)

# Get UUID of datacrypt
USB_UUID=$(blkid -s UUID -o value /dev/sda1)
KEYFILE_USB="/dev/disk/by-uuid/$USB_UUID/keyfile.luks"

# Check if zenity is installed
if ! command -v zenity &> /dev/null; then
    echo "Zenity is required. Install with: sudo apt install zenity"
    exit 1
fi

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    exec sudo "$0" "$@"
fi

function show_status() {
    if grep -q "$KEYFILE_USB" "$CRYPTTAB"; then
        zenity --info --text="Auto-unlock is ENABLED.\nKeyfile: $KEYFILE_USB"
    else
        zenity --info --text="Auto-unlock is DISABLED."
    fi
}

function enable_auto_unlock() {
    # Check if drive is accessible
    if [ ! -d "/media/phantomojo/datacrypt" ]; then
        zenity --error --text="External drive not found at /media/phantomojo/datacrypt"
        return 1
    fi
    
    # Test write access
    if ! touch "/media/phantomojo/datacrypt/test_write" 2>/dev/null; then
        zenity --error --text="Cannot write to external drive. Check permissions."
        return 1
    fi
    rm -f "/media/phantomojo/datacrypt/test_write"
    
    # Generate keyfile if not present
    if [ ! -f "$KEYFILE_SRC" ]; then
        dd if=/dev/urandom of="$KEYFILE_SRC" bs=4096 count=1
        chmod 0400 "$KEYFILE_SRC"
        chown "$REAL_USER:$REAL_USER" "$KEYFILE_SRC"
    fi
    
    # Add keyfile to LUKS
    if ! cryptsetup luksAddKey "$LUKS_DEV" "$KEYFILE_SRC"; then
        zenity --error --text="Failed to add keyfile to LUKS. It may already exist."
        return 1
    fi
    
    # Get UUID and update crypttab
    if ! grep -q "$KEYFILE_USB" "$CRYPTTAB"; then
        # Remove any old keyfile lines for this device
        sed -i "/$LUKS_DEV/d" "$CRYPTTAB"
        echo "$CRYPTTAB_NAME $LUKS_DEV $KEYFILE_USB luks,discard" >> "$CRYPTTAB"
    fi
    
    update-initramfs -u
    zenity --info --text="Auto-unlock ENABLED. System will auto-unlock root if the drive is present at boot."
}

function disable_auto_unlock() {
    # Remove keyfile entry from crypttab
    sed -i "/$KEYFILE_USB/d" "$CRYPTTAB"
    update-initramfs -u
    zenity --info --text="Auto-unlock DISABLED. System will prompt for passphrase at boot."
}

# Main GUI
ACTION=$(zenity --list --radiolist --title="LUKS Auto-Unlock" --column="Select" --column="Action" TRUE "Show Status" FALSE "Enable Auto-Unlock" FALSE "Disable Auto-Unlock" --height=250 --width=400)

case "$ACTION" in
    "Show Status") show_status ;;
    "Enable Auto-Unlock") enable_auto_unlock ;;
    "Disable Auto-Unlock") disable_auto_unlock ;;
    *) exit 0 ;;
esac 