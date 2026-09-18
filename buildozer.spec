[app]

title = Hash Encryptor
package.name = hashapp
package.domain = org.myapp

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas

version = 1.0
orientation = portrait

requirements = python3,kivy,cryptography==42.0.8

android.api = 33
android.minapi = 21
android.ndk_api = 21
android.ndk = 25b

android.archs = arm64-v8a,armeabi-v7a

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

p4a.bootstrap = sdl2
p4a.branch = master
p4a.commit = 58d21141


[buildozer]

log_level = 2
warn_on_root = 0
