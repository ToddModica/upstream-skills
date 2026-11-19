// ZCode and Codex accept the same event envelope and supply separate plugin data directories.
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const hooks = {
  SessionStart: 'ponytail-activate.js',
  UserPromptSubmit: 'ponytail-mode-tracker.js',
};
const child = spawnSync(process.execPath, [path.join(__dirname, hooks[process.argv[2]])], {
  env: { ...process.env, PLUGIN_DATA: process.env.ZCODE_PLUGIN_DATA },
  stdio: ['inherit', 'pipe', 'inherit'],
});
if (child.error) throw child.error;
process.exitCode = child.status ?? 1;
if (child.status === 0) process.stdout.write(child.stdout.length ? child.stdout : '{}');
