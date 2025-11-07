# npm Publishing Scripts

This directory contains scripts to help publish ffmcp to npm.

## Quick Usage

### Publish with automatic version bumping:

```bash
# Patch version (0.1.0 -> 0.1.1)
npm run publish:patch

# Minor version (0.1.0 -> 0.2.0)
npm run publish:minor

# Major version (0.1.0 -> 1.0.0)
npm run publish:major
```

### Or use the script directly:

```bash
./scripts/publish.sh patch
./scripts/publish.sh minor
./scripts/publish.sh major
```

## What the Script Does

1. ✅ Checks for uncommitted changes
2. ✅ Verifies npm login status
3. ✅ Bumps version in `package.json`
4. ✅ Runs tests (if available)
5. ✅ Checks what will be published (dry-run)
6. ✅ Publishes to npm
7. ✅ Commits version change to git
8. ✅ Creates git tag (e.g., `v0.1.1`)
9. ✅ Pushes changes and tag to remote

## Manual Version Bumping

If you just want to bump the version without publishing:

```bash
npm run version:patch   # 0.1.0 -> 0.1.1
npm run version:minor   # 0.1.0 -> 0.2.0
npm run version:major   # 0.1.0 -> 1.0.0
```

## Dry Run

Check what will be published without actually publishing:

```bash
npm run publish:dry-run
```

## Skip Git Operations

If you want to publish without git operations:

```bash
./scripts/publish.sh patch --skip-git
```

## Sync Versions

Sync version between `package.json` and `setup.py`:

```bash
npm run sync-version
# or
./scripts/sync-version.sh
```

## Prerequisites

- Logged in to npm: `npm login`
- Git repository initialized
- No uncommitted changes (unless using `--skip-git`)

## Troubleshooting

**"Not logged in to npm"**
```bash
npm login
```

**"You have uncommitted changes"**
```bash
git add .
git commit -m "Your commit message"
# or
git stash
```

**"Package name already taken"**
- The package name might be taken on npm
- Check: https://www.npmjs.com/package/ffmcp
- Consider using a scoped package: `@yourusername/ffmcp`

## Version Synchronization

**Note:** This script only updates `package.json`. If you want to sync versions with `setup.py`, use:

```bash
npm run sync-version
```

This will update `setup.py` to match the version in `package.json`.

