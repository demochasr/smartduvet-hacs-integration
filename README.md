# SmartDuvet Home Assistant Integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

**This is a custom integration for controlling SmartDuvet devices in Home Assistant.**

## Features

- **Climate Control**: Independent temperature control for left and right sides (1-11 device levels mapped to 20-29°C)
- **Light Control**: RGB LED lighting with intensity control
- **Make Bed Button**: Trigger the make bed functionality
- **Status Sensors**: WiFi connectivity and schedule status monitoring
- **Device Information**: Displays MAC address, IP, and firmware version
- **Local Control**: Works entirely over your local network (no cloud required)

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/smartduvet-ha-integration/smartduvet`
6. Select "Integration" as the category
7. Click "Add"
8. Search for "SmartDuvet" and install

### Manual Installation

1. Download the `smartduvet` folder from this repository
2. Copy it to your `custom_components` directory in your Home Assistant config folder
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for "SmartDuvet"
3. Enter your SmartDuvet device IP address
4. The integration will automatically discover and configure all entities

### Finding Your SmartDuvet IP Address

- Check your router's device list for "SmartDuvet" or the MAC address
- Use a network scanner app to find devices on your network
- Connect to the SmartDuvet WiFi hotspot and configure it to connect to your home WiFi

## Entities Created

This integration creates the following entities for each SmartDuvet device:

| Entity Type | Entity ID | Description |
|-------------|-----------|-------------|
| Climate | `climate.{device_name}_left` | Left side temperature control (20-29°C) |
| Climate | `climate.{device_name}_right` | Right side temperature control (20-29°C) |
| Light | `light.{device_name}` | RGB LED lighting control |
| Button | `button.{device_name}_makebed` | Trigger make bed action |
| Binary Sensor | `binary_sensor.{device_name}_wifi` | WiFi connection status |
| Sensor | `sensor.{device_name}_schedule` | Schedule status |

## Temperature Mapping

The SmartDuvet uses levels 1-11, which are mapped to Home Assistant temperatures:

- **Level 1-5**: Cool modes (20-24°C)
- **Level 6**: Neutral/Off (25°C)
- **Level 7-11**: Heat modes (25-29°C)

## Troubleshooting

### Device Not Found
- Ensure your SmartDuvet is connected to the same network as Home Assistant
- Check that the IP address is correct and reachable
- Verify the device is powered on and functioning

### Entities Not Updating
- Check the integration logs in **Settings** → **System** → **Logs**
- Verify network connectivity to the device
- Try reloading the integration

## Contributing

If you want to contribute to this integration, please read the [Contribution Guidelines](CONTRIBUTING.md).

## License

This project is under the MIT license.

---

[buymecoffee]: https://www.buymeacoffee.com/smartduvet
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/smartduvet-ha-integration/smartduvet.svg?style=for-the-badge
[commits]: https://github.com/smartduvet-ha-integration/smartduvet/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/smartduvet-ha-integration/smartduvet.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40smartduvet--integration-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/smartduvet-ha-integration/smartduvet.svg?style=for-the-badge
[releases]: https://github.com/smartduvet-ha-integration/smartduvet/releases