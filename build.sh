#!/bin/bash
set -e

echo "=== Building React app ==="
bun run build

echo "=== Copying blog to dist/blog ==="
mkdir -p dist/blog
cp -r output/. dist/blog/

echo "=== Verifying blog files ==="
ls -la dist/blog/

echo "=== Build complete ==="
