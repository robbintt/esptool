from dataclasses import dataclass
from typing import Optional, Tuple, Union
from enum import Enum

class FlashMode(Enum):
    QIO = "qio"
    QOUT = "qout"
    DIO = "dio"
    DOUT = "dout"

class FlashFrequency(Enum):
    F80M = "80m"
    F60M = "60m"
    F48M = "48m"
    F40M = "40m"
    F30M = "30m"
    F26M = "26m"
    F24M = "24m"
    F20M = "20m"
    F16M = "16m"
    F15M = "15m"
    F12M = "12m"

class FlashSize(Enum):
    SIZE_256KB = "256KB"
    SIZE_512KB = "512KB"
    SIZE_1MB = "1MB"
    SIZE_2MB = "2MB"
    SIZE_2MB_C1 = "2MB-c1"
    SIZE_4MB = "4MB"
    SIZE_4MB_C1 = "4MB-c1"

@dataclass
class FlashParameters:
    """Class to handle and validate flash parameters for ESP chips."""
    
    size: Union[FlashSize, str]
    mode: Union[FlashMode, str]
    freq: Union[FlashFrequency, str]
    chip_name: str
    spi_connection: Optional[Union[str, Tuple[int, int, int, int, int]]] = None
    flash_encryption: bool = False
    
    def __post_init__(self):
        """Validate parameters after initialization."""
        self._validate_size()
        self._validate_mode()
        self._validate_frequency()
        self._validate_spi_connection()
        self._validate_chip_specific()
    
    def _validate_size(self):
        """Validate flash size parameter."""
        if isinstance(self.size, str):
            try:
                self.size = FlashSize(self.size)
            except ValueError:
                raise ValueError(f"Invalid flash size: {self.size}. Must be one of {[s.value for s in FlashSize]}")
        
        # ESP8266 specific size validation
        if self.chip_name == "ESP8266" and self.size not in [
            FlashSize.SIZE_256KB,
            FlashSize.SIZE_512KB,
            FlashSize.SIZE_2MB_C1,
            FlashSize.SIZE_4MB_C1
        ]:
            raise ValueError(f"ESP8266 only supports flash sizes: 256KB, 512KB, 2MB-c1, 4MB-c1")
    
    def _validate_mode(self):
        """Validate flash mode parameter."""
        if isinstance(self.mode, str):
            try:
                self.mode = FlashMode(self.mode)
            except ValueError:
                raise ValueError(f"Invalid flash mode: {self.mode}. Must be one of {[m.value for m in FlashMode]}")
        
        # ESP8266 specific mode validation
        if self.chip_name == "ESP8266" and self.mode not in [FlashMode.QIO, FlashMode.DIO]:
            raise ValueError("ESP8266 only supports QIO and DIO flash modes")
    
    def _validate_frequency(self):
        """Validate flash frequency parameter."""
        if isinstance(self.freq, str):
            try:
                self.freq = FlashFrequency(self.freq)
            except ValueError:
                raise ValueError(f"Invalid flash frequency: {self.freq}. Must be one of {[f.value for f in FlashFrequency]}")
        
        # ESP8266 specific frequency validation
        if self.chip_name == "ESP8266" and self.freq not in [
            FlashFrequency.F40M,
            FlashFrequency.F26M,
            FlashFrequency.F20M
        ]:
            raise ValueError("ESP8266 only supports 40MHz, 26MHz, and 20MHz flash frequencies")
    
    def _validate_spi_connection(self):
        """Validate SPI connection parameters."""
        if self.spi_connection is None:
            return
            
        if isinstance(self.spi_connection, str):
            if self.spi_connection.upper() not in ["SPI", "HSPI"]:
                raise ValueError("SPI connection must be either 'SPI', 'HSPI', or a tuple of 5 pin numbers")
        elif isinstance(self.spi_connection, tuple):
            if len(self.spi_connection) != 5:
                raise ValueError("SPI connection tuple must contain exactly 5 pin numbers (CLK,Q,D,HD,CS)")
            if not all(isinstance(pin, int) for pin in self.spi_connection):
                raise ValueError("All SPI connection pins must be integers")
            if not all(0 <= pin <= 39 for pin in self.spi_connection):  # ESP32 GPIO range
                raise ValueError("SPI connection pins must be between 0 and 39")
    
    def _validate_chip_specific(self):
        """Validate chip-specific parameter combinations."""
        # ESP32 specific validations
        if self.chip_name == "ESP32":
            if self.flash_encryption and self.mode not in [FlashMode.DIO, FlashMode.DOUT]:
                raise ValueError("Flash encryption requires DIO or DOUT flash mode")
            
            if self.size in [FlashSize.SIZE_2MB_C1, FlashSize.SIZE_4MB_C1]:
                raise ValueError("ESP32 does not support 2MB-c1 or 4MB-c1 flash sizes")
        
        # ESP32-S2 specific validations
        elif self.chip_name == "ESP32-S2":
            if self.flash_encryption and self.mode != FlashMode.DIO:
                raise ValueError("ESP32-S2 flash encryption requires DIO flash mode")
    
    def to_dict(self) -> dict:
        """Convert parameters to a dictionary format."""
        return {
            "size": self.size.value if isinstance(self.size, FlashSize) else self.size,
            "mode": self.mode.value if isinstance(self.mode, FlashMode) else self.mode,
            "freq": self.freq.value if isinstance(self.freq, FlashFrequency) else self.freq,
            "spi_connection": self.spi_connection,
            "flash_encryption": self.flash_encryption
        } 