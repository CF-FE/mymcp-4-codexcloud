// Optional real-runtime check; no account, daemon or external service is used.
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';

if (process.argv.length !== 3) throw Error('Usage: node verify_workers.mjs <installed-runtime-directory>');
const runtime = resolve(process.argv[2]);
const { default: Tinypool } = await import(pathToFileURL(join(runtime, 'node_modules/tinypool/dist/index.js')).href);
const fixture = await mkdtemp(join(tmpdir(), 'lody4dot-workers-'));
const options = { minThreads: 0, idleTimeout: 30_000 };
const diff = new Tinypool({ ...options, filename: join(runtime, 'node_modules/lody/dist/diff-worker.js'), maxThreads: 2 });
const scan = new Tinypool({ ...options, filename: join(runtime, 'node_modules/lody/dist/file-index-scan-worker.js'), maxThreads: 1 });
try {
  await mkdir(join(fixture, 'nested'));
  await mkdir(join(fixture, 'node_modules/ignored'), { recursive: true });
  await writeFile(join(fixture, 'main.txt'), 'a\nc\n');
  await writeFile(join(fixture, 'nested/unicode.txt'), '你好\nworld\n');
  await writeFile(join(fixture, 'node_modules/ignored/file.txt'), 'ignored');
  const tasks = await Promise.all([
    diff.run({ kind: 'line-count', oldText: 'a\nb\n', newText: 'a\nc\n' }),
    diff.run({ kind: 'line-count', oldText: '', newText: '你好\nworld\n' }),
    diff.run({ kind: 'turn-evidence', oldText: 'a\nb\n', newText: 'a\nc\n', absolutePath: join(fixture, 'main.txt') }),
    diff.run({ kind: 'turn-evidence', oldText: 'a\nb\n', newText: 'a\ndifferent\n', absolutePath: join(fixture, 'main.txt') }),
  ]);
  assert.deepEqual(tasks[0], { kind: 'line-count', lineCounts: [1, 1] });
  assert.deepEqual(tasks[1], { kind: 'line-count', lineCounts: [2, 0] });
  assert.equal(tasks[2].newIsCurrent, true);
  assert.equal(tasks[3].newIsCurrent, false);
  const input = { kind: 'scan', directoryAbsolutePath: fixture, directoryWorkspacePath: '', maxRawTextBytes: 1024, entryBudget: 100 };
  const recursive = await scan.run({ ...input, recursive: true });
  assert.deepEqual(recursive.entries, [['main.txt', true], ['nested', { kind: 'lazy' }], ['nested/unicode.txt', true]]);
  assert.deepEqual((await scan.run({ ...input, recursive: false })).entries, [['main.txt', true], ['nested', { kind: 'lazy' }]]);
  const full = await scan.run({ kind: 'full-state', workspaceRoot: fixture, maxRawTextBytes: 1024, entryBudget: 100, providedAllChanges: { source: 'fixture', state: {}, computeMs: 0 } });
  assert.equal(full.status, 'ok');
  assert.equal(full.pathCount, 3);
  await assert.rejects(scan.run({ ...input, directoryAbsolutePath: join(fixture, 'absent'), recursive: true }), /ENOENT/);
  assert.deepEqual((await scan.run({ ...input, recursive: true })).entries, recursive.entries);
  console.log(JSON.stringify({ status: 'pass', node: process.version, checks: ['concurrent-diff', 'unicode', 'file-evidence', 'recursive-scan', 'shallow-scan', 'full-state', 'worker-error-recovery'] }));
} finally {
  await Promise.all([diff.destroy(), scan.destroy()]);
  await rm(fixture, { recursive: true, force: true });
}
