[GenUIBridge.py](https://github.com/user-attachments/files/34246976/GenUIBridge.py)# Nowbar Fix
Although Now Brief appeared in the Now Bar settings menu or in Galaxy AI, it never actually appeared on the Now Bar itself.

#### Why?
The Now Bar on the lock screen is managed by AODService.apk (NowBarItemManager). NowBarItemManager attempts to access the GenUIService within SmartSuggestions (7.3.30.9) in order to draw Now Brief cards on the lock screen.
However, as the S23 Ultra comes with the stock SmartSuggestions (7.2.01.68), the following permission is not defined in either the S23 Ultra’s SystemUI.apk file or the AODService.apk file:

```xml
<uses-permission android:name="com.samsung.android.smartsuggestions.permission.BIND_GENUI_SERVICE" />
```
However, as SmartSuggestions 7.3.30.9, which we set up from S26, requires this permission, the Android ActivityManager was returning the following error: 

```
W ActivityManager: Permission Denial: Accessing service com.samsung.android.smartsuggestions/.feature.aisuggestion.genui.service.GenUIService from pid=21910, uid=10048 requires com.samsung.android.smartsuggestions.permission.BIND_GENUI_SERVICE
```

#### Solution

In Android 16, we need to prepare a custom bridge package that uses the `sharedUserId` permission-sharing architecture.
First, let’s transfer the `com.samsung.android.app.aodservice` package from your phone to your computer.

```bash
adb pull /system/priv-app/AODService_v80/AODService_v80.apk
```

Why `AODService`? Because `SystemU`I and `AODService` share the same group with `sharedUserId="android.uid.systemui" (uid=10048)`. In order to include a new package in this group, the package must contain Samsung’s `b378e95c` certificate.
We used Python script `GenUIBridge.py` to create the GenUIBridge.apk, i.e. the bridge package.
In short, we copy Samsung’s signature from AODService.apk and create an APK that will act as a bridge; this APK is granted the `BIND_GENUI_SERVICE` permission. Without this permission, Now Brief won’t appear in Now Bar or AOD.
Run `GenUIBrigde.py` then install GenUIBridge.apk to device.

Finally NowBarItemManager has restarted; since `BIND_GENUI_SERVIC`E now has `granted=true` for `uid=10048`, it has connected to GenUIService, and a Now Brief card has appeared on the Now Bar on the lock screen.










