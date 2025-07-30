# Veogen Frontend Build Troubleshooting Guide

## Issues Encountered and Solutions

### 1. Missing `public/index.html`
**Issue**: Build failed because `public/index.html` was missing.
**Solution**: Created a minimal `index.html` with the required root div for React mounting.
**Best Practice**:
- Always include `public/index.html` in Create React App projects
- Keep it minimal - React will handle the dynamic content
- Include essential meta tags and the root div

### 2. Missing Public Assets
**Issue**: Missing favicon.ico, logo192.png, logo512.png referenced in manifest.json
**Solution**: Created placeholder SVGs and updated manifest.json
**Best Practice**:
- Include all referenced assets in the public directory
- Use SVGs for logos when possible for better scaling
- Document all required assets in README

### 3. TypeScript Version Conflict
**Issue**: react-scripts@5.0.1 requires TypeScript ^3.2.1 || ^4, but had 5.8.3
**Solution**: Downgraded to TypeScript 4.9.5
**Best Practice**:
- Check peer dependencies before upgrading TypeScript
- Use `npm view react-scripts@5.0.1 peerDependencies` to check requirements
- Consider using `--legacy-peer-deps` as a temporary workaround

### 4. AJV Module Not Found
**Issue**: `Cannot find module 'ajv/dist/compile/codegen'`
**Solution**: Installed ajv@6.12.6 explicitly
**Best Practice**:
- When seeing module not found errors, check if the parent package needs a specific version
- Keep track of dependency versions that work together

### 5. Dependency Resolution Strategy
**What Worked**:
```bash
# Clean install with specific versions
rm -rf node_modules package-lock.json
npm install ajv@6.12.6 typescript@4.9.5 --legacy-peer-deps
npm install --legacy-peer-deps
```

**Recommended Workflow**:
1. Always start with `rm -rf node_modules package-lock.json` when facing dependency issues
2. Install dependencies with `--legacy-peer-deps` for projects with conflicting peer dependencies
3. Document all version-specific installations

## Common Gotchas

1. **Node.js Version**:
   - CRA 5.x works best with Node.js 16.x
   - Consider using nvm for version management

2. **Build Tools**:
   - On Windows, ensure Python and build tools are installed
   - Run `npm install -g windows-build-tools` if needed

3. **Environment Variables**:
   - Prefix with `REACT_APP_` to make them available in the React app
   - Document all required environment variables

## Future Recommendations

1. **Migrate to Vite**:
   - Faster builds and better developer experience
   - More flexible configuration
   - Better dependency management

2. **Dependency Management**:
   - Regularly update dependencies
   - Use `npm outdated` to check for updates
   - Consider using Yarn or pnpm for better dependency resolution

3. **Documentation**:
   - Document all required environment variables
   - Include a setup script for new developers
   - Document known issues and workarounds

## Debugging Tips

1. **Verbose Output**:
   ```bash
   npm run build -- --verbose
   ```

2. **Check Dependencies**:
   ```bash
   npm ls ajv
   npm ls typescript
   ```

3. **Clean Install**:
   ```bash
   rm -rf node_modules package-lock.json
   npm cache clean --force
   npm install
   ```

Remember to update this document as new issues are encountered and resolved.
