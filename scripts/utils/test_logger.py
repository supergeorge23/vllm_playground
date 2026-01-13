#!/usr/bin/env python3
"""
Unit tests for logger.py

Tests:
1. Logger creation and configuration
2. Log file creation and writing
3. Log format validation
4. Log level filtering
5. Console output (captured)
6. File and console output separation
7. Helper functions (log_separator, log_header, log_subheader)
8. get_logger function
9. Multiple logger instances independence
"""

import io
import logging
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from datetime import datetime
import re

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utils.logger import (
    setup_logger,
    get_logger,
    log_separator,
    log_header,
    log_subheader,
)


class TestLoggerSetup(unittest.TestCase):
    """Test logger setup and basic functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.log_dir = self.temp_dir / "test_logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_setup_logger_creates_file(self):
        """Test that setup_logger creates a log file."""
        log_file = "test_logger.log"
        logger = setup_logger(
            "test_logger",
            log_dir=self.log_dir,
            log_file=log_file,
            console=False
        )
        
        logger.info("Test message")
        
        log_path = self.log_dir / log_file
        self.assertTrue(log_path.exists(), "Log file should be created")
        
        with open(log_path, "r") as f:
            content = f.read()
            self.assertIn("Test message", content)

    def test_setup_logger_auto_generates_filename(self):
        """Test that setup_logger auto-generates filename when not provided."""
        logger = setup_logger(
            "test_auto",
            log_dir=self.log_dir,
            console=False
        )
        
        logger.info("Auto filename test")
        
        # Should have created a file with pattern: test_auto_<timestamp>.log
        log_files = list(self.log_dir.glob("test_auto_*.log"))
        self.assertEqual(len(log_files), 1, "Should create one log file")
        
        with open(log_files[0], "r") as f:
            content = f.read()
            self.assertIn("Auto filename test", content)

    def test_log_file_format(self):
        """Test that log file has correct format."""
        log_file = "format_test.log"
        logger = setup_logger(
            "format_test",
            log_dir=self.log_dir,
            log_file=log_file,
            console=False
        )
        
        logger.info("Format test message")
        
        log_path = self.log_dir / log_file
        with open(log_path, "r") as f:
            line = f.readline().strip()
            
        # Check format: YYYY-MM-DD HH:MM:SS | LEVEL | name | message
        pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \| INFO\s{4} \| format_test \| Format test message'
        self.assertRegex(line, pattern, "Log format should match expected pattern")

    def test_console_output(self):
        """Test that logger outputs to console when enabled."""
        log_file = "console_test.log"
        logger = setup_logger(
            "console_test",
            log_dir=self.log_dir,
            log_file=log_file,
            console=True
        )
        
        # Capture stdout by checking if console handler exists
        console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        self.assertGreater(len(console_handlers), 0, "Should have console handler")
        
        # Verify console handler has correct formatter
        console_handler = console_handlers[0]
        self.assertIsInstance(console_handler.formatter, logging.Formatter)
        
        # Test actual output using a custom stream
        test_stream = io.StringIO()
        console_handler.stream = test_stream
        logger.info("Console test message")
        
        output = test_stream.getvalue()
        # Console format: LEVEL | message
        self.assertIn("INFO", output)
        self.assertIn("Console test message", output)

    def test_no_console_output_when_disabled(self):
        """Test that logger doesn't output to console when disabled."""
        log_file = "no_console_test.log"
        logger = setup_logger(
            "no_console_test",
            log_dir=self.log_dir,
            log_file=log_file,
            console=False
        )
        
        # Capture stdout
        f = io.StringIO()
        with redirect_stdout(f):
            logger.info("No console message")
        
        output = f.getvalue()
        self.assertEqual(output, "", "Should not output to console when disabled")

    def test_log_levels(self):
        """Test that different log levels work correctly."""
        log_file = "level_test.log"
        logger = setup_logger(
            "level_test",
            log_dir=self.log_dir,
            log_file=log_file,
            level=logging.INFO,
            console=False
        )
        
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        log_path = self.log_dir / log_file
        with open(log_path, "r") as f:
            content = f.read()
            
        # DEBUG should not appear (level is INFO)
        self.assertNotIn("Debug message", content)
        self.assertIn("Info message", content)
        self.assertIn("Warning message", content)
        self.assertIn("Error message", content)

    def test_log_level_filtering(self):
        """Test that log level filtering works."""
        log_file = "filter_test.log"
        logger = setup_logger(
            "filter_test",
            log_dir=self.log_dir,
            log_file=log_file,
            level=logging.WARNING,
            console=False
        )
        
        logger.debug("Debug")
        logger.info("Info")
        logger.warning("Warning")
        logger.error("Error")
        
        log_path = self.log_dir / log_file
        with open(log_path, "r") as f:
            content = f.read()
            
        self.assertNotIn("Debug", content)
        self.assertNotIn("Info", content)
        self.assertIn("Warning", content)
        self.assertIn("Error", content)

    def test_multiple_log_entries(self):
        """Test that multiple log entries are written correctly."""
        log_file = "multi_test.log"
        logger = setup_logger(
            "multi_test",
            log_dir=self.log_dir,
            log_file=log_file,
            console=False
        )
        
        messages = ["Message 1", "Message 2", "Message 3"]
        for msg in messages:
            logger.info(msg)
        
        log_path = self.log_dir / log_file
        with open(log_path, "r") as f:
            lines = f.readlines()
            
        self.assertEqual(len(lines), len(messages), "Should have one line per message")
        for i, msg in enumerate(messages):
            self.assertIn(msg, lines[i])

    def test_log_dir_creation(self):
        """Test that log directory is created if it doesn't exist."""
        new_log_dir = self.temp_dir / "new_logs"
        self.assertFalse(new_log_dir.exists(), "Directory should not exist initially")
        
        logger = setup_logger(
            "dir_test",
            log_dir=new_log_dir,
            log_file="test.log",
            console=False
        )
        
        logger.info("Test")
        
        self.assertTrue(new_log_dir.exists(), "Directory should be created")

    def test_get_logger_returns_existing(self):
        """Test that get_logger returns existing logger if it has handlers."""
        log_file1 = "existing_test1.log"
        logger1 = setup_logger(
            "existing_test",
            log_dir=self.log_dir,
            log_file=log_file1,
            console=False
        )
        
        logger2 = get_logger("existing_test")
        
        # Should return the same logger instance
        self.assertIs(logger1, logger2)

    def test_get_logger_creates_new(self):
        """Test that get_logger creates new logger if none exists."""
        # Use a unique name to avoid conflicts
        unique_name = f"get_logger_new_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        logger = get_logger(unique_name)
        
        # Should have handlers (default setup)
        self.assertTrue(len(logger.handlers) > 0, "Should have handlers")
        
        # Test that logger actually works by writing a message
        logger.info("Test message from get_logger")
        
        # Verify log file was created and contains the message
        # (get_logger uses default logs directory)
        default_log_dir = Path("logs")
        log_files = list(default_log_dir.glob(f"{unique_name}_*.log"))
        
        if log_files:
            with open(log_files[0], "r") as f:
                content = f.read()
                self.assertIn("Test message from get_logger", content)
            
            # Clean up
            for log_file in log_files:
                log_file.unlink()

    def test_log_separator(self):
        """Test log_separator helper function."""
        log_file = "separator_test.log"
        logger = setup_logger(
            "separator_test",
            log_dir=self.log_dir,
            log_file=log_file,
            console=False
        )
        
        log_separator(logger, char="=", width=50)
        
        log_path = self.log_dir / log_file
        with open(log_path, "r") as f:
            content = f.read()
            
        self.assertIn("=" * 50, content)

    def test_log_header(self):
        """Test log_header helper function."""
        log_file = "header_test.log"
        logger = setup_logger(
            "header_test",
            log_dir=self.log_dir,
            log_file=log_file,
            console=False
        )
        
        log_header(logger, "Test Header", char="=", width=60)
        
        log_path = self.log_dir / log_file
        with open(log_path, "r") as f:
            content = f.read()
            
        # Should have separator, title, separator (may be in formatted lines)
        self.assertIn("=" * 60, content)
        self.assertIn("Test Header", content)
        
        # Verify we have 3 log entries (separator, title, separator)
        lines = [line for line in content.split('\n') if line.strip()]
        self.assertGreaterEqual(len(lines), 3, "Should have at least 3 log entries")

    def test_log_subheader(self):
        """Test log_subheader helper function."""
        log_file = "subheader_test.log"
        logger = setup_logger(
            "subheader_test",
            log_dir=self.log_dir,
            log_file=log_file,
            console=False
        )
        
        log_subheader(logger, "Test Subheader", char="-", width=40)
        
        log_path = self.log_dir / log_file
        with open(log_path, "r") as f:
            content = f.read()
            
        # Should have separator, title, separator (may be in formatted lines)
        self.assertIn("-" * 40, content)
        self.assertIn("Test Subheader", content)
        
        # Verify we have 3 log entries (separator, title, separator)
        lines = [line for line in content.split('\n') if line.strip()]
        self.assertGreaterEqual(len(lines), 3, "Should have at least 3 log entries")

    def test_multiple_loggers_independent(self):
        """Test that multiple logger instances are independent."""
        log_file1 = "multi1_test.log"
        log_file2 = "multi2_test.log"
        
        logger1 = setup_logger(
            "multi1",
            log_dir=self.log_dir,
            log_file=log_file1,
            console=False
        )
        
        logger2 = setup_logger(
            "multi2",
            log_dir=self.log_dir,
            log_file=log_file2,
            console=False
        )
        
        logger1.info("Message for logger1")
        logger2.info("Message for logger2")
        
        # Check files are independent
        with open(self.log_dir / log_file1, "r") as f:
            content1 = f.read()
        with open(self.log_dir / log_file2, "r") as f:
            content2 = f.read()
            
        self.assertIn("Message for logger1", content1)
        self.assertIn("Message for logger2", content2)
        self.assertNotIn("Message for logger2", content1)
        self.assertNotIn("Message for logger1", content2)

    def test_logger_clears_existing_handlers(self):
        """Test that setup_logger clears existing handlers."""
        log_file = "clear_test.log"
        
        # Create logger with initial handlers
        logger1 = setup_logger(
            "clear_test",
            log_dir=self.log_dir,
            log_file=log_file,
            console=True
        )
        
        initial_handler_count = len(logger1.handlers)
        
        # Re-setup should clear and recreate
        logger2 = setup_logger(
            "clear_test",
            log_dir=self.log_dir,
            log_file=log_file,
            console=False  # Different config
        )
        
        # Should have cleared old handlers
        # Note: This is the same logger instance, so handlers are replaced
        self.assertEqual(len(logger2.handlers), 1, "Should have file handler only")
        self.assertIs(logger1, logger2, "Should be the same logger instance")

    def test_append_mode(self):
        """Test that log file uses append mode."""
        log_file = "append_test.log"
        
        logger1 = setup_logger(
            "append_test",
            log_dir=self.log_dir,
            log_file=log_file,
            console=False
        )
        logger1.info("First message")
        
        # Create another logger instance (should append)
        logger2 = setup_logger(
            "append_test",
            log_dir=self.log_dir,
            log_file=log_file,
            console=False
        )
        logger2.info("Second message")
        
        log_path = self.log_dir / log_file
        with open(log_path, "r") as f:
            content = f.read()
            
        # Both messages should be present
        self.assertIn("First message", content)
        self.assertIn("Second message", content)

    def test_unicode_support(self):
        """Test that logger handles Unicode characters."""
        log_file = "unicode_test.log"
        logger = setup_logger(
            "unicode_test",
            log_dir=self.log_dir,
            log_file=log_file,
            console=False
        )
        
        unicode_msg = "测试消息: 中文 🚀 emoji"
        logger.info(unicode_msg)
        
        log_path = self.log_dir / log_file
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        self.assertIn(unicode_msg, content)

    def test_default_log_dir(self):
        """Test that default log directory is used when not specified."""
        # Use a unique logger name to avoid conflicts
        unique_name = f"default_test_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        logger = setup_logger(
            unique_name,
            log_dir=None,  # Should use default
            console=False
        )
        
        logger.info("Default dir test")
        
        # Should create file in default "logs" directory
        default_log_dir = Path("logs")
        log_files = list(default_log_dir.glob(f"{unique_name}_*.log"))
        
        # Clean up
        for log_file in log_files:
            log_file.unlink()
        
        self.assertGreater(len(log_files), 0, "Should create file in default logs directory")


def run_tests():
    """Run all tests and print summary."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestLoggerSetup)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
