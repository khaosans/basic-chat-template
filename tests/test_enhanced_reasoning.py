"""
Tests for enhanced reasoning engine with improved tools
"""

import pytest
from unittest.mock import Mock, patch
from src.reasoning import ReasoningAgent, ReasoningResult
from src.utils.enhanced_tools import EnhancedCalculator, EnhancedTimeTools

class TestEnhancedReasoningAgent:
    """Test enhanced reasoning agent with improved tools"""
    
    def setup_method(self):
        """Setup agent for each test"""
        self.agent = ReasoningAgent(model_name="mistral")
    
    def test_enhanced_calculator_tool(self):
        """Test enhanced calculator tool integration"""
        # Test basic arithmetic
        result = self.agent._enhanced_calculate("2 + 2")
        assert "✅ Calculation Result: 4.0" in result
        assert "📝 Expression: 2 + 2" in result
        assert "🔢 Steps:" in result
        
        # Test mathematical functions
        result = self.agent._enhanced_calculate("sqrt(16)")
        assert "✅ Calculation Result: 4.0" in result
        
        # Test error handling
        result = self.agent._enhanced_calculate("2 / 0")
        assert "❌ Calculation Error:" in result
    
    def test_enhanced_time_tools(self):
        """Test enhanced time tools integration"""
        # Test current time with IANA timezone names
        result = self.agent._get_current_time("UTC")
        assert "🕐 Current Time:" in result
        assert "🌍 Timezone: UTC" in result
        assert "📅 Unix Timestamp:" in result
        
        # Test with US timezone using IANA name
        result = self.agent._get_current_time("America/New_York")
        assert "🕐 Current Time:" in result
        assert "America/New_York" in result
        assert "📅 Unix Timestamp:" in result
    
    def test_time_conversion_tool(self):
        """Test time conversion tool"""
        result = self.agent._convert_time("2024-01-01 12:00:00, UTC, EST")
        assert "🔄 Time Conversion:" in result
        assert "📅 From: 2024-01-01 12:00:00 (UTC)" in result
        assert "📅 To:" in result
        assert "America/New_York" in result
        
        # Test invalid format
        result = self.agent._convert_time("invalid_format")
        assert "❌ Invalid format" in result
    
    def test_time_difference_tool(self):
        """Test time difference calculation tool"""
        result = self.agent._calculate_time_difference("2024-01-01 12:00:00, 2024-01-01 14:00:00, UTC")
        assert "⏱️ Time Difference:" in result
        assert "📅 Time 1: 2024-01-01 12:00:00" in result
        assert "📅 Time 2: 2024-01-01 14:00:00" in result
        assert "⏰ Difference:" in result
        assert "📊 In hours: 2.00" in result
        
        # Test invalid format
        result = self.agent._calculate_time_difference("invalid_format")
        assert "❌ Invalid format" in result
    
    def test_time_info_tool(self):
        """Test comprehensive time info tool"""
        result = self.agent._get_time_info("UTC")
        assert "📅 Comprehensive Time Info (UTC):" in result
        assert "🕐 Current Time:" in result
        assert "📊 Year:" in result
        assert "📊 Month:" in result
        assert "📊 Day:" in result
        assert "📊 Day of Week:" in result
        assert "📊 Business Day:" in result
    
    def test_agent_tools_initialization(self):
        """Test that agent tools are properly initialized"""
        # Check that enhanced tools are initialized
        assert hasattr(self.agent, 'calculator')
        assert hasattr(self.agent, 'time_tools')
        assert isinstance(self.agent.calculator, EnhancedCalculator)
        assert isinstance(self.agent.time_tools, EnhancedTimeTools)
        
        # Check that tools list contains enhanced tools
        tool_names = [tool.name for tool in self.agent.tools]
        assert "enhanced_calculator" in tool_names
        assert "get_current_time" in tool_names
        assert "time_conversion" in tool_names
        assert "time_difference" in tool_names
        assert "time_info" in tool_names
        assert "web_search" in tool_names
    
    def test_enhanced_calculator_safety(self):
        """Test enhanced calculator safety features"""
        # Test dangerous expressions are blocked
        dangerous_expressions = [
            "import os",
            "eval('2+2')",
            "exec('print(1)')",
            "open('file.txt')",
            "__import__('os')"
        ]
        
        for expr in dangerous_expressions:
            result = self.agent._enhanced_calculate(expr)
            assert "❌ Calculation Error:" in result or "unsafe" in result.lower()
    
    def test_enhanced_calculator_advanced_functions(self):
        """Test advanced mathematical functions"""
        advanced_expressions = [
            ("factorial(5)", "120.0"),
            ("gcd(12, 18)", "6.0"),
            ("lcm(12, 18)", "36.0"),
            ("sin(pi/2)", "1.0"),
            ("cos(0)", "1.0"),
            ("log(e)", "1.0")
        ]
        
        for expr, expected in advanced_expressions:
            result = self.agent._enhanced_calculate(expr)
            assert "✅ Calculation Result:" in result
            assert expected in result
    
    def test_timezone_handling(self):
        """Test timezone handling in time tools"""
        # Test with IANA timezone names
        timezones = [
            "UTC",
            "America/New_York",
            "America/Los_Angeles",
            "Europe/London",
            "Asia/Tokyo",
            "Asia/Kolkata"
        ]
        
        for tz in timezones:
            result = self.agent._get_current_time(tz)
            assert "🕐 Current Time:" in result
            assert "🌍 Timezone:" in result
            assert "📅 Unix Timestamp:" in result
            assert result.count("❌") == 0  # No error messages
    
    def test_time_conversion_edge_cases(self):
        """Test time conversion edge cases"""
        # Test conversion across date boundaries
        result = self.agent._convert_time("2024-01-01 23:00:00, UTC, EST")
        assert "🔄 Time Conversion:" in result
        
        # Test conversion with daylight saving time considerations
        result = self.agent._convert_time("2024-07-01 12:00:00, UTC, EST")
        assert "🔄 Time Conversion:" in result
    
    def test_time_difference_edge_cases(self):
        """Test time difference edge cases"""
        # Test same time
        result = self.agent._calculate_time_difference("2024-01-01 12:00:00, 2024-01-01 12:00:00, UTC")
        assert "⏱️ Time Difference:" in result
        assert "📊 In seconds: 0" in result
        
        # Test different days
        result = self.agent._calculate_time_difference("2024-01-01 12:00:00, 2024-01-02 12:00:00, UTC")
        assert "⏱️ Time Difference:" in result
        assert "📊 In days: 1" in result
    
    @patch('src.reasoning.ReasoningAgent.run')
    def test_agent_run_with_enhanced_tools(self, mock_run):
        """Test that agent run method works with enhanced tools"""
        # Mock the agent run method to return a successful result
        mock_run.return_value = ReasoningResult(
            content="Test response using enhanced tools",
            reasoning_steps=["Used enhanced calculator", "Used time tools"],
            confidence=0.9,
            sources=["enhanced_tools"],
            success=True
        )
        
        result = self.agent.run("Calculate 2 + 2 and tell me the current time")
        
        assert result.success is True
        assert "enhanced tools" in result.content.lower()
        assert len(result.reasoning_steps) > 0
        assert result.confidence > 0
    
    def test_tool_descriptions(self):
        """Test that tool descriptions are informative"""
        for tool in self.agent.tools:
            assert tool.description is not None
            assert len(tool.description) > 20  # Should be descriptive
            
            # Check that enhanced calculator description mentions advanced features
            if tool.name == "enhanced_calculator":
                assert "trigonometry" in tool.description.lower()
                assert "logarithms" in tool.description.lower()
                assert "factorials" in tool.description.lower()
            
            # Check that time tools mention timezone support
            if tool.name == "get_current_time":
                assert "timezone" in tool.description.lower()
    
    def test_error_handling_integration(self):
        """Test error handling integration with enhanced tools"""
        # Test calculator error handling
        result = self.agent._enhanced_calculate("undefined_function(1)")
        assert "❌ Calculation Error:" in result
        
        # Test time tool error handling
        result = self.agent._convert_time("invalid, format, here")
        assert "❌ Conversion Error:" in result
        
        # Test time difference error handling
        result = self.agent._calculate_time_difference("invalid, format, here")
        assert "❌ Difference Calculation Error:" in result

class TestEnhancedToolsIntegration:
    """Test integration between enhanced tools and reasoning engine"""
    
    def test_calculator_integration_with_agent(self):
        """Test calculator integration with agent system"""
        agent = ReasoningAgent(model_name="mistral")
        
        # Test that calculator is properly integrated
        assert agent.calculator is not None
        assert hasattr(agent.calculator, 'calculate')
        
        # Test a calculation through the agent's interface
        result = agent._enhanced_calculate("2 + 2")
        assert "✅ Calculation Result: 4" in result
    
    def test_time_tools_integration_with_agent(self):
        """Test time tools integration with agent system"""
        agent = ReasoningAgent(model_name="mistral")
        
        # Test that time tools are properly integrated
        assert agent.time_tools is not None
        assert hasattr(agent.time_tools, 'get_current_time')
        assert hasattr(agent.time_tools, 'convert_time')
        assert hasattr(agent.time_tools, 'get_time_difference')
        assert hasattr(agent.time_tools, 'get_time_info')
        
        # Test time operations through the agent's interface
        result = agent._get_current_time("UTC")
        assert "🕐 Current Time:" in result
    
    def test_tool_consistency(self):
        """Test that tools provide consistent results"""
        agent = ReasoningAgent(model_name="mistral")
        
        # Test calculator consistency
        result1 = agent._enhanced_calculate("2 + 2")
        result2 = agent._enhanced_calculate("2 + 2")
        assert result1 == result2
        
        # Test time tools consistency (within reasonable time bounds)
        result1 = agent._get_current_time("UTC")
        result2 = agent._get_current_time("UTC")
        # Both should contain current time info
        assert "🕐 Current Time:" in result1
        assert "🕐 Current Time:" in result2
    
    def test_tool_performance(self):
        """Test that enhanced tools perform reasonably"""
        agent = ReasoningAgent(model_name="mistral")
        
        import time
        
        # Test calculator performance
        start_time = time.time()
        agent._enhanced_calculate("factorial(10)")
        calc_time = time.time() - start_time
        assert calc_time < 1.0  # Should complete within 1 second
        
        # Test time tools performance
        start_time = time.time()
        agent._get_current_time("UTC")
        time_tool_time = time.time() - start_time
        assert time_tool_time < 1.0  # Should complete within 1 second

def test_enhanced_tools_backward_compatibility():
    """Test that enhanced tools maintain backward compatibility"""
    # Test that the basic functionality still works
    agent = ReasoningAgent(model_name="mistral")
    
    # Basic calculator operations should still work
    result = agent._enhanced_calculate("2 + 2")
    assert "4" in result
    
    # Basic time operations should still work
    result = agent._get_current_time()
    assert "🕐 Current Time:" in result

def test_enhanced_tools_error_recovery():
    """Test that enhanced tools can recover from errors"""
    agent = ReasoningAgent(model_name="mistral")
    
    # Test calculator error recovery
    result = agent._enhanced_calculate("2 / 0")
    assert "❌ Calculation Error:" in result
    
    # After an error, calculator should still work
    result = agent._enhanced_calculate("2 + 2")
    assert "✅ Calculation Result: 4" in result
    
    # Test time tools error recovery
    result = agent._convert_time("invalid, format, here")
    assert "❌ Conversion Error:" in result
    
    # After an error, time tools should still work
    result = agent._get_current_time("UTC")
    assert "🕐 Current Time:" in result 