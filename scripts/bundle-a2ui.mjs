// scripts/bundle-a2ui.mjs
// OpenClaw A2UI Bundle Placeholder Generator
// For public repository users who do not have access to private A2UI source code.
// This script creates a minimal valid ES module to satisfy TypeScript compilation.

import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';

// ── Resolve project root directory correctly on Windows and Unix ──
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..'); // openclaw/ root

// ── Define output paths ──
const OUTPUT_DIR = path.join(ROOT_DIR, 'src', 'canvas-host', 'a2ui');
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'a2ui.bundle.js');
const HASH_FILE = path.join(OUTPUT_DIR, '.bundle.hash');

// ── Ensure output directory exists ──
fs.mkdirSync(OUTPUT_DIR, { recursive: true });

// ── Generate placeholder content (valid ES module) ──
const placeholderContent = `
// Auto-generated placeholder for A2UI
// Source code is not available in the public OpenClaw repository.
// This file exists only to satisfy build dependencies.
export const A2UI = {
  version: '0.0.0-placeholder',
  render: () => {
    throw new Error('A2UI runtime is not available in this build.');
  }
};
`.trim() + '\n';

// ── Write the bundle file ──
fs.writeFileSync(OUTPUT_FILE, placeholderContent);

// ── Compute and write hash to prevent unnecessary rebuilds ──
const hash = createHash('sha256').update(placeholderContent).digest('hex');
fs.writeFileSync(HASH_FILE, hash);

// ── Success message ──
console.log('✅ A2UI placeholder bundle created successfully.');
console.log(`   Bundle: ${OUTPUT_FILE}`);
console.log(`   Hash:   ${HASH_FILE}`);
