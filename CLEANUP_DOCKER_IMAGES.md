# Docker Images Cleanup Guide

## Images You Can Safely Delete

### Old/unused images (can delete):

1. **`<old-backend-image>:latest`** (1.6 GB) ❌ **DELETE**
   - Old backend image from previous project setup
   - No longer used (backend was removed)
   - **Safe to delete**

2. **`<old-scrapers-image>:latest`** (1.5 GB) ❌ **DELETE**
   - Old scrapers image (before we renamed to `staatsoper-scraper`)
   - Replaced by `staatsoper-scraper:latest`
   - **Safe to delete**

### Images You Need to Keep:

1. **`staatsoper-scraper:latest`** (1.5 GB) ✅ **KEEP**
   - Current scraper image (in use)
   - Built from `./scraper` directory

2. **`mcr.microsoft.com/azure-storage/azurite:latest`** (427 MB) ✅ **KEEP**
   - Used for local queue storage
   - Currently running as `staatsoper-azurite` container
   - **Note**: Your list shows it as "Unused" but it's actually in use!

## Quick Cleanup Commands

### Delete Old Images:

```bash
# Delete old backend image (replace with actual image name)
docker rmi <old-backend-image>:latest

# Delete old scrapers image (replace with actual image name)
docker rmi <old-scrapers-image>:latest
```

### Or delete both at once:

```bash
docker rmi <old-backend-image>:latest <old-scrapers-image>:latest
```

### Verify what's left:

```bash
docker images | grep staatsoper
# Should only show: staatsoper-scraper:latest
```

## Other Images (Not Related)

The other images in your list are for other services:
- `cloudflare/cloudflared` - Cloudflare tunnel
- `jc21/nginx-proxy-manager` - Nginx proxy
- `local-ssh-page` - SSH page service
- `louislam/uptime-kuma` - Uptime monitoring
- `mongo:latest` - MongoDB (might be for other projects)
- `nginx:alpine` - Nginx
- `nickfedor/watchtower` - Auto-update containers
- `portainer/agent` - Portainer monitoring
- `vaultwarden/server` - Password manager

**Only delete these if you're sure you don't need them for other projects!**

## Space Saved

Deleting the two old images will free up approximately:
- **~3.1 GB** of disk space

## After Cleanup

Your setup will only have:
- `staatsoper-scraper:latest` - Current scraper (in use)
- `mcr.microsoft.com/azure-storage/azurite:latest` - Queue storage (in use)

Everything will continue working normally!
