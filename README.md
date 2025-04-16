# 90s_tube
linux daemon that plays 90s tv. for kids!

## TODOs
1. Flash Rasberry Pi OS Lite onto 512gb microSD card
  - NOTE: Do not eject drive after writing
  - set ssh and username/password
2. Copy dev videos onto card in media
2. Boot card with wifi adapter
3. install supervisor and vlc
- sudo apt-get update
- sudo apt install python3-pip vlc
4. Set configuration files

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
4. configure startup script
5. dev startup script (could do via ssh) c1254d4b860c
 - https://claude.ai/chat/6d93c9b8-8f65-496c-ae5d-c1254d4b860c  
6. delete dev videos
7. Clone disk image
8. Drop in shows
9. Try it out!