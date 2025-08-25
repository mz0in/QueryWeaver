"""
QueryWeaver Memory Manager with Cognitive Architecture

This module provides the main interface for managing user memories in QueryWeaver.
It coordinates episodic and semantic memory systems using Graphiti temporal knowledge graphs.
Each user gets their own dedicated memory graph via FalkorDB database parameter.
"""

from typing import List, Dict, Any, Optional
from api.extensions import db
from .graphiti_tool import CognitiveMemorySystem


class QueryWeaverMemoryManager:
    """
    Main memory manager for QueryWeaver that coordinates:
    - Episodic Memory: Past interactions and lessons learned
    - Semantic Memory: Facts and knowledge about databases/queries
    
    Each user gets their own memory graph using FalkorDB database={user_id}_memory
    """
    
    def __init__(self):
        """Initialize the memory manager with cognitive memory system."""
        self.cognitive_memory = CognitiveMemorySystem(db)
    
    # ===== EPISODIC MEMORY INTERFACE =====
    async def save_interaction_memory(self, user_id: str, conversation: List[Dict[str, Any]], 
                                    database_name: str, what_worked: str = "", 
                                    what_to_avoid: str = "") -> bool:
        """
        Save episodic memory from user interaction.
        
        Args:
            user_id: Unique user identifier
            conversation: List of user/system exchanges
            database_name: Name of database being queried
            what_worked: Analysis of what worked well
            what_to_avoid: Analysis of what should be avoided
        """
        return await self.cognitive_memory.save_episodic_memory(
            user_id, conversation, database_name, what_worked, what_to_avoid
        )
    
    async def recall_past_interactions(self, user_id: str, query: str, 
                                     database_name: str) -> Dict[str, str]:
        """
        Recall similar past interactions and lessons learned.
        
        Returns:
            Dict with keys: past_interactions, what_worked, what_to_avoid
        """
        return await self.cognitive_memory.recall_episodic_memory(
            user_id, query, database_name
        )
    
    # ===== SEMANTIC MEMORY INTERFACE =====
    async def save_schema_knowledge(self, user_id: str, database_name: str, 
                                  schema_facts: List[str], 
                                  query_patterns: List[str]) -> bool:
        """
        Save semantic memory about database schemas and query patterns.
        
        Args:
            user_id: Unique user identifier
            database_name: Name of database
            schema_facts: List of facts about the database schema
            query_patterns: List of common query patterns
        """
        return await self.cognitive_memory.save_semantic_memory(
            user_id, database_name, schema_facts, query_patterns
        )
    
    async def recall_schema_knowledge(self, user_id: str, query: str, 
                                    database_name: str) -> List[str]:
        """
        Recall relevant facts and concepts about the database.
        
        Returns:
            List of relevant schema facts and query patterns
        """
        return await self.cognitive_memory.recall_semantic_memory(
            user_id, query, database_name
        )
    
    # ===== MEMORY MANAGEMENT =====
    async def initialize_user_memory(self, user_id: str, database_name: str) -> bool:
        """
        Initialize memory graph for a new user.
        Creates user-specific memory database using FalkorDB database parameter.
        
        Args:
            user_id: Unique user identifier
            database_name: Name of database they're working with
        """
        try:
            # Ensure user node exists in their dedicated memory graph
            user_node_uuid = await self.cognitive_memory.ensure_user_node(user_id, database_name)
            return user_node_uuid is not None
        except Exception as e:
            print(f"Failed to initialize memory for user {user_id}: {e}")
            return False
    
    async def get_memory_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get status of user's memory system.
        
        Returns:
            Dictionary with memory statistics and availability
        """
        try:
            if not self.cognitive_memory.is_available():
                return {
                    "available": False,
                    "error": "Graphiti memory system not available"
                }
            
            # Get user's Graphiti client to check their memory database
            user_client = self.cognitive_memory._get_user_graphiti_client(user_id)
            if not user_client:
                return {
                    "available": False,
                    "error": f"Could not create memory database for user {user_id}"
                }
            
            return {
                "available": True,
                "user_id": user_id,
                "database": f"{user_id}_memory",
                "memory_types": ["episodic", "semantic"],
                "status": "ready"
            }
            
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }
    
    def is_available(self) -> bool:
        """Check if memory system is available."""
        return self.cognitive_memory.is_available()


# Global memory manager instance
memory_manager = QueryWeaverMemoryManager()

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import asyncio
from fastapi import Request

from api.extensions import db as falkor_db
from .graphiti_tool import CognitiveMemorySystem


class QueryWeaverMemoryManager:
    """
    Memory manager implementing simplified cognitive architecture for QueryWeaver.
    Coordinates episodic and semantic memory for intelligent query assistance.
    """
    
    def __init__(self):
        """Initialize cognitive memory manager."""
        self.cognitive_memory = CognitiveMemorySystem(falkor_db)
        self.fallback_storage = {}  # Simple in-memory fallback
        
    # ===== PUBLIC API FUNCTIONS =====
    
    async def save_conversation(self, request: Request, conversation: List[Dict[str, Any]], 
                              database_name: str, what_worked: str = "", 
                              what_to_avoid: str = "") -> bool:
        """
        Save complete conversation with cognitive analysis.
        
        Args:
            request: FastAPI request object
            conversation: List of question/SQL/answer exchanges
            database_name: Name of database being queried
            what_worked: What worked well in this interaction
            what_to_avoid: What should be avoided in future
        """
        user_id = self._get_user_id(request)
        
        # Ensure user node exists
        if self.cognitive_memory.is_available():
            await self.cognitive_memory.ensure_user_node(user_id, database_name)
        
        # Save to episodic memory with analysis
        episodic_success = await self.cognitive_memory.save_episodic_memory(
            user_id, conversation, database_name, what_worked, what_to_avoid
        )
        
        # Extract and save semantic knowledge
        await self._extract_and_save_semantic_knowledge(user_id, conversation, database_name)
        
        # Always save to fallback as well
        self._save_to_fallback(user_id, conversation, database_name)
        
        return episodic_success or True
    
    async def get_relevant_context(self, request: Request, query: str, database_name: str) -> Dict[str, Any]:
        """
        Get context from episodic and semantic memory for query processing.
        
        Returns:
            Dict containing:
            - episodic_memory: Past interactions and lessons learned
            - semantic_memory: Relevant facts about database/queries
        """
        user_id = self._get_user_id(request)
        
        # Get episodic memory (past interactions and lessons)
        episodic_context = {"past_interactions": "", "what_worked": "", "what_to_avoid": ""}
        if self.cognitive_memory.is_available():
            episodic_context = await self.cognitive_memory.recall_episodic_memory(
                user_id, query, database_name
            )
        
        # Get semantic memory (facts and knowledge)
        semantic_facts = []
        if self.cognitive_memory.is_available():
            semantic_facts = await self.cognitive_memory.recall_semantic_memory(user_id, query, database_name)
        
        return {
            "episodic_memory": episodic_context,
            "semantic_memory": semantic_facts
        }
    
    async def save_schema_knowledge(self, user_id: str, database_name: str, schema_info: Dict[str, Any]) -> bool:
        """Save database schema information to user's semantic memory."""
        if not self.cognitive_memory.is_available():
            return False
        
        # Extract schema facts
        schema_facts = []
        if 'tables' in schema_info:
            for table, info in schema_info['tables'].items():
                schema_facts.append(f"Table {table} exists with columns: {', '.join(info.get('columns', []))}")
                if 'relationships' in info:
                    for rel in info['relationships']:
                        schema_facts.append(f"Table {table} relates to {rel}")
        
        # Extract common query patterns
        query_patterns = [
            f"Common queries for {database_name} include SELECT, JOIN, and aggregation operations",
            f"Database {database_name} supports standard SQL syntax",
        ]
        
        return await self.cognitive_memory.save_semantic_memory(
            user_id, database_name, schema_facts, query_patterns
        )
    
    # ===== LEGACY API FOR BACKWARD COMPATIBILITY =====
    
    async def get_relevant_facts(self, request: Request, query: str, database_name: str) -> List[str]:
        """Legacy function - get relevant facts from episodic and semantic memory."""
        context = await self.get_relevant_context(request, query, database_name)
        
        facts = []
        
        # Add episodic insights
        if context["episodic_memory"]["past_interactions"]:
            facts.append(f"Past experience: {context['episodic_memory']['past_interactions']}")
        if context["episodic_memory"]["what_worked"]:
            facts.append(f"What worked before: {context['episodic_memory']['what_worked']}")
        
        # Add semantic facts
        facts.extend(context["semantic_memory"][:2])  # Top 2 semantic facts
        
        return facts[:3]  # Return top 3 for compatibility
    
    # ===== HELPER METHODS =====
    
    def _get_user_id(self, request: Request) -> str:
        """Extract user ID from request."""
        if hasattr(request, 'session') and 'user' in request.session:
            return request.session['user'].get('id', 'anonymous')
        
        client_ip = request.client.host if request.client else 'unknown'
        return f"user_{client_ip}"
    
    async def _extract_and_save_semantic_knowledge(self, user_id: str, conversation: List[Dict[str, Any]], 
                                                 database_name: str):
        """Extract semantic knowledge from successful conversations."""
        if not self.cognitive_memory.is_available():
            return
        
        schema_facts = []
        query_patterns = []
        
        for exchange in conversation:
            sql = exchange.get('sql', '')
            if sql and not sql.lower().startswith('error'):
                # Extract table names and patterns
                if 'FROM ' in sql.upper():
                    tables = self._extract_tables_from_sql(sql)
                    for table in tables:
                        schema_facts.append(f"Table {table} is queryable in {database_name}")
                
                # Extract query patterns
                if 'JOIN' in sql.upper():
                    query_patterns.append("JOIN operations are common for this database")
                if 'GROUP BY' in sql.upper():
                    query_patterns.append("Aggregation queries with GROUP BY are supported")
                if 'WHERE' in sql.upper():
                    query_patterns.append("Filtering with WHERE clauses is frequently used")
        
        if schema_facts or query_patterns:
            await self.cognitive_memory.save_semantic_memory(
                user_id, database_name, schema_facts, query_patterns
            )
    
    def _extract_tables_from_sql(self, sql: str) -> List[str]:
        """Simple extraction of table names from SQL."""
        tables = []
        try:
            sql_upper = sql.upper()
            # Simple regex-like extraction for FROM and JOIN clauses
            import re
            from_pattern = r'FROM\s+(\w+)'
            join_pattern = r'JOIN\s+(\w+)'
            
            tables.extend(re.findall(from_pattern, sql_upper))
            tables.extend(re.findall(join_pattern, sql_upper))
        except:
            pass
        
        return list(set(tables))  # Remove duplicates
    
    def _save_to_fallback(self, user_id: str, conversation: List[Dict[str, Any]], database_name: str):
        """Save to simple fallback storage."""
        if user_id not in self.fallback_storage:
            self.fallback_storage[user_id] = {}
        
        if database_name not in self.fallback_storage[user_id]:
            self.fallback_storage[user_id][database_name] = []
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'conversation': conversation
        }
        
        self.fallback_storage[user_id][database_name].append(entry)
        
        # Keep only last 10 conversations per user/database
        if len(self.fallback_storage[user_id][database_name]) > 10:
            self.fallback_storage[user_id][database_name] = \
                self.fallback_storage[user_id][database_name][-10:]


# Global instance
memory_manager = QueryWeaverMemoryManager()


# Public API functions
async def save_conversation(request: Request, conversation: List[Dict[str, Any]], 
                          database_name: str, what_worked: str = "", 
                          what_to_avoid: str = "") -> bool:
    """Save conversation with episodic analysis."""
    return await memory_manager.save_conversation(
        request, conversation, database_name, what_worked, what_to_avoid
    )


async def get_relevant_facts(request: Request, query: str, database_name: str) -> List[str]:
    """Get relevant facts for query from episodic and semantic memory."""
    return await memory_manager.get_relevant_facts(request, query, database_name)


async def get_memory_context(request: Request, query: str, database_name: str) -> Dict[str, Any]:
    """Get context from episodic and semantic memory."""
    return await memory_manager.get_relevant_context(request, query, database_name)
