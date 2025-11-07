# Publishing ffmcp to npm

This guide explains how to publish the ffmcp npm package.

## Prerequisites

1. **npm account**: Create an account at https://www.npmjs.com/signup
2. **Login**: Run `npm login` in your terminal
3. **Python package**: Ensure the Python ffmcp package is working correctly

## Publishing Steps

### 1. Update Version

Update the version in `package.json`:
```json
{
  "version": "0.1.0"
}
```

Follow semantic versioning:
- `0.1.0` → `0.1.1` (patch: bug fixes)
- `0.1.0` → `0.2.0` (minor: new features)
- `0.1.0` → `1.0.0` (major: breaking changes)

### 2. Update Repository URL

Make sure the repository URL in `package.json` points to your actual GitHub repository:
```json
{
  "repository": {
    "type": "git",
    "url": "https://github.com/brandonhenry/ffmcp.git"
  }
}
```

### 3. Update Author Information

Update author information in `package.json`:
```json
{
  "author": "Your Name",
  "author_email": "your.email@example.com"
}
```

### 4. Test Locally

Test the package locally before publishing:
```bash
# Install dependencies
npm install

# Test the CLI wrapper
node bin/ffmcp.js --version

# Test the programmatic API
node -e "const ffmcp = require('./index.js'); console.log('Module loaded:', !!ffmcp);"
```

### 5. Check What Will Be Published

See what files will be included:
```bash
npm pack --dry-run
```

This creates a tarball preview. Check that only necessary files are included.

### 6. Publish to npm

**First time publishing:**
```bash
npm publish
```

**Subsequent publishes:**
```bash
# Update version first
npm version patch  # or minor, or major

# Then publish
npm publish
```

### 7. Verify Publication

Check that your package is available:
```bash
npm view ffmcp
```

Or visit: https://www.npmjs.com/package/ffmcp

## Testing After Publishing

Users can test the package:
```bash
# Install globally
npm install -g ffmcp

# Or install locally in a project
npm install ffmcp

# Test CLI
ffmcp --version
```

## Important Notes

1. **Python Dependency**: Users must install the Python ffmcp package separately. The npm package is a wrapper.

2. **Version Sync**: Consider syncing npm version with Python package version for consistency.

3. **README**: The npm package uses `NPM_README.md` which is automatically included. Make sure it's up to date.

4. **Unpublishing**: If you need to unpublish (within 72 hours):
   ```bash
   npm unpublish ffmcp@0.1.0
   ```
   After 72 hours, you cannot unpublish, only deprecate:
   ```bash
   npm deprecate ffmcp@0.1.0 "Use version 0.2.0 instead"
   ```

## Troubleshooting

### "Package name already taken"
- Choose a different name or add a scope: `@brandonhenry/ffmcp`
- Update `package.json` name field accordingly

### "You do not have permission"
- Make sure you're logged in: `npm whoami`
- If the package name is taken, you need to be added as a maintainer

### "Invalid package name"
- Package names must be lowercase, no spaces, can include hyphens
- Must be <= 214 characters

## Continuous Publishing

For automated publishing, you can use GitHub Actions or similar CI/CD:

```yaml
# .github/workflows/publish-npm.yml
name: Publish to npm
on:
  release:
    types: [created]
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          registry-url: 'https://registry.npmjs.org'
      - run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{secrets.NPM_TOKEN}}
```

## Next Steps

After publishing:
1. Update the main README.md to mention npm installation
2. Add npm badge to README
3. Create release notes
4. Announce on social media/forums

