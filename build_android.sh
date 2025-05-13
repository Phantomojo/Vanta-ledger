#!/bin/bash
export ANDROID_HOME=$HOME/.buildozer/android/platform/android-sdk
export ANDROID_SDK_ROOT=$HOME/.buildozer/android/platform/android-sdk
export PATH=$ANDROID_HOME/build-tools/33.0.0:$PATH
buildozer android debug
