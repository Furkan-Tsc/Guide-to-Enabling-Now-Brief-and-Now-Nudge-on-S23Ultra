# Guide-to-Enabling-Now-Brief-and-Now-Nudge-on-S23Ultra
This document enables the full activation of the Now Brief, Now Nudge, Widget, Galaxy AI, and Now Bar features on the Samsung Galaxy S23 Ultra (SM-S918B - One UI 8.5, August Patch).

# Requirements
Soft Root (Using Root My Galaxy) <br />
LSPosed / Vector (with ZygiskNext) <br />
CorePatch (4.9) module (signature verification and version downgrading patches enabled) <br />
Termux <br />

### Step 1: Bypassing the APK Installation Block
Samsung One UI 8.5 prevents the external updating or downgrading of the `com.samsung.android.smartsuggestions` package, resulting in the error: `-3001: INSTALL_FAILED_REJECTED_BY_BUILDTYPE`. <br />
Download the Samsung Smart Suggestions 7.3.30.9 (latest) APK from APKMirror. <br />
Then push apk with this adb command (or u can do it with termux):  <br />

```bash
adb push "C:\com.samsung.android.smartsuggestions_7.3.30.9-733009000_minAPI34(arm64-v8a)(nodpi)_apkmirror.com.apk" /data/local/tmp/sss.apk
```

### Step 2: Installing the APK by Disabling the Build Type Check

By setting the `ro.build.official.release` property to `false` in RAM, we unlock Samsung's "-3001" restriction and install the APK.

Run in termux.

```bash
su -mm -c '
chmod 644 /data/local/tmp/sss.apk
/data/local/tmp/resetprop ro.build.official.release false
SIZE=$(stat -c%s /data/local/tmp/sss.apk)
cat /data/local/tmp/sss.apk | pm install -r -d -i com.sec.android.app.samsungapps -S $SIZE
'
```

### Step 3: Enabling the Now Brief, Widget, Galaxy AI, and Now Nudge Features
Okay now we have latest Smart Suggestions but most of the features are locked.<br />
To enable the "Now Brief" and "Now Nudge" features, Settings and Smart Suggestions checks for specific tags located in `/system/etc/floating_feature.xml`.

To avoid tripping Knox, we do not physically modify the `/system` partition; instead, we create an edited copy of the file at `/data/local/tmp/ff_s23.xml` and mount it over the original system file using `mount --bind`.

For these run this command block in termux.

```bash
su -mm -c '
umount -l /system/etc/floating_feature.xml 2>/dev/null
cp /system/etc/floating_feature.xml /data/local/tmp/ff_s23.xml

sed -i "s/<SEC_FLOATING_FEATURE_COMMON_CONFIG_AI_VERSION>.*<\/SEC_FLOATING_FEATURE_COMMON_CONFIG_AI_VERSION>/<SEC_FLOATING_FEATURE_COMMON_CONFIG_AI_VERSION>20263<\/SEC_FLOATING_FEATURE_COMMON_CONFIG_AI_VERSION>/g" /data/local/tmp/ff_s23.xml
sed -i "/SEC_FLOATING_FEATURE_FRAMEWORK_SUPPORT_PERSONALIZED_DATA_CORE/d" /data/local/tmp/ff_s23.xml
sed -i "/SEC_FLOATING_FEATURE_FRAMEWORK_SUPPORT_AI_BRIEF_FOR_UT/d" /data/local/tmp/ff_s23.xml
sed -i "/SEC_FLOATING_FEATURE_FRAMEWORK_SUPPORT_NOW_BRIEF/d" /data/local/tmp/ff_s23.xml
sed -i "/SEC_FLOATING_FEATURE_FRAMEWORK_CONFIG_NOW_NUDGE_VERSION/d" /data/local/tmp/ff_s23.xml
sed -i "/SEC_FLOATING_FEATURE_GENAI_CONFIG_LLM_VERSION/d" /data/local/tmp/ff_s23.xml
sed -i "s/<\/SecFloatingFeatureSet>/    <SEC_FLOATING_FEATURE_FRAMEWORK_SUPPORT_PERSONALIZED_DATA_CORE>TRUE<\/SEC_FLOATING_FEATURE_FRAMEWORK_SUPPORT_PERSONALIZED_DATA_CORE>\n    <SEC_FLOATING_FEATURE_FRAMEWORK_SUPPORT_AI_BRIEF_FOR_UT>TRUE<\/SEC_FLOATING_FEATURE_FRAMEWORK_SUPPORT_AI_BRIEF_FOR_UT>\n    <SEC_FLOATING_FEATURE_FRAMEWORK_SUPPORT_NOW_BRIEF>TRUE<\/SEC_FLOATING_FEATURE_FRAMEWORK_SUPPORT_NOW_BRIEF>\n    <SEC_FLOATING_FEATURE_FRAMEWORK_CONFIG_NOW_NUDGE_VERSION>2<\/SEC_FLOATING_FEATURE_FRAMEWORK_CONFIG_NOW_NUDGE_VERSION>\n    <SEC_FLOATING_FEATURE_GENAI_CONFIG_LLM_VERSION>1.70<\/SEC_FLOATING_FEATURE_GENAI_CONFIG_LLM_VERSION>\n<\/SecFloatingFeatureSet>/" /data/local/tmp/ff_s23.xml

chmod 644 /data/local/tmp/ff_s23.xml
chcon u:object_r:system_file:s0 /data/local/tmp/ff_s23.xml
mount --bind /data/local/tmp/ff_s23.xml /system/etc/floating_feature.xml

/data/local/tmp/resetprop ro.build.official.release false

settings put global sss_enabled 1
settings put global nowbrief_enabled 1
settings put global smart_suggestions_enabled 1
settings put global now_nudge_enabled 1

pm enable com.samsung.android.smartsuggestions/.settings.about.developermode.DeveloperModeActivity
pm enable com.samsung.android.smartsuggestions/.feature.aisuggestion.ui.activity.SuggestionUiContentActivity
pm enable com.samsung.android.smartsuggestions/.feature.aisuggestion.ui.appwidget.AiSuggestionAppWidgetReceiver
pm enable com.samsung.android.smartsuggestions/.feature.aisuggestion.ui.onboarding.OnboardingActivity
pm enable com.samsung.android.smartsuggestions/.brief.BriefSettingsActivity
pm enable com.samsung.android.smartsuggestions/.brief.BriefCustomCardManageActivity
pm enable com.samsung.android.smartsuggestions/.brief.EditableCardActivity
pm enable com.samsung.android.smartsuggestions/.brief.CustomCardCreateActivity
pm enable com.samsung.android.smartsuggestions/.nudge.settings.NudgeMainSettingsActivity

setprop ctl.restart zygote
'
```

This command block does the following:<br />

1. Copies the file `/system/etc/floating_feature.xml` to `/data/local/tmp/ff_s23.xml`.<br />
2. Upgrades the AI ​​version from 20253 to 20263.<br />
3. Adds the following tags: Personal Data Core (PDE), Now Brief, AI Brief For UT, Now Nudge Version (2), and LLM Version (1.70).<br />
4. Sets the file permissions and the SELinux label (u:object_r:system_file:s0), then mounts it over /system/etc/floating_feature.xml using `mount --bind`.<br />
5. Enables the global database keys: `nowbrief_enabled`, `sss_enabled`, `smart_suggestions_enabled`, and `now_nudge_enabled`.<br />
6. Activates all hidden Now Brief, Widget, and Now Nudge components using `pm enable`.<br />
7. Performs a soft reboot via `setprop ctl.restart zygote`, ensuring that the SemFloatingFeature RAM cache is reloaded with the new values ​​across the entire system (Settings, SystemUI, AODService, SmartSuggestions).<br />

Smart Suggestions and Settings contain the following controls:<br />

| Control Flag | Class / Method | Searching `floating_feature.xml` Tag / Condition | Original Value | Required Value |
| :--- | :--- | :--- | :--- | :--- |
| **General AI Version** | `Rune.COMMON_CONFIG_AI_VERSION` | `SEC_FLOATING_FEATURE_COMMON_CONFIG_AI_VERSION` | `20253` | **`20263`** |
| **Personal Data Engine (PDE)** | `Rune.SUPPORT_PERSONAL_DATA_ENGINE` | `SEC_FLOATING_FEATURE_FRAMEWORK_SUPPORT_PERSONALIZED_DATA_CORE` | `FALSE` | **`TRUE`** |
| **Now Brief Cards & Settings** | `App.NOW_BRIEF.isPossibleToExpose()` | `SUPPORT_AI_SUGGESTION_UI` and `SUPPORT_PERSONAL_DATA_ENGINE` | `false` | **`true`** |
| **Now Brief UT Support** | `Rune.SUPPORT_AI_BRIEF_FOR_UT` | `SEC_FLOATING_FEATURE_FRAMEWORK_SUPPORT_AI_BRIEF_FOR_UT` | No Value (`FALSE`) | **`TRUE`** |
| **Now Nudge Feature** | `Rune.SUPPORT_NOW_NUDGE` | `SEC_FLOATING_FEATURE_FRAMEWORK_CONFIG_NOW_NUDGE_VERSION` > 0 | No Value (`""`) | **`2`** |
| **Galaxy AI > Now Nudge Menu** | `NowNudgesGalaxyAIController` | `SEC_FLOATING_FEATURE_GENAI_CONFIG_LLM_VERSION` | No Value | **`1.70`** |

### Persistence Status: What Happens When the Phone Is Restarted (Rebooted)?

`mount --bind /data/local/tmp/ff_s23.xml /system/etc/floating_feature.xml`:
To avoid tripping Knox we used a bind-mount instead of physically writing to the `/system` partition. <br />
When the phone is restarted (a hardware reboot) this bind-mount is removed and the device reverts to the original `/system/etc/floating_feature.xml` file.<br />
You need to re-obtain soft root after a restart. Since the file `/data/local/tmp/ff_s23.xml` is already prepared just run this command block on termux:<br />

```bash
su -mm -c '
mount --bind /data/local/tmp/ff_s23.xml /system/etc/floating_feature.xml
setprop ctl.restart zygote
'
```

#### Finally you have these features enjoy them!

<img width="720" height="1482" alt="Screenshot_20261030_231737_Personal data intelligence" src="https://github.com/user-attachments/assets/2cf83b55-a197-4a5e-8ddb-e954822797d9" />
<img width="720" height="1482" alt="Screenshot_20261030_231813_AlwaysOnDisplay" src="https://github.com/user-attachments/assets/b5bf59a0-165b-4064-b5d3-d7616c0e79ba" />
<img width="720" height="1482" alt="Screenshot_20261030_230540_Settings" src="https://github.com/user-attachments/assets/e611e198-5c0f-4a6f-aa76-9ddce998bd6d" />
