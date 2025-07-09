#!/usr/bin/env node

/**
 * Notion Client for Dashboard GitHub Actions Commit Tracker
 * Handles Notion database integration and OpenAI analysis
 */

const { Client } = require('@notionhq/client');
const fs = require('fs');
const AIAnalyzer = require('./ai-analyzer');

class NotionClient {
  constructor() {
    this.notion = new Client({
      auth: process.env.NOTION_TOKEN
    });
    
    this.databaseId = process.env.NOTION_DATABASE_ID;
    this.aiAnalyzer = new AIAnalyzer();
    
    if (!this.databaseId) {
      throw new Error('NOTION_DATABASE_ID environment variable is required');
    }
    
    console.log('🔗 Notion client initialized');
    console.log(`📊 Database ID: ${this.databaseId.substring(0, 8)}...`);
  }

  /**
   * Create a new page in Notion database for each commit
   */
  async createCommitPage(commitData) {
    try {
      console.log(`📝 Creating Notion page for commit: ${commitData.commit_hash}`);
      
      // Get AI analysis if OpenAI is configured
      let aiAnalysis = null;
      if (process.env.OPENAI_API_KEY) {
        console.log('🤖 Getting AI analysis...');
        aiAnalysis = await this.aiAnalyzer.analyzeCommit(commitData);
      }
      
      // Prepare properties for Notion
      const properties = {
        // Title (required)
        'Name': {
          title: [
            {
              text: {
                content: commitData.title
              }
            }
          ]
        },
        
        // Basic commit info
        'Commit Hash': {
          rich_text: [
            {
              text: {
                content: commitData.commit_hash
              }
            }
          ]
        },
        
        'Full Hash': {
          rich_text: [
            {
              text: {
                content: commitData.full_hash
              }
            }
          ]
        },
        
        'Author': {
          rich_text: [
            {
              text: {
                content: commitData.author
              }
            }
          ]
        },
        
        'Email': {
          email: commitData.email
        },
        
        'Date': {
          date: {
            start: commitData.date
          }
        },
        
        'Repository': {
          rich_text: [
            {
              text: {
                content: commitData.repository
              }
            }
          ]
        },
        
        'Branch': {
          rich_text: [
            {
              text: {
                content: commitData.branch
              }
            }
          ]
        },
        
        'URL': {
          url: commitData.url
        },
        
        // Analysis results
        'Priority': {
          select: {
            name: commitData.priority
          }
        },
        
        'Status': {
          select: {
            name: commitData.status
          }
        },
        
        'Categories': {
          multi_select: commitData.categories.map(cat => ({ name: cat }))
        },
        
        'Priority Score': {
          number: commitData.priority_score
        },
        
        'Files Changed': {
          number: commitData.files_changed
        },
        
        'Lines Added': {
          number: commitData.lines_added || 0
        },
        
        'Lines Deleted': {
          number: commitData.lines_deleted || 0
        },
        
        'CI/CD Status': {
          select: {
            name: commitData.cicd_status
          }
        },
        
        // Boolean flags
        'Security Related': {
          checkbox: commitData.security_related || false
        },
        
        'API Related': {
          checkbox: commitData.api_related || false
        },
        
        'Database Related': {
          checkbox: commitData.database_related || false
        }
      };
      
      // Add AI analysis if available
      if (aiAnalysis) {
        properties['AI Summary'] = {
          rich_text: [
            {
              text: {
                content: aiAnalysis.summary.substring(0, 2000) // Notion limit
              }
            }
          ]
        };
        
        properties['AI Sentiment'] = {
          select: {
            name: aiAnalysis.sentiment
          }
        };
        
        properties['AI Risk Level'] = {
          select: {
            name: aiAnalysis.riskLevel
          }
        };
        
        if (aiAnalysis.suggestedActions) {
          properties['AI Suggestions'] = {
            rich_text: [
              {
                text: {
                  content: aiAnalysis.suggestedActions.substring(0, 2000)
                }
              }
            ]
          };
        }
      }
      
      // Create the page
      const response = await this.notion.pages.create({
        parent: {
          database_id: this.databaseId
        },
        properties: properties,
        children: [
          {
            object: 'block',
            type: 'heading_2',
            heading_2: {
              rich_text: [
                {
                  type: 'text',
                  text: {
                    content: '커밋 상세 정보'
                  }
                }
              ]
            }
          },
          {
            object: 'block',
            type: 'paragraph',
            paragraph: {
              rich_text: [
                {
                  type: 'text',
                  text: {
                    content: `설명: ${commitData.description}`
                  }
                }
              ]
            }
          },
          {
            object: 'block',
            type: 'heading_3',
            heading_3: {
              rich_text: [
                {
                  type: 'text',
                  text: {
                    content: '변경된 파일'
                  }
                }
              ]
            }
          },
          {
            object: 'block',
            type: 'bulleted_list_item',
            bulleted_list_item: {
              rich_text: [
                {
                  type: 'text',
                  text: {
                    content: commitData.changed_files.length > 0 
                      ? commitData.changed_files.join(', ')
                      : '파일 정보 없음'
                  }
                }
              ]
            }
          }
        ]
      });
      
      console.log(`✅ Notion page created: ${response.url}`);
      return response;
      
    } catch (error) {
      console.error(`❌ Error creating Notion page for ${commitData.commit_hash}:`, error.message);
      throw error;
    }
  }

  /**
   * Process all commits from analysis
   */
  async processCommits() {
    try {
      const analysisPath = '/tmp/commit-analysis.json';
      
      if (!fs.existsSync(analysisPath)) {
        console.log('ℹ️ No commit analysis found, skipping Notion update');
        return;
      }
      
      const commits = JSON.parse(fs.readFileSync(analysisPath, 'utf8'));
      console.log(`📦 Processing ${commits.length} commits for Notion`);
      
      const results = [];
      
      for (const commit of commits) {
        try {
          const page = await this.createCommitPage(commit);
          results.push({
            commit_hash: commit.commit_hash,
            notion_page_id: page.id,
            notion_url: page.url,
            status: 'success'
          });
          
          // Rate limiting - wait between requests
          await new Promise(resolve => setTimeout(resolve, 500));
          
        } catch (error) {
          console.error(`❌ Failed to process commit ${commit.commit_hash}:`, error.message);
          results.push({
            commit_hash: commit.commit_hash,
            status: 'error',
            error: error.message
          });
        }
      }
      
      // Save results
      const resultsPath = '/tmp/notion-results.json';
      fs.writeFileSync(resultsPath, JSON.stringify(results, null, 2));
      
      console.log(`✅ Notion processing complete!`);
      console.log(`📊 Success: ${results.filter(r => r.status === 'success').length}`);
      console.log(`❌ Errors: ${results.filter(r => r.status === 'error').length}`);
      
      return results;
      
    } catch (error) {
      console.error('❌ Fatal error processing commits:', error);
      throw error;
    }
  }

  /**
   * Verify Notion database structure
   */
  async verifyDatabase() {
    try {
      console.log('🔍 Verifying Notion database structure...');
      
      const database = await this.notion.databases.retrieve({
        database_id: this.databaseId
      });
      
      console.log(`✅ Database found: ${database.title[0]?.plain_text || 'Untitled'}`);
      
      // Check required properties
      const requiredProps = [
        'Name', 'Commit Hash', 'Author', 'Date', 'Priority', 'Status', 'Categories'
      ];
      
      const existingProps = Object.keys(database.properties);
      const missingProps = requiredProps.filter(prop => !existingProps.includes(prop));
      
      if (missingProps.length > 0) {
        console.warn(`⚠️ Missing properties in database: ${missingProps.join(', ')}`);
        console.warn('Please ensure your Notion database has all required properties');
      } else {
        console.log('✅ All required properties found');
      }
      
      return database;
      
    } catch (error) {
      console.error('❌ Error verifying database:', error.message);
      throw error;
    }
  }

  /**
   * Main execution function
   */
  async run() {
    try {
      console.log('🚀 Starting Notion integration...');
      
      // Verify database first
      await this.verifyDatabase();
      
      // Process commits
      await this.processCommits();
      
      console.log('✅ Notion integration complete!');
      
    } catch (error) {
      console.error('❌ Fatal error in Notion client:', error);
      process.exit(1);
    }
  }
}

// Run the client
if (require.main === module) {
  const client = new NotionClient();
  client.run();
}

module.exports = NotionClient;