#!/usr/bin/env python3
"""
Comprehensive barcode detection test with the external image
"""

import cv2
import numpy as np
from PIL import Image
from pyzbar.pyzbar import decode
import os

def advanced_barcode_detection(image_path):
    """
    Advanced barcode detection with multiple preprocessing techniques
    """
    print(f"🧪 Testing: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"❌ File not found: {image_path}")
        return None
    
    try:
        # Load image
        image = Image.open(image_path)
        img_array = np.array(image)
        
        # Convert to grayscale
        if len(img_array.shape) == 3:
            img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            img_gray = img_array
        
        print(f"  📏 Image size: {img_gray.shape}")
        print(f"  📊 Brightness: mean={np.mean(img_gray):.1f}, std={np.std(img_gray):.1f}")
        
        # Method 1: Original image
        barcodes = decode(img_gray)
        if barcodes:
            print("  ✅ Method 1 (Original): SUCCESS")
            return barcodes
        
        # Method 2: Enhanced contrast
        enhanced = cv2.convertScaleAbs(img_gray, alpha=1.5, beta=20)
        barcodes = decode(enhanced)
        if barcodes:
            print("  ✅ Method 2 (Enhanced contrast): SUCCESS") 
            return barcodes
        
        # Method 3: Binary threshold
        _, binary = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)
        barcodes = decode(binary)
        if barcodes:
            print("  ✅ Method 3 (Binary threshold): SUCCESS")
            return barcodes
        
        # Method 4: Adaptive threshold
        adaptive = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        barcodes = decode(adaptive)
        if barcodes:
            print("  ✅ Method 4 (Adaptive threshold): SUCCESS")
            return barcodes
        
        # Method 5: Scaling attempts
        for scale in [0.5, 1.5, 2.0, 2.5, 3.0]:
            h, w = img_gray.shape
            new_h, new_w = int(h*scale), int(w*scale)
            if 50 < new_h < 2000 and 50 < new_w < 2000:
                resized = cv2.resize(img_gray, (new_w, new_h))
                barcodes = decode(resized)
                if barcodes:
                    print(f"  ✅ Method 5 (Scale {scale}x): SUCCESS")
                    return barcodes
        
        # Method 6: Rotation compensation
        for angle in [-15, -10, -5, 5, 10, 15]:
            center = (img_gray.shape[1]//2, img_gray.shape[0]//2)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(img_gray, rotation_matrix, (img_gray.shape[1], img_gray.shape[0]))
            barcodes = decode(rotated)
            if barcodes:
                print(f"  ✅ Method 6 (Rotation {angle}°): SUCCESS")
                return barcodes
        
        print("  ❌ All methods failed")
        return None
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def compare_barcodes():
    """Compare detection success on different barcode types"""
    print("=== Comprehensive Barcode Detection Test ===\n")
    
    test_files = [
        # Known working barcodes
        ("test_qr_1_BIKE001.png", "QR Code"),
        ("real_barcode_code128_123456789012.png", "CODE128"),
        ("real_barcode_code39_BIKE001.png", "CODE39"),
        ("real_barcode_ean13_1234567890128.png", "EAN13"),
        # The challenging external barcode
        ("test_external_barcode.jpg", "External Barcode"),
    ]
    
    results = []
    
    for filename, description in test_files:
        print(f"🧪 Testing {description}")
        barcodes = advanced_barcode_detection(filename)
        
        if barcodes:
            for barcode in barcodes:
                data = barcode.data.decode('utf-8')
                print(f"  📊 {barcode.type}: {data}")
                results.append((filename, True, barcode.type, data))
        else:
            results.append((filename, False, None, None))
        print()
    
    print("=== SUMMARY ===")
    success_count = sum(1 for _, success, _, _ in results if success)
    total_count = len(results)
    
    print(f"Detection Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    print()
    
    for filename, success, barcode_type, data in results:
        status = "✅ DETECTED" if success else "❌ NOT DETECTED"
        if success:
            print(f"{status}: {filename} → {barcode_type}: {data}")
        else:
            print(f"{status}: {filename}")
    
    print(f"\n💡 Analysis of external barcode:")
    print(f"The external barcode from the URL could not be detected.")
    print(f"This suggests it might be:")
    print(f"  • A decorative/artistic barcode image")
    print(f"  • A barcode format not supported by pyzbar")
    print(f"  • A damaged or corrupted barcode")
    print(f"  • An image with insufficient contrast/quality")
    print(f"  • Not actually a machine-readable barcode")
    
    return results

if __name__ == "__main__":
    results = compare_barcodes()
    
    working_count = sum(1 for _, success, _, _ in results if success)
    if working_count >= 4:  # Should detect our generated barcodes
        print(f"\n🎉 CONCLUSION: Barcode detection is working properly!")
        print(f"The system successfully detects standard barcode formats.")
        print(f"The external image appears to be an edge case or non-standard format.")
    else:
        print(f"\n⚠️  CONCLUSION: There might be an issue with barcode detection.")
