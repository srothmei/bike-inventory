#!/usr/bin/env python3
"""
Generate real barcodes in formats that pyzbar can detect
"""

import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import qrcode
import os

def create_real_barcodes():
    """Create real barcodes in various formats"""
    print("Creating real barcodes...")
    
    # Test data
    test_codes = [
        ("123456789012", "EAN13", "ean13"),      # EAN-13 format
        ("1234567890128", "EAN13", "ean13"),     # Another EAN-13 
        ("12345678", "CODE39", "code39"),        # Code 39
        ("BIKE001", "CODE39", "code39"),         # Code 39 with letters
        ("123456789012", "CODE128", "code128"),  # Code 128
        ("FRAME-001", "CODE128", "code128"),     # Code 128 with text
    ]
    
    created_files = []
    
    for data, barcode_name, barcode_type in test_codes:
        try:
            print(f"Creating {barcode_name} barcode: {data}")
            
            # Get the barcode class
            code_class = barcode.get_barcode_class(barcode_type)
            
            # Create the barcode
            code = code_class(data, writer=ImageWriter())
            
            # Save the barcode
            filename = f"real_barcode_{barcode_type}_{data.replace('-', '_')}"
            filepath = code.save(filename)
            
            # The save method returns the full path with extension
            print(f"  Created: {filepath}")
            created_files.append(filepath)
            
        except Exception as e:
            print(f"  ❌ Failed to create {barcode_name} with data '{data}': {e}")
    
    return created_files

def create_mixed_test_codes():
    """Create a mix of QR codes and barcodes for comprehensive testing"""
    print("\nCreating mixed QR codes and barcodes...")
    
    # QR codes
    qr_data = [
        "BIKE-QR-001",
        "https://example.com/bike/12345",
        "FRAME:XTR-2024:SIZE:L"
    ]
    
    for i, data in enumerate(qr_data):
        qr = qrcode.QRCode(version=1, box_size=8, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        filename = f"mixed_qr_{i+1}_{data[:10].replace(':', '_').replace('/', '_')}.png"
        qr_img.save(filename)
        print(f"  Created QR: {filename}")

def test_barcode_detection(filepath):
    """Test if a barcode can be detected"""
    try:
        from pyzbar.pyzbar import decode
        import cv2
        import numpy as np
        from PIL import Image
        
        print(f"\n🧪 Testing detection: {filepath}")
        
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            return False
        
        # Load and process image
        image = Image.open(filepath)
        img_array = np.array(image)
        
        # Convert to BGR if needed
        if len(img_array.shape) == 3:
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        else:
            img_bgr = img_array
        
        # Test detection
        barcodes = decode(img_bgr)
        if barcodes:
            for barcode in barcodes:
                print(f"  ✅ {barcode.type} detected: {barcode.data.decode('utf-8')}")
            return True
        else:
            # Try grayscale
            if len(img_array.shape) == 3:
                img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
                barcodes = decode(img_gray)
                if barcodes:
                    for barcode in barcodes:
                        print(f"  ✅ {barcode.type} detected (grayscale): {barcode.data.decode('utf-8')}")
                    return True
            
            print(f"  ❌ No barcode detected")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing {filepath}: {e}")
        return False

if __name__ == "__main__":
    print("=== Real Barcode Generator ===\n")
    
    # Create real barcodes
    barcode_files = create_real_barcodes()
    
    # Create mixed test codes
    create_mixed_test_codes()
    
    print(f"\n=== Testing Detection ===")
    
    # Test each created barcode
    success_count = 0
    total_count = len(barcode_files)
    
    for filepath in barcode_files:
        if test_barcode_detection(filepath):
            success_count += 1
    
    print(f"\n=== Results ===")
    print(f"Successfully detected: {success_count}/{total_count} barcodes")
    
    if success_count == total_count:
        print("🎉 All barcodes can be detected!")
    elif success_count > 0:
        print("⚠️  Some barcodes detected - may need format adjustments")
    else:
        print("❌ No barcodes detected - check barcode generation")
    
    print(f"\n📁 Generated files:")
    for filepath in barcode_files:
        print(f"  - {filepath}")
    
    print(f"\n💡 Use these files to test barcode scanning in the app!")
