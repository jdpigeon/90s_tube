# 90s Tube — Claude Context

## What this is
A Raspberry Pi daemon that simulates a 90s TV channel for kids. Plays MP4 shows and commercials in a loop via VLC over HDMI. Runs headless on Raspberry Pi OS Lite.

## Pi access
- Hostname: `nineties.local`
- User: `nineties`, password: `tube`
- SSH is password-based — use `sshpass` for non-interactive commands:
  ```bash
  sshpass -p tube ssh -o StrictHostKeyChecking=no nineties@nineties.local "..."
  ```
- Install sshpass on Mac: `brew install hudochenkov/sshpass/sshpass`

## Media
- Shows live at `/media/shows/<show_name>/*.mp4` on the Pi
- Commercials live at `/media/commercials/*.mp4` on the Pi
- Only H.264/AVC encoded MP4s are tested
- Always transfer media over the network via rsync — never write directly to a mounted SD card (causes filesystem corruption)
- rsync from another machine requires `-e ssh` flag: `rsync -av -e ssh src/ nineties@nineties.local:/media/shows/`

## Service
- Managed by `supervisord`, process name: `nineties-tube`
- Logs: `/tmp/stdout.log` and `/tmp/stderr.log` on the Pi
- Service crashes on start if `/media/shows/` is empty — this is expected, not a bug
- Restart after adding media: `sudo supervisorctl restart nineties-tube`

## SD card setup
- Use `/setup-pi` skill for full automated setup of a fresh card
- Flash with Raspberry Pi Imager → boot → rsync media → done
- Do NOT copy media to the card before booting — the ext4 rootfs is unexpanded (~2GB) until first boot

## Hardware
- Raspberry Pi (not Zero/Zero W — too slow for video decoding)
- HDMI for video + audio output
- Audio device: `hdmi:CARD=vc4hdmi,DEV=0`
