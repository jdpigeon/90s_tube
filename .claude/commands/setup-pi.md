# Setup 90s Tube Pi

Set up a fresh Raspberry Pi for the 90s_tube project. Follow these steps in order.

## Credentials & constants
- User: `nineties`, password: `tube`
- Hostname: `nineties.local`
- Project root: `/Users/dano/work/90s_tube`

All SSH/SCP commands use this pattern:
```bash
sshpass -p tube ssh -o StrictHostKeyChecking=no nineties@nineties.local "..."
sshpass -p tube scp -o StrictHostKeyChecking=no <src> nineties@nineties.local:<dst>
```

## Step 1 — Install sshpass

Install if not already present:
```bash
brew list sshpass 2>/dev/null || brew install hudochenkov/sshpass/sshpass
```

## Step 2 — Wait for Pi to be reachable

Poll until SSH responds (Pi may still be booting — first boot can take 2-3 minutes):
```bash
until sshpass -p tube ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 nineties@nineties.local "echo ok" 2>/dev/null; do
  echo "Waiting for Pi..."; sleep 5
done
echo "Pi is up!"
```

## Step 3 — Install packages

```bash
sshpass -p tube ssh -o StrictHostKeyChecking=no nineties@nineties.local \
  "sudo apt-get update -y && sudo apt-get install -y vlc supervisor"
```

This takes a few minutes. Wait for it to complete before continuing.

## Step 4 — Write audio config

Write `/etc/asound.conf`:
```bash
sshpass -p tube ssh -o StrictHostKeyChecking=no nineties@nineties.local "sudo tee /etc/asound.conf > /dev/null << 'EOF'
pcm.!default {
    type plug
    slave.pcm \"hdmi:CARD=vc4hdmi,DEV=0\"
}

ctl.!default {
    type hw
    card 1
}
EOF"
```

Append HDMI audio lines to `/boot/firmware/config.txt` (idempotent — skips if already present):
```bash
sshpass -p tube ssh -o StrictHostKeyChecking=no nineties@nineties.local \
  "grep -q 'hdmi_drive=2' /boot/firmware/config.txt || sudo tee -a /boot/firmware/config.txt > /dev/null << 'EOF'

# Force HDMI audio
hdmi_drive=2
hdmi_force_hotplug=1
hdmi_force_edid_audio=1
EOF"
```

## Step 5 — Deploy service files

Copy `service.py` to the Pi:
```bash
sshpass -p tube scp -o StrictHostKeyChecking=no /Users/dano/work/90s_tube/daemon/service.py nineties@nineties.local:/home/nineties/service.py
```

Copy supervisor config:
```bash
sshpass -p tube scp -o StrictHostKeyChecking=no /Users/dano/work/90s_tube/daemon/service.conf nineties@nineties.local:/tmp/service.conf
sshpass -p tube ssh -o StrictHostKeyChecking=no nineties@nineties.local \
  "sudo cp /tmp/service.conf /etc/supervisor/conf.d/service.conf"
```

## Step 6 — Create media directories

```bash
sshpass -p tube ssh -o StrictHostKeyChecking=no nineties@nineties.local \
  "sudo mkdir -p /media/shows /media/commercials && sudo chown -R nineties:nineties /media"
```

## Step 7 — Enable and start supervisor

```bash
sshpass -p tube ssh -o StrictHostKeyChecking=no nineties@nineties.local \
  "sudo systemctl enable supervisor && sudo systemctl start supervisor && sudo supervisorctl reread && sudo supervisorctl update"
```

## Step 8 — Verify service started (or is waiting for media)

```bash
sshpass -p tube ssh -o StrictHostKeyChecking=no nineties@nineties.local \
  "sudo supervisorctl status nineties-tube"
```

The service will show `BACKOFF` if `/media/shows/` is empty — this is expected. It will start properly once media is present.

Check logs if needed:
```bash
sshpass -p tube ssh -o StrictHostKeyChecking=no nineties@nineties.local "cat /tmp/stdout.log /tmp/stderr.log"
```

## Step 9 — Rsync media files

Ask the user where their shows and commercials are. They may be on this Mac or on another machine on the network.

**From this Mac:**
```bash
rsync -av --progress -e "sshpass -p tube ssh -o StrictHostKeyChecking=no" \
  /path/to/shows/ nineties@nineties.local:/media/shows/

rsync -av --progress -e "sshpass -p tube ssh -o StrictHostKeyChecking=no" \
  /path/to/commercials/ nineties@nineties.local:/media/commercials/
```

**From another machine on the network (e.g. Linux laptop)** — give the user these commands to run themselves on that machine:
```bash
rsync -av --progress -e ssh /path/to/shows/ nineties@nineties.local:/media/shows/
rsync -av --progress -e ssh /path/to/commercials/ nineties@nineties.local:/media/commercials/
```
Password: `tube`. Rsync is resumable — if interrupted, re-run the same command.

## Step 10 — Restart service after media is loaded

Once media transfer is complete:
```bash
sshpass -p tube ssh -o StrictHostKeyChecking=no nineties@nineties.local \
  "sudo supervisorctl restart nineties-tube && sudo supervisorctl status nineties-tube"
```

Expected output: `nineties-tube    RUNNING   pid XXXX, uptime 0:00:XX`
