import json
import logging
from django.conf import settings
from django.db.models import Q
from kanban.models import Task, Board
from ai_assistant.models import ProjectKnowledgeBase
from .ai_clients import GeminiClient
from .google_search import GoogleSearchClient

logger = logging.getLogger(__name__)


class TaskFlowChatbotService:
    """
    Chatbot service for TaskFlow project assistant
    Adapted from Nexus 360 for TaskFlow's project management data
    """
    
    def __init__(self, user=None, board=None):
        self.user = user
        self.board = board
        self.gemini_client = GeminiClient()
        self.search_client = GoogleSearchClient()
    
    def get_taskflow_context(self, use_cache=True):
        """
        Get context from TaskFlow project data
        
        Args:
            use_cache (bool): Whether to use cached context
            
        Returns:
            str: Formatted project context
        """
        try:
            context = "**TaskFlow Project Context:**\n\n"
            
            if self.board:
                context += f"Board: {self.board.name}\n"
                
                # Get tasks
                tasks = Task.objects.filter(column__board=self.board)
                if tasks.exists():
                    context += f"\n**Tasks ({tasks.count()}):**\n"
                    for task in tasks[:20]:  # Limit to first 20
                        status = task.column.name if task.column else 'Unknown'
                        priority = task.get_priority_display() if hasattr(task, 'get_priority_display') else task.priority
                        assignee = task.assigned_to.username if task.assigned_to else 'Unassigned'
                        context += f"- [{status}] {task.title} (Priority: {priority}, Assigned: {assignee})\n"
                
                # Get team members
                members = self.board.members.all()
                if members.exists():
                    context += f"\n**Team Members:** {', '.join([m.get_full_name() or m.username for m in members])}\n"
            
            elif self.user:
                # Get all user's boards and projects
                boards = Board.objects.filter(
                    Q(created_by=self.user) | Q(members=self.user)
                ).distinct()[:5]
                
                if boards:
                    context += f"**User's Boards ({boards.count()}):**\n"
                    for board in boards:
                        context += f"- {board.name}\n"
            
            return context
        
        except Exception as e:
            logger.error(f"Error getting TaskFlow context: {e}")
            return "Project context unavailable."
    
    def get_knowledge_base_context(self, query, max_results=3):
        """
        Get relevant knowledge base entries
        
        Args:
            query (str): Search query
            max_results (int): Max results to return
            
        Returns:
            str: Formatted KB context
        """
        try:
            # Simple keyword search in KB
            kb_entries = ProjectKnowledgeBase.objects.filter(
                is_active=True,
                content__icontains=query
            )
            
            if self.board:
                kb_entries = kb_entries.filter(board=self.board)
            
            if not kb_entries.exists():
                return ""
            
            context = "**From Project Knowledge Base:**\n\n"
            for entry in kb_entries[:max_results]:
                context += f"- {entry.title}: {entry.summary or entry.content[:200]}\n"
            
            return context
        
        except Exception as e:
            logger.error(f"Error getting KB context: {e}")
            return ""
    
    def _is_search_query(self, prompt):
        """
        Detect if query should trigger web search (RAG)
        
        Args:
            prompt (str): User prompt
            
        Returns:
            bool: True if web search should be triggered
        """
        search_triggers = [
            'latest', 'recent', 'current', 'new', 'today', '2025',
            'trend', 'news', 'update', 'web', 'online', 'internet',
            'what is the', 'how do', 'tell me about', 'find',
            'best practices', 'industry', 'methodology', 'tool', 'framework'
        ]
        
        prompt_lower = prompt.lower()
        return any(trigger in prompt_lower for trigger in search_triggers)
    
    def _is_project_query(self, prompt):
        """
        Detect if query is about project tasks/data
        """
        project_triggers = [
            'task', 'project', 'team', 'deadline', 'assigned',
            'priority', 'status', 'board', 'sprint', 'release',
            'milestone', 'member', 'resource', 'workload', 'risk',
            'risk', 'dependency', 'blocker', 'schedule', 'capacity'
        ]
        
        prompt_lower = prompt.lower()
        return any(trigger in prompt_lower for trigger in project_triggers)
    
    def generate_system_prompt(self):
        """Generate system prompt for AI model"""
        return """You are TaskFlow AI Project Assistant, an intelligent project management assistant. 
Your role is to help project managers and team members with:
- Project planning and strategy
- Task management and prioritization
- Team resource allocation and workload management
- Risk identification and mitigation
- Timeline optimization and scheduling
- Report generation and insights
- Best practices and recommendations

Provide clear, actionable, and data-driven responses.
When analyzing project data, consider multiple factors like risk, resource availability, dependencies, and timeline.
Always ask clarifying questions if context is unclear.
For suggestions, provide confidence levels and reasoning."""
    
    def get_response(self, prompt, history=None, use_cache=True):
        """
        Get response from chatbot using Gemini
        
        Args:
            prompt (str): User message
            history (list): Chat history
            use_cache (bool): Use cached data
            
        Returns:
            dict: Response with content, source, and metadata
        """
        try:
            # Detect query type
            is_search_query = self._is_search_query(prompt)
            is_project_query = self._is_project_query(prompt)
            
            # Build context
            context_parts = []
            
            # Add TaskFlow project context
            if is_project_query:
                taskflow_context = self.get_taskflow_context(use_cache)
                if taskflow_context:
                    context_parts.append(taskflow_context)
            
            # Add KB context
            kb_context = self.get_knowledge_base_context(prompt)
            if kb_context:
                context_parts.append(kb_context)
            
            # Add web search context for recent/trending queries
            search_context = ""
            used_web_search = False
            search_sources = []
            
            if is_search_query and getattr(settings, 'ENABLE_WEB_SEARCH', False):
                try:
                    search_context = self.search_client.get_search_context(prompt, max_results=3)
                    if search_context and "No relevant" not in search_context:
                        context_parts.append(search_context)
                        used_web_search = True
                        # Extract sources
                        for line in search_context.split('\n'):
                            if 'Source' in line or 'URL:' in line:
                                search_sources.append(line)
                except Exception as e:
                    logger.warning(f"Web search failed: {e}")
            
            # Build system prompt
            system_prompt = self.generate_system_prompt()
            if context_parts:
                system_prompt += "\n\n**Available Context:**\n" + "\n".join(context_parts)
            
            # Get response from Gemini model (single model approach)
            response = self.gemini_client.get_response(prompt, system_prompt, history)
            
            return {
                'response': response['content'],
                'source': 'gemini',
                'tokens': response.get('tokens', 0),
                'error': response.get('error'),
                'used_web_search': used_web_search,
                'search_sources': search_sources,
                'context': {
                    'is_project_query': is_project_query,
                    'is_search_query': is_search_query,
                }
            }
        
        except Exception as e:
            logger.error(f"Error in chatbot service: {e}")
            return {
                'response': f"I encountered an error: {str(e)}. Please try again.",
                'source': 'error',
                'tokens': 0,
                'error': str(e),
                'used_web_search': False,
                'search_sources': [],
                'context': {}
            }
    
    def generate_project_report(self, board_id):
        """Generate AI-powered project report"""
        try:
            board = Board.objects.get(id=board_id)
            tasks = Task.objects.filter(column__board=board)
            
            report_prompt = f"""Generate a comprehensive project status report for "{board.name}" based on:
            - Total tasks: {tasks.count()}
            - Completed: {tasks.filter(column__name__icontains='done').count()}
            - In Progress: {tasks.filter(column__name__icontains='progress').count()}
            - Not Started: {tasks.filter(column__name__icontains='todo').count()}
            
            Provide: 1. Overall status, 2. Key achievements, 3. Risks/Blockers, 4. Recommendations
            """
            
            response = self.gemini_client.get_response(report_prompt)
            return response['content']
        
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return f"Unable to generate report: {str(e)}"
