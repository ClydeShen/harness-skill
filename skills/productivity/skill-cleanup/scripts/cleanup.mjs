#!/usr/bin/env node
/**
 * skill-cleanup — interactive skill removal tool
 * Scans all agent platform directories, presents a TUI multi-select,
 * and removes confirmed entries using OS-native methods.
 *
 * Supports: macOS · Linux · Windows (PowerShell / Windows Terminal)
 *
 * Usage:
 *   node cleanup.mjs              # interactive TUI
 *   node cleanup.mjs --dry-run    # select and preview, no changes made
 *   node cleanup.mjs --list       # non-interactive: print all installed skills
 */

import { checkbox, confirm } from '@inquirer/prompts';
import { existsSync, readdirSync, rmSync, lstatSync } from 'node:fs';
import { join } from 'node:path';
import { homedir, platform as osPlatform } from 'node:os';

const HOME    = homedir();
const IS_WIN  = osPlatform() === 'win32';
const DRY_RUN = process.argv.includes('--dry-run');
const LIST    = process.argv.includes('--list');

// ── Platform definitions ─────────────────────────────────────────────────────
// path.join() is OS-aware: uses \ on Windows, / on macOS/Linux automatically.

const PLATFORMS = [
  // Central store — source of truth; always remove last
  { id: 'central',       label: 'Central store',   path: join(HOME, '.agents', 'skills'),                       type: 'central' },
  // Symlink platforms — entries are symlinks (macOS/Linux) or junctions (Windows)
  { id: 'claude',        label: 'Claude Code',     path: join(HOME, '.claude', 'skills'),                       type: 'symlink' },
  { id: 'kiro',          label: 'Kiro CLI',        path: join(HOME, '.kiro', 'skills'),                         type: 'symlink' },
  { id: 'pi',            label: 'Pi',              path: join(HOME, '.pi', 'agent', 'skills'),                  type: 'symlink' },
  { id: 'kilocode',      label: 'Kilo Code',       path: join(HOME, '.kilocode', 'skills'),                     type: 'symlink' },
  { id: 'qwen',          label: 'Qwen Code',       path: join(HOME, '.qwen', 'skills'),                         type: 'symlink' },
  // Copy platforms — independent full copies; remove each platform separately
  { id: 'codex',         label: 'Codex',           path: join(HOME, '.codex', 'skills'),                        type: 'copy' },
  { id: 'windsurf',      label: 'Windsurf',        path: join(HOME, '.codeium', 'windsurf', 'skills'),          type: 'copy' },
  { id: 'gemini-config', label: 'Gemini (config)', path: join(HOME, '.gemini', 'config', 'skills'),             type: 'copy' },
  { id: 'gemini-ide',    label: 'Gemini (IDE)',    path: join(HOME, '.gemini', 'antigravity-ide', 'skills'),    type: 'copy' },
  { id: 'gemini-backup', label: 'Gemini (backup)', path: join(HOME, '.gemini', 'antigravity-backup', 'skills'), type: 'copy' },
];

// ── Scanning ─────────────────────────────────────────────────────────────────

function scanPlatform(plat) {
  if (!existsSync(plat.path)) return [];
  try {
    return readdirSync(plat.path).map(name => ({
      skill:    name,
      platform: plat,
      fullPath: join(plat.path, name),
    }));
  } catch {
    return [];
  }
}

// ── Broken-link detection ─────────────────────────────────────────────────────

function isBrokenLink(fullPath) {
  let stat;
  try {
    stat = lstatSync(fullPath);
  } catch {
    return false; // path doesn't exist at all — handled elsewhere
  }

  // macOS / Linux: standard symlink
  if (stat.isSymbolicLink()) {
    return !existsSync(fullPath); // existsSync follows the link; false = target missing
  }

  // Windows: npx skills creates junctions (isSymbolicLink() === false, isDirectory() === true)
  // A broken junction makes the directory unreadable.
  if (IS_WIN && stat.isDirectory()) {
    try {
      readdirSync(fullPath);
      return false; // readable → not broken
    } catch {
      return true; // unreadable → broken junction
    }
  }

  return false;
}

// ── Staleness detection ───────────────────────────────────────────────────────

const ARTIFACT_SUFFIXES = ['.zip', '-workspace', '-backup'];

function detectStale(entries) {
  const centralNames = new Set(
    entries.filter(e => e.platform.type === 'central').map(e => e.skill)
  );

  return entries.map(entry => {
    const reasons = [];

    // Install artifacts (.zip, -workspace, -backup)
    if (ARTIFACT_SUFFIXES.some(s => entry.skill.endsWith(s)))
      reasons.push('install artifact');

    // Broken symlink or broken Windows junction
    if (isBrokenLink(entry.fullPath))
      reasons.push('broken link');

    // Platform entry that has no matching install in central store
    if (entry.platform.type !== 'central' && !centralNames.has(entry.skill))
      reasons.push('orphaned — not in central store');

    return { ...entry, reasons, stale: reasons.length > 0 };
  });
}

// ── Display helpers ───────────────────────────────────────────────────────────

function groupBySkill(entries) {
  const map = new Map();
  for (const e of entries) {
    if (!map.has(e.skill)) map.set(e.skill, []);
    map.get(e.skill).push(e);
  }
  return map;
}

function buildChoices(entries) {
  const grouped = groupBySkill(entries);
  const choices = [];

  for (const [skill, items] of [...grouped.entries()].sort()) {
    const anyStale  = items.some(i => i.stale);
    const platforms = items.map(i => i.platform.label).join(', ');
    const reasons   = [...new Set(items.flatMap(i => i.reasons))];
    const tag       = anyStale ? `  ! ${reasons.join(' · ')}` : '';

    choices.push({
      name:    `${skill.padEnd(36)}[${platforms}]${tag}`,
      value:   items,
      checked: anyStale,
    });
  }

  return choices;
}

// ── Non-interactive list mode ─────────────────────────────────────────────────

function printList(entries) {
  const grouped = groupBySkill(entries);
  console.log('\nInstalled skills:\n');
  for (const [skill, items] of [...grouped.entries()].sort()) {
    const platforms = items.map(i => i.platform.label).join(', ');
    const stale     = items.filter(i => i.stale);
    const tag       = stale.length ? `  [STALE: ${[...new Set(stale.flatMap(i => i.reasons))].join(', ')}]` : '';
    console.log(`  ${skill.padEnd(36)}${platforms}${tag}`);
  }
  console.log('');
}

// ── Removal ───────────────────────────────────────────────────────────────────

function removeEntry(entry) {
  // rmSync handles: regular dirs, symlinks (macOS/Linux), junctions (Windows)
  rmSync(entry.fullPath, { recursive: true, force: true });
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  // Non-TTY guard: @inquirer/prompts requires an interactive terminal
  if (!LIST && !process.stdin.isTTY) {
    console.error([
      '',
      'skill-cleanup requires an interactive terminal.',
      '',
      'Run directly in your terminal:',
      `  node ${new URL(import.meta.url).pathname.split('/').pop()}`,
      '',
      'Non-interactive options:',
      '  --list      print all installed skills (no prompts)',
      '  --dry-run   select in TUI then preview without removing',
      '',
    ].join('\n'));
    process.exit(1);
  }

  const label = DRY_RUN ? '\n[DRY RUN] Scanning installed skills...\n'
                        : '\nScanning installed skills...\n';
  console.log(label);

  const allEntries = PLATFORMS.flatMap(scanPlatform);

  if (allEntries.length === 0) {
    console.log('No skills found in any platform directory.');
    return;
  }

  const entries = detectStale(allEntries);

  if (LIST) {
    printList(entries);
    return;
  }

  const choices    = buildChoices(entries);
  const staleCount = choices.filter(c => c.checked).length;

  if (staleCount > 0) {
    console.log(`Found ${staleCount} potentially stale skill(s) — pre-selected below.\n`);
  }

  const selected = await checkbox({
    message: 'Select skills to remove  (space toggle · a select-all · i invert · enter confirm)',
    choices,
    pageSize: 20,
  });

  if (selected.length === 0) {
    console.log('\nNothing selected. No changes made.');
    return;
  }

  // Flatten entries; platform copies first, central store last
  const toRemove = selected
    .flat()
    .sort((a, b) => {
      if (a.platform.type === 'central') return 1;
      if (b.platform.type === 'central') return -1;
      return 0;
    });

  console.log('\nSelected for removal:');
  toRemove.forEach(e => console.log(`  ${e.skill}  ->  ${e.fullPath}`));

  if (DRY_RUN) {
    console.log('\n[DRY RUN] No files were removed.');
    return;
  }

  const ok = await confirm({
    message: `Remove ${toRemove.length} item(s)? This cannot be undone.`,
    default: false,
  });

  if (!ok) {
    console.log('Aborted. No changes made.');
    return;
  }

  let removed = 0, failed = 0;
  for (const entry of toRemove) {
    try {
      removeEntry(entry);
      console.log(`  OK  ${entry.fullPath}`);
      removed++;
    } catch (err) {
      console.error(`  ERR ${entry.fullPath}  (${err.message})`);
      failed++;
    }
  }

  console.log(`\nDone.  Removed: ${removed}  Failed: ${failed}`);
  if (removed > 0) console.log('Restart your agent to refresh the skills list.');
}

main().catch(err => {
  // @inquirer/prompts throws ExitPromptError when user presses Ctrl+C
  if (err.name === 'ExitPromptError') {
    console.log('\nCancelled.');
    process.exit(0);
  }
  console.error('\nUnexpected error:', err.message);
  process.exit(1);
});
