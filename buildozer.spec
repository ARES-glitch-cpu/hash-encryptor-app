[app]

# ==========================================
# APPLICATION
# ==========================================

title = Hash Encryptor

package.name = hashapp

package.domain = org.myapp

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,atlas

version = 1.0


# ==========================================
# PYTHON REQUIREMENTS
# ==========================================

requirements = python3,kivy,cryptography


# ==========================================
# DISPLAY
# ==========================================

orientation = portrait


# ==========================================
# ANDROID
# ==========================================

android.api = 33

android.minapi = 21

android.ndk_api = 21

android.ndk = 25b

android.archs = arm64-v8a,armeabi-v7a


# ==========================================
# PERMISSIONS
# ==========================================

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE


# ==========================================
# BOOTSTRAP
# ==========================================

p4a.bootstrap = sdl2

p4a.branch = master


# ==========================================
# GRADLE
# ==========================================

android.gradle_dependencies = com.android.tools.build:gradle:7.4.2


# ==========================================
# BUILDOZER
# ==========================================

[buildozer]

log_level = 2

warn_on_root = 0
