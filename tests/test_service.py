import importlib.util
import logging
from pathlib import Path
from types import SimpleNamespace

import configobj
import pytest
import weewx
import weewx.engine
import weewx.units

ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location('bme_service', ROOT / 'bin/user/bme280wx.py')
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class Engine:
    def bind(self, *args):
        pass


class Bus:
    def __init__(self, port):
        self.port = port
        self.closed = False
    def close(self):
        self.closed = True


@pytest.fixture
def sensor(monkeypatch):
    monkeypatch.setattr(module.smbus2, 'SMBus', Bus)
    monkeypatch.setattr(module.bme280, 'load_calibration_params', lambda bus, address: 'calibration')
    monkeypatch.setattr(module.bme280, 'sample', lambda *args: SimpleNamespace(
        temperature=0.0, pressure=1000.0, humidity=0.0))
    return module


@pytest.mark.parametrize('debug', [False, True])
def test_logging(sensor, caplog, debug):
    service = sensor.Bme280wx(Engine(), {'Bme280wx': {'debug': debug}})
    caplog.clear()
    with caplog.at_level(logging.DEBUG):
        service.new_loop_packet(SimpleNamespace(packet={'usUnits': weewx.METRIC, 'outTemp': 1}))
    assert any('BME280 data' in message for message in caplog.messages) == debug
    service.shutDown()
    assert service.bus.closed


@pytest.mark.parametrize('units,temp,pressure', [(weewx.US, 32.0, 29.5299830714),
                                              (weewx.METRIC, 0.0, 1000.0),
                                              (weewx.METRICWX, 0.0, 1000.0)])
def test_sensor_conversions(sensor, units, temp, pressure):
    service = sensor.Bme280wx(Engine(), {'Bme280wx': {}})
    packet = {'usUnits': units, 'outTemp': 1.0}
    service.new_loop_packet(SimpleNamespace(packet=packet))
    assert packet['inTemp'] == temp
    assert packet['pressure'] == pytest.approx(pressure)
    assert packet['inHumidity'] == 0.0


def test_i2c_failure_keeps_loop_packet(sensor, monkeypatch, caplog):
    service = sensor.Bme280wx(Engine(), {})
    def unavailable(*args):
        raise OSError('fixture I2C disconnected')
    monkeypatch.setattr(sensor.bme280, 'sample', unavailable)
    packet = {'dateTime': 10, 'usUnits': weewx.METRIC}
    service.new_loop_packet(SimpleNamespace(packet=packet))
    assert packet == {'dateTime': 10, 'usUnits': weewx.METRIC}
    assert 'fixture I2C disconnected' in caplog.text


def test_station_type_is_not_a_sensor_service():
    config = configobj.ConfigObj({'Station': {'station_type': 'BME280wx'}})
    with pytest.raises(KeyError, match='BME280wx'):
        weewx.engine.StdEngine.setupStation(SimpleNamespace(), config)


def test_installer_uses_data_service():
    spec = importlib.util.spec_from_file_location('bme_install', ROOT / 'install.py')
    installer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(installer)
    definition = installer.loader()
    assert definition['data_services'] == 'user.bme280wx.Bme280wx'
    assert 'Station' not in definition['config']
