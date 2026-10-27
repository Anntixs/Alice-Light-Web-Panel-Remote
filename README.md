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

## Windows + Node.js (local network)

Install [Node.js 20 or newer](https://nodejs.org/) and Git on the Windows PC. In PowerShell:

```powershell
git clone https://github.com/Anntixs/Alice-Light-Web-Panel-Remote.git
cd Alice-Light-Web-Panel-Remote
$env:ALICE_PANEL_TOKEN = [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
$env:ALICE_BIND = '0.0.0.0'
$env:ALICE_PORT = '8765'
Write-Host "Save panel token: $env:ALICE_PANEL_TOKEN"
.\start-windows.ps1
```

No `npm install` is required: the Node backend uses only built-in modules. Find the PC address with `ipconfig`, then open `http://PC_IP:8765` on a phone connected to the same Wi-Fi. Enter the saved token. Allow inbound TCP port 8765 only on Windows **Private** network and preferably only from your LAN. For example, in an elevated PowerShell, substituting your actual subnet:

```powershell
New-NetFirewallRule -DisplayName 'Alice Light Panel LAN' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8765 -Profile Private -RemoteAddress 192.168.1.0/24
```

For SSH monitoring, Windows OpenSSH Client must be installed. Configure key authentication for the Windows user running the panel and verify the speaker host key in that user's `known_hosts` before selecting SSH in the setup screen. Node launches only fixed read-only commands. To stop the panel, press Ctrl+C. To run it again, set the **same** token (store it securely on the PC) and execute `.\start-windows.ps1`. Never expose port 8765 directly to the internet; plain HTTP on a LAN does not encrypt the token. Use HTTPS reverse proxy if encryption is needed.

Run `node --test tests/node.test.js` for Node tests. A socket-capable machine is required for the API integration test.

## Полный форк панели dimap для первой Станции Лайт

Полная копия исходного проекта [dimap/yandex-station-web](https://github.com/dimap/yandex-station-web) с сохранённой MIT-лицензией лежит в [`upstream-fork/`](upstream-fork/). Это отдельное приложение; прежний лёгкий backend в корне проекта сохранён. Для запуска форка на Windows откройте папку `upstream-fork` и выполните `start.bat`. Форк требует root-доступ по **ADB**, как и исходный проект; имеющийся доступ по SSH на порту 2222 сам по себе для него недостаточен.

Изменения для первой Лайт: отдельный профиль `lite` с `yandexmicro`, распознавание `Station Micro`, выбор этого профиля по умолчанию, скрытые часы и отключённая непроверенная запись в подсветку, заставку и будильник. Плеер использует Glagol из исходного проекта. Не выбирайте вручную профиль `lite2` для первой Лайт. Функции файлов и root-консоли исходного проекта остаются мощными операциями; установите пароль доступа и не публикуйте порт панели в интернет. Аппаратное тестирование на первой Лайт ещё не проведено.
