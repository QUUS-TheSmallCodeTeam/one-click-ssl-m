import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { v4 as uuidv4 } from 'uuid';
import { SSLAnalyzer } from '@/lib/ssl-analyzer';
import {
  calculateSecurityScore,
  extractIssues,
  calculateBusinessImpact,
  generateRecommendations,
  type AnalysisResponse
} from '@/lib/business-logic';

// Request validation schema
const AnalyzeRequestSchema = z.object({
  url: z.string().url('유효한 URL을 입력하세요')
});

import { analysisResults } from '@/lib/analysis-storage';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Validate request
    const { url } = AnalyzeRequestSchema.parse(body);

    const analysisId = uuidv4();
    const sslAnalyzer = new SSLAnalyzer();

    console.log(`Starting analysis for URL: ${url} with ID: ${analysisId}`);

    // Perform SSL analysis
    const sslResult = await sslAnalyzer.analyze(url);

    // Calculate security score
    const securityScore = calculateSecurityScore(sslResult);

    // Extract issues
    const issues = extractIssues(sslResult);

    // Calculate business impact
    const businessImpact = calculateBusinessImpact(securityScore, sslResult, issues);

    // Generate recommendations
    const recommendations = generateRecommendations(sslResult, issues);

    // Create response data
    const responseData: AnalysisResponse = {
      id: analysisId,
      url,
      ssl_grade: sslResult.ssl_grade,
      security_score: securityScore,
      issues,
      business_impact: businessImpact,
      recommendations,
      created_at: new Date().toISOString(),
      ssl_result: sslResult
    };

    // Store analysis results in memory
    analysisResults.set(analysisId, responseData);

    console.log(`Analysis completed for ${url}: Grade ${sslResult.ssl_grade}, Score ${securityScore}`);

    return NextResponse.json(responseData);

  } catch (error) {
    console.error('Analysis error:', error);

    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          error: 'Validation error',
          details: error.errors.map(e => `${e.path.join('.')}: ${e.message}`)
        },
        { status: 400 }
      );
    }

    return NextResponse.json(
      {
        error: '분석 중 오류가 발생했습니다',
        details: String(error)
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    message: '원클릭 SSL체크 API',
    version: '1.0.0',
    endpoint: 'POST /api/analyze'
  });
}

