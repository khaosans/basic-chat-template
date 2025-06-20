"""
Tests for enhanced tools functionality
"""

import pytest
import math
import datetime
from unittest.mock import Mock, patch
from src.utils.enhanced_tools import (
    EnhancedCalculator,
    EnhancedTimeTools,
    CalculationResult,
    TimeResult
)

class TestEnhancedCalculator:
    """Test enhanced calculator functionality"""
    
    def setup_method(self):
        """Setup calculator for each test"""
        self.calculator = EnhancedCalculator()
    
    def test_basic_arithmetic(self):
        """Test basic arithmetic operations"""
        test_cases = [
            ("2 + 2", "4.0"),
            ("10 - 5", "5.0"),
            ("3 * 4", "12.0"),
            ("15 / 3", "5.0"),
            ("7 % 3", "1.0"),
            ("2 ** 3", "8.0")
        ]
        
        for expression, expected in test_cases:
            result = self.calculator.calculate(expression)
            assert result.success is True
            assert result.result == expected
            assert result.error is None
    
    def test_mathematical_functions(self):
        """Test mathematical functions"""
        test_cases = [
            ("sqrt(16)", "4.0"),
            ("abs(-5)", "5.0"),
            ("round(3.7)", "4.0"),
            ("floor(3.7)", "3.0"),
            ("ceil(3.2)", "4.0")
        ]
        
        for expression, expected in test_cases:
            result = self.calculator.calculate(expression)
            assert result.success is True
            assert result.result == expected
            assert result.error is None
    
    def test_trigonometric_functions(self):
        """Test trigonometric functions"""
        test_cases = [
            ("sin(0)", "0.0"),
            ("cos(0)", "1.0"),
            ("tan(0)", "0.0"),
            ("sin(pi/2)", "1.0")
        ]
        
        for expression, expected in test_cases:
            result = self.calculator.calculate(expression)
            assert result.success is True
            assert result.result == expected
            assert result.error is None
    
    def test_logarithmic_functions(self):
        """Test logarithmic functions"""
        test_cases = [
            ("log(10)", "1.0"),
            ("ln(e)", "1.0"),
            ("log10(100)", "2.0")
        ]
        
        for expression, expected in test_cases:
            result = self.calculator.calculate(expression)
            assert result.success is True
            assert result.result == expected
            assert result.error is None
    
    def test_constants(self):
        """Test mathematical constants"""
        test_cases = [
            ("pi", "3.141592653589793"),
            ("e", "2.718281828459045"),
            ("tau", "6.283185307179586")
        ]
        
        for expression, expected in test_cases:
            result = self.calculator.calculate(expression)
            assert result.success is True
            assert result.result == expected
            assert result.error is None
    
    def test_complex_expressions(self):
        """Test complex mathematical expressions"""
        test_cases = [
            ("2 + 3 * 4", "14.0"),
            ("(2 + 3) * 4", "20.0"),
            ("sqrt(16) + abs(-5)", "9.0"),
            ("sin(pi/2) + cos(0)", "2.0")
        ]
        
        for expression, expected in test_cases:
            result = self.calculator.calculate(expression)
            assert result.success is True
            assert result.result == expected
            assert result.error is None
    
    def test_expression_cleaning(self):
        """Test expression cleaning and normalization"""
        test_cases = [
            ("2 + 2", "4.0"),
            ("2+2", "4.0"),
            (" 2 + 2 ", "4.0"),
            ("2 + 2 + 2", "6.0")
        ]
        
        for expression, expected in test_cases:
            result = self.calculator.calculate(expression)
            assert result.success is True
            assert result.result == expected
            assert result.error is None
    
    def test_error_handling(self):
        """Test error handling for invalid expressions"""
        test_cases = [
            "2 / 0",
            "sqrt(-1)",
            "factorial(-1)",
            "log(0)",
            "undefined_function(1)",
        ]
        
        for expression in test_cases:
            result = self.calculator.calculate(expression)
            assert result.success is False
            assert result.error is not None
            assert len(result.steps) > 0
    
    def test_safety_validation(self):
        """Test safety validation of expressions"""
        dangerous_expressions = [
            "import os",
            "eval('2+2')",
            "exec('print(1)')",
            "open('file.txt')",
            "input('Enter:')",
            "__import__('os')",
            "globals()",
            "locals()",
            "vars()",
            "dir()"
        ]
        
        for expression in dangerous_expressions:
            result = self.calculator.calculate(expression)
            assert result.success is False
            assert "unsafe" in result.error.lower() or "error" in result.error.lower()
    
    def test_result_formatting(self):
        """Test result formatting and presentation"""
        result = self.calculator.calculate("1 + 1")
        assert result.success is True
        assert result.result == "2.0"
        assert result.error is None
        assert len(result.steps) > 0

class TestEnhancedTimeTools:
    """Test enhanced time tools functionality"""
    
    def setup_method(self):
        """Setup time tools for each test"""
        self.time_tools = EnhancedTimeTools()
    
    def test_get_current_time_utc(self):
        """Test getting current time in UTC"""
        result = self.time_tools.get_current_time("UTC")
        
        assert result.success is True
        assert "UTC" in result.current_time
        assert result.timezone == "UTC"
        assert result.unix_timestamp > 0
        assert isinstance(result.formatted_time, str)
    
    def test_get_current_time_different_timezones(self):
        """Test getting current time in different timezones"""
        timezones = ["UTC", "America/New_York", "Europe/London"]
        
        for tz in timezones:
            result = self.time_tools.get_current_time(tz)
            assert result.success is True
            assert result.current_time is not None
            assert result.timezone in self.time_tools.common_timezones.values() or result.timezone in ["UTC", "GMT"]
            assert result.formatted_time is not None
            assert result.unix_timestamp > 0
    
    def test_timezone_normalization(self):
        """Test timezone name normalization"""
        assert self.time_tools._normalize_timezone("EST") == "America/New_York"
        assert self.time_tools._normalize_timezone("PST") == "America/Los_Angeles"
        assert self.time_tools._normalize_timezone("UTC") == "UTC"
        
        assert self.time_tools._normalize_timezone("America/New_York") == "America/New_York"
        
        assert self.time_tools._normalize_timezone("INVALID_TZ") == "UTC"
    
    def test_time_conversion(self):
        """Test time conversion between timezones"""
        result = self.time_tools.convert_time(
            "2024-01-01 12:00:00",
            "UTC",
            "EST"
        )
        
        assert result.success is True
        assert "EST" in result.current_time or "EDT" in result.current_time
        assert result.timezone == "America/New_York"
    
    def test_time_difference_calculation(self):
        """Test time difference calculation"""
        result = self.time_tools.get_time_difference(
            "2024-01-01 12:00:00",
            "2024-01-01 14:00:00",
            "UTC"
        )
        
        assert result["success"] is True
        assert result["difference_seconds"] == 7200
        assert result["difference_hours"] == 2.0
        assert result["difference_minutes"] == 120.0
        assert "2:00:00" in result["formatted_difference"]
    
    def test_time_info_comprehensive(self):
        """Test comprehensive time information"""
        result = self.time_tools.get_time_info("UTC")
        
        assert result["success"] is True
        assert "current_time" in result
        assert "timezone" in result
        assert "unix_timestamp" in result
        assert "year" in result
        assert "month" in result
        assert "day" in result
        assert "hour" in result
        assert "minute" in result
        assert "second" in result
        assert "weekday" in result
        assert "month_name" in result
        assert "day_of_year" in result
        assert "is_weekend" in result
        assert "is_business_day" in result
    
    def test_available_timezones(self):
        """Test getting available timezones"""
        timezones = self.time_tools.get_available_timezones()
        
        assert isinstance(timezones, list)
        assert len(timezones) > 0
        assert "UTC" in timezones
        assert "EST" in timezones
        assert "PST" in timezones
    
    def test_error_handling_invalid_timezone(self):
        """Test error handling for invalid timezone"""
        result = self.time_tools.get_current_time("INVALID_TIMEZONE")
        
        assert result.success is True
        assert result.timezone == "UTC"
    
    def test_error_handling_invalid_time_format(self):
        """Test error handling for invalid time format"""
        result = self.time_tools.convert_time(
            "invalid_time_format",
            "UTC",
            "EST"
        )
        
        assert result.success is False
        assert result.error is not None
    
    def test_error_handling_invalid_timezone_conversion(self):
        """Test error handling for invalid timezone in conversion"""
        result = self.time_tools.convert_time(
            "2024-01-01 12:00:00",
            "INVALID_FROM_TZ",
            "INVALID_TO_TZ"
        )
        
        assert result.success is True
    
    @patch('utils.enhanced_tools.pytz')
    def test_pytz_import_error_handling(self, mock_pytz):
        """Test handling of pytz import errors"""
        mock_pytz.timezone.side_effect = ImportError("pytz not available")
        
        result = self.time_tools.get_current_time("UTC")
        
        assert result.success is False
        assert result.error is not None

class TestIntegration:
    """Integration tests for enhanced tools"""
    
    def test_calculator_and_time_integration(self):
        """Test integration between calculator and time tools"""
        # Get current timestamp
        time_result = self.time_tools.get_current_time("UTC")
        assert time_result.success is True
        
        # Use timestamp in calculation
        calc_result = self.calculator.calculate(f"{time_result.unix_timestamp} / 1000")
        assert calc_result.success is True
        assert float(calc_result.result) > 0
    
    def test_complex_calculation_with_time(self):
        """Test complex calculations involving time"""
        # Get current time info
        time_result = self.time_tools.get_current_time("UTC")
        assert time_result.success is True
        
        # Calculate hours since epoch
        calc_result = self.calculator.calculate(f"{time_result.unix_timestamp} / 3600")
        assert calc_result.success is True
        assert float(calc_result.result) > 0

@pytest.mark.parametrize("tool_class", [EnhancedCalculator, EnhancedTimeTools])
def test_tool_initialization(tool_class):
    """Test that tools can be initialized properly"""
    tool = tool_class()
    assert tool is not None
    assert isinstance(tool, tool_class)

def test_calculation_result_dataclass():
    """Test CalculationResult dataclass"""
    result = CalculationResult(
        result="42",
        expression="40 + 2",
        steps=["Step 1", "Step 2"],
        success=True
    )
    
    assert result.result == "42"
    assert result.expression == "40 + 2"
    assert len(result.steps) == 2
    assert result.success is True
    assert result.error is None

def test_time_result_dataclass():
    """Test TimeResult dataclass"""
    result = TimeResult(
        current_time="2024-01-01 12:00:00 UTC",
        timezone="UTC",
        formatted_time="2024-01-01 12:00:00 UTC",
        unix_timestamp=1704110400.0,
        success=True
    )
    
    assert result.current_time == "2024-01-01 12:00:00 UTC"
    assert result.timezone == "UTC"
    assert result.formatted_time == "2024-01-01 12:00:00 UTC"
    assert result.unix_timestamp == 1704110400.0
    assert result.success is True
    assert result.error is None 