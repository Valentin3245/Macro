[app]
title = Macro Vision AI
package.name = macrovisionai
package.domain = com.macrovision

source.dir = .
source.include_exts = py,png,jpg,json

version = 1.0.0

# SEM PILLOW - só Kivy básico
requirements = python3,kivy,pyjnius,android

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

android.accept_sdk_license = True

android.presplash_color = #0a0a1a

orientation = portrait
fullscreen = 0

android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 0
