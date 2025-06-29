const fs = require('fs');
const path = require('path');

// Node.js barcode detection test - creates an HTML page with the actual images for testing
function createBarcodeTestPage() {
    const exampleDir = path.join(__dirname, 'example_data');
    const files = fs.readdirSync(exampleDir).filter(f => f.toLowerCase().endsWith('.jpg') || f.toLowerCase().endsWith('.jpeg'));
    
    const htmlContent = `
<!DOCTYPE html>
<html>
<head>
    <title>Example Images Barcode Test</title>
    <script src="https://unpkg.com/@zxing/browser@latest/dist/index.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .image-test { border: 1px solid #ccc; margin: 20px 0; padding: 20px; }
        .result { background: #f0f0f0; padding: 10px; margin: 10px 0; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        img { max-width: 400px; max-height: 300px; }
    </style>
</head>
<body>
    <h1>Barcode Detection Test - Example Images</h1>
    <p>Testing ${files.length} example images for barcode detection...</p>
    
    ${files.map((file, index) => `
    <div class="image-test">
        <h2>Test ${index + 1}: ${file}</h2>
        <img src="example_data/${file}" id="img${index}" alt="${file}" />
        <div id="result${index}" class="result">Testing...</div>
        <div id="debug${index}" class="result"></div>
    </div>
    `).join('')}

    <script>
        const codeReader = new ZXing.BrowserMultiFormatReader();
        
        async function testImage(index, filename) {
            const img = document.getElementById('img' + index);
            const resultDiv = document.getElementById('result' + index);
            const debugDiv = document.getElementById('debug' + index);
            
            resultDiv.innerHTML = 'Loading image...';
            
            try {
                // Wait for image to load
                if (!img.complete) {
                    await new Promise(resolve => {
                        img.onload = resolve;
                        img.onerror = () => resolve(); // Continue even if image fails to load
                    });
                }
                
                if (img.naturalWidth === 0) {
                    resultDiv.innerHTML = '<span class="error">❌ Failed to load image</span>';
                    return;
                }
                
                debugDiv.innerHTML = 'Image dimensions: ' + img.naturalWidth + 'x' + img.naturalHeight;
                resultDiv.innerHTML = 'Scanning for barcodes...';
                
                // Method 1: Direct image scan
                try {
                    const result = await codeReader.decodeFromImageElement(img);
                    resultDiv.innerHTML = '<span class="success">✅ BARCODE FOUND: <strong>' + result.getText() + '</strong><br>Format: ' + result.getBarcodeFormat() + '</span>';
                    debugDiv.innerHTML += '<br>✅ Method: decodeFromImageElement';
                    return;
                } catch (err1) {
                    debugDiv.innerHTML += '<br>❌ Method 1 failed: ' + err1.message;
                }
                
                // Method 2: Canvas scan
                try {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    canvas.width = img.naturalWidth;
                    canvas.height = img.naturalHeight;
                    ctx.drawImage(img, 0, 0);
                    
                    const result = await codeReader.decodeFromCanvas(canvas);
                    resultDiv.innerHTML = '<span class="success">✅ BARCODE FOUND: <strong>' + result.getText() + '</strong><br>Format: ' + result.getBarcodeFormat() + '</span>';
                    debugDiv.innerHTML += '<br>✅ Method: canvas';
                    return;
                } catch (err2) {
                    debugDiv.innerHTML += '<br>❌ Method 2 failed: ' + err2.message;
                }
                
                // Method 3: ImageData scan
                try {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    canvas.width = img.naturalWidth;
                    canvas.height = img.naturalHeight;
                    ctx.drawImage(img, 0, 0);
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    
                    const result = await codeReader.decodeFromImageData(imageData);
                    resultDiv.innerHTML = '<span class="success">✅ BARCODE FOUND: <strong>' + result.getText() + '</strong><br>Format: ' + result.getBarcodeFormat() + '</span>';
                    debugDiv.innerHTML += '<br>✅ Method: ImageData';
                    return;
                } catch (err3) {
                    debugDiv.innerHTML += '<br>❌ Method 3 failed: ' + err3.message;
                }
                
                resultDiv.innerHTML = '<span class="error">❌ No barcode detected in this image</span>';
                
            } catch (error) {
                resultDiv.innerHTML = '<span class="error">❌ Error: ' + error.message + '</span>';
                debugDiv.innerHTML += '<br>❌ General error: ' + error.message;
            }
        }
        
        // Test all images
        const testFiles = [${files.map((f, i) => `'${f}'`).join(', ')}];
        testFiles.forEach((filename, index) => {
            // Wait a bit between tests to avoid overwhelming the browser
            setTimeout(() => testImage(index, filename), index * 1000);
        });
    </script>
</body>
</html>`;
    
    fs.writeFileSync(path.join(__dirname, 'test-example-images.html'), htmlContent);
    console.log('Created test-example-images.html');
    console.log('Open this file in a browser to test barcode detection on example images');
    console.log('');
    console.log('Example images found:');
    files.forEach((file, i) => {
        const stats = fs.statSync(path.join(exampleDir, file));
        console.log(`${i + 1}. ${file} (${(stats.size / 1024).toFixed(2)} KB)`);
    });
}

createBarcodeTestPage();
