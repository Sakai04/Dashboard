#!/usr/bin/env node

/**
 * GitHub Actions Commit Analyzer for Dashboard FastAPI Project
 * Replaces n8n workflow logic with GitHub Actions-native approach
 */

const { Octokit } = require('@octokit/rest');
const fs = require('fs');
const path = require('path');

class CommitAnalyzer {
  constructor() {
    this.octokit = new Octokit({
      auth: process.env.GITHUB_TOKEN
    });
    
    this.repository = process.env.GITHUB_REPOSITORY;
    this.sha = process.env.GITHUB_SHA;
    this.ref = process.env.GITHUB_REF;
    this.eventName = process.env.GITHUB_EVENT_NAME;
    
    // Parse repository owner and name
    [this.owner, this.repo] = this.repository.split('/');
    
    console.log(`🔍 Analyzing commits for ${this.repository}`);
    console.log(`📍 SHA: ${this.sha}`);
    console.log(`🌿 Ref: ${this.ref}`);
    console.log(`⚡ Event: ${this.eventName}`);
  }

  /**
   * Get commits to analyze based on event type
   */
  async getCommitsToAnalyze() {
    try {
      let commits = [];
      
      if (this.eventName === 'push') {
        // For push events, get the pushed commits
        const eventPayload = JSON.parse(fs.readFileSync(process.env.GITHUB_EVENT_PATH, 'utf8'));
        
        if (eventPayload.commits && eventPayload.commits.length > 0) {
          // Use commits from push payload
          commits = eventPayload.commits;
          console.log(`📦 Found ${commits.length} commits in push event`);
        } else {
          // Fallback: get latest commit
          const { data: commit } = await this.octokit.rest.repos.getCommit({
            owner: this.owner,
            repo: this.repo,
            ref: this.sha
          });
          commits = [this.transformGitHubCommit(commit)];
          console.log(`📦 Analyzed latest commit as fallback`);
        }
      } else if (this.eventName === 'pull_request') {
        // For merged PRs, get all commits in the PR
        const eventPayload = JSON.parse(fs.readFileSync(process.env.GITHUB_EVENT_PATH, 'utf8'));
        const prNumber = eventPayload.pull_request.number;
        
        const { data: prCommits } = await this.octokit.rest.pulls.listCommits({
          owner: this.owner,
          repo: this.repo,
          pull_number: prNumber
        });
        
        commits = prCommits.map(commit => this.transformGitHubCommit(commit));
        console.log(`📦 Found ${commits.length} commits in merged PR #${prNumber}`);
      }
      
      return commits;
    } catch (error) {
      console.error('❌ Error getting commits:', error.message);
      return [];
    }
  }

  /**
   * Transform GitHub API commit format to our internal format
   */
  transformGitHubCommit(commit) {
    const files = commit.files || [];
    
    return {
      id: commit.sha,
      message: commit.commit.message,
      author: {
        name: commit.commit.author.name,
        email: commit.commit.author.email
      },
      timestamp: commit.commit.author.date,
      url: commit.html_url,
      added: files.filter(f => f.status === 'added').map(f => f.filename),
      removed: files.filter(f => f.status === 'removed').map(f => f.filename),
      modified: files.filter(f => f.status === 'modified').map(f => f.filename)
    };
  }

  /**
   * Analyze commits with Dashboard FastAPI project-specific logic
   */
  async analyzeCommits(commits) {
    const results = [];
    
    for (const commit of commits) {
      try {
        console.log(`🔍 Analyzing commit: ${commit.id.substring(0, 8)} - ${commit.message.split('\\n')[0]}`);
        
        // Get detailed commit info if not available
        let detailedCommit = commit;
        if (!commit.added && !commit.modified && !commit.removed) {
          const { data } = await this.octokit.rest.repos.getCommit({
            owner: this.owner,
            repo: this.repo,
            ref: commit.id
          });
          detailedCommit = this.transformGitHubCommit(data);
        }
        
        const analysis = this.analyzeCommit(detailedCommit);
        results.push(analysis);
        
        console.log(`✅ Priority: ${analysis.priority}, Categories: ${analysis.categories.join(', ')}`);
      } catch (error) {
        console.error(`❌ Error analyzing commit ${commit.id}:`, error.message);
      }
    }
    
    return results;
  }

  /**
   * Main commit analysis logic (ported from n8n workflow)
   */
  analyzeCommit(commit) {
    // Basic information extraction
    const commitData = {
      title: commit.message.split('\\n')[0].substring(0, 100),
      commit_hash: commit.id.substring(0, 8),
      full_hash: commit.id,
      author: commit.author.name,
      email: commit.author.email,
      date: commit.timestamp,
      repository: this.repository,
      branch: this.ref.replace('refs/heads/', ''),
      url: commit.url,
      files_changed: (commit.added?.length || 0) + (commit.removed?.length || 0) + (commit.modified?.length || 0),
      lines_added: 0, // Will be enriched later
      lines_deleted: 0,
      description: commit.message
    };

    // Dashboard project-specific file analysis
    const changedFiles = [...(commit.added || []), ...(commit.removed || []), ...(commit.modified || [])];
    
    // Priority calculation and categorization
    let priorityScore = 0;
    let categories = [];
    let cicdStatus = 'Pending';
    
    // Security related files (highest priority)
    const securityFiles = ['.env', 'requirements.txt', 'Dockerfile', 'docker-compose.yml'];
    if (changedFiles.some(file => securityFiles.some(secFile => file.includes(secFile)))) {
      priorityScore += 100;
      categories.push('Security', 'Configuration');
      console.log(`🔒 Security files detected: ${changedFiles.filter(f => securityFiles.some(sf => f.includes(sf)))}`)
    }
    
    // CI/CD related files
    if (changedFiles.some(file => file.includes('Jenkinsfile') || file.includes('docker'))) {
      priorityScore += 90;
      categories.push('CI/CD');
      cicdStatus = 'Building';
      console.log(`🚀 CI/CD files detected`);
    }
    
    // API development related files
    if (changedFiles.some(file => file.includes('app/routers/') || file.includes('app/main.py'))) {
      priorityScore += 80;
      categories.push('API Development');
      console.log(`🔌 API files detected`);
    }
    
    // Database related files
    if (changedFiles.some(file => file.includes('app/models/') || file.includes('database.py'))) {
      priorityScore += 60;
      categories.push('Database');
      console.log(`🗄️ Database files detected`);
    }
    
    // Schema related files
    if (changedFiles.some(file => file.includes('app/schemas/'))) {
      priorityScore += 50;
      categories.push('API Development');
    }
    
    // CRUD related files
    if (changedFiles.some(file => file.includes('app/crud/'))) {
      priorityScore += 40;
      categories.push('Database');
    }
    
    // Documentation files
    if (changedFiles.some(file => file.includes('README.md') || file.includes('docs/'))) {
      priorityScore += 10;
      categories.push('Documentation');
    }
    
    // Test files
    if (changedFiles.some(file => file.includes('test') || file.includes('spec'))) {
      priorityScore += 30;
      categories.push('Testing');
      console.log(`🧪 Test files detected`);
    }
    
    // Commit message keyword analysis
    const message = commit.message.toLowerCase();
    const highPriorityKeywords = ['fix', 'security', 'urgent', 'hotfix', 'critical', 'bug'];
    const featureKeywords = ['feat', 'feature', 'add', 'new'];
    const refactorKeywords = ['refactor', 'refactoring', 'cleanup', 'improve'];
    
    if (highPriorityKeywords.some(keyword => message.includes(keyword))) {
      priorityScore += 70;
      categories.push('Bug Fix');
      console.log(`🚨 High priority keywords detected`);
    } else if (featureKeywords.some(keyword => message.includes(keyword))) {
      priorityScore += 50;
      categories.push('Feature');
    } else if (refactorKeywords.some(keyword => message.includes(keyword))) {
      priorityScore += 30;
      categories.push('Refactoring');
    }
    
    // Priority level determination
    let priority;
    if (priorityScore >= 100) {
      priority = 'Critical';
    } else if (priorityScore >= 70) {
      priority = 'High';
    } else if (priorityScore >= 40) {
      priority = 'Medium';
    } else {
      priority = 'Low';
    }
    
    // Status determination
    let status;
    if (priority === 'Critical') {
      status = 'Review Required';
    } else if (changedFiles.some(file => file.includes('Jenkinsfile'))) {
      status = 'Pending';
    } else {
      status = 'Completed';
    }
    
    // Remove category duplicates
    categories = [...new Set(categories)];
    if (categories.length === 0) {
      categories = ['General'];
    }
    
    // Final data composition
    return {
      ...commitData,
      priority: priority,
      status: status,
      categories: categories,
      priority_score: priorityScore,
      cicd_status: cicdStatus,
      changed_files: changedFiles,
      security_related: securityFiles.some(secFile => 
        changedFiles.some(file => file.includes(secFile))
      ),
      api_related: changedFiles.some(file => 
        file.includes('app/routers/') || file.includes('app/main.py')
      ),
      database_related: changedFiles.some(file => 
        file.includes('app/models/') || file.includes('database.py')
      )
    };
  }

  /**
   * Main execution function
   */
  async run() {
    try {
      console.log('🚀 Starting commit analysis...');
      
      const commits = await this.getCommitsToAnalyze();
      
      if (commits.length === 0) {
        console.log('ℹ️ No commits to analyze');
        fs.appendFileSync(process.env.GITHUB_OUTPUT, 'commits_found=false\n');
        return;
      }
      
      const analysis = await this.analyzeCommits(commits);
      
      // Save results to temporary file for next step
      const outputPath = '/tmp/commit-analysis.json';
      fs.writeFileSync(outputPath, JSON.stringify(analysis, null, 2));
      
      console.log(`✅ Analysis complete! ${analysis.length} commits analyzed`);
      console.log(`💾 Results saved to ${outputPath}`);
      fs.appendFileSync(process.env.GITHUB_OUTPUT, 'commits_found=true\n');
      
      // Output summary
      analysis.forEach(commit => {
        console.log(`📋 ${commit.commit_hash}: ${commit.title} (${commit.priority})`);
      });
      
    } catch (error) {
      console.error('❌ Fatal error:', error);
      process.exit(1);
    }
  }
}

// Run the analyzer
if (require.main === module) {
  const analyzer = new CommitAnalyzer();
  analyzer.run();
}

module.exports = CommitAnalyzer;