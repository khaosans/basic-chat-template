"""
Reasoning Engine for Enhanced AI Capabilities
Provides chain-of-thought, multi-step reasoning, and agent-based processing
"""

import os
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import streamlit as st
import datetime

from langchain.agents import initialize_agent, AgentType, Tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder, PromptTemplate, ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from langchain.chains import LLMChain
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from src.api.web_search import search_web
from src.utils.enhanced_tools import EnhancedCalculator, EnhancedTimeTools

# Load environment variables
OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral")

@dataclass
class ReasoningResult:
    """Result from reasoning operations"""
    content: str  # Final answer/conclusion
    reasoning_steps: List[str]  # Step-by-step thought process
    confidence: float
    sources: List[str]
    intermediate_thoughts: List[str] = None  # For storing intermediate reasoning steps
    success: bool = True
    error: Optional[str] = None

class ReasoningAgent:
    """Enhanced agent with reasoning capabilities"""
    
    def __init__(self, model_name: str = OLLAMA_MODEL):
        self.llm = ChatOllama(
            model=model_name,
            base_url=OLLAMA_API_URL.replace("/api", "")
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize enhanced tools
        self.calculator = EnhancedCalculator()
        self.time_tools = EnhancedTimeTools()
        
        # Initialize tools
        self.tools = self._create_tools()
        
        # Initialize agent with better configuration
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            early_stopping_method="generate"
        )
    
    def _create_tools(self) -> List[Tool]:
        """Create enhanced tools for the agent"""
        return [
            Tool(
                name="web_search",
                func=self._web_search,
                description="Search the web for current information. Use this for questions about recent events, current prices, weather, or any information that might change over time."
            ),
            Tool(
                name="enhanced_calculator",
                func=self._enhanced_calculate,
                description="Perform advanced mathematical calculations including trigonometry, logarithms, factorials, and more. Input should be a mathematical expression like '2 + 2', 'sqrt(16)', 'sin(pi/2)', 'factorial(5)', or 'gcd(12, 18)'."
            ),
            Tool(
                name="get_current_time",
                func=self._get_current_time,
                description="Get the current date and time with timezone support. Use this when asked about the current time or date. You can specify a timezone like 'UTC', 'EST', 'PST', 'GMT', 'JST', etc."
            ),
            Tool(
                name="time_conversion",
                func=self._convert_time,
                description="Convert time between different timezones. Input format: 'time_string, from_timezone, to_timezone' (e.g., '2024-01-01 12:00:00, UTC, EST')."
            ),
            Tool(
                name="time_difference",
                func=self._calculate_time_difference,
                description="Calculate the difference between two times. Input format: 'time1, time2, timezone' (e.g., '2024-01-01 12:00:00, 2024-01-01 14:00:00, UTC')."
            ),
            Tool(
                name="time_info",
                func=self._get_time_info,
                description="Get comprehensive time information including weekday, month, day of year, etc. Input should be a timezone name (e.g., 'UTC', 'EST')."
            )
        ]
    
    def _enhanced_calculate(self, expression: str) -> str:
        """Enhanced calculator function with detailed output"""
        result = self.calculator.calculate(expression)
        
        if result.success:
            # Format the output with steps
            output = f"✅ Calculation Result: {result.result}\n"
            output += f"📝 Expression: {result.expression}\n"
            output += "🔢 Steps:\n"
            for step in result.steps:
                output += f"  {step}\n"
            return output
        else:
            return f"❌ Calculation Error: {result.error}\n📝 Expression: {result.expression}"
    
    def _get_current_time(self, timezone: str = "UTC") -> str:
        """Get current time with enhanced formatting"""
        result = self.time_tools.get_current_time(timezone)
        
        if result.success:
            output = f"🕐 Current Time: {result.current_time}\n"
            output += f"🌍 Timezone: {result.timezone}\n"
            output += f"📅 Unix Timestamp: {result.unix_timestamp:.0f}\n"
            
            # Add additional time info
            time_info = self.time_tools.get_time_info(timezone)
            if time_info["success"]:
                output += f"📊 Day of Week: {time_info['weekday']}\n"
                output += f"📊 Month: {time_info['month_name']}\n"
                output += f"📊 Day of Year: {time_info['day_of_year']}\n"
                output += f"📊 Business Day: {'Yes' if time_info['is_business_day'] else 'No'}\n"
            
            return output
        else:
            return f"❌ Time Error: {result.error}"
    
    def _convert_time(self, input_str: str) -> str:
        """Convert time between timezones"""
        try:
            # Parse input: "time_string, from_timezone, to_timezone"
            parts = [part.strip() for part in input_str.split(',')]
            if len(parts) != 3:
                return "❌ Invalid format. Use: 'time_string, from_timezone, to_timezone'"
            
            time_str, from_tz, to_tz = parts
            result = self.time_tools.convert_time(time_str, from_tz, to_tz)
            
            if result.success:
                output = f"🔄 Time Conversion:\n"
                output += f"📅 From: {time_str} ({from_tz})\n"
                output += f"📅 To: {result.current_time}\n"
                output += f"🌍 Target Timezone: {result.timezone}\n"
                output += f"📅 Unix Timestamp: {result.unix_timestamp:.0f}\n"
                return output
            else:
                return f"❌ Conversion Error: {result.error}"
        except Exception as e:
            return f"❌ Conversion Error: {str(e)}"
    
    def _calculate_time_difference(self, input_str: str) -> str:
        """Calculate time difference between two times"""
        try:
            # Parse input: "time1, time2, timezone"
            parts = [part.strip() for part in input_str.split(',')]
            if len(parts) != 3:
                return "❌ Invalid format. Use: 'time1, time2, timezone'"
            
            time1, time2, timezone = parts
            result = self.time_tools.get_time_difference(time1, time2, timezone)
            
            if result["success"]:
                output = f"⏱️ Time Difference:\n"
                output += f"📅 Time 1: {time1}\n"
                output += f"📅 Time 2: {time2}\n"
                output += f"🌍 Timezone: {timezone}\n"
                output += f"⏰ Difference: {result['formatted_difference']}\n"
                output += f"📊 In seconds: {result['difference_seconds']:.0f}\n"
                output += f"📊 In minutes: {result['difference_minutes']:.1f}\n"
                output += f"📊 In hours: {result['difference_hours']:.2f}\n"
                output += f"📊 In days: {result['difference_days']}\n"
                return output
            else:
                return f"❌ Difference Calculation Error: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"❌ Difference Calculation Error: {str(e)}"
    
    def _get_time_info(self, timezone: str = "UTC") -> str:
        """Get comprehensive time information"""
        result = self.time_tools.get_time_info(timezone)
        
        if result["success"]:
            output = f"📅 Comprehensive Time Info ({timezone}):\n"
            output += f"🕐 Current Time: {result['current_time']}\n"
            output += f"📊 Year: {result['year']}\n"
            output += f"📊 Month: {result['month_name']} ({result['month']})\n"
            output += f"📊 Day: {result['day']}\n"
            output += f"📊 Time: {result['hour']:02d}:{result['minute']:02d}:{result['second']:02d}\n"
            output += f"📊 Day of Week: {result['weekday']}\n"
            output += f"📊 Day of Year: {result['day_of_year']}\n"
            output += f"🏖️ Weekend: {'Yes' if result['is_weekend'] else 'No'}\n"
            output += f"📊 Business Day: {'Yes' if result['is_business_day'] else 'No'}\n"
            output += f"📅 Unix Timestamp: {result['unix_timestamp']:.0f}\n"
            return output
        else:
            return f"❌ Time Info Error: {result.get('error', 'Unknown error')}"
    
    def _web_search(self, query: str) -> str:
        """Perform web search with improved error handling"""
        try:
            results = search_web(query, max_results=3)
            
            # Check if we got meaningful results
            if "Unable to perform real-time search" in results or "Search Temporarily Unavailable" in results:
                return f"Web search is currently experiencing high traffic. For '{query}', please try again in a few minutes or visit a search engine directly."
            
            return results
        except Exception as e:
            return f"Web search failed: {str(e)}. Please try again later."
    
    def run(self, query: str) -> ReasoningResult:
        """Execute agent-based reasoning"""
        try:
            # Run the agent with the query
            response = self.agent.invoke({
                "input": query,
                "chat_history": self.memory.chat_memory.messages if hasattr(self.memory, 'chat_memory') else []
            })
            
            # Extract steps from the agent's thought process
            steps = []
            if hasattr(response, 'intermediate_steps'):
                for step in response.intermediate_steps:
                    if isinstance(step, tuple) and len(step) >= 2:
                        action, observation = step
                        steps.append(f"🤔 Thought: {action.log}")
                        steps.append(f"🔍 Action: Used {action.tool}")
                        steps.append(f"📝 Result: {observation}")
            
            # If no intermediate steps, try to extract from the output
            if not steps:
                output = response["output"] if isinstance(response, dict) else str(response)
                # Try to parse the output for any structured information
                if "Thought:" in output:
                    lines = output.split('\n')
                    for line in lines:
                        if line.strip() and any(keyword in line for keyword in ['Thought:', 'Action:', 'Result:', 'Observation:']):
                            steps.append(line.strip())
            
            # If still no steps, create a basic step from the output
            if not steps:
                output = response["output"] if isinstance(response, dict) else str(response)
                steps = [f"🤔 Processed query: {query}", f"📝 Generated response: {output[:100]}..."]
            
            return ReasoningResult(
                content=response["output"] if isinstance(response, dict) else str(response),
                reasoning_steps=steps,
                confidence=0.9,
                sources=["agent_based_reasoning"],
                intermediate_thoughts=steps
            )
        except Exception as e:
            return ReasoningResult(
                content="",
                reasoning_steps=[],
                confidence=0.0,
                sources=[],
                success=False,
                error=str(e)
            )

class ReasoningChain:
    """Chain-of-thought reasoning implementation"""
    
    def __init__(self, model_name: str = OLLAMA_MODEL):
        self.llm = ChatOllama(
            model=model_name,
            base_url=OLLAMA_API_URL.replace("/api", ""),
            streaming=True  # Enable streaming
        )
        
        # Use ChatPromptTemplate for better chat model compatibility
        self.reasoning_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI assistant that excels at step-by-step reasoning. 
            When given a question, break down your thinking into clear, numbered steps.
            Separate your thought process from your final answer.
            Format your response as follows:
            
            THINKING:
            1) First step...
            2) Second step...
            3) Final step...
            
            ANSWER:
            [Your final, concise answer here]"""),
            ("human", "{question}")
        ])
        
        # Use the newer RunnableSequence approach
        self.chain = self.reasoning_prompt | self.llm

    def execute_reasoning(self, question: str) -> ReasoningResult:
        """Execute chain-of-thought reasoning"""
        try:
            response = self.chain.invoke({"question": question})
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Split thinking and answer
            parts = content.split("ANSWER:")
            thinking = parts[0].replace("THINKING:", "").strip()
            answer = parts[1].strip() if len(parts) > 1 else content
            
            # Extract reasoning steps
            steps = [step.strip() for step in thinking.split("\n") if step.strip()]
            
            return ReasoningResult(
                content=answer,
                reasoning_steps=steps,
                confidence=0.9,
                sources=["chain_of_thought"],
                intermediate_thoughts=steps
            )
        except Exception as e:
            return ReasoningResult(
                content="",
                reasoning_steps=[],
                confidence=0.0,
                sources=[],
                success=False,
                error=str(e)
            )

class MultiStepReasoning:
    """Multi-step reasoning with document context"""
    
    def __init__(self, doc_processor, model_name: str = OLLAMA_MODEL):
        self.doc_processor = doc_processor
        self.llm = ChatOllama(
            model=model_name,
            base_url=OLLAMA_API_URL.replace("/api", ""),
            streaming=True
        )
        
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI assistant that analyzes questions and breaks them down into clear steps.
            Format your response as follows:
            
            ANALYSIS:
            1) Question type...
            2) Key components...
            3) Required information...
            
            STEPS:
            1) First step to solve...
            2) Second step...
            3) Final step..."""),
            ("human", "{query}")
        ])
        
        self.reasoning_prompt = ChatPromptTemplate.from_messages([
            ("system", """Based on the analysis and context, provide a structured solution.
            Format your response as follows:
            
            PROCESS:
            1) Understanding...
            2) Applying context...
            3) Reasoning...
            
            ANSWER:
            [Your final, concise answer here]"""),
            ("human", """Analysis: {analysis}
            Context: {context}
            Query: {query}""")
        ])
        
        # Create chains using RunnableSequence
        self.analysis_chain = self.analysis_prompt | self.llm
        self.reasoning_chain = self.reasoning_prompt | self.llm
    
    def step_by_step_reasoning(self, query: str) -> ReasoningResult:
        """Execute multi-step reasoning"""
        try:
            # Step 1: Analyze the query
            analysis_response = self.analysis_chain.invoke({"query": query})
            analysis = analysis_response.content if hasattr(analysis_response, 'content') else str(analysis_response)
            
            # Extract analysis steps
            analysis_steps = [step.strip() for step in analysis.split("\n") if step.strip() and not step.startswith("STEPS:")]
            
            # Step 2: Gather relevant context
            context = self.doc_processor.get_relevant_context(query) if self.doc_processor else ""
            
            # Step 3: Reason through the information
            reasoning_response = self.reasoning_chain.invoke({
                "analysis": analysis,
                "context": context,
                "query": query
            })
            reasoning = reasoning_response.content if hasattr(reasoning_response, 'content') else str(reasoning_response)
            
            # Split process and answer
            parts = reasoning.split("ANSWER:")
            process = parts[0].replace("PROCESS:", "").strip()
            answer = parts[1].strip() if len(parts) > 1 else reasoning
            
            # Extract reasoning steps
            reasoning_steps = [step.strip() for step in process.split("\n") if step.strip()]
            
            # Combine all steps for the thought process
            all_steps = analysis_steps + ["---"] + reasoning_steps
            
            return ReasoningResult(
                content=answer,
                reasoning_steps=all_steps,
                confidence=0.9,
                sources=["multi_step_reasoning", "document_context"] if context else ["multi_step_reasoning"],
                intermediate_thoughts=all_steps
            )
        except Exception as e:
            return ReasoningResult(
                content="",
                reasoning_steps=[],
                confidence=0.0,
                sources=[],
                success=False,
                error=str(e)
            )

class ReasoningDocumentProcessor:
    """Enhanced document processor with reasoning capabilities"""
    
    def __init__(self, model_name: str = OLLAMA_MODEL):
        self.llm = ChatOllama(
            model=model_name,
            base_url=OLLAMA_API_URL.replace("/api", "")
        )
        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url=OLLAMA_API_URL.replace("/api", "")
        )
        self.vectorstore = None
        self.processed_files = []
        
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI assistant that analyzes documents and extracts key information."),
            ("human", """Analyze this document and extract:
1. Key topics and themes
2. Important facts and data
3. Relationships between concepts
4. Potential questions this document could answer

Document: {document_text}

Provide a structured analysis:""")
        ])
        
        # Create chain using RunnableSequence
        self.analysis_chain = self.analysis_prompt | self.llm
    
    def analyze_document_content(self, document_text: str) -> Dict[str, str]:
        """Analyze document content for reasoning capabilities"""
        try:
            response = self.analysis_chain.invoke({"document_text": document_text[:2000]})  # Limit for analysis
            analysis = response.content if hasattr(response, 'content') else str(response)
            
            return {
                "analysis": analysis,
                "content": document_text,
                "key_topics": self._extract_topics(analysis),
                "reasoning_potential": self._assess_reasoning_potential(analysis)
            }
        except Exception as e:
            return {
                "analysis": f"Error analyzing document: {str(e)}",
                "content": document_text,
                "key_topics": [],
                "reasoning_potential": "low"
            }
    
    def _extract_topics(self, analysis: str) -> List[str]:
        """Extract key topics from analysis"""
        # Simple topic extraction - could be enhanced
        topics = []
        lines = analysis.split('\n')
        for line in lines:
            if line.strip().startswith(('1.', '2.', '3.', '4.')):
                topics.append(line.strip())
        return topics
    
    def _assess_reasoning_potential(self, analysis: str) -> str:
        """Assess the reasoning potential of the document"""
        if any(word in analysis.lower() for word in ['data', 'facts', 'relationships', 'analysis']):
            return "high"
        elif any(word in analysis.lower() for word in ['information', 'details', 'content']):
            return "medium"
        else:
            return "low"
    
    def create_reasoning_context(self, query: str) -> str:
        """Create context optimized for reasoning"""
        if not self.vectorstore:
            return "No documents available for context"
        
        try:
            relevant_docs = self.vectorstore.similarity_search(query, k=3)
            
            reasoning_context_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an AI assistant that creates reasoning frameworks."),
                ("human", """Given this query: {query}

And these relevant documents: {relevant_docs}

Create a reasoning framework that:
1. Identifies the key information needed
2. Shows how different pieces connect
3. Provides a logical structure for answering

Format this as a reasoning template.""")
            ])
            
            context_chain = reasoning_context_prompt | self.llm
            response = context_chain.invoke({
                "query": query,
                "relevant_docs": "\n".join([doc.page_content for doc in relevant_docs])
            })
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return f"Error creating reasoning context: {str(e)}"
    
    def get_relevant_context(self, query: str, k: int = 3) -> str:
        """Get relevant context from documents"""
        if not self.vectorstore:
            return ""
        
        try:
            docs = self.vectorstore.similarity_search(query, k=k)
            return "\n\n".join([doc.page_content for doc in docs])
        except Exception as e:
            return f"Error retrieving context: {str(e)}" 