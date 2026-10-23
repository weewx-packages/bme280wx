# bme280wx

_Copyright (c) 2019, WJCarpenter_

Bme280wx adds temperature, station pressure and relative humidity from a Bosch
BME280 over I2C to an existing WeeWX station's LOOP packets. This independent
continuation maintains version 1.1.1 for Python 3.10–3.14 and
WeeWX 5.5.2–5.6. Keep your existing station driver.

## Install

Enable I2C on the Raspberry Pi and give the WeeWX account access to its I2C
bus. Install `RPi.bme280` and `smbus2` in the Python environment running WeeWX:

```sh
python -m pip install 'RPi.bme280==0.2.4' 'smbus2>=0.6.1,<1'
```

In a container, expose the corresponding `/dev/i2c-*` device. The extension
uses I2C, including on breakout boards that also offer SPI. See
[RPi.bme280](https://pypi.org/project/RPi.bme280/) for wiring information.

Install the published archive with WeeWX 5's extension installer:

```sh
weectl extension install https://github.com/weewx-packages/bme280wx/releases/download/v1.1.1/bme280wx-1.1.1.zip
```

Use the `weectl` from your WeeWX environment. Add
`--config /path/to/weewx.conf` when the station configuration is not found
automatically. Package installations may require `sudo`; activate the WeeWX
virtual environment for pip installations. Restart your WeeWX service after
configuration, for example `sudo systemctl restart weewx` on systemd.
The installer does not restart it for you.

The installer adds `user.bme280wx.Bme280wx` to `data_services`, copies
`bme280wx.py` into the station's `bin/user`, and adds `[Bme280wx]`.
Check `i2c_port` and `i2c_address` in the configuration below before restarting.
The default temperature and humidity fields are `inTemp` and `inHumidity`.
Pressure goes into `pressure` only when `outTemp` is present.

## Upgrade or remove

Back up `[Bme280wx]` before upgrading, then install the desired fixed archive.
To remove, run `weectl extension uninstall bme280wx` and restart WeeWX.
Uninstallation removes the installed configuration.

## Hardware limits and license

The supported sensor is BME280. BMP280 humidity readings and pressure accuracy
are not verified; BMP085 is incompatible with these conversions. Physical
wiring and calibration require checks on your own device. Place the sensor
away from the Raspberry Pi's heat. The project retains WJCarpenter's
[BSD-2-Clause license](LICENSE).

## Configuration
Installation will add a default configuration to `/etc/weewx/weewx.conf`:
```
# Options for extension 'bme280wx'
[Bme280wx]
    i2c_port = 1
    i2c_address = 0x76
    usUnits = US
    temperatureKeys = inTemp
    temperature_must_have = ""
    pressureKeys = pressure
    pressure_must_have = outTemp
    humidityKeys = inHumidity
    humidity_must_have = ""
```
(The items might be in a different order, which doesn't matter.)
There is a good chance that these defaults will work for you as-is.
You should at least check the values of `i2c_port` and `i2c_address`.
(If you are unsure how to do that, follow the guidance at [RPi.bme280](https://pypi.org/project/RPi.bme280/)
or [AdaFruit's Configuring I2C](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c).)
These are the same as the defaults in the extension code,
so simply removing configuration items will not affect the defaults used by the extension.

The configuration items have the following meanings:

* `i2c_port`: The I2C port number. The default is `1`.
  Most Raspberry Pis use port number `1`, but some early models used port number `0`.
* `i2c_address`: The address of your BME280 sensor on the I2C interface.
  The default is `0x76`.
  This value must be in hex notation, as seen in the example.
  Most breakout boards use an address of `0x76` for BME280, but it is not guaranteed.
* `usUnits`: Ordinarily, a weewx loop data packet will contain a `usUnits` key identifying the units system for the values in the packet.
  The BME280 data will be converted to that units system before being added to the packet.
  It is possible that the loop data packet will not have the `usUnits` key.
  In that case, the BME280 data will be converted to the units system from this configuration item.
  Allowed values are `US` (the default), `METRIC`, or `METRICWX`,
  which are the units systems understood by weewx.
  A `usUnits` key with this value will _not_ be added to the weewx loop data packet.
* `temperatureKeys`: When the BME280 temperature data is added to weewx loop data packets, it will use this key or keys.
  If you don't want to use this BME280 value, set this to empty string (`""`).
  The value can be an empty string (meaning, do not add at all), a single item, or a comma-separated list of items.
  If multiple keys are configured, the same value is used with each key.
  The default is `inTemp` under the assumption that your Raspberry Pi is running indoors.
  _You should also make sure your BME280 sensor is at least a few inches away from the Raspberry Pi
  so that it's not affected by the heat of the running computer._
* `temperature_must_have`: The BME280 temperature will only be added to the weewx loop data packet if these items are already present in the packet.
  The value can be an empty string (meaning, no requirements), a single item, or a comma-separated list of items.
  The default is empty string.
* `pressureKeys`: When the BME280 pressure data is added to weewx loop data packets, it will use this key or keys.
  If you don't want to use this BME280 value, set this to empty string (`""`).
  The value can be an empty string (meaning, do not add at all), a single item, or a comma-separated list of items.
  If multiple keys are configured, the same value is used with each key.
  The default is `pressure`. Do _not_ use `barometer`.
  _This is "station pressure". The weewx software will calculate the MSL "barometric pressure" from this.
  That calculation depends upon the ambient temperature and the altitude._
  **Check to make sure that your weewx configuration reflects the altitude of your BME280 sensor, not that of other sensors you may have.**
* `pressure_must_have`: The BME280 pressure will only be added to the weewx loop data packet if these items are already present in the packet.
  The value can be an empty string (meaning, no requirements), a single item, or a comma-separated list of items.
  The default is `outTemp` because the calculation of MSL barometric pressure depends upon the ambient temperature.
  Although the pressure inside will be the same as the pressure outside, the temperature probably will not be.
* `humidityKeys`: When the BME280 humidity data is added to weewx loop data packets, it will use this key or keys.
  If you don't want to use this BME280 value, set this to empty string (`""`).
  The value can be an empty string (meaning, do not add at all), a single item, or a comma-separated list of items.
  If multiple keys are configured, the same value is used with each key.
  The default is `inHumidity`.
* `humidity_must_have`: The BME280 humidity will only be added to the weewx loop data packet if these items are already present in the packet.
  The value can be an empty string (meaning, no requirements), a single item, or a comma-separated list of items.
  The default is empty string.

After making any configuration changes, you must restart weewx.
Be sure to also have a look at the system log to see that weewx started properly.
Mistakes in configuration can lead to unrecoverable errors that prompt weewx to shut down.


## Independent continuation

This repository continues https://gitlab.com/wjcarpenter/bme280wx from
b897cfc3ce2c1b981d33ef93d76d80f280c47289, retaining full history and BSD-2-Clause
license. It is maintained separately. The logging contribution in upstream MR !2
is preserved through commit 859eb1cebabf8c36924f27bb169b896a8802c5d8.

Version 1.1.1 provides a versioned continuation download and uses the WeeWX 5 installer. Sample logging follows the optional
`[Bme280wx] debug` setting, which defaults to WeeWX's debug setting. Debug
messages also require a logger configured to emit DEBUG records. Normal
operation logs startup information without one sample message per loop packet.
Temporary I2C read failures leave the loop packet unchanged and log an error.
Shutdown closes the I2C bus.

### Keep your station driver

Bme280wx is a data service, not a station driver. Keep `[Station] station_type`
set to your existing weather station, or `Simulator` for an isolated test.
The installer registers `user.bme280wx.Bme280wx` in `[Engine][[Services]]`
`data_services` and adds `[Bme280wx]`. Do not set `station_type = BME280wx`.
That setting asks WeeWX to load a driver from a different, case-sensitive
section and reproduces the `KeyError: BME280wx` in upstream issue #2.

Tests use a local fake I2C bus and sensor samples with the real WeeWX unit
converters for US, METRIC and METRICWX. Physical I2C wiring, calibration and
sensor accuracy require the operator's device and are not verified by these tests.
