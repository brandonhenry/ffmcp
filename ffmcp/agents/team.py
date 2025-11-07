"""Team management for multi-agent collaboration with hierarchical support"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
import json

from ffmcp.agents import Agent


class Team:
    """Manages a hierarchical team of agents that can work together on tasks.
    
    Teams support:
    - One orchestrator agent at the top level
    - Multiple member agents or sub-teams below
    - Nested teams (teams within teams) for multiple management layers
    - Shared brain/memory context that flows up the hierarchy
    """
    
    def __init__(
        self,
        *,
        config,
        name: str,
        orchestrator: str,
        members: Optional[List[str]] = None,
        sub_teams: Optional[List[str]] = None,
        shared_brain: Optional[str] = None,
        shared_thread: Optional[str] = None,
        parent_team: Optional[str] = None,
    ):
        self.config = config
        self.name = name
        self.orchestrator = orchestrator
        self.members = members or []  # Agent names
        self.sub_teams = sub_teams or []  # Sub-team names
        self.shared_brain = shared_brain
        self.shared_thread = shared_thread
        self.parent_team = parent_team
        
        # Validate orchestrator exists
        if not config.get_agent(orchestrator):
            raise ValueError(f"Orchestrator agent '{orchestrator}' not found")
        
        # Validate members exist
        for agent_name in self.members:
            if not config.get_agent(agent_name):
                raise ValueError(f"Member agent '{agent_name}' not found")
        
        # Validate sub-teams exist
        for sub_team_name in self.sub_teams:
            if not config.get_team(sub_team_name):
                raise ValueError(f"Sub-team '{sub_team_name}' not found")
            # Set parent relationship
            sub_team_data = config.get_team(sub_team_name)
            if sub_team_data:
                config.update_team(sub_team_name, {'parent_team': self.name})
    
    def get_orchestrator(self) -> Optional[Agent]:
        """Get the orchestrator agent instance."""
        spec = self.config.get_agent(self.orchestrator)
        if not spec:
            return None
        
        # Use shared brain if available
        brain_name = self.shared_brain or spec.get('brain')
        
        return Agent(
            config=self.config,
            name=self.orchestrator,
            provider=spec.get('provider'),
            model=spec.get('model'),
            instructions=spec.get('instructions'),
            brain=brain_name,
            properties=spec.get('properties') or {},
            actions_config=spec.get('actions') or {},
        )
    
    def get_member_agent(self, agent_name: str) -> Optional[Agent]:
        """Get a member agent instance by name."""
        if agent_name not in self.members:
            return None
        
        spec = self.config.get_agent(agent_name)
        if not spec:
            return None
        
        # Use shared brain if available
        brain_name = self.shared_brain or spec.get('brain')
        
        return Agent(
            config=self.config,
            name=agent_name,
            provider=spec.get('provider'),
            model=spec.get('model'),
            instructions=spec.get('instructions'),
            brain=brain_name,
            properties=spec.get('properties') or {},
            actions_config=spec.get('actions') or {},
        )
    
    def get_sub_team(self, sub_team_name: str) -> Optional['Team']:
        """Get a sub-team instance by name."""
        if sub_team_name not in self.sub_teams:
            return None
        
        sub_team_data = self.config.get_team(sub_team_name)
        if not sub_team_data:
            return None
        
        return Team(
            config=self.config,
            name=sub_team_name,
            orchestrator=sub_team_data.get('orchestrator'),
            members=sub_team_data.get('members', []),
            sub_teams=sub_team_data.get('sub_teams', []),
            shared_brain=self.shared_brain or sub_team_data.get('shared_brain'),
            shared_thread=sub_team_data.get('shared_thread'),
            parent_team=self.name,
        )
    
    def get_all_agents_recursive(self) -> Set[str]:
        """Get all agent names in this team and all sub-teams recursively."""
        agents = {self.orchestrator}
        agents.update(self.members)
        
        for sub_team_name in self.sub_teams:
            sub_team = self.get_sub_team(sub_team_name)
            if sub_team:
                agents.update(sub_team.get_all_agents_recursive())
        
        return agents
    
    def get_hierarchy_context(self) -> str:
        """Build context string describing the team hierarchy."""
        lines = [f"Team: {self.name}"]
        lines.append(f"  Orchestrator: {self.orchestrator}")
        
        if self.members:
            lines.append(f"  Direct Members ({len(self.members)}): {', '.join(self.members)}")
        
        if self.sub_teams:
            lines.append(f"  Sub-teams ({len(self.sub_teams)}): {', '.join(self.sub_teams)}")
            for sub_team_name in self.sub_teams:
                sub_team = self.get_sub_team(sub_team_name)
                if sub_team:
                    sub_agents = sub_team.get_all_agents_recursive()
                    lines.append(f"    - {sub_team_name}: {len(sub_agents)} agents")
        
        if self.parent_team:
            lines.append(f"  Parent Team: {self.parent_team}")
        
        return "\n".join(lines)
    
    def run(
        self,
        *,
        task: str,
        thread_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run a task with the team, using the orchestrator to orchestrate.
        
        The orchestrator has visibility into all activity through shared brain/memory.
        
        Args:
            task: The task for the team to accomplish
            thread_name: Thread to use (defaults to shared_thread or creates one)
        
        Returns:
            Dict with 'result', 'orchestrator', 'thread_name', etc.
        """
        orchestrator_agent = self.get_orchestrator()
        if not orchestrator_agent:
            return {
                "error": f"Orchestrator agent '{self.orchestrator}' not found",
                "success": False,
            }
        
        # Ensure delegate_to_agent action is enabled for orchestrator
        if 'delegate_to_agent' not in orchestrator_agent._actions:
            from ffmcp.agents.actions import DelegateToAgentAction
            orchestrator_agent.register_action('delegate_to_agent', DelegateToAgentAction())
        
        # Use provided thread or shared thread or create one
        if not thread_name:
            thread_name = self.shared_thread or f"team-{self.name}"
            # Auto-create thread if it doesn't exist
            try:
                self.config.create_thread(self.orchestrator, thread_name)
            except ValueError:
                # Thread already exists, that's fine
                pass
        
        # Build comprehensive context about the team hierarchy
        all_agents = self.get_all_agents_recursive()
        hierarchy_info = self.get_hierarchy_context()
        
        team_context = f"""You are the orchestrator for a hierarchical team structure.

{hierarchy_info}

Available agents (including all sub-teams): {', '.join(sorted(all_agents))}

You can delegate tasks to:
- Direct member agents: {', '.join(self.members) if self.members else 'None'}
- Sub-team orchestrators: {', '.join(self.sub_teams) if self.sub_teams else 'None'}

When delegating to sub-teams, they will handle the task with their own orchestrators and members.
All activity flows up through the hierarchy, and you have visibility into everything through shared memory.

Your role is to break down the task, delegate appropriately across the hierarchy, and synthesize results.

Task: {task}
"""
        
        # If shared brain is configured, add memory context
        if self.shared_brain:
            try:
                from ffmcp.brain import ZepBrainClient, BrainInfo
                zcfg = self.config.get_zep_settings()
                client = ZepBrainClient(api_key=zcfg.get('api_key'), base_url=zcfg.get('base_url'), env=zcfg.get('env'))
                brain_info = BrainInfo(name=self.shared_brain)
                mem = client.memory_get(brain=brain_info, session_id=None)
                mem_text = json.dumps(mem.get('result'), default=str)
                if len(mem_text) > 50000:
                    mem_text = mem_text[:50000]
                team_context += f"\n\nShared Memory Context:\n{mem_text}"
            except Exception:
                # If memory unavailable, continue without failing
                pass
        
        try:
            result = orchestrator_agent.run(
                input_text=team_context,
                thread_name=thread_name,
            )
            
            return {
                "result": result,
                "orchestrator": self.orchestrator,
                "thread_name": thread_name,
                "members": self.members,
                "sub_teams": self.sub_teams,
                "all_agents": list(all_agents),
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "orchestrator": self.orchestrator,
                "thread_name": thread_name,
                "success": False,
            }
    
    def add_member(self, agent_name: str):
        """Add an agent as a direct member."""
        if agent_name in self.members:
            raise ValueError(f"Agent '{agent_name}' is already a member")
        
        if not self.config.get_agent(agent_name):
            raise ValueError(f"Agent '{agent_name}' not found")
        
        self.members.append(agent_name)
    
    def remove_member(self, agent_name: str):
        """Remove an agent from direct members."""
        if agent_name not in self.members:
            raise ValueError(f"Agent '{agent_name}' is not a member")
        
        self.members.remove(agent_name)
    
    def add_sub_team(self, sub_team_name: str):
        """Add a sub-team."""
        if sub_team_name in self.sub_teams:
            raise ValueError(f"Sub-team '{sub_team_name}' is already in this team")
        
        if not self.config.get_team(sub_team_name):
            raise ValueError(f"Team '{sub_team_name}' not found")
        
        self.sub_teams.append(sub_team_name)
        # Set parent relationship
        self.config.update_team(sub_team_name, {'parent_team': self.name})
    
    def remove_sub_team(self, sub_team_name: str):
        """Remove a sub-team."""
        if sub_team_name not in self.sub_teams:
            raise ValueError(f"Sub-team '{sub_team_name}' is not in this team")
        
        self.sub_teams.remove(sub_team_name)
        # Clear parent relationship
        self.config.update_team(sub_team_name, {'parent_team': None})
    
    def set_orchestrator(self, agent_name: str):
        """Set the orchestrator agent."""
        if not self.config.get_agent(agent_name):
            raise ValueError(f"Agent '{agent_name}' not found")
        self.orchestrator = agent_name
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize team to dict."""
        return {
            "name": self.name,
            "orchestrator": self.orchestrator,
            "members": self.members,
            "sub_teams": self.sub_teams,
            "shared_brain": self.shared_brain,
            "shared_thread": self.shared_thread,
            "parent_team": self.parent_team,
        }
