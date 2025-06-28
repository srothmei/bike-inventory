#!/usr/bin/env python3
"""
Test the enhanced barcode detection with generated test images
"""

import cv2
import numpy as np
from PIL import Image
from pyzbar.pyzbar import decode
import os

def test_enhanced_detection(image_path):
    """Test enhanced barcode detection on a test image"""
    print(f"\n🧪 Testing enhanced detection on: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"❌ File not found: {image_path}")
        return False
    
    # Load image like the app does
    image = Image.open(image_path)
    img_array = np.array(image)
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    # Enhanced barcode detection (same as in app)
    barcodes = []
    
    print("  Attempt 1: Original image...")
    barcodes = decode(img_bgr)
    if barcodes:
        print(f"  ✅ Success! Found {len(barcodes)} barcode(s)")
        for barcode in barcodes:
            print(f"    Type: {barcode.type}, Data: {barcode.data.decode('utf-8')}")
        return True
    
    print("  Attempt 2: Grayscale conversion...")
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    barcodes = decode(img_gray)
    if barcodes:
        print(f"  ✅ Success! Found {len(barcodes)} barcode(s)")
        for barcode in barcodes:
            print(f"    Type: {barcode.type}, Data: {barcode.data.decode('utf-8')}")
        return True
    
    print("  Attempt 3: Enhanced contrast...")
    img_enhanced = cv2.convertScaleAbs(img_gray, alpha=1.5, beta=20)
    barcodes = decode(img_enhanced)
    if barcodes:
        print(f"  ✅ Success! Found {len(barcodes)} barcode(s)")
        for barcode in barcodes:
            print(f"    Type: {barcode.type}, Data: {barcode.data.decode('utf-8')}")
        return True
    
    print("  Attempt 4: Different resolutions...")
    for scale in [0.5, 1.5, 2.0]:
        h, w = img_gray.shape
        img_resized = cv2.resize(img_gray, (int(w*scale), int(h*scale)))
        barcodes = decode(img_resized)
        if barcodes:
            print(f"  ✅ Success at {scale}x scale! Found {len(barcodes)} barcode(s)")
            for barcode in barcodes:
                print(f"    Type: {barcode.type}, Data: {barcode.data.decode('utf-8')}")
            return True
    
    print("  ❌ No barcodes detected with any method")
    return False

def run_all_tests():
    """Run tests on all generated test images"""
    print("=== Enhanced Barcode Detection Test ===")
    
    test_files = [
        "test_qr_1_BIKE001.png",
        "test_qr_2_FRAME_XTR_2024.png", 
        "test_qr_3_WHEEL_MAVIC_29ER.png",
        "test_qr_4_BRAKE_SHIMANO_M7120.png",
        "test_qr_5_123456789012.png",
        "test_qr_6_TEST_QR_CODE.png",
        "test_barcode_pattern.png"
    ]
    
    results = []
    for test_file in test_files:
        success = test_enhanced_detection(test_file)
        results.append((test_file, success))
    
    print(f"\n=== Test Results Summary ===")
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for filename, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {filename}")
    
    print(f"\nOverall: {successful}/{total} tests passed ({successful/total*100:.1f}%)")
    
    if successful == total:
        print("🎉 All tests passed! The enhanced barcode detection is working correctly.")
    elif successful > 0:
        print("⚠️  Some tests passed. The barcode detection is working but may need fine-tuning.")
    else:
        print("❌ No tests passed. There may be an issue with the barcode detection setup.")
    
    return successful == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
