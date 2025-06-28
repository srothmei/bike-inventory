#!/usr/bin/env python3
"""
Debug script to test barcode/QR code detection functionality
"""

import cv2
import numpy as np
from PIL import Image
from pyzbar.pyzbar import decode
import sys
import os

def test_barcode_detection():
    """Test if pyzbar and OpenCV are working correctly"""
    print("Testing barcode detection libraries...")
    
    # Test 1: Check if pyzbar is installed and working
    try:
        from pyzbar import pyzbar
        print("✅ pyzbar imported successfully")
    except ImportError as e:
        print(f"❌ pyzbar import failed: {e}")
        return False
    
    # Test 2: Check if OpenCV is working
    try:
        import cv2
        print(f"✅ OpenCV imported successfully (version: {cv2.__version__})")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    # Test 3: Create a simple test image with known QR code
    try:
        # Create a simple test barcode/QR code pattern
        # This creates a basic test pattern that should be detectable
        test_image = np.zeros((200, 200, 3), dtype=np.uint8)
        
        # Add some pattern that might be detected as a barcode
        cv2.rectangle(test_image, (50, 50), (150, 150), (255, 255, 255), -1)
        cv2.rectangle(test_image, (60, 60), (140, 140), (0, 0, 0), -1)
        cv2.rectangle(test_image, (70, 70), (130, 130), (255, 255, 255), -1)
        
        # Try to decode
        barcodes = decode(test_image)
        print(f"Test pattern detection result: {len(barcodes)} codes found")
        
    except Exception as e:
        print(f"❌ Basic detection test failed: {e}")
        return False
    
    return True

def test_image_conversion():
    """Test the image conversion process used in the app"""
    print("\nTesting image conversion process...")
    
    try:
        # Simulate the process used in the app
        # Create a test PIL image
        pil_image = Image.new('RGB', (640, 480), color='white')
        
        # Add some black rectangles to simulate a barcode pattern
        pixels = pil_image.load()
        for x in range(100, 540, 20):
            for y in range(200, 280):
                pixels[x, y] = (0, 0, 0)
        
        # Convert PIL to numpy array (as done in app)
        img_array = np.array(pil_image)
        print(f"✅ PIL to numpy conversion: shape {img_array.shape}")
        
        # Convert RGB to BGR (as done in app)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        print(f"✅ RGB to BGR conversion: shape {img_bgr.shape}")
        
        # Try to decode
        barcodes = decode(img_bgr)
        print(f"Barcode detection result: {len(barcodes)} codes found")
        
        # Also try with grayscale
        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        barcodes_gray = decode(img_gray)
        print(f"Barcode detection (grayscale): {len(barcodes_gray)} codes found")
        
        return True
        
    except Exception as e:
        print(f"❌ Image conversion test failed: {e}")
        return False

def print_detection_info():
    """Print information about detection capabilities"""
    print("\nBarcode/QR code detection information:")
    
    try:
        from pyzbar import pyzbar
        print("Supported barcode types:")
        # pyzbar supports various formats
        supported_formats = [
            "CODE128", "EAN13", "EAN8", "UPC_A", "UPC_E", 
            "CODE39", "CODE93", "CODABAR", "ITF", "QR_CODE",
            "DATA_MATRIX", "PDF417", "AZTEC"
        ]
        for fmt in supported_formats:
            print(f"  - {fmt}")
        
    except Exception as e:
        print(f"Could not get format info: {e}")

if __name__ == "__main__":
    print("=== Barcode Detection Debug Script ===\n")
    
    # Run all tests
    success = True
    success &= test_barcode_detection()
    success &= test_image_conversion()
    print_detection_info()
    
    print(f"\n=== Debug Results ===")
    if success:
        print("✅ All basic tests passed")
        print("\nPossible issues with barcode scanning:")
        print("1. Image quality: Camera images might be too blurry or low resolution")
        print("2. Barcode type: Make sure you're using a supported barcode/QR code format")
        print("3. Barcode size: Code might be too small or too large in the frame")
        print("4. Lighting: Poor lighting can affect detection")
        print("5. Contrast: Low contrast between code and background")
        print("\nRecommendations:")
        print("- Try with high-contrast QR codes")
        print("- Ensure good lighting")
        print("- Hold the camera steady")
        print("- Try different distances from the code")
    else:
        print("❌ Some tests failed - check the library installation")
    
    sys.exit(0 if success else 1)
