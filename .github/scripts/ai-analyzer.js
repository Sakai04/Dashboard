#!/usr/bin/env node

/**
 * OpenAI Analyzer for Dashboard GitHub Actions Commit Tracker
 * Provides intelligent commit analysis using OpenAI GPT models
 */

const OpenAI = require('openai');

class AIAnalyzer {
  constructor() {
    if (!process.env.OPENAI_API_KEY) {
      console.log('⚠️ OpenAI API key not provided, AI analysis will be skipped');
      this.openai = null;
      return;
    }
    
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
    
    console.log('🤖 OpenAI analyzer initialized');
  }

  /**
   * Analyze commit using OpenAI GPT
   */
  async analyzeCommit(commitData) {
    if (!this.openai) {
      return null;
    }

    try {
      console.log(`🧠 AI analyzing commit: ${commitData.commit_hash}`);
      
      const prompt = this.buildAnalysisPrompt(commitData);
      
      const response = await this.openai.chat.completions.create({
        model: 'gpt-3.5-turbo',
        messages: [
          {
            role: 'system',
            content: this.getSystemPrompt()
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        max_tokens: 1000,
        temperature: 0.3
      });

      const analysisText = response.choices[0].message.content;
      return this.parseAnalysisResponse(analysisText);
      
    } catch (error) {
      console.error(`❌ AI analysis error for ${commitData.commit_hash}:`, error.message);
      return {
        summary: '자동 분석 실패',
        sentiment: 'Neutral',
        riskLevel: 'Unknown',
        suggestedActions: '수동 검토 필요'
      };
    }
  }

  /**
   * Build analysis prompt for the commit
   */
  buildAnalysisPrompt(commitData) {
    return `
다음 FastAPI/Python Dashboard 프로젝트의 커밋을 분석해주세요:

=== 커밋 정보 ===
제목: ${commitData.title}
작성자: ${commitData.author}
설명: ${commitData.description}
브랜치: ${commitData.branch}
우선순위: ${commitData.priority}
카테고리: ${commitData.categories.join(', ')}

=== 변경 파일 (${commitData.files_changed}개) ===
${commitData.changed_files.length > 0 ? commitData.changed_files.join('\n') : '파일 정보 없음'}

=== 프로젝트 컨텍스트 ===
- FastAPI 기반 Python 백엔드 프로젝트
- PostgreSQL 데이터베이스 사용
- Docker 컨테이너화
- Jenkins CI/CD 파이프라인
- Notion 기반 프로젝트 관리

=== 분석 플래그 ===
- 보안 관련: ${commitData.security_related ? '예' : '아니오'}
- API 관련: ${commitData.api_related ? '예' : '아니오'}
- 데이터베이스 관련: ${commitData.database_related ? '예' : '아니오'}

한국어로 다음 형식에 맞춰 분석 결과를 제공해주세요:

SUMMARY: [커밋의 주요 변경사항과 영향도를 2-3문장으로 요약]
SENTIMENT: [Positive/Negative/Neutral 중 하나]
RISK_LEVEL: [Low/Medium/High/Critical 중 하나]
ACTIONS: [권장되는 후속 조치나 주의사항을 1-2문장으로]
    `;
  }

  /**
   * System prompt for OpenAI
   */
  getSystemPrompt() {
    return `
당신은 FastAPI/Python 프로젝트의 커밋을 분석하는 전문가입니다.

분석 시 다음 사항을 고려하세요:

1. **보안 영향도**: 
   - .env, requirements.txt, Dockerfile 변경 시 높은 위험도
   - 인증/권한 관련 코드 변경 시 주의 필요

2. **API 영향도**:
   - app/routers/ 변경 시 엔드포인트 영향 분석
   - app/main.py 변경 시 전체 서비스 영향 고려

3. **데이터베이스 영향도**:
   - app/models/ 변경 시 스키마 변경 영향
   - 마이그레이션 필요성 검토

4. **CI/CD 영향도**:
   - Jenkinsfile 변경 시 빌드 파이프라인 영향
   - Docker 설정 변경 시 배포 영향

5. **한국어 응답**: 
   - 기술적이지만 이해하기 쉬운 한국어로 작성
   - 개발팀이 빠르게 파악할 수 있도록 간결하게 요약

항상 지정된 형식(SUMMARY:, SENTIMENT:, RISK_LEVEL:, ACTIONS:)을 정확히 지켜주세요.
    `;
  }

  /**
   * Parse OpenAI response into structured data
   */
  parseAnalysisResponse(analysisText) {
    try {
      const lines = analysisText.split('\n').map(line => line.trim()).filter(line => line);
      
      let summary = '';
      let sentiment = 'Neutral';
      let riskLevel = 'Unknown';
      let suggestedActions = '';

      for (const line of lines) {
        if (line.startsWith('SUMMARY:')) {
          summary = line.replace('SUMMARY:', '').trim();
        } else if (line.startsWith('SENTIMENT:')) {
          const sentimentText = line.replace('SENTIMENT:', '').trim().toLowerCase();
          if (sentimentText.includes('positive')) sentiment = 'Positive';
          else if (sentimentText.includes('negative')) sentiment = 'Negative';
          else sentiment = 'Neutral';
        } else if (line.startsWith('RISK_LEVEL:')) {
          const riskText = line.replace('RISK_LEVEL:', '').trim().toLowerCase();
          if (riskText.includes('critical')) riskLevel = 'Critical';
          else if (riskText.includes('high')) riskLevel = 'High';
          else if (riskText.includes('medium')) riskLevel = 'Medium';
          else if (riskText.includes('low')) riskLevel = 'Low';
        } else if (line.startsWith('ACTIONS:')) {
          suggestedActions = line.replace('ACTIONS:', '').trim();
        }
      }

      // Fallback values
      if (!summary) {
        summary = '커밋 분석 완료. 추가 검토가 필요할 수 있습니다.';
      }
      if (!suggestedActions) {
        suggestedActions = '특별한 후속 조치 없음';
      }

      return {
        summary,
        sentiment,
        riskLevel,
        suggestedActions
      };
      
    } catch (error) {
      console.error('❌ Error parsing AI response:', error.message);
      return {
        summary: 'AI 응답 파싱 실패',
        sentiment: 'Neutral',
        riskLevel: 'Unknown',
        suggestedActions: '수동 검토 필요'
      };
    }
  }

  /**
   * Batch analyze multiple commits
   */
  async analyzeCommits(commits) {
    if (!this.openai) {
      console.log('⚠️ OpenAI not configured, skipping AI analysis');
      return commits;
    }

    console.log(`🤖 Starting AI analysis for ${commits.length} commits`);
    const results = [];

    for (const commit of commits) {
      try {
        const analysis = await this.analyzeCommit(commit);
        results.push({
          ...commit,
          ai_analysis: analysis
        });
        
        // Rate limiting
        await new Promise(resolve => setTimeout(resolve, 1000));
        
      } catch (error) {
        console.error(`❌ AI analysis failed for ${commit.commit_hash}:`, error.message);
        results.push({
          ...commit,
          ai_analysis: null
        });
      }
    }

    console.log(`✅ AI analysis complete for ${results.length} commits`);
    return results;
  }

  /**
   * Test OpenAI connection
   */
  async testConnection() {
    if (!this.openai) {
      return false;
    }

    try {
      console.log('🔍 Testing OpenAI connection...');
      
      const response = await this.openai.chat.completions.create({
        model: 'gpt-3.5-turbo',
        messages: [
          {
            role: 'user',
            content: '안녕하세요. 연결 테스트입니다.'
          }
        ],
        max_tokens: 10
      });

      console.log('✅ OpenAI connection successful');
      return true;
      
    } catch (error) {
      console.error('❌ OpenAI connection failed:', error.message);
      return false;
    }
  }
}

module.exports = AIAnalyzer;