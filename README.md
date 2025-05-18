# 90s_tube
linux daemon that plays 90s tv. for kids!

## Install Steps for fresh SD Card 
1. Flash Rasberry Pi OS Lite onto microSD card
  - NOTE: Do not eject drive after writing
  - set ssh and username/password
2. Copy videos onto card in media
  - Shows should live in `/media/shows/name_of_show/*.mp4`
  - Commercials should lve in `/media/commercials/*.mp4`
  - Only H.264/AVC encode .mp4 files have been tested.
3. Boot card in pi, connect wifi adapter
4. install supervisor and vlc
- sudo apt-get update
- sudo apt install python3-pip vlc supervisor
5. Set audio configuration files
/etc/asound.conf:
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

/boot/firmware/config.txt
```
# Add these lines
# Force HDMI audio
hdmi_drive=2
hdmi_force_hotplug=1
hdmi_force_edid_audio=1
```
NOTE: vlc needs to be prefixed with "--aout=alsa --alsa-audio-device=hdmi:CARD=vc4hdmi,DEV=0"
6. configure startup script
- set supervisord.conf in /etc/supervisor
- sudo systemctl enable supervisor
- sudo systemctl start supervisor
- sudo supervisorctl reread
- sudo supervisorctrl update
7. Copy service.py to ~ 
8. Clone disk image for easier install next time
9. Plug it in!