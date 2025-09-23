import asyncio
import json
import asyncpg
from typing import Optional, List
from datetime import datetime, timezone

from google.genai import types
from google.adk.artifacts import BaseArtifactService
from src.api.logging.logger import get_logger

logger = get_logger(__name__)


class CustomDatabaseArtifactService(BaseArtifactService):
    """Custom artifact service with hierarchical structure: user_id → workspace_id → agent_id → session → artifacts.
    
    This service extends the base artifact service to support a hierarchical structure where:
    - Each user can have multiple workspaces
    - Each workspace can have multiple agents  
    - Each agent can have multiple sessions
    - Each session can contain multiple artifacts
    """

    def __init__(self, db_url: str, user_id: str = None, workspace_id: str = None, agent_id: str = None, session_id: str = None):
        """Initialize the custom database artifact service.
        
        Args:
            db_url: Database connection URL (PostgreSQL).
            user_id: User ID for the current context.
            workspace_id: Workspace ID for the current context.
            agent_id: Agent ID for the current context.
            session_id: Session ID for the current context.
        """
        self.db_url = db_url
        self.user_id = user_id
        self.workspace_id = workspace_id
        self.agent_id = agent_id
        self.session_id = session_id
        self._init_lock = asyncio.Lock()
        self._initialized = False
        
        # Log initialization
        logger.info(f"CustomDatabaseArtifactService initialized - User: {user_id}, Workspace: {workspace_id}, Agent: {agent_id}, Session: {session_id}")

    async def _get_connection(self) -> asyncpg.Connection:
        return await asyncpg.connect(self.db_url)

    async def _ensure_tables_exist(self) -> None:
        if self._initialized:
            return
            
        async with self._init_lock:
            if self._initialized:
                return
                
            conn = await self._get_connection()
            try:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS artifacts (
                        id SERIAL PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        workspace_id TEXT NOT NULL,
                        agent_id TEXT NOT NULL,
                        app_name TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        filename TEXT NOT NULL,
                        version INTEGER NOT NULL DEFAULT 0,
                        content_type TEXT,
                        content_data BYTEA,
                        content_text TEXT,
                        content_uri TEXT,
                        metadata JSONB DEFAULT '{}',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        UNIQUE(user_id, workspace_id, agent_id, app_name, session_id, filename, version)
                    );
                """)
                
                # Create indexes for better performance
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_artifacts_user_workspace_agent 
                    ON artifacts(user_id, workspace_id, agent_id);
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_artifacts_session 
                    ON artifacts(user_id, workspace_id, agent_id, app_name, session_id);
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_artifacts_filename 
                    ON artifacts(user_id, workspace_id, agent_id, app_name, session_id, filename);
                """)
                
                self._initialized = True
                
            finally:
                await conn.close()

    async def _get_session_metadata(self, app_name: str, user_id: str, session_id: str) -> tuple[str, str]:
        """Get workspace_id and agent_id from session metadata.
        
        Returns:
            Tuple of (workspace_id, agent_id)
        """
        conn = await self._get_connection()
        try:
            # Query session state to get workspace_id and agent_id
            query = """
                SELECT state 
                FROM sessions 
                WHERE app_name = $1 AND user_id = $2 AND id = $3
                LIMIT 1
            """
            result = await conn.fetchval(query, app_name, user_id, session_id)
            
            if not result:
                raise ValueError(f"Session {session_id} not found for user {user_id} and app {app_name}")
            
            # Parse state JSON to get workspace_id and agent_id
            state = json.loads(result) if isinstance(result, str) else result
            workspace_id = state.get('workspace_id')
            agent_id = state.get('agent_id')
            
            if not workspace_id:
                raise ValueError(f"workspace_id not found in session {session_id} state")
            if not agent_id:
                raise ValueError(f"agent_id not found in session {session_id} state")
                
            return workspace_id, agent_id
            
        finally:
            await conn.close()

    async def save_artifact(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
        artifact: types.Part,
    ) -> int:
        """Save an artifact to the database with hierarchical structure."""
        await self._ensure_tables_exist()
        
        # Use values from self if available, otherwise get from session metadata
        if self.user_id and self.workspace_id and self.agent_id and self.session_id:
            workspace_id = self.workspace_id
            agent_id = self.agent_id
            actual_user_id = self.user_id
            actual_session_id = self.session_id
        else:
            # Fallback to old behavior - get from session metadata
            workspace_id, agent_id = await self._get_session_metadata(app_name, user_id, session_id)
            actual_user_id = user_id
            actual_session_id = session_id
        
        logger.info(f"Agent {agent_id} saving artifact {filename} for user {actual_user_id} in workspace {workspace_id}")
        
        conn = await self._get_connection()
        try:
            # Get the next version number for this artifact
            version_query = """
                SELECT COALESCE(MAX(version), -1) + 1 as next_version
                FROM artifacts 
                WHERE user_id = $1 AND workspace_id = $2 AND agent_id = $3 
                AND app_name = $4 AND session_id = $5 AND filename = $6
            """
            next_version = await conn.fetchval(
                version_query, actual_user_id, workspace_id, agent_id, app_name, actual_session_id, filename
            )
            
            # Prepare artifact data based on its type
            content_type = None
            content_data = None
            content_text = None
            content_uri = None
            
            if hasattr(artifact, 'text'):
                content_type = 'text'
                content_text = artifact.text
            if hasattr(artifact, 'image'):
                content_type = 'image'
                content_text = artifact.text
            elif hasattr(artifact, 'data'):
                content_type = 'data'
                content_data = artifact.data
            elif hasattr(artifact, 'uri'):
                content_type = 'uri'
                content_uri = artifact.uri
            else:
                # Fallback - try to serialize the artifact
                content_type = 'text'
                content_text = str(artifact)
            
            # Insert the new artifact version
            insert_query = """
                INSERT INTO artifacts (
                    user_id, workspace_id, agent_id, app_name, session_id, 
                    filename, version, content_type, content_data, content_text, content_uri,
                    metadata, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            """
            
            now = datetime.now(timezone.utc)
            metadata = {
                'mime_type': getattr(artifact, 'mime_type', None),
                'size': len(content_data) if content_data else (len(content_text) if content_text else 0),
                'created_by': 'custom_artifact_service'
            }
            
            await conn.execute(
                insert_query,
                actual_user_id, workspace_id, agent_id, app_name, actual_session_id,
                filename, next_version, content_type, content_data, content_text, content_uri,
                json.dumps(metadata), now, now
            )
            
            logger.info(f"Artifact {filename} v{next_version} created successfully by agent {agent_id}")
            
            return next_version
            
        except Exception as e:
            logger.error(f"Failed to save artifact {filename} by agent {agent_id}: {str(e)}")
            raise
        finally:
            await conn.close()

    async def load_artifact(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
        version: Optional[int] = None,
    ) -> Optional[types.Part]:
        """Load an artifact from the database."""
        await self._ensure_tables_exist()
        
        # Use values from self if available, otherwise get from session metadata
        if self.user_id and self.workspace_id and self.agent_id and self.session_id:
            workspace_id = self.workspace_id
            agent_id = self.agent_id
            actual_user_id = self.user_id
            actual_session_id = self.session_id
        else:
            # Fallback to old behavior - get from session metadata
            workspace_id, agent_id = await self._get_session_metadata(app_name, user_id, session_id)
            actual_user_id = user_id
            actual_session_id = session_id
        
        logger.info(f"Agent {agent_id} attempting to load artifact {filename} v{version or 'latest'} for user {actual_user_id} in workspace {workspace_id}")
        
        conn = await self._get_connection()
        try:
            if version is None:
                # Get the latest version
                query = """
                    SELECT content_type, content_data, content_text, content_uri, metadata
                    FROM artifacts 
                    WHERE user_id = $1 AND workspace_id = $2 AND agent_id = $3 
                    AND app_name = $4 AND session_id = $5 AND filename = $6
                    ORDER BY version DESC
                    LIMIT 1
                """
                result = await conn.fetchrow(query, actual_user_id, workspace_id, agent_id, app_name, actual_session_id, filename)
            else:
                # Get specific version
                query = """
                    SELECT content_type, content_data, content_text, content_uri, metadata
                    FROM artifacts 
                    WHERE user_id = $1 AND workspace_id = $2 AND agent_id = $3 
                    AND app_name = $4 AND session_id = $5 AND filename = $6 AND version = $7
                """
                result = await conn.fetchrow(
                    query, actual_user_id, workspace_id, agent_id, app_name, actual_session_id, filename, version
                )
            
            if not result:
                logger.warning(f"Artifact {filename} not found for agent {agent_id} in workspace {workspace_id}")
                return None
            
            # Reconstruct the artifact based on its content type
            content_type = result['content_type']
            metadata = json.loads(result['metadata']) if result['metadata'] else {}
            
            logger.info(f"Artifact {filename} loaded successfully by agent {agent_id}")
            
            if content_type == 'text':
                return types.Part.from_text(text=result['content_text'])
            elif content_type == 'data':
                mime_type = metadata.get('mime_type', 'application/octet-stream')
                return types.Part.from_bytes(data=result['content_data'], mime_type=mime_type)
            elif content_type == 'uri':
                return types.Part.from_uri(result['content_uri'])
            else:
                # Fallback to text
                return types.Part.from_text(text=result['content_text'] or str(result))
                
        except Exception as e:
            logger.error(f"Failed to load artifact {filename} by agent {agent_id}: {str(e)}")
            raise
        finally:
            await conn.close()

    async def list_artifact_keys(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> list[str]:
        """List all artifact filenames within a session."""
        await self._ensure_tables_exist()
        
        # Use values from self if available, otherwise get from session metadata
        if self.user_id and self.workspace_id and self.agent_id and self.session_id:
            workspace_id = self.workspace_id
            agent_id = self.agent_id
            actual_user_id = self.user_id
            actual_session_id = self.session_id
        else:
            # Fallback to old behavior - get from session metadata
            workspace_id, agent_id = await self._get_session_metadata(app_name, user_id, session_id)
            actual_user_id = user_id
            actual_session_id = session_id
        
        conn = await self._get_connection()
        try:
            query = """
                SELECT DISTINCT filename
                FROM artifacts 
                WHERE user_id = $1 AND workspace_id = $2 AND agent_id = $3 
                AND app_name = $4 AND session_id = $5
                ORDER BY filename
            """
            results = await conn.fetch(query, actual_user_id, workspace_id, agent_id, app_name, actual_session_id)
            return [row['filename'] for row in results]
            
        finally:
            await conn.close()

    async def delete_artifact(
        self, *, app_name: str, user_id: str, session_id: str, filename: str
    ) -> None:
        """Delete all versions of an artifact."""
        await self._ensure_tables_exist()
        
        # Use values from self if available, otherwise get from session metadata
        if self.user_id and self.workspace_id and self.agent_id and self.session_id:
            workspace_id = self.workspace_id
            agent_id = self.agent_id
            actual_user_id = self.user_id
            actual_session_id = self.session_id
        else:
            # Fallback to old behavior - get from session metadata
            workspace_id, agent_id = await self._get_session_metadata(app_name, user_id, session_id)
            actual_user_id = user_id
            actual_session_id = session_id
        
        conn = await self._get_connection()
        try:
            query = """
                DELETE FROM artifacts 
                WHERE user_id = $1 AND workspace_id = $2 AND agent_id = $3 
                AND app_name = $4 AND session_id = $5 AND filename = $6
            """
            await conn.execute(query, actual_user_id, workspace_id, agent_id, app_name, actual_session_id, filename)
            
        finally:
            await conn.close()

    async def list_versions(
        self, *, app_name: str, user_id: str, session_id: str, filename: str
    ) -> list[int]:
        """List all versions of an artifact."""
        await self._ensure_tables_exist()
        
        # Use values from self if available, otherwise get from session metadata
        if self.user_id and self.workspace_id and self.agent_id and self.session_id:
            workspace_id = self.workspace_id
            agent_id = self.agent_id
            actual_user_id = self.user_id
            actual_session_id = self.session_id
        else:
            # Fallback to old behavior - get from session metadata
            workspace_id, agent_id = await self._get_session_metadata(app_name, user_id, session_id)
            actual_user_id = user_id
            actual_session_id = session_id
        
        conn = await self._get_connection()
        try:
            query = """
                SELECT version
                FROM artifacts 
                WHERE user_id = $1 AND workspace_id = $2 AND agent_id = $3 
                AND app_name = $4 AND session_id = $5 AND filename = $6
                ORDER BY version
            """
            results = await conn.fetch(query, actual_user_id, workspace_id, agent_id, app_name, actual_session_id, filename)
            return [row['version'] for row in results]
            
        finally:
            await conn.close()

    # Core methods for getting artifacts by workspace
    
    async def list_artifacts_by_workspace(self, user_id: str, workspace_id: str) -> list[dict]:
        """List all artifacts for a user within a specific workspace.
        
        Args:
            user_id: User ID
            workspace_id: Workspace ID
            
        Returns:
            List of artifact info with structure details
        """
        await self._ensure_tables_exist()
        
        logger.info(f"Listing artifacts for user {user_id} in workspace {workspace_id}")
        
        conn = await self._get_connection()
        try:
            query = """
                SELECT 
                    user_id, workspace_id, agent_id, app_name, session_id,
                    filename, version, content_type, metadata,
                    created_at, updated_at
                FROM artifacts 
                WHERE user_id = $1 AND workspace_id = $2
                ORDER BY created_at DESC
            """
            results = await conn.fetch(query, user_id, workspace_id)
            
            artifacts = []
            for row in results:
                artifacts.append({
                    'user_id': row['user_id'],
                    'workspace_id': row['workspace_id'], 
                    'agent_id': row['agent_id'],
                    'app_name': row['app_name'],
                    'session_id': row['session_id'],
                    'filename': row['filename'],
                    'version': row['version'],
                    'content_type': row['content_type'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            
            logger.info(f"Found {len(artifacts)} artifacts for user {user_id} in workspace {workspace_id}")
            if artifacts:
                # Log summary by agent
                agent_counts = {}
                for artifact in artifacts:
                    agent_id = artifact['agent_id']
                    agent_counts[agent_id] = agent_counts.get(agent_id, 0) + 1
                
                for agent_id, count in agent_counts.items():
                    logger.info(f"Agent {agent_id}: {count} artifacts")
            
            return artifacts
            
        except Exception as e:
            logger.error(f"Failed to list artifacts for user {user_id} in workspace {workspace_id} - Error: {str(e)}")
            raise
        finally:
            await conn.close()

    async def log_artifact_activity_summary(self) -> None:
        """Log a summary of recent artifact activities for monitoring."""
        await self._ensure_tables_exist()
        
        logger.info("ARTIFACT ACTIVITY SUMMARY")
        
        conn = await self._get_connection()
        try:
            # Total artifacts count
            total_query = "SELECT COUNT(*) as total FROM artifacts"
            total_count = await conn.fetchval(total_query)
            logger.info(f"Total artifacts in system: {total_count}")
            
            # Recent artifacts (last 24 hours)
            recent_query = """
                SELECT COUNT(*) as recent_count 
                FROM artifacts 
                WHERE created_at > NOW() - INTERVAL '24 hours'
            """
            recent_count = await conn.fetchval(recent_query)
            logger.info(f"Artifacts created in last 24h: {recent_count}")
            
            # Artifacts by agent (top 10)
            agent_stats_query = """
                SELECT agent_id, COUNT(*) as count
                FROM artifacts 
                GROUP BY agent_id 
                ORDER BY count DESC 
                LIMIT 10
            """
            agent_stats = await conn.fetch(agent_stats_query)
            
            logger.info("Top active agents:")
            for row in agent_stats:
                logger.info(f"   - Agent {row['agent_id']}: {row['count']} artifacts")
                
        except Exception as e:
            logger.error(f"Failed to generate activity summary - Error: {str(e)}")
        finally:
            await conn.close()
