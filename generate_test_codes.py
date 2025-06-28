#!/usr/bin/env python3
"""
Generate test QR codes and barcodes for testing the bike inventory scanner
"""

import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

def create_test_qr_codes():
    """Create test QR codes for bike inventory testing"""
    
    # Test data for bike parts
    test_data = [
        "BIKE001",
        "FRAME-XTR-2024",
        "WHEEL-MAVIC-29ER",
        "BRAKE-SHIMANO-M7120",
        "123456789012",  # Standard barcode format
        "TEST-QR-CODE"
    ]
    
    print("Creating test QR codes...")
    
    for i, data in enumerate(test_data):
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Create a larger image with label
        final_img = Image.new('RGB', (300, 350), 'white')
        
        # Paste QR code
        qr_resized = qr_img.resize((250, 250))
        final_img.paste(qr_resized, (25, 25))
        
        # Add text label
        draw = ImageDraw.Draw(final_img)
        try:
            # Try to use a nice font, fallback to default if not available
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
            except:
                font = ImageFont.load_default()
        
        # Calculate text position to center it
        try:
            text_bbox = draw.textbbox((0, 0), data, font=font)
            text_width = text_bbox[2] - text_bbox[0]
        except:
            text_width = len(data) * 8  # Fallback estimate
        
        text_x = max(0, (300 - text_width) // 2)
        
        draw.text((text_x, 290), data, fill="black", font=font)
        
        # Save the image
        filename = f"test_qr_{i+1}_{data.replace('-', '_').replace(' ', '_')}.png"
        final_img.save(filename)
        print(f"Created: {filename}")
    
    print(f"\n✅ Created {len(test_data)} test QR codes")
    print("\nTo test:")
    print("1. Open the bike inventory app at http://localhost:8501")
    print("2. Go to 'Add New Item' tab")
    print("3. Click 'Scan Barcode'")
    print("4. Take a photo of one of the generated QR code images on your screen")
    print("5. The barcode should be detected automatically")

def create_simple_barcode():
    """Create a simple barcode pattern for testing"""
    print("\nCreating simple barcode pattern...")
    
    # Create a simple Code 128-style pattern
    img = Image.new('RGB', (400, 150), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw vertical bars to simulate a barcode
    x = 50
    bars = [3, 1, 2, 1, 1, 2, 3, 1, 2, 2, 1, 1, 3, 2, 1, 1, 2, 3, 1, 2]
    
    for bar_width in bars:
        draw.rectangle([x, 30, x + bar_width * 2, 90], fill='black')
        x += bar_width * 2 + 1
    
    # Add text
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        except:
            font = ImageFont.load_default()
    
    draw.text((120, 100), "123456789012", fill="black", font=font)
    
    img.save("test_barcode_pattern.png")
    print("Created: test_barcode_pattern.png")

if __name__ == "__main__":
    print("=== QR Code & Barcode Generator for Testing ===\n")
    
    create_test_qr_codes()
    create_simple_barcode()
    
    print(f"\n=== Files created in current directory ===")
    print("You can now test the barcode scanner with these images!")
    print("\nTips for testing:")
    print("- Display the QR codes on your computer screen")
    print("- Use your phone/camera to scan them through the web app")
    print("- Try different lighting conditions")
    print("- Test both QR codes and barcodes")
