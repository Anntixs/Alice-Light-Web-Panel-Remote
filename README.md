# Alice Light Web Panel Remote

PC hosted dashboard for first generation Yandex Station Light. **Prototype with read only SSH monitoring and mock mode.** No files are installed on the speaker. Player, lighting, Quasar and Glagol commands are disabled until device specific interfaces are verified. The project does not claim full hardware control.

## Install on Linux

```sh
./install.sh
export ALICE_PANEL_TOKEN='choose-a-long-random-secret'
./start.sh
```

Open http://127.0.0.1:8765. To access it from a trusted LAN, set `ALICE_BIND` to the PC's LAN address and restrict port 8765 to that subnet with your firewall. Use a trusted HTTPS reverse proxy for remote phones. Browser stores the token in sessionStorage, so HTTPS is necessary outside localhost.

The setup page accepts a private device IP, mock or SSH, and sampling interval. Settings are stored only in `data/settings.json` on the PC. SSH requires preconfigured key authentication and a verified entry in the PC user's `known_hosts`. No password or SSH key is sent to the browser. The SSH probe uses fixed commands only. Ensure the service user's SSH host key and keypair are configured before starting as systemd. The service template uses a dedicated `alicepanel` account; provision it and set ownership/permissions before enabling it.

## Research and hardware limits

The requested HackAlice and yandex-station-web URLs were inaccessible in this environment (proxy connection refused). Therefore commands and sysfs LED paths for first generation Light could not be verified. QuasarAdapter, GlagolAdapter, ADBAdapter and LightingAdapter report unsupported. SSHAdapter runs only a fixed read only batch for Linux system data. Wi-Fi signal, CPU load, Quasar version, player metadata, LED zones and restart actions remain unavailable instead of fabricated. No agent is installed. The pictured device is a CSS illustration, not a product image. The reference screenshot's clock screen was intentionally omitted.

## Hardware test plan

1. Confirm device identity and firmware version on a physical first generation Light.
2. Verify SSH host key fingerprint out of band; use a limited network and key authentication.
3. Check `/proc/uptime`, `/proc/meminfo`, thermal zone and filesystem outputs against device readings.
4. Disconnect/reboot device and confirm 503/connection status, then reconnect.
5. Document verified Quasar, Glagol, ADB and LED interfaces before enabling controls.
6. Check audio and light effects after any future write control.

## API

Every `/api/` route requires `X-Panel-Token`. Implemented routes: status, system, player, player/control, lighting, settings. Unsupported operations return 501. No arbitrary shell parameters are accepted.
