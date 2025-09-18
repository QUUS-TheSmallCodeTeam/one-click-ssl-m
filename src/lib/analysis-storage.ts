import type { AnalysisResponse } from './business-logic';

// In-memory storage for analysis results (실제로는 데이터베이스를 사용해야 함)
export const analysisResults = new Map<string, AnalysisResponse>();