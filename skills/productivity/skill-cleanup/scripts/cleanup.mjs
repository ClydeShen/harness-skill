#!/usr/bin/env node
/**
 * skill-cleanup — interactive skill removal tool
 * Scans all agent platform directories, presents a TUI multi-select,
 * and removes confirmed entries using OS-native methods.
 *
 * Usage:
 *   node cleanup.mjs
 *   node cleanup.mjs --dry-run    # show what would be removed, no changes
 */

import { checkbox, confirm } from '@inquirer/prompts';
import { existsSync, readdirSync, rmSync, lstatSync } from 'node:fs';
import { join } from 'node:path';
import { homedir, platform as osPlatform } from 'node:os';

const HOME = homedir();
const IS_WIN = osPlatform() === 'win32';
const DRY_RUN = process.argv.includes('--dry-run');

// ── Platform definitions ────────────────────────────────────────────────────

const PLATFORMS = [
  // Central store — source of truth; remove last
  { id: 'central',          label: 'Central store',    path: join(HOME, '.agents', 'skills'),                    type: 'central' },
  // Symlink platforms — entries are symlinks/junctions pointing into central store
  { id: 'claude',           label: 'Claude Code',      path: join(HOME, '.claude', 'skills'),                    type: 'symlink' },
  { id: 'kiro',             label: 'Kiro CLI',         path: join(HOME, '.kiro', 'skills'),                      type: 'symlink' },
  { id: 'pi',               label: 'Pi',               path: join(HOME, '.pi', 'agent', 'skills'),               type: 'symlink' },
  { id: 'kilocode',         label: 'Kilo Code',        path: join(HOME, '.kilocode', 'skills'),                  type: 'symlink' },
  { id: 'qwen',             label: 'Qwen Code',        path: join(HOME, '.qwen', 'skills'),                      type: 'symlink' },
  // Copy platforms — independent full copies; remove each separately
  { id: 'codex',            label: 'Codex',            path: join(HOME, '.codex', 'skills'),                     type: 'copy' },
  { id: 'windsurf',         label: 'Windsurf',         path: join(HOME, '.codeium', 'windsurf', 'skills'),       type: 'copy' },
  { id: 'gemini-config',    label: 'Gemini (config)',  path: join(HOME, '.gemini', 'config', 'skills'),          type: 'copy' },
  { id: 'gemini-ide',       label: 'Gemini (IDE)',     path: join(HOME, '.gemini', 'antigravity-ide', 'skills'), type: 'copy' },
  { id: 'gemini-backup',    label: 'Gemini (backup)',  path: join(HOME, '.gemini', 'antigravity-backup', 'skills'), type: 'copy' },
];

// ── Scanning ────────────────────────────────────────────────────────────────

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

function isBrokenSymlink(fullPath) {
  try {
    const stat = lstatSync(fullPath);
    if (!stat.isSymbolicLink()) return false;
    existsSync(fullPath); // throws if target missing on some systems
    return false;
  } catch {
    return true;
  }
}

// ── Staleness detection ─────────────────────────────────────────────────────

function detectStale(entries) {
  const centralNames = new Set(
    entries.filter(e => e.platform.type === 'central').map(e => e.skill)
  );
  const allNames = new Set(entries.map(e => e.skill));

  // Detect renamed pairs: both old and new present in central store
  // Heuristic: if a name is a prefix-substring of another name that also exists
  const renames = new Map(); // oldName → newName
  for (const a of centralNames) {
    for (const b of centralNames) {
      if (a !== b && b.startsWith(a) && (b[a.length] === '-' || b[a.length] === '_')) {
        renames.set(a, b);
      }
    }
  }

  return entries.map(entry => {
    const reasons = [];

    if (entry.skill.endsWith('.zip'))
      reasons.push('install artifact (.zip)');
    if (entry.skill.endsWith('-workspace'))
      reasons.push('install artifact (-workspace)');
    if (entry.skill.endsWith('-backup') && entry.platform.type !== 'central')
      reasons.push('install artifact (-backup)');
    if (isBrokenSymlink(entry.fullPath))
      reasons.push('broken symlink');
    if (entry.platform.type !== 'central' && !centralNames.has(entry.skill))
      reasons.push('orphaned — not in central store');
    if (renames.has(entry.skill) && allNames.has(renames.get(entry.skill)))
      reasons.push(`renamed → ${renames.get(entry.skill)}`);

    return { ...entry, reasons, stale: reasons.length > 0 };
  });
}

// ── Grouping for display ─────────────────────────────────────────────────────

function groupBySkill(entries) {
  const map = new Map();
  for (const e of entries) {
    if (!map.has(e.skill)) map.set(e.skill, []);
    map.get(e.skill).push(e);
  }
  return map;
}

// ── TUI choices ─────────────────────────────────────────────────────────────

function buildChoices(entries) {
  const grouped = groupBySkill(entries);
  const choices = [];

  for (const [skill, items] of [...grouped.entries()].sort()) {
    const anyStale  = items.some(i => i.stale);
    const platforms = items.map(i => i.platform.label).join(', ');
    const reasons   = [...new Set(items.flatMap(i => i.reasons))];
    const tag       = anyStale ? ` ⚠  ${reasons.join(' · ')}` : '';

    // One entry per skill — selects all platform entries for that skill
    choices.push({
      name:    `${skill.padEnd(35)} [${platforms}]${tag}`,
      value:   items,
      checked: anyStale,
    });
  }

  return choices;
}

// ── Removal ──────────────────────────────────────────────────────────────────

function removeEntry(entry) {
  // Sort: platform entries before central store
  rmSync(entry.fullPath, { recursive: true, force: true });
}

// ── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  console.log(DRY_RUN ? '\n[DRY RUN] Scanning installed skills…\n' : '\nScanning installed skills…\n');

  const allEntries = PLATFORMS.flatMap(scanPlatform);

  if (allEntries.length === 0) {
    console.log('No skills found. Nothing to clean up.');
    return;
  }

  const entries  = detectStale(allEntries);
  const choices  = buildChoices(entries);
  const staleCount = choices.filter(c => c.checked).length;

  if (staleCount > 0) {
    console.log(`Found ${staleCount} potentially stale skill(s) (pre-selected).\n`);
  }

  const selected = await checkbox({
    message: 'Select skills to remove  (↑↓ navigate · space toggle · a select-all · enter confirm)',
    choices,
    pageSize: 20,
  });

  if (selected.length === 0) {
    console.log('\nNothing selected. No changes made.');
    return;
  }

  // Flatten: collect all individual entries, sort so central store is last
  const toRemove = selected
    .flat()
    .sort((a, b) => {
      if (a.platform.type === 'central') return 1;
      if (b.platform.type === 'central') return -1;
      return 0;
    });

  console.log('\nSelected for removal:');
  toRemove.forEach(e => console.log(`  • ${e.skill}  →  ${e.fullPath}`));

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
      console.log(`  ✓  ${entry.fullPath}`);
      removed++;
    } catch (err) {
      console.error(`  ✗  ${entry.fullPath}  (${err.message})`);
      failed++;
    }
  }

  console.log(`\nDone.  Removed: ${removed}  Failed: ${failed}`);
  if (removed > 0) {
    console.log('Restart your agent to refresh the skills list.');
  }
}

main().catch(err => {
  console.error('\nError:', err.message);
  process.exit(1);
});
