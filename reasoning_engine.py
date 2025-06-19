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
from web_search import search_web

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
        """Create tools for the agent"""
        return [
            Tool(
                name="web_search",
                func=self._web_search,
                description="Search the web for current information. Use this for questions about recent events, current prices, weather, or any information that might change over time."
            ),
            Tool(
                name="calculator",
                func=self._calculate,
                description="Perform mathematical calculations. Input should be a mathematical expression like '2 + 2' or 'sqrt(16)'."
            ),
            Tool(
                name="get_current_time",
                func=self._get_current_time,
                description="Get the current date and time. Use this when asked about the current time or date."
            )
        ]
    
    def _calculate(self, expression: str) -> str:
        """Safe calculator function"""
        try:
            # Use safer eval with limited scope
            allowed_names = {"abs": abs, "float": float, "int": int, "pow": pow, "round": round}
            code = compile(expression, "<string>", "eval")
            for name in code.co_names:
                if name not in allowed_names:
                    raise NameError(f"Use of {name} not allowed")
            return str(eval(expression, {"__builtins__": {}}, allowed_names))
        except Exception as e:
            return f"Error in calculation: {str(e)}"
    
    def _get_current_time(self) -> str:
        """Get current time in a readable format"""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
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