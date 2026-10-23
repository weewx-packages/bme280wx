# bme280wx

_Copyright (c) 2019, WJCarpenter_

bme280wx adds temperature, station pressure and relative humidity from a Bosch
BME280 sensor to the LOOP packets of an existing WeeWX station. It is a data
service, not a station driver: your station driver stays in place. It reads
the sensor over I2C only, also on breakout boards that offer SPI.

Independent continuation of
[wjcarpenter/bme280wx](https://gitlab.com/wjcarpenter/bme280wx), with its full
history. The logging contribution from upstream MR !2 is preserved in commit
`859eb1c`.

## Requirements

- A BME280 on an I2C bus of a Linux host, for example a Raspberry Pi, with
  I2C enabled. See [RPi.bme280](https://pypi.org/project/RPi.bme280/) for
  wiring, and
  [Adafruit's Configuring I2C](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c)
  for enabling the bus.
- Read and write access for the WeeWX user to the bus device `/dev/i2c-N`. In
  a container, pass that device through.
- The Python packages `RPi.bme280` and `smbus2` in the Python environment
  running WeeWX:

  ```sh
  python -m pip install 'RPi.bme280==0.2.4' 'smbus2>=0.6.1,<1'
  ```

  If WeeWX runs on the system Python from a distribution package, install
  them with the distribution's package manager where it has them.

## Installation

Install `bme280wx` from the [WeeWX packages catalog](https://github.com/weewx-packages/catalog/blob/main/packages/bme280wx.md).
The catalog page lists the current release, its WeeWX and Python
requirements, and the install, update and removal commands.

The installer registers `user.bme280wx.Bme280wx` in `data_services`, copies
`bin/user/bme280wx.py` and adds the `[Bme280wx]` section below. Check
`i2c_port` and `i2c_address` before you restart WeeWX. After the restart,
check the log: the service logs the I2C port and address it uses.

Keep `[Station] station_type` set to your weather station, or to `Simulator`
for a test. Do not set `station_type = BME280wx`. WeeWX would then look for a
driver in a section `[BME280wx]` and stop with `KeyError: BME280wx`, as in
upstream issue #2.

## Configuration

What the installer adds to `weewx.conf`. The values are the defaults of the
code, so removing a line does not change the behaviour:

```ini
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

| Option | Default | Meaning |
| --- | --- | --- |
| `i2c_port` | `1` | I2C bus number. Most Raspberry Pis use `1`, some early models `0`. |
| `i2c_address` | `0x76` | Address of the sensor. Read as hexadecimal, with or without `0x`. Many BME280 boards use `0x76`, but not all. |
| `usUnits` | `US` | Unit system used when the LOOP packet has no `usUnits`: `US`, `METRIC` or `METRICWX`. Otherwise the readings are converted to the packet's unit system. The option does not add `usUnits` to the packet. |
| `temperatureKeys` | `inTemp` | Packet fields that receive the temperature. |
| `temperature_must_have` | `""` | Fields that must already be in the packet before the temperature is added. |
| `pressureKeys` | `pressure` | Packet fields that receive the pressure. |
| `pressure_must_have` | `outTemp` | Fields that must already be in the packet before the pressure is added. |
| `humidityKeys` | `inHumidity` | Packet fields that receive the humidity. |
| `humidity_must_have` | `""` | Fields that must already be in the packet before the humidity is added. |
| `debug` | WeeWX `debug` | When true, each sample and the resulting packet are logged at debug level. |

Each `...Keys` and `..._must_have` option takes an empty string, one field or
a comma-separated list. An empty `...Keys` value leaves that reading out. With
several keys, each gets the same value.

The pressure is station pressure. Put it in `pressure`, not in `barometer`.
WeeWX calculates the sea-level barometer from it, using the outside
temperature and the station altitude. That is why `pressure_must_have`
defaults to `outTemp`. Check that `[Station] altitude` is the altitude of the
BME280.

The default `inTemp` assumes the sensor is indoors. Mount it a few inches away
from the Raspberry Pi, so the computer's heat does not affect it.

Debug messages also need a logger that emits DEBUG records.

## Limitations

- When a reading fails with an I/O error, the service logs the error and
  leaves that LOOP packet unchanged.
- The calibration data is read once at startup. After swapping the sensor,
  restart WeeWX.
- If the bus cannot be opened or the calibration cannot be read at startup,
  WeeWX logs `Caught OSError` and retries every 10 seconds. Invalid values
  for `i2c_port`, `i2c_address` or `usUnits` stop WeeWX at startup.
- The upstream author found that a BMP280 reports a humidity of zero and
  plausible other readings, which were not verified. A BMP085 gives wrong
  values.
- The tests use a fake I2C bus. Wiring, calibration and sensor accuracy are
  not verified on real hardware.

## Development

```sh
python -m pytest -q tests
```

Run it in an environment with WeeWX, pytest, `RPi.bme280` and `smbus2`. The
tests use a fake bus and the WeeWX unit converters for `US`, `METRIC` and
`METRICWX`.

## License

[BSD-2-Clause](LICENSE), as in the original.
