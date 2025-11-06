# Website Deployment Guide

This directory contains the static website for ffmcp.org.

## Files

- `index.html` - Main homepage
- `style.css` - Stylesheet
- `CNAME` - Custom domain configuration for GitHub Pages

## Deployment Options

### Option 1: GitHub Pages

1. **Enable GitHub Pages:**
   - Go to your repository settings on GitHub
   - Navigate to "Pages" in the left sidebar
   - Under "Source", select "Deploy from a branch"
   - Choose the `main` branch and `/docs` folder
   - Click "Save"

2. **Configure Custom Domain:**
   - The `CNAME` file is already configured for `ffmcp.org`
   - In your domain registrar, add a CNAME record:
     - Name: `@` (or `www`)
     - Value: `brandonhenry.github.io`
   - GitHub will automatically provision SSL certificates

3. **Your site will be available at:**
   - `https://brandonhenry.github.io/ffmcp` (temporary)
   - `https://ffmcp.org` (after DNS propagates)

### Option 2: Netlify

1. **Sign up/Login:**
   - Go to [netlify.com](https://netlify.com)
   - Sign up or log in with your GitHub account

2. **Deploy:**
   - Click "Add new site" → "Import an existing project"
   - Connect your GitHub repository
   - Netlify will detect the `netlify.toml` configuration
   - Build settings:
     - Build command: (leave empty, no build needed)
     - Publish directory: `docs`
   - Click "Deploy site"

3. **Configure Custom Domain:**
   - Go to Site settings → Domain management
   - Click "Add custom domain"
   - Enter `ffmcp.org`
   - Follow Netlify's DNS instructions:
     - Add an A record pointing to Netlify's load balancer IPs
     - Or add a CNAME record pointing to your Netlify subdomain
   - Netlify will automatically provision SSL certificates

## DNS Configuration

For `ffmcp.org` domain:

### GitHub Pages:
- Add CNAME record: `@` → `brandonhenry.github.io`
- Or A records: Point to GitHub Pages IPs (see GitHub Pages docs)

### Netlify:
- Add A records pointing to Netlify's load balancer IPs
- Or CNAME: `@` → `your-site-name.netlify.app`

## Testing Locally

You can test the website locally by opening `index.html` in a browser, or using a simple HTTP server:

```bash
cd docs
python3 -m http.server 8000
```

Then visit `http://localhost:8000`

## Notes

- The website is a simple static site, no build process required
- All files are in the `docs/` directory
- Both GitHub Pages and Netlify support custom domains with free SSL
- DNS propagation can take 24-48 hours

