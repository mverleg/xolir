#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const protoDir = path.join(__dirname, '..', 'proto', 'xolir');
const outputDir = path.join(__dirname, 'generated');

// Create output directory
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
}

// Find all proto files
const protoFiles = fs.readdirSync(protoDir)
    .filter(file => file.endsWith('.proto'))
    .map(file => path.join(protoDir, file));

if (protoFiles.length === 0) {
    console.error('No proto files found in', protoDir);
    process.exit(1);
}

console.log('Generating TypeScript from proto files...');

// Generate TypeScript files using protobufjs-cli
try {
    const protoRootDir = path.join(__dirname, '..', 'proto');
    const cmd = `npx pbjs -t static-module -w commonjs -p ${protoRootDir} -o ${outputDir}/xolir.js ${protoFiles.join(' ')}`;
    console.log('Running:', cmd);
    execSync(cmd, { stdio: 'inherit' });

    const dtsCmd = `npx pbts -o ${outputDir}/xolir.d.ts ${outputDir}/xolir.js`;
    console.log('Running:', dtsCmd);
    execSync(dtsCmd, { stdio: 'inherit' });

    console.log('TypeScript protobuf files generated successfully!');
} catch (error) {
    console.error('Failed to generate TypeScript protobuf files:', error.message);
    process.exit(1);
}