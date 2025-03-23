import pytest
from esptool.flash_params import FlashParameters, FlashMode, FlashFrequency, FlashSize

def test_valid_esp32_params():
    """Test valid flash parameters for ESP32"""
    params = FlashParameters(
        size="4MB",
        mode="qio",
        freq="40m",
        chip_name="ESP32"
    )
    assert params.size == FlashSize.SIZE_4MB
    assert params.mode == FlashMode.QIO
    assert params.freq == FlashFrequency.F40M

def test_valid_esp8266_params():
    """Test valid flash parameters for ESP8266"""
    params = FlashParameters(
        size="2MB-c1",
        mode="qio",
        freq="40m",
        chip_name="ESP8266"
    )
    assert params.size == FlashSize.SIZE_2MB_C1
    assert params.mode == FlashMode.QIO
    assert params.freq == FlashFrequency.F40M

def test_invalid_esp8266_size():
    """Test invalid flash size for ESP8266"""
    with pytest.raises(ValueError) as exc_info:
        FlashParameters(
            size="8MB",
            mode="qio",
            freq="40m",
            chip_name="ESP8266"
        )
    assert "Invalid flash size: 8MB" in str(exc_info.value)

def test_invalid_esp8266_mode():
    """Test invalid flash mode for ESP8266"""
    with pytest.raises(ValueError) as exc_info:
        FlashParameters(
            size="2MB-c1",
            mode="qout",
            freq="40m",
            chip_name="ESP8266"
        )
    assert "ESP8266 only supports QIO and DIO flash modes" in str(exc_info.value)

def test_invalid_esp8266_frequency():
    """Test invalid flash frequency for ESP8266"""
    with pytest.raises(ValueError) as exc_info:
        FlashParameters(
            size="2MB-c1",
            mode="qio",
            freq="80m",
            chip_name="ESP8266"
        )
    assert "ESP8266 only supports 40MHz, 26MHz, and 20MHz flash frequencies" in str(exc_info.value)

def test_esp32_flash_encryption_mode():
    """Test flash encryption mode requirements for ESP32"""
    with pytest.raises(ValueError) as exc_info:
        FlashParameters(
            size="4MB",
            mode="qio",
            freq="40m",
            chip_name="ESP32",
            flash_encryption=True
        )
    assert "Flash encryption requires DIO or DOUT flash mode" in str(exc_info.value)

def test_esp32_s2_flash_encryption_mode():
    """Test flash encryption mode requirements for ESP32-S2"""
    with pytest.raises(ValueError) as exc_info:
        FlashParameters(
            size="4MB",
            mode="qout",
            freq="40m",
            chip_name="ESP32-S2",
            flash_encryption=True
        )
    assert "ESP32-S2 flash encryption requires DIO flash mode" in str(exc_info.value)

def test_invalid_spi_connection():
    """Test invalid SPI connection parameters"""
    with pytest.raises(ValueError) as exc_info:
        FlashParameters(
            size="4MB",
            mode="qio",
            freq="40m",
            chip_name="ESP32",
            spi_connection="INVALID"
        )
    assert "SPI connection must be either 'SPI', 'HSPI'" in str(exc_info.value)

def test_invalid_spi_pins():
    """Test invalid SPI pin numbers"""
    with pytest.raises(ValueError) as exc_info:
        FlashParameters(
            size="4MB",
            mode="qio",
            freq="40m",
            chip_name="ESP32",
            spi_connection=(1, 2, 3, 4)  # Missing one pin
        )
    assert "SPI connection tuple must contain exactly 5 pin numbers" in str(exc_info.value)

def test_invalid_spi_pin_range():
    """Test SPI pin numbers out of range"""
    with pytest.raises(ValueError) as exc_info:
        FlashParameters(
            size="4MB",
            mode="qio",
            freq="40m",
            chip_name="ESP32",
            spi_connection=(1, 2, 3, 4, 40)  # Pin 40 is out of range
        )
    assert "SPI connection pins must be between 0 and 39" in str(exc_info.value) 