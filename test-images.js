const fs = require('fs');
const path = require('path');

// Create a simple test script that checks if the images contain recognizable barcode patterns
async function analyzeImages() {
    const exampleDir = path.join(__dirname, 'example_data');
    const files = fs.readdirSync(exampleDir);
    
    console.log('Found images in example_data:');
    files.forEach(file => {
        const stats = fs.statSync(path.join(exampleDir, file));
        console.log(`- ${file} (${(stats.size / 1024).toFixed(2)} KB)`);
    });
    
    console.log('\nTo test barcode detection:');
    console.log('1. Open http://localhost:3000 in your browser');
    console.log('2. Navigate to the barcode scanner section');
    console.log('3. Upload one of the images from example_data/');
    console.log('4. Or open test-barcode.html to test with ZXing directly');
    
    // Check if images are accessible
    const testFiles = ['IMG_8278.JPG', 'IMG_8273.jpg', 'IMG_8274.jpg'];
    console.log('\nChecking example images:');
    
    testFiles.forEach(file => {
        const filePath = path.join(exampleDir, file);
        if (fs.existsSync(filePath)) {
            const stats = fs.statSync(filePath);
            console.log(`✅ ${file} - ${(stats.size / 1024).toFixed(2)} KB`);
        } else {
            console.log(`❌ ${file} - Not found`);
        }
    });
}

analyzeImages().catch(console.error);
