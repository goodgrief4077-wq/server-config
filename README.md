# Server Config — Ubuntu 24.04 ThinkPad

Configuration for running a ThinkPad laptop as an always-on server.

## What's included

### `logind.conf`
- Lid close does NOT suspend the laptop
- Works on both battery and AC power

### `tlp.conf`
- Battery charges up to **80%** (stop threshold)
- Battery resumes charging at **40%** (start threshold)
- Extends battery lifespan up to 3x vs always charging to 100%

## How to apply

```bash
sudo cp logind.conf /etc/systemd/logind.conf
sudo systemctl restart systemd-logind

sudo apt install -y tlp tlp-rdw
sudo cp tlp.conf /etc/tlp.conf
sudo systemctl enable --now tlp
sudo tlp start
```

## Verify

```bash
# Check lid config
grep HandleLidSwitch /etc/systemd/logind.conf

# Check battery thresholds
cat /sys/class/power_supply/BAT0/charge_control_start_threshold
cat /sys/class/power_supply/BAT0/charge_control_end_threshold
```
