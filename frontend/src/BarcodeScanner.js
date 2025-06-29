import React, { useRef, useState } from 'react';
import { BrowserMultiFormatReader } from '@zxing/browser';
import { Button, Typography, Box, TextField, MenuItem, Select } from '@mui/material';

const API_URL = process.env.REACT_APP_API_URL || 'https://localhost:4000';
const categories = ['brakes', 'frame', 'tires', 'drivetrain', 'other'];

export default function BarcodeScanner() {
  const videoRef = useRef();
  const [scanning, setScanning] = useState(false);
  const [gtin, setGtin] = useState('');
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('');
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);
  const [imgPreview, setImgPreview] = useState(null);

  const startScan = async () => {
    setScanning(true);
    const codeReader = new BrowserMultiFormatReader();
    try {
      await codeReader.decodeFromVideoDevice(
        undefined,
        videoRef.current,
        (result, err) => {
          if (result) {
            setGtin(result.getText());
            setScanning(false);
            codeReader.reset();
          }
        }
      );
    } catch (err) {
      setScanning(false);
    }
  };

  const scanImage = async (file) => {
    const codeReader = new BrowserMultiFormatReader();
    
    try {
      console.log('Starting barcode scan for file:', file.name, file.type);
      
      // Create image element and wait for it to load
      const img = document.createElement('img');
      const imageUrl = URL.createObjectURL(file);
      img.src = imageUrl;
      
      await new Promise((resolve, reject) => {
        img.onload = resolve;
        img.onerror = reject;
      });
      
      console.log('Image loaded, dimensions:', img.width, 'x', img.height);

      // Method 1: Try decodeFromImageElement
      try {
        console.log('Trying decodeFromImageElement...');
        const result = await codeReader.decodeFromImageElement(img);
        console.log('Success with decodeFromImageElement:', result.getText());
        setGtin(result.getText());
        URL.revokeObjectURL(imageUrl);
        return;
      } catch (err1) {
        console.log('Method 1 (decodeFromImageElement) failed:', err1.message);
      }

      // Method 2: Try with canvas
      try {
        console.log('Trying canvas method...');
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
        
        const result = await codeReader.decodeFromCanvas(canvas);
        console.log('Success with canvas method:', result.getText());
        setGtin(result.getText());
        URL.revokeObjectURL(imageUrl);
        return;
      } catch (err2) {
        console.log('Method 2 (canvas) failed:', err2.message);
      }

      // Method 3: Try with ImageData
      try {
        console.log('Trying ImageData method...');
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
        
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const result = await codeReader.decodeFromImageData(imageData);
        console.log('Success with ImageData method:', result.getText());
        setGtin(result.getText());
        URL.revokeObjectURL(imageUrl);
        return;
      } catch (err3) {
        console.log('Method 3 (ImageData) failed:', err3.message);
      }

      // Clean up and show error
      URL.revokeObjectURL(imageUrl);
      setGtin('');
      alert('No barcode found in image. Please try a clearer image or check if the barcode is visible. Note: HEIC format may not be supported - try converting to JPG/PNG.');
    } catch (err) {
      console.error('Barcode scanning error:', err);
      setGtin('');
      alert('Error scanning barcode: ' + err.message);
    }
  };

  const handleAdd = async () => {
    const formData = new FormData();
    formData.append('title', title);
    formData.append('gtin', gtin);
    formData.append('category', category);
    if (image) formData.append('image', image);
    const res = await fetch(`${API_URL}/api/items`, {
      method: 'POST',
      body: formData
    });
    setResult(await res.json());
  };

  const handleImage = e => {
    const file = e.target.files[0];
    if (!file) return;
    
    // Check file type
    const supportedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];
    if (!supportedTypes.includes(file.type.toLowerCase())) {
      alert('Unsupported file format. Please use JPG, PNG, GIF, BMP, or WebP. HEIC files are not supported by browsers.');
      return;
    }
    
    console.log('Processing file:', file.name, file.type, file.size, 'bytes');
    setImage(file);
    setImgPreview(URL.createObjectURL(file));
    scanImage(file);
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h5">Add Item via Barcode</Typography>
      <Box sx={{ my: 2 }}>
        <Button variant="contained" onClick={startScan} disabled={scanning}>Scan Barcode (Camera)</Button>
        <video ref={videoRef} style={{ width: 300, display: scanning ? 'block' : 'none' }} />
      </Box>
      <Button variant="contained" component="label" sx={{ mb: 2 }}>
        Upload Image for Barcode
        <input type="file" accept="image/jpeg,image/jpg,image/png,image/gif,image/bmp,image/webp" hidden onChange={handleImage} />
      </Button>
      {imgPreview && <img src={imgPreview} alt="preview" style={{ maxWidth: 300, display: 'block', marginBottom: 8 }} />}
      <TextField label="GTIN" value={gtin} onChange={e => setGtin(e.target.value)} fullWidth sx={{ mb: 2 }} />
      <TextField label="Title" value={title} onChange={e => setTitle(e.target.value)} fullWidth sx={{ mb: 2 }} />
      <Select value={category} onChange={e => setCategory(e.target.value)} displayEmpty fullWidth sx={{ mb: 2 }}>
        <MenuItem value="">Select Category</MenuItem>
        {categories.map(cat => <MenuItem key={cat} value={cat}>{cat}</MenuItem>)}
      </Select>
      <Button variant="contained" onClick={handleAdd} sx={{ ml: 2 }}>Add Item</Button>
      {result && <Typography sx={{ mt: 2 }}>Added! ID: {result.id}</Typography>}
    </Box>
  );
}
