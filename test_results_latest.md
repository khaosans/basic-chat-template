============================= test session starts ==============================
platform darwin -- Python 3.11.9, pytest-8.4.1, pluggy-1.6.0 -- /Users/Sour/.pyenv/versions/3.11.9/bin/python
cachedir: .pytest_cache
rootdir: /Users/Sour/github/basic-chat-template
configfile: pytest.ini
plugins: anyio-4.9.0, cov-6.2.1, langsmith-0.3.45, asyncio-1.0.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 168 items

tests/test_app.py::test_document_processor_init PASSED                   [  0%]
tests/test_app.py::test_mime_type_detection PASSED                       [  1%]
tests/test_app.py::test_ollama_chat_initialization PASSED                [  1%]
tests/test_app.py::test_chat_query_structure PASSED                      [  2%]
tests/test_app.py::test_error_handling PASSED                            [  2%]
tests/test_app.py::test_async_chat PASSED                                [  3%]
tests/test_app.py::test_chat_fallback_mechanism PASSED                   [  4%]
tests/test_app.py::test_health_check PASSED                              [  4%]
tests/test_app.py::test_cache_stats PASSED                               [  5%]
tests/test_app.py::test_stream_query PASSED                              [  5%]
tests/test_app.py::test_config_integration PASSED                        [  6%]
tests/test_app.py::test_async_chat_integration PASSED                    [  7%]
tests/test_app.py::test_cache_integration PASSED                         [  7%]
tests/test_basic.py::TestBasicFunctionality::test_ollamachat_initialization PASSED [  8%]
tests/test_basic.py::TestConfiguration::test_app_config_defaults PASSED  [  8%]
tests/test_basic.py::TestConfiguration::test_app_config_validation PASSED [  9%]
tests/test_basic.py::TestConfiguration::test_global_config_exists PASSED [ 10%]
tests/test_basic.py::TestCaching::test_global_cache_exists PASSED        [ 10%]
tests/test_basic.py::TestCaching::test_memory_cache_basic PASSED         [ 11%]
tests/test_basic.py::TestCaching::test_response_cache_basic PASSED       [ 11%]
tests/test_database_migrations.py::TestMigration::test_migration_creation PASSED [ 12%]
tests/test_database_migrations.py::TestMigrationManager::test_migration_manager_initialization PASSED [ 13%]
tests/test_database_migrations.py::TestMigrationManager::test_calculate_checksum PASSED [ 13%]
tests/test_database_migrations.py::TestMigrationManager::test_parse_migration_file PASSED [ 14%]
tests/test_database_migrations.py::TestMigrationManager::test_parse_invalid_migration_file PASSED [ 14%]
tests/test_database_migrations.py::TestMigrationManager::test_get_migration_files PASSED [ 15%]
tests/test_database_migrations.py::TestMigrationManager::test_apply_migration PASSED [ 16%]
tests/test_database_migrations.py::TestMigrationManager::test_apply_failed_migration PASSED [ 16%]
tests/test_database_migrations.py::TestMigrationManager::test_validate_migration PASSED [ 17%]
tests/test_database_migrations.py::TestMigrationManager::test_migrate_empty_database PASSED [ 17%]
tests/test_database_migrations.py::TestMigrationManager::test_migrate_with_files PASSED [ 18%]
tests/test_database_migrations.py::TestMigrationManager::test_migrate_with_existing_migrations PASSED [ 19%]
tests/test_database_migrations.py::TestMigrationManager::test_get_migration_status PASSED [ 19%]
tests/test_database_migrations.py::TestMigrationManager::test_create_migration PASSED [ 20%]
tests/test_database_migrations.py::TestMigrationManager::test_create_duplicate_migration PASSED [ 20%]
tests/test_database_migrations.py::TestMigrationIntegration::test_full_migration_workflow PASSED [ 21%]
tests/test_database_migrations.py::TestMigrationIntegration::test_migration_rollback_simulation PASSED [ 22%]
tests/test_database_migrations.py::TestGlobalFunctions::test_initialize_migrations PASSED [ 22%]
tests/test_database_migrations.py::TestGlobalFunctions::test_run_migrations FAILED [ 23%]
tests/test_database_migrations.py::TestGlobalFunctions::test_get_migration_status PASSED [ 23%]
tests/test_enhanced_audio.py::TestEnhancedAudioFunctionality::test_create_enhanced_audio_button_initialization PASSED [ 24%]
tests/test_enhanced_audio.py::TestEnhancedAudioFunctionality::test_get_professional_audio_html_creates_valid_html PASSED [ 25%]
tests/test_enhanced_audio.py::TestEnhancedAudioFunctionality::test_get_professional_audio_html_file_not_found PASSED [ 25%]
tests/test_enhanced_audio.py::TestEnhancedAudioFunctionality::test_get_professional_audio_html_none_file PASSED [ 26%]
tests/test_enhanced_audio.py::TestEnhancedAudioFunctionality::test_get_professional_audio_html_empty_string PASSED [ 26%]
tests/test_enhanced_audio.py::TestEnhancedAudioFunctionality::test_get_audio_file_size_bytes PASSED [ 27%]
tests/test_enhanced_audio.py::TestEnhancedAudioFunctionality::test_get_audio_file_size_kilobytes PASSED [ 27%]
tests/test_enhanced_audio.py::TestEnhancedAudioFunctionality::test_get_audio_file_size_megabytes PASSED [ 28%]
tests/test_enhanced_audio.py::TestEnhancedAudioFunctionality::test_get_audio_file_size_nonexistent PASSED [ 29%]
tests/test_enhanced_audio.py::TestEnhancedAudioFunctionality::test_cleanup_audio_files PASSED [ 29%]
tests/test_enhanced_audio.py::TestEnhancedAudioFunctionality::test_professional_audio_html_contains_modern_styling PASSED [ 30%]
tests/test_enhanced_audio.py::TestEnhancedAudioFunctionality::test_professional_audio_html_contains_accessibility_features PASSED [ 30%]
tests/test_enhanced_audio.py::TestEnhancedAudioFunctionality::test_professional_audio_html_error_handling PASSED [ 31%]
tests/test_enhanced_audio.py::TestEnhancedAudioFunctionality::test_professional_audio_html_base64_encoding PASSED [ 32%]
tests/test_enhanced_audio.py::TestEnhancedAudioFunctionality::test_professional_audio_html_file_size_display PASSED [ 32%]
tests/test_enhanced_audio.py::TestEnhancedAudioFunctionality::test_professional_audio_html_malformed_file PASSED [ 33%]
tests/test_enhanced_reasoning.py::TestEnhancedReasoningAgent::test_enhanced_calculator_tool PASSED [ 33%]
tests/test_enhanced_reasoning.py::TestEnhancedReasoningAgent::test_enhanced_time_tools PASSED [ 34%]
tests/test_enhanced_reasoning.py::TestEnhancedReasoningAgent::test_time_conversion_tool PASSED [ 35%]
tests/test_enhanced_reasoning.py::TestEnhancedReasoningAgent::test_time_difference_tool PASSED [ 35%]
tests/test_enhanced_reasoning.py::TestEnhancedReasoningAgent::test_time_info_tool PASSED [ 36%]
tests/test_enhanced_reasoning.py::TestEnhancedReasoningAgent::test_agent_tools_initialization FAILED [ 36%]
tests/test_enhanced_reasoning.py::TestEnhancedReasoningAgent::test_enhanced_calculator_safety PASSED [ 37%]
tests/test_enhanced_reasoning.py::TestEnhancedReasoningAgent::test_enhanced_calculator_advanced_functions PASSED [ 38%]
tests/test_enhanced_reasoning.py::TestEnhancedReasoningAgent::test_timezone_handling PASSED [ 38%]
tests/test_enhanced_reasoning.py::TestEnhancedReasoningAgent::test_time_conversion_edge_cases PASSED [ 39%]
tests/test_enhanced_reasoning.py::TestEnhancedReasoningAgent::test_time_difference_edge_cases PASSED [ 39%]
tests/test_enhanced_reasoning.py::TestEnhancedReasoningAgent::test_agent_run_with_enhanced_tools PASSED [ 40%]
tests/test_enhanced_reasoning.py::TestEnhancedReasoningAgent::test_tool_descriptions PASSED [ 41%]
tests/test_enhanced_reasoning.py::TestEnhancedReasoningAgent::test_error_handling_integration PASSED [ 41%]
tests/test_enhanced_reasoning.py::TestEnhancedToolsIntegration::test_calculator_integration_with_agent PASSED [ 42%]
tests/test_enhanced_reasoning.py::TestEnhancedToolsIntegration::test_time_tools_integration_with_agent PASSED [ 42%]
tests/test_enhanced_reasoning.py::TestEnhancedToolsIntegration::test_tool_consistency PASSED [ 43%]
tests/test_enhanced_reasoning.py::TestEnhancedToolsIntegration::test_tool_performance PASSED [ 44%]
tests/test_enhanced_reasoning.py::test_enhanced_tools_backward_compatibility PASSED [ 44%]
tests/test_enhanced_reasoning.py::test_enhanced_tools_error_recovery PASSED [ 45%]
tests/test_enhanced_tools.py::TestEnhancedCalculator::test_basic_arithmetic PASSED [ 45%]
tests/test_enhanced_tools.py::TestEnhancedCalculator::test_mathematical_functions PASSED [ 46%]
tests/test_enhanced_tools.py::TestEnhancedCalculator::test_trigonometric_functions PASSED [ 47%]
tests/test_enhanced_tools.py::TestEnhancedCalculator::test_logarithmic_functions FAILED [ 47%]
tests/test_enhanced_tools.py::TestEnhancedCalculator::test_constants FAILED [ 48%]
tests/test_enhanced_tools.py::TestEnhancedCalculator::test_complex_expressions PASSED [ 48%]
tests/test_enhanced_tools.py::TestEnhancedCalculator::test_expression_cleaning PASSED [ 49%]
tests/test_enhanced_tools.py::TestEnhancedCalculator::test_error_handling PASSED [ 50%]
tests/test_enhanced_tools.py::TestEnhancedCalculator::test_safety_validation PASSED [ 50%]
tests/test_enhanced_tools.py::TestEnhancedCalculator::test_result_formatting PASSED [ 51%]
tests/test_enhanced_tools.py::TestEnhancedTimeTools::test_get_current_time_utc PASSED [ 51%]
tests/test_enhanced_tools.py::TestEnhancedTimeTools::test_get_current_time_different_timezones PASSED [ 52%]
tests/test_enhanced_tools.py::TestEnhancedTimeTools::test_timezone_normalization PASSED [ 52%]
tests/test_enhanced_tools.py::TestEnhancedTimeTools::test_time_conversion PASSED [ 53%]
tests/test_enhanced_tools.py::TestEnhancedTimeTools::test_time_difference_calculation PASSED [ 54%]
tests/test_enhanced_tools.py::TestEnhancedTimeTools::test_time_info_comprehensive PASSED [ 54%]
tests/test_enhanced_tools.py::TestEnhancedTimeTools::test_available_timezones PASSED [ 55%]
tests/test_enhanced_tools.py::TestEnhancedTimeTools::test_error_handling_invalid_timezone PASSED [ 55%]
tests/test_enhanced_tools.py::TestEnhancedTimeTools::test_error_handling_invalid_time_format PASSED [ 56%]
tests/test_enhanced_tools.py::TestEnhancedTimeTools::test_error_handling_invalid_timezone_conversion PASSED [ 57%]
tests/test_enhanced_tools.py::TestEnhancedTimeTools::test_pytz_import_error_handling FAILED [ 57%]
tests/test_enhanced_tools.py::TestIntegration::test_calculator_and_time_integration FAILED [ 58%]
tests/test_enhanced_tools.py::TestIntegration::test_complex_calculation_with_time FAILED [ 58%]
tests/test_enhanced_tools.py::test_tool_initialization[EnhancedCalculator] PASSED [ 59%]
tests/test_enhanced_tools.py::test_tool_initialization[EnhancedTimeTools] PASSED [ 60%]
tests/test_enhanced_tools.py::test_calculation_result_dataclass PASSED   [ 60%]
tests/test_enhanced_tools.py::test_time_result_dataclass PASSED          [ 61%]
tests/test_processing.py::test_document_processor_initialization PASSED  [ 61%]
tests/test_processing.py::test_text_splitting PASSED                     [ 62%]
tests/test_processing.py::test_empty_document_handling PASSED            [ 63%]
tests/test_processing.py::test_document_metadata_handling PASSED         [ 63%]
tests/test_processing.py::test_async_processing PASSED                   [ 64%]
tests/test_reasoning.py::test_reasoning_result_creation PASSED           [ 64%]
tests/test_reasoning.py::test_chain_of_thought PASSED                    [ 65%]
tests/test_reasoning.py::test_multi_step_reasoning PASSED                [ 66%]
tests/test_reasoning.py::test_agent_based_reasoning PASSED               [ 66%]
tests/test_reasoning.py::test_error_handling PASSED                      [ 67%]
tests/test_reasoning.py::test_reasoning_components[ReasoningChain] PASSED [ 67%]
tests/test_reasoning.py::test_reasoning_components[<lambda>] PASSED      [ 68%]
tests/test_reasoning.py::test_reasoning_components[ReasoningAgent] PASSED [ 69%]
tests/test_reasoning.py::TestAsyncFunctionality::test_async_ollama_client_init PASSED [ 69%]
tests/test_reasoning.py::TestAsyncFunctionality::test_async_ollama_chat_init PASSED [ 70%]
tests/test_reasoning.py::TestAsyncFunctionality::test_async_chat_query PASSED [ 70%]
tests/test_reasoning.py::TestAsyncFunctionality::test_async_health_check PASSED [ 71%]
tests/test_reasoning.py::TestAsyncFunctionality::test_async_stream_query PASSED [ 72%]
tests/test_session_manager.py::TestChatSession::test_chat_session_creation PASSED [ 72%]
tests/test_session_manager.py::TestChatSession::test_chat_session_with_optional_fields PASSED [ 73%]
tests/test_session_manager.py::TestSessionMetadata::test_session_metadata_defaults PASSED [ 73%]
tests/test_session_manager.py::TestSessionMetadata::test_session_metadata_with_values PASSED [ 74%]
tests/test_session_manager.py::TestSessionManager::test_session_manager_initialization PASSED [ 75%]
tests/test_session_manager.py::TestSessionManager::test_create_session PASSED [ 75%]
tests/test_session_manager.py::TestSessionManager::test_save_and_load_session PASSED [ 76%]
tests/test_session_manager.py::TestSessionManager::test_load_nonexistent_session PASSED [ 76%]
tests/test_session_manager.py::TestSessionManager::test_list_sessions PASSED [ 77%]
tests/test_session_manager.py::TestSessionManager::test_list_sessions_with_pagination PASSED [ 77%]
tests/test_session_manager.py::TestSessionManager::test_update_session PASSED [ 78%]
tests/test_session_manager.py::TestSessionManager::test_delete_session PASSED [ 79%]
tests/test_session_manager.py::TestSessionManager::test_search_sessions PASSED [ 79%]
tests/test_session_manager.py::TestSessionManager::test_export_session_json PASSED [ 80%]
tests/test_session_manager.py::TestSessionManager::test_export_session_markdown PASSED [ 80%]
tests/test_session_manager.py::TestSessionManager::test_export_invalid_format PASSED [ 81%]
tests/test_session_manager.py::TestSessionManager::test_import_session PASSED [ 82%]
tests/test_session_manager.py::TestSessionManager::test_auto_save_session PASSED [ 82%]
tests/test_session_manager.py::TestSessionManager::test_get_session_stats PASSED [ 83%]
tests/test_session_manager.py::TestSessionManager::test_get_session_stats_nonexistent PASSED [ 83%]
tests/test_session_manager.py::TestSessionManager::test_cleanup_old_sessions PASSED [ 84%]
tests/test_session_manager.py::TestSessionManager::test_get_database_stats PASSED [ 85%]
tests/test_session_manager.py::TestSessionManager::test_session_manager_error_handling PASSED [ 85%]
tests/test_session_manager.py::TestSessionManagerIntegration::test_full_session_lifecycle PASSED [ 86%]
tests/test_session_manager.py::TestSessionManagerIntegration::test_multiple_users PASSED [ 86%]
tests/test_voice.py::TestVoiceFunctionality::test_text_to_speech_creates_file PASSED [ 87%]
tests/test_voice.py::TestVoiceFunctionality::test_text_to_speech_consistent_hash PASSED [ 88%]
tests/test_voice.py::TestVoiceFunctionality::test_text_to_speech_different_texts PASSED [ 88%]
tests/test_voice.py::TestVoiceFunctionality::test_text_to_speech_empty_text PASSED [ 89%]
tests/test_voice.py::TestVoiceFunctionality::test_text_to_speech_none_text PASSED [ 89%]
tests/test_voice.py::TestVoiceFunctionality::test_text_to_speech_whitespace_text PASSED [ 90%]
tests/test_voice.py::TestVoiceFunctionality::test_get_audio_html_creates_valid_html PASSED [ 91%]
tests/test_voice.py::TestVoiceFunctionality::test_get_audio_html_file_not_found PASSED [ 91%]
tests/test_voice.py::TestVoiceFunctionality::test_get_audio_html_none_file PASSED [ 92%]
tests/test_voice.py::TestVoiceFunctionality::test_voice_integration PASSED [ 92%]
tests/test_voice.py::TestVoiceFunctionality::test_text_to_speech_gtts_integration FAILED [ 93%]
tests/test_voice.py::TestVoiceFunctionality::test_voice_with_special_characters PASSED [ 94%]
tests/test_voice.py::TestVoiceFunctionality::test_voice_with_long_text PASSED [ 94%]
tests/test_voice.py::TestVoiceFunctionality::test_voice_with_unicode PASSED [ 95%]
tests/test_web_search.py::TestWebSearch::test_basic_search PASSED        [ 95%]
tests/test_web_search.py::TestWebSearch::test_empty_query PASSED         [ 96%]
tests/test_web_search.py::TestWebSearch::test_formatted_output PASSED    [ 97%]
tests/test_web_search.py::TestWebSearch::test_max_results PASSED         [ 97%]
tests/test_web_search.py::TestWebSearch::test_rate_limit_handling FAILED [ 98%]
tests/test_web_search.py::TestWebSearch::test_search_result_creation PASSED [ 98%]
tests/test_web_search.py::TestWebSearch::test_search_result_string_representation PASSED [ 99%]
tests/test_web_search.py::TestWebSearch::test_web_search_class PASSED    [100%]

=================================== FAILURES ===================================
___________________ TestGlobalFunctions.test_run_migrations ____________________
tests/test_database_migrations.py:527: in test_run_migrations
    original_manager = database_migrations.migration_manager
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: module 'database_migrations' has no attribute 'migration_manager'
__________ TestEnhancedReasoningAgent.test_agent_tools_initialization __________
tests/test_enhanced_reasoning.py:88: in test_agent_tools_initialization
    assert isinstance(self.agent.calculator, EnhancedCalculator)
E   assert False
E    +  where False = isinstance(<utils.enhanced_tools.EnhancedCalculator object at 0x10d574790>, EnhancedCalculator)
E    +    where <utils.enhanced_tools.EnhancedCalculator object at 0x10d574790> = <src.reasoning.reasoning_engine.ReasoningAgent object at 0x10d574250>.calculator
E    +      where <src.reasoning.reasoning_engine.ReasoningAgent object at 0x10d574250> = <test_enhanced_reasoning.TestEnhancedReasoningAgent object at 0x10bd219d0>.agent
______________ TestEnhancedCalculator.test_logarithmic_functions _______________
tests/test_enhanced_tools.py:82: in test_logarithmic_functions
    assert result.result == expected
E   AssertionError: assert '2.3' == '1.0'
E     
E     - 1.0
E     + 2.3
____________________ TestEnhancedCalculator.test_constants _____________________
tests/test_enhanced_tools.py:96: in test_constants
    assert result.result == expected
E   AssertionError: assert '3.1' == '3.141592653589793'
E     
E     - 3.141592653589793
E     + 3.1
____________ TestEnhancedTimeTools.test_pytz_import_error_handling _____________
tests/test_enhanced_tools.py:303: in test_pytz_import_error_handling
    assert result.success is False
E   AssertionError: assert True is False
E    +  where True = TimeResult(current_time='2025-06-20 20:48:54 UTC', timezone='UTC', formatted_time='2025-06-20 20:48:54 UTC', unix_timestamp=1750452534.693691, success=True, error=None).success
_____________ TestIntegration.test_calculator_and_time_integration _____________
tests/test_enhanced_tools.py:312: in test_calculator_and_time_integration
    time_result = self.time_tools.get_current_time("UTC")
                  ^^^^^^^^^^^^^^^
E   AttributeError: 'TestIntegration' object has no attribute 'time_tools'
______________ TestIntegration.test_complex_calculation_with_time ______________
tests/test_enhanced_tools.py:323: in test_complex_calculation_with_time
    time_result = self.time_tools.get_current_time("UTC")
                  ^^^^^^^^^^^^^^^
E   AttributeError: 'TestIntegration' object has no attribute 'time_tools'
_________ TestVoiceFunctionality.test_text_to_speech_gtts_integration __________
tests/test_voice.py:186: in test_text_to_speech_gtts_integration
    mock_gtts.assert_called_once_with(text=test_text, lang='en', slow=False)
../../.pyenv/versions/3.11.9/lib/python3.11/unittest/mock.py:950: in assert_called_once_with
    raise AssertionError(msg)
E   AssertionError: Expected 'gTTS' to be called once. Called 0 times.
----------------------------- Captured stderr call -----------------------------
2025-06-20 13:49:27.534 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
____________________ TestWebSearch.test_rate_limit_handling ____________________
tests/test_web_search.py:100: in test_rate_limit_handling
    self.assertIn("Unable to perform real-time search", results, "Should indicate search failure")
E   AssertionError: 'Unable to perform real-time search' not found in 'Search Results:\n\n1. **Welcome to Python.org**\n   Python is a versatile and easy-to-learn programming language that lets you work quickly and integrate systems more effectively. Learn Python basics, download the latest version, access documentation, find jobs, events, success stories and more on the official website.\n   [Link]()\n\n2. **Python (programming language) - Wikipedia**\n   Learn about Python, a high-level, general-purpose language created by Guido van Rossum in 1991. Python supports multiple paradigms, has a comprehensive standard library, and is widely used in machine learning and other domains.\n   [Link]()\n\n3. **Python Tutorial - W3Schools**\n   W3Schools offers a comprehensive and interactive Python tutorial with examples, exercises, quizzes, and references. Learn how to create web applications, handle files and databases, and get certified by completing the PYTHON course.\n   [Link]()\n\n4. **Python Tutorial | Learn Python Programming Language - GeeksforGeeks**\n   A comprehensive guide to learn Python, a popular and versatile programming language for web development, data science, automation and more. Covering basics, functions, data structures, OOPs, exceptions, file handling, databases, packages, data science and web development with Python.\n   [Link]()\n\n5. **Learn Python Programming**\n   A comprehensive guide to learn Python, one of the top programming languages in the world, widely used in AI, data science, and web development. Find free tutorials, interactive courses, online compiler, and career tips for beginners and advanced learners.\n   [Link]()\n\n' : Should indicate search failure
----------------------------- Captured stdout call -----------------------------
Search attempt 1 failed: https://lite.duckduckgo.com/lite/ 202 Ratelimit
Rate limited, waiting 2.4 seconds...
=============================== warnings summary ===============================
tests/test_app.py::test_async_chat
  /Users/Sour/github/basic-chat-template/src/core/app.py:110: RuntimeWarning: coroutine 'OllamaChat._query_async' was never awaited
    self._use_sync_fallback = True
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

tests/test_enhanced_reasoning.py::TestEnhancedReasoningAgent::test_enhanced_calculator_tool
  /Users/Sour/github/basic-chat-template/src/reasoning/reasoning_engine.py:48: LangChainDeprecationWarning: Please see the migration guide at: https://python.langchain.com/docs/versions/migrating_memory/
    self.memory = ConversationBufferMemory(

tests/test_enhanced_reasoning.py::TestEnhancedReasoningAgent::test_enhanced_calculator_tool
  /Users/Sour/github/basic-chat-template/src/reasoning/reasoning_engine.py:61: LangChainDeprecationWarning: LangChain agents will continue to be supported, but it is recommended for new use cases to be built with LangGraph. LangGraph offers a more flexible and full-featured framework for building agents, including support for tool-calling, persistence of state, and human-in-the-loop workflows. For details, refer to the `LangGraph documentation <https://langchain-ai.github.io/langgraph/>`_ as well as guides for `Migrating from AgentExecutor <https://python.langchain.com/docs/how_to/migrate_agent/>`_ and LangGraph's `Pre-built ReAct agent <https://langchain-ai.github.io/langgraph/how-tos/create-react-agent/>`_.
    self.agent = initialize_agent(

tests/test_processing.py::test_document_processor_initialization
  /Users/Sour/github/basic-chat-template/src/core/document_processor.py:34: LangChainDeprecationWarning: The class `OllamaEmbeddings` was deprecated in LangChain 0.3.1 and will be removed in 1.0.0. An updated version of the class exists in the :class:`~langchain-ollama package and should be used instead. To use it run `pip install -U :class:`~langchain-ollama` and import as `from :class:`~langchain_ollama import OllamaEmbeddings``.
    self.embeddings = OllamaEmbeddings(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============================= slowest 10 durations =============================
9.04s call     tests/test_reasoning.py::test_agent_based_reasoning
8.82s call     tests/test_app.py::test_async_chat
8.21s call     tests/test_app.py::test_chat_fallback_mechanism
7.94s call     tests/test_reasoning.py::test_multi_step_reasoning
5.48s call     tests/test_web_search.py::TestWebSearch::test_max_results
4.94s call     tests/test_reasoning.py::test_reasoning_components[<lambda>]
4.90s call     tests/test_web_search.py::TestWebSearch::test_rate_limit_handling
4.81s call     tests/test_reasoning.py::test_reasoning_components[ReasoningAgent]
2.94s call     tests/test_reasoning.py::test_chain_of_thought
2.75s call     tests/test_app.py::test_chat_query_structure
=========================== short test summary info ============================
FAILED tests/test_database_migrations.py::TestGlobalFunctions::test_run_migrations
FAILED tests/test_enhanced_reasoning.py::TestEnhancedReasoningAgent::test_agent_tools_initialization
FAILED tests/test_enhanced_tools.py::TestEnhancedCalculator::test_logarithmic_functions
FAILED tests/test_enhanced_tools.py::TestEnhancedCalculator::test_constants
FAILED tests/test_enhanced_tools.py::TestEnhancedTimeTools::test_pytz_import_error_handling
FAILED tests/test_enhanced_tools.py::TestIntegration::test_calculator_and_time_integration
FAILED tests/test_enhanced_tools.py::TestIntegration::test_complex_calculation_with_time
FAILED tests/test_voice.py::TestVoiceFunctionality::test_text_to_speech_gtts_integration
FAILED tests/test_web_search.py::TestWebSearch::test_rate_limit_handling - As...
============= 9 failed, 159 passed, 4 warnings in 69.65s (0:01:09) =============
