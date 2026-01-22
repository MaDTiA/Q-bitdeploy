#!/usr/bin/env python3
"""
Q-bitdeploy - qBittorrent Docker Installer for Debian/Ubuntu
Interactive setup with install/remove/custom port/password display
Supports $HOME/docker, /storage, and custom paths

Author: MaDTiA
GitHub: https://github.com/MaDTiA
Website: https://madtia.cc
"""

import subprocess
import os
import sys
import time
from pathlib import Path

# Default configurations
DEFAULT_PORT = 2096
DEFAULT_IMAGE = "linuxserver/qbittorrent"
TORRENT_PORT = 6881

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_color(msg, color=Colors.CYAN):
    """Print colored output"""
    print(f"{color}{msg}{Colors.END}")

def print_footer():
    """Display promotional footer"""
    print_color("\n" + "─" * 60, Colors.CYAN)
    print_color("⭐ Enjoyed Q-bitdeploy? Check out more projects!", Colors.GREEN)
    print_color("   GitHub: https://github.com/MaDTiA", Colors.BLUE)
    print_color("   Website: https://madtia.cc", Colors.BLUE)
    print_color("─" * 60 + "\n", Colors.CYAN)

def run_cmd(cmd, check=True, capture=False, shell=True):
    """Run shell command with error handling"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=capture, text=True, check=check)
        return result.stdout.strip() if capture else True
    except subprocess.CalledProcessError as e:
        print_color(f"[ERROR] Command failed", Colors.RED)
        if capture and e.stderr:
            print_color(f"Details: {e.stderr}", Colors.RED)
        return False

def check_root():
    """Ensure script runs with sudo privileges"""
    if os.geteuid() != 0:
        print_color("[WARNING] This script requires sudo privileges", Colors.YELLOW)
        print_color("Restarting with sudo...\n", Colors.YELLOW)
        os.execvp("sudo", ["sudo", "python3"] + sys.argv)

def ensure_dirs(base_path):
    """Create required directories"""
    config_dir = Path(base_path) / "config"
    downloads_dir = Path(base_path) / "downloads"
    
    run_cmd(f"mkdir -p {config_dir}")
    run_cmd(f"mkdir -p {downloads_dir}")
    print_color(f"[OK] Created: {base_path}", Colors.GREEN)

def get_temp_password():
    """Extract temporary password from logs"""
    print_color("\n[INFO] Extracting WebUI password from logs...", Colors.CYAN)
    time.sleep(12)
    
    logs = run_cmd("docker logs qbittorrent 2>&1 | grep -i 'temporary password'", capture=True, check=False)
    if logs:
        print_color(f"[PASSWORD] {logs}", Colors.GREEN)
        return True
    
    print_color("[WARNING] No temp password found (may already be set)", Colors.YELLOW)
    return False

def install_docker():
    """Install and enable Docker"""
    print_color("\n[INSTALL] Installing Docker...", Colors.BLUE)
    
    if not run_cmd("apt-get update"):
        return False
    
    if not run_cmd("apt-get install -y docker.io"):
        return False
    
    if not run_cmd("systemctl enable --now docker"):
        return False
    
    print_color("[OK] Docker installed and running", Colors.GREEN)
    return True

def stop_existing_container():
    """Stop and remove existing qBittorrent container"""
    print_color("\n[CHECK] Checking for existing container...", Colors.YELLOW)
    run_cmd("docker stop qbittorrent 2>/dev/null", check=False)
    run_cmd("docker rm qbittorrent 2>/dev/null", check=False)

def install_qbittorrent():
    """Interactive installation"""
    print_color("=" * 60, Colors.HEADER)
    print_color("Q-bitdeploy - qBittorrent Docker Installation", Colors.HEADER)
    print_color("=" * 60, Colors.HEADER)
    
    # Storage path selection
    print_color("\nSelect storage location:", Colors.CYAN)
    print("  1) $HOME/docker/qbittorrent (User home directory)")
    print("  2) /storage/qbittorrent (System/External storage)")
    print("  3) Custom path")
    
    choice = input("\nChoice [1]: ").strip() or "1"
    
    if choice == "2":
        base_path = "/storage/qbittorrent"
    elif choice == "3":
        base_path = input("Enter custom path (e.g. /mnt/data/qbittorrent): ").strip()
        if not base_path:
            print_color("[ERROR] Path cannot be empty", Colors.RED)
            return False
    else:
        home = os.path.expanduser("~" if os.geteuid() != 0 else f"~{os.getenv('SUDO_USER', 'root')}")
        base_path = f"{home}/docker/qbittorrent"
    
    # Custom port with validation
    while True:
        port_input = input(f"\nWebUI Port [{DEFAULT_PORT}]: ").strip() or str(DEFAULT_PORT)
        try:
            port = int(port_input)
            if 1024 <= port <= 65535:
                break
            else:
                print_color("[ERROR] Port must be between 1024-65535", Colors.RED)
        except ValueError:
            print_color("[ERROR] Invalid port number", Colors.RED)
    
    # Custom torrent port
    torrent_port_input = input(f"Torrent Port [{TORRENT_PORT}]: ").strip() or str(TORRENT_PORT)
    try:
        torrent_port = int(torrent_port_input)
    except ValueError:
        torrent_port = TORRENT_PORT
    
    # Credentials option
    print_color("\nWebUI Credentials:", Colors.CYAN)
    print("  1) Use default (temporary password from logs)")
    print("  2) Set custom credentials now")
    
    cred_choice = input("\nChoice [1]: ").strip() or "1"
    
    custom_creds = ""
    username = None
    password = None
    
    if cred_choice == "2":
        username = input("Username [admin]: ").strip() or "admin"
        password = input("Password [adminadmin]: ").strip() or "adminadmin"
        custom_creds = f"-e WEBUI_USERNAME={username} -e WEBUI_PASSWORD={password} "
    
    # Timezone
    tz = input("\nTimezone [Europe/Rome]: ").strip() or "Europe/Rome"
    
    # Get UID/GID
    if os.getenv('SUDO_USER'):
        uid = run_cmd(f"id -u {os.getenv('SUDO_USER')}", capture=True)
        gid = run_cmd(f"id -g {os.getenv('SUDO_USER')}", capture=True)
    else:
        uid = os.getuid()
        gid = os.getgid()
    
    # Install Docker
    if not install_docker():
        return False
    
    # Prepare directories
    ensure_dirs(base_path)
    
    # Stop existing container
    stop_existing_container()
    
    # Build Docker run command
    docker_cmd = f"""docker run -d --name=qbittorrent \
        -e PUID={uid} \
        -e PGID={gid} \
        -e TZ={tz} \
        -e WEBUI_PORT={port} \
        {custom_creds}\
        -p {port}:{port} \
        -p {torrent_port}:{torrent_port} \
        -p {torrent_port}:{torrent_port}/udp \
        -v {base_path}/config:/config \
        -v {base_path}/downloads:/downloads \
        --restart unless-stopped \
        {DEFAULT_IMAGE}"""
    
    print_color(f"\n[DOCKER] Starting qBittorrent container...", Colors.BLUE)
    
    if not run_cmd(docker_cmd):
        return False
    
    print_color("\n" + "=" * 60, Colors.GREEN)
    print_color("[SUCCESS] qBittorrent container started!", Colors.GREEN)
    print_color("=" * 60, Colors.GREEN)
    
    print_color(f"\nWebUI URL: http://localhost:{port}", Colors.CYAN)
    print_color(f"Config: {base_path}/config", Colors.CYAN)
    print_color(f"Downloads: {base_path}/downloads", Colors.CYAN)
    print_color(f"Torrent Port: {torrent_port}", Colors.CYAN)
    
    # Always show credentials at the end
    if cred_choice == "2":
        print_color(f"\n[CREDENTIALS]", Colors.HEADER)
        print_color(f"Username: {username}", Colors.GREEN)
        print_color(f"Password: {password}", Colors.GREEN)
    
    # Always attempt to show password from logs
    get_temp_password()
    
    # Show footer
    print_footer()
    
    return True

def show_password():
    """Display temporary password from logs"""
    print_color("\n[INFO] Checking qBittorrent logs for password...", Colors.CYAN)
    
    # Check if container exists
    container_check = run_cmd("docker ps -a --filter name=qbittorrent --format '{{.Names}}'", capture=True, check=False)
    if container_check != "qbittorrent":
        print_color("[ERROR] qBittorrent container not found", Colors.RED)
        return False
    
    get_temp_password()
    return True

def remove_qbittorrent():
    """Complete removal of qBittorrent and Docker"""
    print_color("=" * 60, Colors.RED)
    print_color("qBittorrent Docker Removal", Colors.RED)
    print_color("=" * 60, Colors.RED)
    
    confirm = input("\n[WARNING] This will remove qBittorrent, Docker, and all data. Continue? [y/N]: ").strip().lower()
    if confirm != 'y':
        print_color("[CANCELLED] Removal cancelled", Colors.YELLOW)
        return False
    
    print_color("\n[STOP] Stopping container...", Colors.YELLOW)
    run_cmd("docker stop qbittorrent 2>/dev/null", check=False)
    
    print_color("[REMOVE] Removing container...", Colors.YELLOW)
    run_cmd("docker rm qbittorrent 2>/dev/null", check=False)
    
    print_color("[REMOVE] Removing image...", Colors.YELLOW)
    run_cmd("docker rmi linuxserver/qbittorrent 2>/dev/null", check=False)
    
    # Detect and remove data directories
    home = os.path.expanduser("~" if os.geteuid() != 0 else f"~{os.getenv('SUDO_USER', 'root')}")
    paths_to_check = [
        f"{home}/docker/qbittorrent",
        "/storage/qbittorrent"
    ]
    
    for path in paths_to_check:
        if Path(path).exists():
            remove = input(f"\n[CONFIRM] Remove {path}? [y/N]: ").strip().lower()
            if remove == 'y':
                run_cmd(f"rm -rf {path}")
                print_color(f"[OK] Removed {path}", Colors.GREEN)
    
    remove_docker = input("\n[CONFIRM] Remove Docker entirely? [y/N]: ").strip().lower()
    if remove_docker == 'y':
        print_color("[STOP] Stopping Docker...", Colors.YELLOW)
        run_cmd("systemctl disable --now docker", check=False)
        
        print_color("[PURGE] Purging Docker...", Colors.YELLOW)
        run_cmd("apt-get purge -y docker.io", check=False)
        run_cmd("apt-get autoremove -y", check=False)
        run_cmd("apt-get autoclean", check=False)
        
        print_color("[OK] Docker removed", Colors.GREEN)
    
    print_color("\n[COMPLETE] Removal complete", Colors.GREEN)
    print_footer()
    return True

def show_status():
    """Display container status"""
    print_color("\n[STATUS] qBittorrent Container Status:", Colors.CYAN)
    run_cmd("docker ps -a --filter name=qbittorrent --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'", check=False)

def main():
    """Main menu"""
    check_root()
    
    while True:
        print_color("\n" + "=" * 60, Colors.HEADER)
        print_color("Q-bitdeploy - qBittorrent Docker Manager", Colors.HEADER)
        print_color("by MaDTiA", Colors.CYAN)
        print_color("=" * 60, Colors.HEADER)
        
        print("\n1) Install qBittorrent")
        print("2) Show WebUI Password")
        print("3) Show Status")
        print("4) Remove qBittorrent")
        print("5) Exit")
        
        choice = input("\nSelect option [1-5]: ").strip()
        
        if choice == "1":
            install_qbittorrent()
        elif choice == "2":
            show_password()
        elif choice == "3":
            show_status()
        elif choice == "4":
            remove_qbittorrent()
        elif choice == "5":
            print_color("\n" + "=" * 60, Colors.GREEN)
            print_color("Thanks for using Q-bitdeploy!", Colors.GREEN)
            print_color("=" * 60, Colors.GREEN)
            print_footer()
            print_color("Happy seeding! 🌱\n", Colors.CYAN)
            sys.exit(0)
        else:
            print_color("[ERROR] Invalid choice", Colors.RED)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_color("\n\n[INTERRUPTED] Cancelled by user", Colors.YELLOW)
        print_footer()
        sys.exit(1)
