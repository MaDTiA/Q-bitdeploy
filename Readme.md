# Q-bitdeploy

Deploy qBittorrent in Docker with confidence. Q-bitdeploy handles the entire setup process on Debian/Ubuntu systems, from Docker installation to container configuration. No unnecessary complexity, just clean, reliable automation for server environments.

## What It Does

Q-bitdeploy automates your qBittorrent Docker deployment from start to finish. Whether you're setting up a home server or managing a seedbox, you'll get sensible defaults and full customization when you need it.

## Key Features

- **Flexible Storage Options**: Store your data in your home directory, system storage (`/storage`), or any custom path you choose
- **Configurable Ports**: Set custom WebUI and torrent ports to match your network setup
- **Credential Management**: Generate temporary passwords automatically or set permanent credentials during installation
- **Password Recovery**: Retrieve temporary passwords anytime from container logs
- **Selective Removal**: Remove components individually or clean up everything- your choice
- **Status Monitoring**: Quick health checks for your container
- **Zero Dependencies**: Built with Python 3 standard library only
- **Production Ready**: Designed for headless servers and automated deployments

## What You'll Need

- Debian 10+ or Ubuntu 18.04+
- Python 3.6 or newer
- Root or sudo access
- Internet connection

## Quick Start

Download and run Q-bitdeploy in one command:

wget https://raw.githubusercontent.com/MaDTiA/Q-bitdeploy/main/qbitdeploy.py && chmod +x qbitdeploy.py && sudo python3 qbitdeploy.py


Or download first, then execute:

`wget https://raw.githubusercontent.com/MaDTiA/Q-bitdeploy/main/qbitdeploy.py`
`chmod +x qbitdeploy.py`
`sudo python3 qbitdeploy.py`

## How It Works

Q-bitdeploy presents a straightforward menu:

Q-bitdeploy - qBittorrent Docker Manager
1) Install qBittorrent
2) Show WebUI Password
3) Show Status
4) Remove qBittorrent
5) Exit


### Installing qBittorrent

The installation wizard guides you through these configuration steps:

**Storage Location**  
Choose where your torrents and configuration files live:
- `$HOME/docker/qbittorrent` - Your home directory (survives system upgrades)
- `/storage/qbittorrent` - Dedicated storage mount
- Custom path - Specify any location (e.g., `/mnt/external/qbittorrent`)

**Port Configuration**  
- **WebUI Port**: Default 2096 (valid range: 1024-65535)
- **Torrent Port**: Default 6881 (customize as needed)

**Access Credentials**  
- Use a temporary password (extracted from logs after install)
- Or set a permanent username and password immediately

**Timezone**  
- Default: Europe/Rome
- Customize for accurate timestamps in your region

### Retrieving Your Password

Forgot your temporary password? Select option 2 from the menu to extract it from the container logs. Works whether your container is freshly installed or already running.

### Checking Status

Option 3 displays your container's current state, uptime, and active port mappings- helpful for quick troubleshooting.

### Removing qBittorrent

Option 4 walks you through removal with granular control:
- Stop and remove the container
- Remove the Docker image
- Optionally delete data directories
- Optionally purge Docker entirely

Each step asks for confirmation to prevent accidental data loss.

## Real-World Examples

### Home Server Setup


Storage: $HOME/docker/qbittorrent
WebUI Port: 2096
Torrent Port: 6881
Credentials: Temporary password
Timezone: Europe/Rome

Access at: `http://localhost:2096`

### Seedbox Configuration


Storage: /storage/qbittorrent
WebUI Port: 8443
Torrent Port: 51413
Credentials: admin / your_secure_password
Timezone: America/New_York


Access at: `http://your-server:8443`

### External Drive Setup


Storage: /mnt/external/qbittorrent
WebUI Port: 3000
Torrent Port: 6881
Credentials: Temporary password
Timezone: Asia/Tokyo


Access at: `http://localhost:3000`

## Advanced Usage

### Scripted Installation

You can automate Q-bitdeploy by piping responses:

`echo -e "1\n2\n8443\n6881\n2\nadmin\nsecurepass\nEurope/Rome\n" | sudo python3 qbitdeploy.py`


### Understanding the Docker Command

Q-bitdeploy generates commands equivalent to:

`docker run -d \
  --name=qbittorrent \
  -e PUID=1000 \
  -e PGID=1000 \
  -e TZ=Europe/Rome \
  -e WEBUI_PORT=2096 \
  -p 2096:2096 \
  -p 6881:6881 \
  -p 6881:6881/udp \
  -v /path/to/config:/config \
  -v /path/to/downloads:/downloads \
  --restart unless-stopped \
  linuxserver/qbittorrent`


### Manual Password Retrieval

Check the password outside Q-bitdeploy:

docker logs qbittorrent 2>&1 | grep -i "temporary password"

## Troubleshooting

### Port Already in Use

**Symptom**: `Error starting userland proxy: listen tcp 0.0.0.0:2096: bind: address already in use`

**Solution**: Choose a different port during installation, or identify and stop the conflicting service:

`sudo lsof -i :2096  # Find what's using the port`
`sudo docker stop qbittorrent  # Stop existing container`

### Permission Denied on /storage

**Symptom**: `mkdir: cannot create directory '/storage/qbittorrent': Permission denied`

**Solution**: Create the directory and set proper permissions:

`sudo mkdir -p /storage`
`sudo chown $USER:$USER /storage`


### Container Won't Start

First, check the logs:

`docker logs qbittorrent`


Common causes:
- Port conflicts (try different ports)
- Insufficient disk space (run `df -h`)
- Corrupted configuration (remove and reinstall)

### Docker Service Issues

Ensure Docker is running:

`sudo systemctl enable docker`
`sudo systemctl start docker`
`sudo systemctl status docker`


### No Password in Logs

Temporary passwords appear only on the first container start. If you don't see one:

1. Wait 15-20 seconds after installation completes
2. Check manually: `docker logs qbittorrent | grep password`
3. Use menu option 2 to retry extraction
4. Try common defaults in the WebUI if password was previously set

## Managing Your Container

### Basic Controls

`docker stop qbittorrent`   # Stop the container
`docker start qbittorrent`  # Start it back up
`docker restart qbittorrent`  # Restart

### Container Shell Access

`docker exec -it qbittorrent bash`

### Live Log Monitoring

`docker logs -f qbittorrent`

### Updating to Latest Version

`docker stop qbittorrent`
`docker rm qbittorrent`
`docker pull linuxserver/qbittorrent:latest`
# Re-run Q-bitdeploy (your config and downloads remain intact)

## Understanding File Structure

Your data persists outside the container in your chosen storage path:
Removing the container never touches these directories unless you explicitly choose to delete them.

## Security Best Practices

1. **Change Default Credentials**: Update the temporary password in WebUI settings after first login
2. **Configure Firewall**: Restrict WebUI access if your server is internet-facing
3. **Use Reverse Proxy**: Add HTTPS with nginx or Caddy for remote access
4. **VPN Integration**: Route traffic through a VPN container for privacy

### Auto-start Behavior

Docker's `--restart unless-stopped` flag handles automatic startup on boot- no additional configuration needed.

## Frequently Asked Questions

**Can I run multiple instances?**  
Yes. Use different container names and ports for each instance:

`docker run -d --name=qbittorrent-movies -e WEBUI_PORT=2096 -p 2096:2096 ...`
`docker run -d --name=qbittorrent-tv -e WEBUI_PORT=2097 -p 2097:2097 ...`


**How do I back up my configuration?**  
Archive the config directory:
`tar -czf qbittorrent-backup-$(date +%F).tar.gz /path/to/config/`


**Does this work on Raspberry Pi?**  
Yes, with ARM-compatible images. Modify the `DEFAULT_IMAGE` variable in the script:
docker pull linuxserver/qbittorrent:arm64v8-latest

**Can I use a different qBittorrent version?**  
Absolutely. Edit the `DEFAULT_IMAGE` variable at the top of `qbitdeploy.py` to use any compatible Docker image.

**What if I need to change ports after installation?**  
The easiest approach is to use option 4 (Remove), then reinstall with new ports. Your configuration files remain safe if you choose not to delete them during removal.

## Contributing

Found a bug or have an idea? Open an issue or submit a pull request on [GitHub](https://github.com/MaDTiA/Q-bitdeploy). Q-bitdeploy prioritizes simplicity- feature requests should align with that philosophy.

## License

MIT License. Use it however you want, modify it as needed, share it freely.

## Author

**MaDTiA** - [GitHub Profile](https://github.com/MaDTiA)

## Credits

Built for server administrators who value clean, scriptable deployments. Q-bitdeploy uses the excellent [linuxserver/qbittorrent](https://hub.docker.com/r/linuxserver/qbittorrent) Docker image maintained by LinuxServer.io.

***

*Q-bitdeploy is an independent tool, not affiliated with qBittorrent or LinuxServer.io.*
 
