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
