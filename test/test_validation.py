import pytest
import os
from esptool.validation import CLIValidator, ValidationError

def test_validate_chip():
    # Valid cases
    CLIValidator.validate_chip("auto")
    CLIValidator.validate_chip("esp32")
    
    # Invalid cases
    with pytest.raises(ValidationError, match="Invalid chip"):
        CLIValidator.validate_chip("invalid_chip")

def test_validate_baud():
    # Valid cases
    CLIValidator.validate_baud(115200)
    CLIValidator.validate_baud(921600)
    
    # Invalid cases
    with pytest.raises(ValidationError, match="Invalid baud rate"):
        CLIValidator.validate_baud(123456)

def test_validate_flash_mode():
    # Valid cases
    CLIValidator.validate_flash_mode("dio")
    CLIValidator.validate_flash_mode("qio")
    
    # Invalid cases
    with pytest.raises(ValidationError, match="Invalid flash mode"):
        CLIValidator.validate_flash_mode("invalid_mode")

def test_validate_flash_size():
    # Valid cases
    CLIValidator.validate_flash_size("4MB")
    CLIValidator.validate_flash_size("16MB")
    
    # Invalid cases
    with pytest.raises(ValidationError, match="Invalid flash size"):
        CLIValidator.validate_flash_size("3MB")

def test_validate_flash_freq():
    # Valid cases
    CLIValidator.validate_flash_freq("40m")
    CLIValidator.validate_flash_freq("80m")
    
    # Invalid cases
    with pytest.raises(ValidationError, match="Invalid flash frequency"):
        CLIValidator.validate_flash_freq("30m")

def test_validate_address():
    # Valid cases
    CLIValidator.validate_address(0x1000)
    CLIValidator.validate_address(0x8000)

    # Invalid cases
    with pytest.raises(ValidationError, match="Address cannot be negative"):
        CLIValidator.validate_address(-1)
    with pytest.raises(ValidationError, match="Address must be 4-byte aligned"):
        CLIValidator.validate_address(0x1001)
    with pytest.raises(ValidationError, match="Address exceeds maximum flash size"):
        CLIValidator.validate_address(0x1000004)  # Using a 4-byte aligned value that exceeds MAX_FLASH_SIZE

def test_validate_size():
    # Valid cases
    CLIValidator.validate_size(4)
    CLIValidator.validate_size(1024)
    
    # Invalid cases
    with pytest.raises(ValidationError, match="Size must be positive"):
        CLIValidator.validate_size(0)
    with pytest.raises(ValidationError, match="Size must be 4-byte aligned"):
        CLIValidator.validate_size(3)

def test_validate_file(tmp_path):
    # Create a test file
    test_file = tmp_path / "test.bin"
    test_file.write_bytes(b"test data")
    
    # Valid cases
    CLIValidator.validate_file(str(test_file), "write")
    
    # Invalid cases
    with pytest.raises(ValidationError, match="File not found"):
        CLIValidator.validate_file("nonexistent.bin", "write")
    
    empty_file = tmp_path / "empty.bin"
    empty_file.write_bytes(b"")
    with pytest.raises(ValidationError, match="File is empty"):
        CLIValidator.validate_file(str(empty_file), "write")

def test_validate_write_flash_params(tmp_path):
    # Create a test file
    test_file = tmp_path / "test.bin"
    test_file.write_bytes(b"test data")
    
    # Valid cases
    valid_params = {
        'addr_filename': [(0x1000, str(test_file))],
        'flash_mode': 'dio',
        'flash_freq': '40m',
        'flash_size': '4MB'
    }
    CLIValidator.validate_command_params("write_flash", valid_params)
    
    # Invalid cases
    invalid_params = {
        'addr_filename': [(0x1001, str(test_file))],  # Unaligned address
        'flash_mode': 'invalid'
    }
    with pytest.raises(ValidationError):
        CLIValidator.validate_command_params("write_flash", invalid_params)

def test_validate_read_flash_params():
    valid_params = {
        'address': 0x1000,
        'size': 4096,
        'filename': 'output.bin'
    }
    CLIValidator.validate_command_params("read_flash", valid_params)
    
    invalid_params = {
        'address': -1,
        'size': 0,
        'filename': 'output.bin'
    }
    with pytest.raises(ValidationError):
        CLIValidator.validate_command_params("read_flash", invalid_params)

def test_validate_erase_region_params():
    valid_params = {
        'address': 0x1000,
        'size': 4096
    }
    CLIValidator.validate_command_params("erase_region", valid_params)
    
    invalid_params = {
        'address': 0x1001,  # Unaligned
        'size': 4095  # Unaligned
    }
    with pytest.raises(ValidationError):
        CLIValidator.validate_command_params("erase_region", invalid_params)
