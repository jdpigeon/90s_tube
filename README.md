# 📺 90s_tube

🛋️ A Linux daemon that plays 90s TV shows and commercials in a loop. For kids!

Runs on a Raspberry Pi connected to your TV. Automatically alternates between shows with commercial breaks, just like you remember. No remote needed — just plug it in. 🌈

## 🚌 Install Steps for Fresh SD Card

1. **Flash Raspberry Pi OS Lite** onto a microSD card using Raspberry Pi Imager
   - Enable SSH and set username/password during flashing
   - Set hostname, username (`nineties`), and WiFi credentials
   - Do **not** copy media to the card before booting — the filesystem expands on first boot

2. **Boot the Pi** and wait 2-3 minutes for first-boot setup to complete

3. **Run the setup skill** in Claude Code from this repo:
   ```
   /setup-pi
   ```
   This installs dependencies, writes audio config, deploys the service, and guides you through transferring media.

4. **Transfer your media** over the network via rsync (the skill will prompt you for paths):
   - Shows → `/media/shows/<show_name>/*.mp4`
   - Commercials → `/media/commercials/*.mp4`
   - Only H.264/AVC encoded MP4s are tested

5. 🪱 **Plug it in and enjoy!**

## 🐾 Manual Setup (without the skill)

If you prefer to set up manually:

```bash
# Install dependencies
sudo apt-get update
sudo apt install vlc supervisor -y
```

**`/etc/asound.conf`:**
```
pcm.!default {
    type plug
    slave.pcm "hdmi:CARD=vc4hdmi,DEV=0"
}

ctl.!default {
    type hw
    card 1
}
```

**`/boot/firmware/config.txt`** — add these lines:
```
# Force HDMI audio
hdmi_drive=2
hdmi_force_hotplug=1
hdmi_force_edid_audio=1
```

Then deploy the service:
```bash
sudo cp daemon/service.conf /etc/supervisor/conf.d/service.conf
cp daemon/service.py ~/service.py
sudo systemctl enable supervisor
sudo systemctl start supervisor
sudo supervisorctl reread
sudo supervisorctl update
```

## 📼 Media Format

- Container: `.mp4`
- Video codec: H.264/AVC (only format tested)
- Shows: `/media/shows/<show_name>/*.mp4` — each subdirectory is a different show
- Commercials: `/media/commercials/*.mp4`

## 🖥️ Hardware

- Raspberry Pi (3B+ or newer recommended — Zero is too slow for video decoding)
- MicroSD card (32GB+ recommended, SanDisk or Samsung for reliability)
- HDMI cable
