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

orientation = portrait


# ==========================================
# PYTHON / KIVY
# ==========================================

requirements = python3,kivy,cryptography


# ==========================================
# ANDROID
# ==========================================

android.api = 33

android.minapi = 21

android.ndk_api = 21

android.ndk = 25b


# ==========================================
# ARCHITECTURES
# ==========================================

android.archs = arm64-v8a


# ==========================================
# PERMISSIONS
# ==========================================

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE


# ==========================================
# PYTHON-FOR-ANDROID
# ==========================================

p4a.branch = v2024.01.21

p4a.commit = 957a3e5

p4a.bootstrap = sdl2


# ==========================================
# BUILDOZER
# ==========================================

[buildozer]

log_level = 2

warn_on_root = 0
