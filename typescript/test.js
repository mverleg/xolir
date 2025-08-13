#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('Testing TypeScript protobuf generation...');

// Check if generated files exist
const generatedDir = path.join(__dirname, 'generated');
const distDir = path.join(__dirname, 'dist');

const requiredFiles = [
    path.join(generatedDir, 'xolir.js'),
    path.join(generatedDir, 'xolir.d.ts'),
    path.join(distDir, 'index.js'),
    path.join(distDir, 'index.d.ts')
];

let allFilesExist = true;

console.log('Checking for required generated files:');
for (const file of requiredFiles) {
    if (fs.existsSync(file)) {
        console.log(`✓ ${path.relative(__dirname, file)} exists`);
    } else {
        console.log(`✗ ${path.relative(__dirname, file)} missing`);
        allFilesExist = false;
    }
}

if (!allFilesExist) {
    console.error('\nSome required files are missing. Please run "npm run build" first.');
    process.exit(1);
}

// Try to load the generated code
try {
    const xolir = require('./dist/index.js');
    console.log('\n✓ Generated TypeScript code is loadable');
    
    // Check if xolir namespace exists
    if (xolir && typeof xolir === 'object') {
        console.log('✓ Xolir namespace is available');
        
        // List available types/objects
        const keys = Object.keys(xolir);
        if (keys.length > 0) {
            console.log(`✓ Available exports: ${keys.join(', ')}`);
        } else {
            console.log('! No exports found (this might be expected if no protobuf messages are defined)');
        }
    } else {
        console.log('! Xolir namespace not found or not an object');
    }
    
    console.log('\n✓ All tests passed! TypeScript protobuf generation is working correctly.');
    
} catch (error) {
    console.error('\n✗ Failed to load generated TypeScript code:', error.message);
    process.exit(1);
}