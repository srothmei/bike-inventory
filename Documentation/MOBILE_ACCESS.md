# 📱 Mobile Access Guide for Bike Inventory App

This guide explains how to access the Bike Inventory app from mobile devices, with special attention to iOS.

## 📋 Table of Contents
- [🌐 Basic Access](#-basic-access)
- [🍎 iOS-Specific Setup](#-ios-specific-setup)
  - [Add to Home Screen](#add-to-home-screen)
  - [Camera Access](#camera-access)
  - [Troubleshooting Camera Issues](#troubleshooting-camera-issues)
- [🤖 Android-Specific Setup](#-android-specific-setup)
- [🔒 Secure Access (HTTPS)](#-secure-access-https)
- [❓ Troubleshooting Connectivity](#-troubleshooting-connectivity)

## 🌐 Basic Access

1. **🔍 Find Server IP**: Determine the IP address of the computer/server running the application.

   On Linux/macOS run:
   ```bash
   ifconfig
   ```
   
   On Windows run:
   ```
   ipconfig
   ```

2. **🌍 Access the app**: Open a browser on your mobile device and navigate to:
   ```
   http://SERVER_IP:8501
   ```
   Replace `SERVER_IP` with the IP address from step 1.

## 🍎 iOS-Specific Setup

### 📲 Add to Home Screen

For quick access on iOS, add the app to your home screen:

1. Open Safari and navigate to the app URL
2. Tap the Share button (rectangle with up arrow)
3. Scroll down and tap "Add to Home Screen"
4. Name your app and tap "Add"

This creates an icon on your home screen that launches the app in full-screen mode.

### 📷 Camera Access

When using the app on iOS:

1. 🧭 Use Safari browser (recommended) as it has better camera integration
2. 🔔 When prompted, allow camera access
3. 🚫 If camera access is denied:
   - 🔧 Go to Settings > Safari > Camera
   - ✅ Change the setting to "Allow"

### 🔧 Troubleshooting Camera Issues

If you experience camera issues on iOS:

1. **🔒 Ensure HTTPS**: Camera access works more reliably over HTTPS (use the secure deployment option)
2. **🔍 Check Camera Permissions**: Go to Settings > Safari > Camera
3. **🔄 Update iOS**: Make sure your iOS version is up to date
4. **📱 Try Different Orientation**: Sometimes rotating the device helps
5. **🧹 Clear Safari Cache**: Go to Settings > Safari > Clear History and Website Data

## 🤖 Android-Specific Setup

Android devices generally work without special configuration. However:

1. **🌐 Chrome Recommended**: Use Chrome for best compatibility
2. **📲 Add to Home Screen**:
   - 🔍 Open Chrome and navigate to the app
   - ⋮ Tap the menu (three dots)
   - ➕ Select "Add to Home screen"

## 🔒 Secure Access (HTTPS)

For better camera access and security, use the HTTPS deployment option:

1. 📝 Follow the "HTTPS Deployment" section in the DOCKER_DEPLOYMENT.md file
2. 🌍 Access the app using:
   ```
   https://SERVER_IP
   ```

## ❓ Troubleshooting Connectivity

If you can't connect to the app:

1. **🧱 Check Firewall**: Make sure port 8501 (or 80/443 for HTTPS) is allowed
2. **📡 Same Network**: Ensure your mobile device is on the same network as the server
3. **🏃‍♂️ Server Running**: Make sure the Docker container is running
   ```bash
   docker ps | grep bike-inventory
   ```
4. **📊 Check Logs**: View logs for potential errors
   ```bash
   docker-compose logs -f
   ```
