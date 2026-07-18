// Copy the pre-built static blog (output/, produced + committed by the blog engine)
// into the deploy output at dist/blog, so Render serves it at benchmarkps.org/blog.
// No Python needed at deploy time — output/ is already built and committed.
import { existsSync, rmSync, cpSync, readdirSync } from 'node:fs';

const SRC = 'output';
const DEST = 'dist/blog';

if (!existsSync(SRC)) {
  console.warn('[copy-blog] no output/ directory found — skipping blog copy');
  process.exit(0);
}
rmSync(DEST, { recursive: true, force: true });
cpSync(SRC, DEST, { recursive: true });
const posts = existsSync(`${DEST}/posts`) ? readdirSync(`${DEST}/posts`).length : 0;
console.log(`[copy-blog] copied output/ -> ${DEST} (${posts} post folders)`);
