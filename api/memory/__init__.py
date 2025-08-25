"""
QueryWeaver Memory System

Cognitive memory architecture with user-specific graphs:
- Each user gets their own memory database via FalkorDB database parameter
- Episodic Memory: Past interactions and lessons learned
- Semantic Memory: Facts and knowledge about databases/queries

Usage:
    from api.memory import memory_manager
    
    # Initialize user memory
    await memory_manager.initialize_user_memory(user_id, database_name)
    
    # Save interaction
    await memory_manager.save_interaction_memory(user_id, conversation, database_name)
    
    # Recall past experiences
    past_lessons = await memory_manager.recall_past_interactions(user_id, query, database_name)
"""

from .memory_manager import memory_manager, QueryWeaverMemoryManager
from .graphiti_tool import CognitiveMemorySystem

__all__ = [
    'memory_manager',
    'QueryWeaverMemoryManager', 
    'CognitiveMemorySystem'
]