"""Validation module for esptool CLI operations."""

import os
from typing import Optional, Tuple, List, Dict, Any
from .util import FatalError
from .targets import CHIP_DEFS

class ValidationError(FatalError):
    """Specific exception for validation errors"""
    pass

class CLIValidator:
    """Validator for esptool CLI parameters and operations"""
    
    VALID_BAUD_RATES = [9600, 74880, 115200, 230400, 460800, 921600]
    FLASH_MODES = ['qio', 'qout', 'dio', 'dout']
    FLASH_SIZES = ['1MB', '2MB', '4MB', '8MB', '16MB', '32MB', '64MB', '128MB']
    FLASH_FREQS = ['20m', '26m', '40m', '80m']
    SUPPORTED_CHIPS = list(CHIP_DEFS.keys())
    MAX_FLASH_SIZE = 0x1000000  # 16MB maximum flash size
    
    @classmethod
    def validate_chip(cls, chip: str) -> None:
        """Validate chip parameter"""
        if chip != "auto" and chip not in cls.SUPPORTED_CHIPS:
            raise ValidationError(
                f"Invalid chip '{chip}'. Supported chips: {', '.join(cls.SUPPORTED_CHIPS)}"
            )

    @classmethod
    def validate_port(cls, port: str) -> None:
        """Validate serial port parameter"""
        if not port:
            raise ValidationError("Port must be specified")
        
        # Check if port exists (for standard ports)
        if port.startswith(("/dev/", "COM")):
            if not os.path.exists(port):
                raise ValidationError(f"Port {port} does not exist")

    @classmethod
    def validate_baud(cls, baud: int) -> None:
        """Validate baud rate"""
        if baud not in cls.VALID_BAUD_RATES:
            raise ValidationError(
                f"Invalid baud rate {baud}. Valid rates: {', '.join(map(str, cls.VALID_BAUD_RATES))}"
            )

    @classmethod
    def validate_flash_mode(cls, mode: str) -> None:
        """Validate flash mode"""
        if mode.lower() not in cls.FLASH_MODES:
            raise ValidationError(
                f"Invalid flash mode '{mode}'. Valid modes: {', '.join(cls.FLASH_MODES)}"
            )

    @classmethod
    def validate_flash_size(cls, size: str) -> None:
        """Validate flash size"""
        if size.upper() not in cls.FLASH_SIZES:
            raise ValidationError(
                f"Invalid flash size '{size}'. Valid sizes: {', '.join(cls.FLASH_SIZES)}"
            )

    @classmethod
    def validate_flash_freq(cls, freq: str) -> None:
        """Validate flash frequency"""
        if freq.lower() not in cls.FLASH_FREQS:
            raise ValidationError(
                f"Invalid flash frequency '{freq}'. Valid frequencies: {', '.join(cls.FLASH_FREQS)}"
            )

    @classmethod
    def validate_address(cls, addr: int, operation: str = "general") -> None:
        """Validate flash address"""
        if addr < 0:
            raise ValidationError("Address cannot be negative")

        if addr >= cls.MAX_FLASH_SIZE:
            raise ValidationError("Address exceeds maximum flash size")

        if addr % 4 != 0:
            raise ValidationError("Address must be 4-byte aligned")

    @classmethod
    def validate_size(cls, size: int) -> None:
        """Validate size parameter"""
        if size <= 0:
            raise ValidationError("Size must be positive")
        
        if size % 4 != 0:
            raise ValidationError("Size must be 4-byte aligned")

    @classmethod
    def validate_file(cls, filepath: str, operation: str = "write") -> None:
        """Validate file operations"""
        if operation == "write":
            if not os.path.exists(filepath):
                raise ValidationError(f"File not found: {filepath}")
            if not os.path.isfile(filepath):
                raise ValidationError(f"Not a regular file: {filepath}")
            if os.path.getsize(filepath) == 0:
                raise ValidationError(f"File is empty: {filepath}")

    @classmethod
    def validate_command_params(cls, command: str, params: Dict[str, Any]) -> None:
        """Validate parameters for specific commands"""
        if command == "write_flash":
            cls._validate_write_flash(params)
        elif command == "read_flash":
            cls._validate_read_flash(params)
        elif command == "erase_region":
            cls._validate_erase_region(params)

    @classmethod
    def _validate_write_flash(cls, params: Dict[str, Any]) -> None:
        """Validate write_flash command parameters"""
        if 'addr_filename' not in params or not params['addr_filename']:
            raise ValidationError("No flash addresses or files specified")
        
        for addr, filename in params['addr_filename']:
            cls.validate_address(addr)
            cls.validate_file(filename, "write")
        
        if params.get('flash_mode'):
            cls.validate_flash_mode(params['flash_mode'])
        if params.get('flash_size'):
            cls.validate_flash_size(params['flash_size'])
        if params.get('flash_freq'):
            cls.validate_flash_freq(params['flash_freq'])

    @classmethod
    def _validate_read_flash(cls, params: Dict[str, Any]) -> None:
        """Validate read_flash command parameters"""
        cls.validate_address(params['address'])
        cls.validate_size(params['size'])
        cls.validate_file(params['filename'], "read")

    @classmethod
    def _validate_erase_region(cls, params: Dict[str, Any]) -> None:
        """Validate erase_region command parameters"""
        cls.validate_address(params['address'])
        cls.validate_size(params['size'])
