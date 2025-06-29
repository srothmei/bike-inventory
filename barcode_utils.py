#!/usr/bin/env python3
"""
Enhanced barcode detection utilities for real-world camera images
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from pyzbar.pyzbar import decode
import logging

# Try to import pillow-heif for HEIC support
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORT = True
except ImportError:
    HEIC_SUPPORT = False
    logging.warning("pillow-heif not available. HEIC files may not be supported.")

def load_image_safely(image_input):
    """
    Safely load an image from various input types including HEIC files
    
    Args:
        image_input: PIL Image, file path, or uploaded file object
        
    Returns:
        PIL Image object or None if failed
    """
    try:
        if isinstance(image_input, Image.Image):
            return image_input
        elif hasattr(image_input, 'read'):
            # File-like object (uploaded file)
            return Image.open(image_input)
        else:
            # File path
            return Image.open(image_input)
    except Exception as e:
        logging.error(f"Error loading image: {e}")
        return None

def preprocess_iphone_image(image):
    """
    Special preprocessing for iPhone photos to improve barcode detection
    
    Args:
        image: PIL Image
        
    Returns:
        PIL Image: Preprocessed image
    """
    # Convert to RGB if necessary
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # iPhone photos are often very high resolution - resize if too large
    max_dimension = 2000
    if max(image.size) > max_dimension:
        ratio = max_dimension / max(image.size)
        new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
        image = image.resize(new_size, Image.LANCZOS)
    
    # Apply slight sharpening for iPhone photos which may be slightly soft
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.2)
    
    # Enhance contrast slightly
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.1)
    
    return image

def enhanced_barcode_detection(image_input, debug=False):
    """
    Enhanced barcode detection with multiple preprocessing techniques
    optimized for real-world camera images like iPhone photos.
    
    Args:
        image_input: PIL Image, file path, or uploaded file object
        debug: If True, returns detailed processing information
    
    Returns:
        tuple: (barcodes_found, detection_method, processed_images_tried)
    """
    
    # Safely load the image
    image = load_image_safely(image_input)
    if image is None:
        return [], "Failed to load image", []
    
    # Special preprocessing for iPhone images
    image = preprocess_iphone_image(image)
    
    # Convert to numpy array
    img_array = np.array(image)
    
    # Convert to BGR and grayscale
    if len(img_array.shape) == 3:
        if img_array.shape[2] == 4:  # RGBA
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = img_array
        img_bgr = img_array
    
    if debug:
        print(f"Preprocessed image shape: {img_array.shape}")
        print(f"Mean brightness: {np.mean(img_gray):.1f}")
    
    detection_methods = []
    
    # Method 1: Original image (both BGR and grayscale)
    barcodes = decode(img_bgr)
    if barcodes:
        return barcodes, "Original BGR", detection_methods if debug else None
    
    barcodes = decode(img_gray)
    if barcodes:
        return barcodes, "Original grayscale", detection_methods if debug else None
    
    # Method 2: Histogram equalization (improves contrast in poor lighting)
    img_eq = cv2.equalizeHist(img_gray)
    barcodes = decode(img_eq)
    if barcodes:
        return barcodes, "Histogram equalization", detection_methods if debug else None
    
    # Method 3: CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    img_clahe = clahe.apply(img_gray)
    barcodes = decode(img_clahe)
    if barcodes:
        return barcodes, "CLAHE enhancement", detection_methods if debug else None
    
    # Method 4: Enhanced contrast with multiple parameters
    for alpha, beta in [(1.5, 20), (2.0, 30), (2.5, 40), (1.2, 10)]:
        img_enhanced = cv2.convertScaleAbs(img_gray, alpha=alpha, beta=beta)
        barcodes = decode(img_enhanced)
        if barcodes:
            return barcodes, f"Enhanced contrast (α={alpha}, β={beta})", detection_methods if debug else None
    
    # Method 5: Gaussian blur to reduce noise
    img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)
    barcodes = decode(img_blur)
    if barcodes:
        return barcodes, "Gaussian blur", detection_methods if debug else None
    
    # Method 6: Median filter to remove salt-and-pepper noise
    img_median = cv2.medianBlur(img_gray, 3)
    barcodes = decode(img_median)
    if barcodes:
        return barcodes, "Median filter", detection_methods if debug else None
    
    # Method 7: Morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    img_morph = cv2.morphologyEx(img_gray, cv2.MORPH_CLOSE, kernel)
    barcodes = decode(img_morph)
    if barcodes:
        return barcodes, "Morphological closing", detection_methods if debug else None
    
    # Method 8: Multiple threshold methods
    threshold_methods = [
        (cv2.THRESH_BINARY, "Binary"),
        (cv2.THRESH_BINARY_INV, "Binary inverted"),
        (cv2.THRESH_TOZERO, "To zero"),
        (cv2.THRESH_TOZERO_INV, "To zero inverted")
    ]
    
    for thresh_type, method_name in threshold_methods:
        _, img_thresh = cv2.threshold(img_gray, 127, 255, thresh_type)
        barcodes = decode(img_thresh)
        if barcodes:
            return barcodes, f"Threshold ({method_name})", detection_methods if debug else None
    
    # Method 9: Adaptive threshold with different parameters
    adaptive_methods = [
        (cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2, "Mean adaptive"),
        (cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2, "Gaussian adaptive"),
        (cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 5, "Mean adaptive (15,5)"),
        (cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 5, "Gaussian adaptive (15,5)"),
        (cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 21, 10, "Mean adaptive (21,10)"),
    ]
    
    for adaptive_method, thresh_type, block_size, C, method_name in adaptive_methods:
        img_adaptive = cv2.adaptiveThreshold(img_gray, 255, adaptive_method, thresh_type, block_size, C)
        barcodes = decode(img_adaptive)
        if barcodes:
            return barcodes, f"Adaptive threshold ({method_name})", detection_methods if debug else None
    
    # Method 10: Multi-scale detection (more scales)
    scales = [0.3, 0.5, 0.7, 1.5, 2.0, 2.5, 3.0, 4.0]
    for scale in scales:
        h, w = img_gray.shape
        new_h, new_w = int(h*scale), int(w*scale)
        if 30 < new_h < 3000 and 30 < new_w < 3000:  # Expanded range
            img_resized = cv2.resize(img_gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
            barcodes = decode(img_resized)
            if barcodes:
                return barcodes, f"Scaling ({scale}x)", detection_methods if debug else None
    
    # Method 11: Rotation compensation (more angles)
    angles = [-15, -10, -5, -2, 2, 5, 10, 15, -20, 20, -30, 30]
    for angle in angles:
        center = (img_gray.shape[1]//2, img_gray.shape[0]//2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        img_rotated = cv2.warpAffine(img_gray, rotation_matrix, (img_gray.shape[1], img_gray.shape[0]))
        barcodes = decode(img_rotated)
        if barcodes:
            return barcodes, f"Rotation ({angle}°)", detection_methods if debug else None
    
    # Method 12: Edge detection + dilation
    edges = cv2.Canny(img_gray, 50, 150)
    kernel = np.ones((2,2), np.uint8)
    img_dilated = cv2.dilate(edges, kernel, iterations=1)
    barcodes = decode(img_dilated)
    if barcodes:
        return barcodes, "Edge detection + dilation", detection_methods if debug else None
    
    # Method 13: Combination techniques - enhance then resize
    for scale in [0.5, 1.5, 2.0]:
        img_enhanced = cv2.convertScaleAbs(img_gray, alpha=2.0, beta=30)
        h, w = img_enhanced.shape
        new_h, new_w = int(h*scale), int(w*scale)
        if 50 < new_h < 2000 and 50 < new_w < 2000:
            img_combo = cv2.resize(img_enhanced, (new_w, new_h))
            barcodes = decode(img_combo)
            if barcodes:
                return barcodes, f"Enhanced + scaling ({scale}x)", detection_methods if debug else None
    
    # Method 14: Bilateral filter (preserves edges while reducing noise)
    img_bilateral = cv2.bilateralFilter(img_gray, 9, 75, 75)
    barcodes = decode(img_bilateral)
    if barcodes:
        return barcodes, "Bilateral filter", detection_methods if debug else None
    
    # Method 15: Unsharp masking
    gaussian = cv2.GaussianBlur(img_gray, (9, 9), 10.0)
    img_unsharp = cv2.addWeighted(img_gray, 1.5, gaussian, -0.5, 0)
    barcodes = decode(img_unsharp)
    if barcodes:
        return barcodes, "Unsharp masking", detection_methods if debug else None
    
    # No barcodes found with any method
    return [], "No detection", detection_methods if debug else None

def ultra_enhanced_barcode_detection(image_input, debug=False):
    """
    Ultra-enhanced barcode detection with even more aggressive preprocessing
    specifically designed for challenging real-world images.
    """
    
    # Safely load the image
    image = load_image_safely(image_input)
    if image is None:
        return [], "Failed to load image", []
    
    # Special preprocessing for iPhone images
    image = preprocess_iphone_image(image)
    
    # Convert to numpy array
    img_array = np.array(image)
    
    # Convert to BGR and grayscale
    if len(img_array.shape) == 3:
        if img_array.shape[2] == 4:  # RGBA
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = img_array
        img_bgr = img_array
    
    if debug:
        print(f"Ultra-enhanced processing: image shape {img_array.shape}")
        print(f"Mean brightness: {np.mean(img_gray):.1f}")
    
    # Store all methods tried for debugging
    methods_tried = []
    
    # Ultra method 1: Extreme scaling variations
    extreme_scales = [0.1, 0.15, 0.2, 0.3, 0.4, 0.6, 0.8, 1.2, 1.8, 2.5, 3.5, 5.0, 7.0, 10.0]
    for scale in extreme_scales:
        h, w = img_gray.shape
        new_h, new_w = int(h * scale), int(w * scale)
        if 20 <= new_h <= 8000 and 20 <= new_w <= 8000:
            try:
                resized = cv2.resize(img_gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
                barcodes = decode(resized)
                methods_tried.append(f"Extreme scale {scale}x")
                if barcodes:
                    return barcodes, f"Extreme scaling ({scale}x)", methods_tried if debug else None
            except Exception as e:
                if debug:
                    print(f"Scale {scale}x failed: {e}")
    
    # Ultra method 2: Extreme rotation variations
    extreme_angles = list(range(-180, 181, 5))  # Every 5 degrees
    for angle in extreme_angles:
        try:
            center = (img_gray.shape[1]//2, img_gray.shape[0]//2)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(img_gray, rotation_matrix, (img_gray.shape[1], img_gray.shape[0]))
            barcodes = decode(rotated)
            methods_tried.append(f"Extreme rotation {angle}°")
            if barcodes:
                return barcodes, f"Extreme rotation ({angle}°)", methods_tried if debug else None
        except Exception as e:
            if debug and angle % 45 == 0:  # Only log every 45 degrees to avoid spam
                print(f"Rotation {angle}° failed: {e}")
    
    # Ultra method 3: Multiple preprocessing combinations
    preprocessing_combinations = [
        # (description, preprocessing_function)
        ("Extreme contrast + blur", lambda img: cv2.GaussianBlur(cv2.convertScaleAbs(img, alpha=5.0, beta=80), (3, 3), 0)),
        ("Histogram eq + unsharp", lambda img: cv2.addWeighted(cv2.equalizeHist(img), 1.5, cv2.GaussianBlur(cv2.equalizeHist(img), (9, 9), 10.0), -0.5, 0)),
        ("CLAHE + median filter", lambda img: cv2.medianBlur(cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8,8)).apply(img), 5)),
        ("Bilateral + adaptive thresh", lambda img: cv2.adaptiveThreshold(cv2.bilateralFilter(img, 15, 80, 80), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 10)),
        ("Morph opening + closing", lambda img: cv2.morphologyEx(cv2.morphologyEx(img, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))),
    ]
    
    for desc, preprocess_func in preprocessing_combinations:
        try:
            processed = preprocess_func(img_gray)
            barcodes = decode(processed)
            methods_tried.append(desc)
            if barcodes:
                return barcodes, desc, methods_tried if debug else None
        except Exception as e:
            if debug:
                print(f"{desc} failed: {e}")
    
    # Ultra method 4: Try on different color channels
    if len(img_array.shape) == 3:
        for i, channel_name in enumerate(['Red', 'Green', 'Blue']):
            try:
                channel = img_array[:, :, i]
                barcodes = decode(channel)
                methods_tried.append(f"{channel_name} channel")
                if barcodes:
                    return barcodes, f"{channel_name} channel", methods_tried if debug else None
            except Exception as e:
                if debug:
                    print(f"{channel_name} channel failed: {e}")
    
    # Ultra method 5: Try with different threshold methods and values
    threshold_methods = [
        (cv2.THRESH_BINARY, "Binary"),
        (cv2.THRESH_BINARY_INV, "Binary inverted"),
        (cv2.THRESH_TRUNC, "Truncated"),
        (cv2.THRESH_TOZERO, "To zero"),
        (cv2.THRESH_TOZERO_INV, "To zero inverted")
    ]
    
    for thresh_val in range(30, 226, 20):  # Try many threshold values
        for thresh_type, method_name in threshold_methods:
            try:
                _, thresholded = cv2.threshold(img_gray, thresh_val, 255, thresh_type)
                barcodes = decode(thresholded)
                methods_tried.append(f"{method_name} threshold {thresh_val}")
                if barcodes:
                    return barcodes, f"{method_name} threshold {thresh_val}", methods_tried if debug else None
            except Exception as e:
                if debug and thresh_val % 60 == 30:  # Only log occasionally
                    print(f"{method_name} threshold {thresh_val} failed: {e}")
    
    # Ultra method 6: Combination of scale + rotation + preprocessing
    key_scales = [0.5, 1.0, 2.0, 3.0]
    key_angles = [-45, -30, -15, 0, 15, 30, 45]
    key_preprocessing = [
        ("Original", lambda x: x),
        ("Enhanced", lambda x: cv2.convertScaleAbs(x, alpha=2.0, beta=30)),
        ("CLAHE", lambda x: cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(x))
    ]
    
    for scale in key_scales:
        for angle in key_angles:
            for preprocess_name, preprocess_func in key_preprocessing:
                try:
                    # First resize
                    h, w = img_gray.shape
                    new_h, new_w = int(h * scale), int(w * scale)
                    if 30 <= new_h <= 3000 and 30 <= new_w <= 3000:
                        resized = cv2.resize(img_gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
                        
                        # Then rotate
                        center = (resized.shape[1]//2, resized.shape[0]//2)
                        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                        rotated = cv2.warpAffine(resized, rotation_matrix, (resized.shape[1], resized.shape[0]))
                        
                        # Then preprocess
                        processed = preprocess_func(rotated)
                        
                        barcodes = decode(processed)
                        method_desc = f"{preprocess_name} + {scale}x + {angle}°"
                        methods_tried.append(method_desc)
                        if barcodes:
                            return barcodes, method_desc, methods_tried if debug else None
                except Exception as e:
                    if debug and scale == 1.0 and angle == 0:  # Only log the baseline case
                        print(f"Combo {preprocess_name} + {scale}x + {angle}° failed: {e}")
    
    # If still no barcodes found, return empty result
    return [], "No detection (ultra-enhanced)", methods_tried if debug else None


# Additional barcode detection methods using different libraries
try:
    import cv2.aruco as aruco
    ARUCO_SUPPORT = True
except ImportError:
    ARUCO_SUPPORT = False

try:
    import qrcode
    QR_DECODE_SUPPORT = True
except ImportError:
    QR_DECODE_SUPPORT = False

def alternative_barcode_detection(image_input):
    """
    Alternative barcode detection using different methods when pyzbar fails
    """
    image = load_image_safely(image_input)
    if image is None:
        return [], "Failed to load image for alternative detection"
    
    img_array = np.array(image)
    
    # Convert to grayscale
    if len(img_array.shape) == 3:
        img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        img_gray = img_array
    
    detected_barcodes = []
    detection_methods = []
    
    # Method 1: Try ArUco marker detection (for QR-like codes)
    if ARUCO_SUPPORT:
        try:
            # Try different ArUco dictionaries
            aruco_dicts = [
                aruco.DICT_4X4_50,
                aruco.DICT_4X4_100,
                aruco.DICT_4X4_250,
                aruco.DICT_5X5_50,
                aruco.DICT_6X6_50
            ]
            
            for dict_type in aruco_dicts:
                aruco_dict = aruco.Dictionary_get(dict_type)
                parameters = aruco.DetectorParameters_create()
                corners, ids, _ = aruco.detectMarkers(img_gray, aruco_dict, parameters=parameters)
                
                if ids is not None and len(ids) > 0:
                    for i, marker_id in enumerate(ids):
                        # Create a fake barcode result to match pyzbar format
                        class FakeBarcode:
                            def __init__(self, data, barcode_type="ARUCO"):
                                self.data = str(data).encode('utf-8')
                                self.type = barcode_type
                                self.rect = None
                        
                        detected_barcodes.append(FakeBarcode(marker_id[0]))
                    
                    detection_methods.append(f"ArUco detection (dict: {dict_type})")
                    return detected_barcodes, f"ArUco detection (dict: {dict_type})"
        
        except Exception as e:
            logging.warning(f"ArUco detection failed: {e}")
    
    # Method 2: Template matching for common barcode patterns
    try:
        # Look for repetitive vertical patterns (typical of linear barcodes)
        height, width = img_gray.shape
        
        # Create templates for common barcode patterns
        templates = []
        
        # Vertical lines pattern
        for line_width in [1, 2, 3]:
            for spacing in [2, 3, 4, 5]:
                template = np.zeros((20, line_width * 4 + spacing * 3), dtype=np.uint8)
                for i in range(4):
                    start_col = i * (line_width + spacing)
                    template[:, start_col:start_col + line_width] = 255
                templates.append((template, f"Lines {line_width}px spacing {spacing}px"))
        
        best_match = 0
        best_method = "No template match"
        
        for template, template_name in templates:
            try:
                result = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                
                if max_val > best_match:
                    best_match = max_val
                    best_method = template_name
                
                # If we find a strong match, consider it a potential barcode area
                if max_val > 0.5:  # Threshold for considering a match
                    class FakeBarcode:
                        def __init__(self, location, confidence):
                            self.data = f"PATTERN_DETECTED_AT_{location[0]}_{location[1]}_CONF_{confidence:.2f}".encode('utf-8')
                            self.type = "PATTERN"
                            self.rect = None
                    
                    detected_barcodes.append(FakeBarcode(max_loc, max_val))
                    return detected_barcodes, f"Template matching: {template_name} (confidence: {max_val:.2f})"
            
            except Exception as e:
                continue
        
        detection_methods.append(f"Template matching (best: {best_method}, score: {best_match:.2f})")
    
    except Exception as e:
        logging.warning(f"Template matching failed: {e}")
    
    # Method 3: Detect rectangular regions that might contain barcodes
    try:
        # Find contours
        edges = cv2.Canny(img_gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        potential_barcodes = []
        
        for contour in contours:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            # Filter for barcode-like shapes (rectangular, reasonable size)
            aspect_ratio = w / h if h > 0 else 0
            
            # Linear barcodes: wide and short
            # QR codes: square-ish
            if (area > 500 and 
                ((aspect_ratio > 2 and aspect_ratio < 10) or  # Linear barcode
                 (aspect_ratio > 0.5 and aspect_ratio < 2))):  # Square-ish (QR)
                
                potential_barcodes.append((x, y, w, h, area, aspect_ratio))
        
        if potential_barcodes:
            # Sort by area (largest first)
            potential_barcodes.sort(key=lambda x: x[4], reverse=True)
            
            class FakeBarcode:
                def __init__(self, rect_info):
                    x, y, w, h, area, ratio = rect_info
                    self.data = f"RECT_REGION_{x}_{y}_{w}x{h}_AREA_{area}_RATIO_{ratio:.1f}".encode('utf-8')
                    self.type = "REGION"
                    self.rect = None
            
            detected_barcodes.append(FakeBarcode(potential_barcodes[0]))
            detection_methods.append(f"Rectangular region detection ({len(potential_barcodes)} regions found)")
            return detected_barcodes, f"Rectangular region detection"
    
    except Exception as e:
        logging.warning(f"Contour detection failed: {e}")
    
    return [], "No alternative detection methods succeeded"


def comprehensive_barcode_detection(image_input, debug=False):
    """
    Comprehensive barcode detection that tries multiple approaches
    """
    # First try the enhanced pyzbar detection
    barcodes, method, debug_info = enhanced_barcode_detection(image_input, debug=debug)
    
    if barcodes:
        return barcodes, method, debug_info
    
    # If pyzbar fails, try alternative methods
    alt_barcodes, alt_method = alternative_barcode_detection(image_input)
    
    if alt_barcodes:
        return alt_barcodes, f"Alternative: {alt_method}", debug_info
    
    return [], "All detection methods failed", debug_info

def test_barcode_on_image(image_path, use_ultra_enhanced=True):
    """
    Test barcode detection on a specific image with detailed logging
    """
    print(f"Testing barcode detection on: {image_path}")
    
    if use_ultra_enhanced:
        barcodes, method, methods_tried = ultra_enhanced_barcode_detection(image_path, debug=True)
        print(f"Ultra-enhanced detection result: {len(barcodes)} barcodes found")
        print(f"Successful method: {method}")
        if methods_tried:
            print(f"Total methods tried: {len(methods_tried)}")
    else:
        barcodes, method, methods_tried = enhanced_barcode_detection(image_path, debug=True)
        print(f"Enhanced detection result: {len(barcodes)} barcodes found")
        print(f"Successful method: {method}")
    
    if barcodes:
        for i, barcode in enumerate(barcodes):
            data = barcode.data.decode('utf-8', errors='ignore')
            print(f"Barcode {i+1}: '{data}' (type: {barcode.type})")
            if hasattr(barcode, 'rect'):
                print(f"  Location: x={barcode.rect.left}, y={barcode.rect.top}, w={barcode.rect.width}, h={barcode.rect.height}")
    else:
        print("No barcodes detected")
    
    return barcodes, method

def analyze_image_quality(image_input):
    """
    Analyze image quality for barcode detection
    """
    if isinstance(image_input, Image.Image):
        img_array = np.array(image_input)
    else:
        img_array = image_input
    
    # Convert to grayscale if needed
    if len(img_array.shape) == 3:
        img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        img_gray = img_array
    
    # Calculate quality metrics
    mean_brightness = np.mean(img_gray)
    std_brightness = np.std(img_gray)
    
    # Calculate sharpness using Laplacian variance
    laplacian_var = cv2.Laplacian(img_gray, cv2.CV_64F).var()
    
    # Calculate contrast
    contrast = img_gray.max() - img_gray.min()
    
    quality_info = {
        'mean_brightness': mean_brightness,
        'std_brightness': std_brightness,
        'sharpness': laplacian_var,
        'contrast': contrast,
        'size': img_gray.shape
    }
    
    # Provide recommendations
    recommendations = []
    if mean_brightness < 50:
        recommendations.append("Image is too dark - try better lighting")
    elif mean_brightness > 200:
        recommendations.append("Image is too bright - reduce lighting or adjust camera exposure")
    
    if std_brightness < 30:
        recommendations.append("Low contrast - try to improve lighting conditions")
    
    if laplacian_var < 100:
        recommendations.append("Image appears blurry - hold camera steady and ensure good focus")
    
    if contrast < 100:
        recommendations.append("Poor contrast between barcode and background")
    
    quality_info['recommendations'] = recommendations
    return quality_info
