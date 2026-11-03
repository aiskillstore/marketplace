# Android device owner by QR code

A factory-reset Android 10+ device with a camera becomes the Player's device owner
and a screen of the project with no pairing code and no device manager. The
person opens the fleet link in the dashboard (Settings, Fleet links, Android
device owner, Show QR code), taps the device's Welcome screen six times and scans
the code. The Player runs full screen as the home app with no navigation bar,
notifications or lock screen. Create the link first (`fleet-links create`; its
URL creates screens, and so does the code: give it only to the person at the
device).

To hand the person the payload instead of the dashboard, print it (the dashboard's
Copy provisioning JSON copies the same). It needs a Manage sign-in, because the
payload holds the link's secret, and the last line is the JSON, ready to encode as a
QR code:

```bash
screenrig fleet-links show flk_ID --android-provisioning
```

The JSON names the managed build's device administrator, its versioned download
address on the site, the signing certificate's checksum, every system app left
enabled, and the link's secret under `fleet_link`:

```json
{
  "android.app.extra.PROVISIONING_DEVICE_ADMIN_COMPONENT_NAME": "PACKAGE/ai.screenrig.player.managed.ScreenRigDeviceAdminReceiver",
  "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_DOWNLOAD_LOCATION": "DOWNLOAD_URL",
  "android.app.extra.PROVISIONING_DEVICE_ADMIN_SIGNATURE_CHECKSUM": "CHECKSUM",
  "android.app.extra.PROVISIONING_LEAVE_ALL_SYSTEM_APPS_ENABLED": true,
  "android.app.extra.PROVISIONING_ADMIN_EXTRAS_BUNDLE": { "fleet_link": "FLEET_LINK_URL" }
}
```

The command reads the `managed` entry of the site's `/android/manifest.json`. When the
site lists none it answers `android_device_owner_build_unavailable`: say so rather
than using the `player` entry, whose package has no device administrator. A Read only
credential gets no link URL and so no payload (`fleet_link_secret_unavailable`).
