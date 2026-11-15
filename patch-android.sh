#!/usr/bin/env bash
# Nagdadagdag ng permissions (mic + audio + storage) sa AndroidManifest.xml
set -e
M=android/app/src/main/AndroidManifest.xml
add() { grep -q "$1" "$M" || sed -i "s#</manifest>#    $2\n</manifest>#" "$M"; }
add "android.permission.RECORD_AUDIO" '<uses-permission android:name="android.permission.RECORD_AUDIO" />'
add "android.permission.MODIFY_AUDIO_SETTINGS" '<uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />'
add "android.permission.WRITE_EXTERNAL_STORAGE" '<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="28" />'
# Pigilan ang pag-sleep ng screen habang nagmi-mix
add "android.permission.WAKE_LOCK" '<uses-permission android:name="android.permission.WAKE_LOCK" />'
echo "AndroidManifest patched."
