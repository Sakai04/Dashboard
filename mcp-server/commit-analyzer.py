#!/usr/bin/env python3
"""
MCP Server for GitHub Commit Analysis
Provides commit analysis and report generation capabilities
"""

import json
import logging
import os
import asyncio
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
from openai import AsyncOpenAI


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
def load_config():
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

config = load_config()

# FastAPI app initialization
app = FastAPI(
    title="MCP Commit Analyzer",
    description="MCP Server for analyzing GitHub commits and generating reports",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
) if os.getenv("OPENAI_API_KEY") else None

# Pydantic models
class CommitData(BaseModel):
    commit_hash: str = Field(..., description="Git commit hash")
    commit_message: str = Field(..., description="Commit message")
    commit_author: str = Field(..., description="Commit author name")
    repository_name: str = Field(..., description="Repository name")
    branch_name: str = Field(..., description="Branch name")
    added_files: List[str] = Field(default=[], description="List of added files")
    modified_files: List[str] = Field(default=[], description="List of modified files")
    removed_files: List[str] = Field(default=[], description="List of removed files")
    total_files_changed: int = Field(..., description="Total number of files changed")
    commit_url: str = Field(..., description="GitHub commit URL")

class AnalysisResult(BaseModel):
    commit_hash: str
    quality_score: int = Field(..., ge=1, le=10, description="Commit quality score (1-10)")
    category: str = Field(..., description="Commit category (feature, bugfix, refactor, docs, etc.)")
    impact_level: str = Field(..., description="Impact level (low, medium, high)")
    stats: Dict[str, Any] = Field(default_factory=dict, description="Commit statistics")
    issues_identified: List[str] = Field(default_factory=list, description="Potential issues found")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")
    report: str = Field(..., description="Detailed analysis report in markdown format")

class HealthResponse(BaseModel):
    status: str
    version: str
    uptime: str
    config_loaded: bool

# Global variables for tracking
start_time = datetime.now()
analysis_cache = {}

class CommitAnalyzer:
    """Core commit analysis logic"""
    
    def __init__(self):
        self.openai_enabled = openai_client is not None
        
    async def analyze_commit(self, commit_data: CommitData) -> AnalysisResult:
        """Analyze a commit and generate comprehensive report"""
        try:
            # Check cache first
            cache_key = self._generate_cache_key(commit_data)
            if cache_key in analysis_cache:
                logger.info(f"Returning cached analysis for {commit_data.commit_hash}")
                return analysis_cache[cache_key]
            
            # Perform basic analysis
            basic_analysis = self._analyze_basic_metrics(commit_data)
            
            # Generate AI-powered analysis if available
            ai_analysis = await self._analyze_with_ai(commit_data) if self.openai_enabled else {}
            
            # Combine results
            result = self._combine_analysis(commit_data, basic_analysis, ai_analysis)
            
            # Cache result
            analysis_cache[cache_key] = result
            
            logger.info(f"Analysis completed for commit {commit_data.commit_hash}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing commit {commit_data.commit_hash}: {str(e)}")
            # Return fallback analysis
            return self._create_fallback_analysis(commit_data, str(e))
    
    def _generate_cache_key(self, commit_data: CommitData) -> str:
        """Generate cache key for commit"""
        content = f"{commit_data.commit_hash}{commit_data.commit_message}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _analyze_basic_metrics(self, commit_data: CommitData) -> Dict[str, Any]:
        """Perform basic commit analysis"""
        total_files = commit_data.total_files_changed
        message = commit_data.commit_message.lower()
        
        # Categorize commit
        category = self._categorize_commit(commit_data)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(commit_data)
        
        # Determine impact level
        impact_level = self._determine_impact_level(commit_data)
        
        # Identify potential issues
        issues = self._identify_issues(commit_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(commit_data, issues)
        
        return {
            "category": category,
            "quality_score": quality_score,
            "impact_level": impact_level,
            "issues": issues,
            "recommendations": recommendations,
            "stats": {
                "files_changed": total_files,
                "added_files": len(commit_data.added_files),
                "modified_files": len(commit_data.modified_files),
                "removed_files": len(commit_data.removed_files),
                "message_length": len(commit_data.commit_message)
            }
        }
    
    def _categorize_commit(self, commit_data: CommitData) -> str:
        """Categorize the commit based on message and file changes"""
        message = commit_data.commit_message.lower()
        
        if any(keyword in message for keyword in ['fix', 'bug', 'patch', 'hotfix']):
            return "bugfix"
        elif any(keyword in message for keyword in ['feat', 'feature', 'add', 'implement']):
            return "feature"
        elif any(keyword in message for keyword in ['refactor', 'cleanup', 'improve']):
            return "refactor"
        elif any(keyword in message for keyword in ['doc', 'readme', 'comment']):
            return "documentation"
        elif any(keyword in message for keyword in ['test', 'spec']):
            return "test"
        elif any(keyword in message for keyword in ['style', 'format', 'lint']):
            return "style"
        elif any(keyword in message for keyword in ['chore', 'build', 'ci', 'deploy']):
            return "chore"
        else:
            return "other"
    
    def _calculate_quality_score(self, commit_data: CommitData) -> int:
        """Calculate commit quality score (1-10)"""
        score = 5  # Base score
        
        message = commit_data.commit_message
        
        # Message quality factors
        if len(message) > 10:
            score += 1
        if len(message) > 50:
            score += 1
        if not message.startswith(('WIP', 'wip', 'Merge')):
            score += 1
        if any(char.isupper() for char in message):
            score += 1
        
        # File change factors
        if commit_data.total_files_changed <= 5:
            score += 1
        elif commit_data.total_files_changed > 20:
            score -= 2
        
        # Ensure score is within bounds
        return max(1, min(10, score))
    
    def _determine_impact_level(self, commit_data: CommitData) -> str:
        """Determine the impact level of the commit"""
        total_files = commit_data.total_files_changed
        
        if total_files <= 3:
            return "low"
        elif total_files <= 10:
            return "medium"
        else:
            return "high"
    
    def _identify_issues(self, commit_data: CommitData) -> List[str]:
        """Identify potential issues with the commit"""
        issues = []
        
        message = commit_data.commit_message
        
        if len(message) < 10:
            issues.append("Commit message is too short")
        if message.lower().startswith(('wip', 'tmp', 'temp')):
            issues.append("Appears to be a work-in-progress commit")
        if commit_data.total_files_changed > 20:
            issues.append("Large number of files changed - consider splitting")
        if commit_data.total_files_changed == 0:
            issues.append("No files changed in this commit")
        
        return issues
    
    def _generate_recommendations(self, commit_data: CommitData, issues: List[str]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if "Commit message is too short" in issues:
            recommendations.append("Consider adding more descriptive commit messages")
        if "Large number of files changed" in issues:
            recommendations.append("Consider breaking large commits into smaller, focused changes")
        if commit_data.total_files_changed > 10:
            recommendations.append("Add unit tests for significant changes")
        
        return recommendations
    
    async def _analyze_with_ai(self, commit_data: CommitData) -> Dict[str, Any]:
        """Perform AI-powered analysis using OpenAI"""
        try:
            prompt = self._build_ai_prompt(commit_data)
            
            response = await openai_client.chat.completions.create(
                model=config.get("openai_model", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are a senior software engineer reviewing code commits."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            return {"ai_insights": analysis_text}
            
        except Exception as e:
            logger.warning(f"AI analysis failed: {str(e)}")
            return {}
    
    def _build_ai_prompt(self, commit_data: CommitData) -> str:
        """Build prompt for AI analysis"""
        return f"""
Analyze this Git commit:

Commit Message: {commit_data.commit_message}
Author: {commit_data.commit_author}
Repository: {commit_data.repository_name}
Branch: {commit_data.branch_name}
Files Changed: {commit_data.total_files_changed}
Added Files: {', '.join(commit_data.added_files[:5])}
Modified Files: {', '.join(commit_data.modified_files[:5])}
Removed Files: {', '.join(commit_data.removed_files[:5])}

Provide a brief analysis focusing on:
1. Code quality aspects
2. Potential risks or concerns
3. Best practices compliance
4. Development progress assessment

Keep the response concise and actionable.
"""
    
    def _combine_analysis(self, commit_data: CommitData, basic: Dict, ai: Dict) -> AnalysisResult:
        """Combine basic and AI analysis into final result"""
        
        # Generate comprehensive report
        report = self._generate_report(commit_data, basic, ai)
        
        return AnalysisResult(
            commit_hash=commit_data.commit_hash,
            quality_score=basic["quality_score"],
            category=basic["category"],
            impact_level=basic["impact_level"],
            stats=basic["stats"],
            issues_identified=basic["issues"],
            recommendations=basic["recommendations"],
            report=report
        )
    
    def _generate_report(self, commit_data: CommitData, basic: Dict, ai: Dict) -> str:
        """Generate comprehensive markdown report"""
        report = f"""# Commit Analysis Report

## Commit Details
- **Hash**: `{commit_data.commit_hash[:8]}...`
- **Message**: {commit_data.commit_message}
- **Author**: {commit_data.commit_author}
- **Repository**: {commit_data.repository_name}
- **Branch**: {commit_data.branch_name}

## Analysis Summary
- **Category**: {basic["category"]}
- **Quality Score**: {basic["quality_score"]}/10
- **Impact Level**: {basic["impact_level"]}

## File Changes
- **Total Files**: {basic["stats"]["files_changed"]}
- **Added**: {basic["stats"]["added_files"]} files
- **Modified**: {basic["stats"]["modified_files"]} files
- **Removed**: {basic["stats"]["removed_files"]} files

## Issues Identified
{chr(10).join(f"- {issue}" for issue in basic["issues"]) if basic["issues"] else "- No issues identified"}

## Recommendations
{chr(10).join(f"- {rec}" for rec in basic["recommendations"]) if basic["recommendations"] else "- No specific recommendations"}

{f'## AI Insights\\n{ai.get("ai_insights", "")}' if ai.get("ai_insights") else ""}

---
*Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC*
"""
        return report
    
    def _create_fallback_analysis(self, commit_data: CommitData, error: str) -> AnalysisResult:
        """Create fallback analysis when main analysis fails"""
        return AnalysisResult(
            commit_hash=commit_data.commit_hash,
            quality_score=5,
            category="unknown",
            impact_level="medium",
            stats={"files_changed": commit_data.total_files_changed},
            issues_identified=[f"Analysis failed: {error}"],
            recommendations=["Manual review recommended"],
            report=f"# Analysis Failed\n\nAutomatic analysis failed for commit `{commit_data.commit_hash[:8]}...`\n\nError: {error}\n\nPlease review manually."
        )

# Initialize analyzer
analyzer = CommitAnalyzer()

# API Routes
@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = datetime.now() - start_time
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime=str(uptime),
        config_loaded=bool(config)
    )

@app.post("/analyze-commit", response_model=AnalysisResult)
async def analyze_commit(commit_data: CommitData):
    """Analyze a commit and return detailed analysis"""
    try:
        logger.info(f"Analyzing commit {commit_data.commit_hash} from {commit_data.repository_name}")
        result = await analyzer.analyze_commit(commit_data)
        return result
    except Exception as e:
        logger.error(f"Error in analyze_commit endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/capabilities")
async def get_capabilities():
    """Return MCP server capabilities"""
    return {
        "name": "commit-analyzer",
        "version": "1.0.0",
        "description": "GitHub commit analysis and reporting",
        "capabilities": [
            "commit_analysis",
            "quality_scoring",
            "report_generation",
            "issue_identification",
            "recommendation_generation"
        ],
        "ai_enabled": analyzer.openai_enabled,
        "cache_size": len(analysis_cache)
    }

@app.delete("/cache")
async def clear_cache():
    """Clear analysis cache"""
    global analysis_cache
    cache_size = len(analysis_cache)
    analysis_cache.clear()
    return {"message": f"Cache cleared. {cache_size} entries removed."}

@app.get("/stats")
async def get_stats():
    """Get server statistics"""
    return {
        "uptime": str(datetime.now() - start_time),
        "cache_size": len(analysis_cache),
        "ai_enabled": analyzer.openai_enabled,
        "config_loaded": bool(config)
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("MCP_SERVER_PORT", 8001))
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    
    logger.info(f"Starting MCP Commit Analyzer on {host}:{port}")
    uvicorn.run(app, host=host, port=port)