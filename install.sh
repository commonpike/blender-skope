#!/bin/bash
set -e

# --------------------------
# this script downloads a mac blender .dmg, mounts it
# and copies the app to BLENDER_LOCATION in your .env
# If you already have blender, dont bother running this;
# just update your .env to point to your blender. ymmv.
# --------------------------

source .env

# Vendor supplied DMG file
VendorDMG="blender.dmg"
VendorMnt="/Volumes/Blender"
VendorApp="Blender.app"
# VendorDownload=""  # "Latest" download link, if universal
VendorDownloadARM=$BLENDER_DOWNLOAD_ARM
VendorDownloadIntel=$BLENDER_DOWNLOAD_INTEL
TempLog="/tmp/blender.log"

# Evaluate if this is arm or x86 and set install dir appropriately
if [[ $(uname -m) == 'arm64' ]]; then
	# Apple Silicone
	VendorDownload=$VendorDownloadARM
else
	VendorDownload=$VendorDownloadIntel
fi

# Download vendor supplied DMG file into /tmp/
echo "Starting download: ${VendorDownload}" | tee -a $TempLog
curl -4 -sSL "${VendorDownload}" -o "/tmp/${VendorDMG}"  | tee -a $TempLog


# Mount vendor supplied DMG File
echo "Mounting..."  | tee -a $TempLog
hdiutil attach "/tmp/${VendorDMG}" -nobrowse  | tee -a $TempLog

# Copy contents of vendor supplied DMG file to /Applications/
# Preserve all file attributes and ACLs
echo "Copying to $BLENDER_LOCATION ..."  | tee -a $TempLog
mkdir -p "$BLENDER_LOCATION"
cp -pR "${VendorMnt}/${VendorApp}" "$BLENDER_LOCATION"  | tee -a $TempLog

# Identify the correct mount point for the vendor supplied DMG file 
echo "Identifying Mountpoint..."  | tee -a $TempLog
MntDev="$(hdiutil info | grep "${VendorMnt}" | awk '{ print $1 }')"  | tee -a $TempLog

# Unmount the vendor supplied DMG file
echo "Dismounting..." | tee -a $TempLog
hdiutil detach $MntDev | tee -a $TempLog

# Remove the downloaded vendor supplied DMG file
echo "Cleaning up..." | tee -a $TempLog
rm -f /tmp/$VendorDMG 
rm $TempLog

echo "Done!"