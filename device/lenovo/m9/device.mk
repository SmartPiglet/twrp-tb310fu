# Copyright (C) 2025 The Android Open Source Project
# Copyright (C) 2025 SebaUbuntu's TWRP device tree generator
#
# SPDX-License-Identifier: Apache-2.0
#

LOCAL_PATH := device/lenovo/m9

# A/B OTA configuration
AB_OTA_POSTINSTALL_CONFIG += \
    RUN_POSTINSTALL_system=true \
    POSTINSTALL_PATH_system=system/bin/otapreopt_script \
    FILESYSTEM_TYPE_system=ext4 \
    POSTINSTALL_OPTIONAL_system=true

# Boot control HAL
PRODUCT_PACKAGES += \
    android.hardware.boot@1.0-impl-1.2-mtkimpl \
    bootctrl.mt6768.recovery

# Health HAL
PRODUCT_PACKAGES += \
    android.hardware.health@2.0-impl-2.1 \
    android.hardware.health@2.0-impl-default \
    libhealthd.mt6768

# Fastboot HAL
PRODUCT_PACKAGES += \
    android.hardware.fastboot@1.0-impl-mtk \
    fastbootd

# OTA and recovery utilities
PRODUCT_PACKAGES += \
    otapreopt_script \
    cppreopts.sh \
    update_engine \
    update_verifier \
    update_engine_sideload

# Additional libraries
PRODUCT_PACKAGES += \
    libgptutils \
    libz \
    libcutils
