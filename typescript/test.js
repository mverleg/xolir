#!/usr/bin/env node

console.log('Testing TypeScript protobuf generation...');

// Try to create a dummy program data object
try {
    const xolir = require('./dist/index.js');
    
    // Create a Program object similar to Java test
    const program = new xolir.xolir.Program({
        programName: "HelloWorld"
    });
    
    if (program.programName === "HelloWorld") {
        console.log('✓ Successfully created Program object with programName:', program.programName);
        console.log('✓ All tests passed! TypeScript protobuf generation is working correctly.');
    } else {
        console.error('✗ Program object creation failed - programName mismatch');
        process.exit(1);
    }
    
} catch (error) {
    console.error('✗ Failed to create Program object:', error.message);
    console.error('Make sure to run "npm run build" first.');
    process.exit(1);
}