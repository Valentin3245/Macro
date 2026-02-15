[app]
title = Macro Vision AI
package.name = macrovisionai
package.domain = com.macrovision

source.dir = .
source.include_exts = py,png,jpg,json,txt

version = 3.0.0

requirements = python3,kivy,pyjnius,android

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET,FOREGROUND_SERVICE,SYSTEM_ALERT_WINDOW

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

android.accept_sdk_license = True

presplash.filename =
android.presplash_color = #0a0a14

orientation = portrait
fullscreen = 0

android.allow_backup = True
android.wakelock = True

[buildozer]
log_level = 2
warn_on_root = 0