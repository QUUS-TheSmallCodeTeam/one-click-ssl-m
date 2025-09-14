'use client';

import { useState } from 'react';
import { SecurityReport } from './SecurityReport';

interface AnalysisResult {
  id: string;
  url: string;
  ssl_grade: string;
  security_score: number;
  issues: Array<{
    type: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    title: string;
    description: string;
  }>;
  business_impact: {
    revenue_loss_annual: number;
    seo_impact: number;
    user_trust_impact: number;
  };
  recommendations: string[];
  created_at: string;
}

export function SecurityAnalyzer() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!url.trim()) {
      setError('URL을 입력해주세요.');
      return;
    }

    // URL 형식 검증
    if (!url.match(/^https?:\/\/.+/)) {
      setError('올바른 URL 형식을 입력해주세요 (https://example.com)');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // Call FastAPI backend directly
      const response = await fetch('/api/v1/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error('분석 중 오류가 발생했습니다.');
      }

      const data = await response.json();
      setResult(data);
      
      // Save analysis data to localStorage for PDF generation
      localStorage.setItem('latestAnalysisData', JSON.stringify(data));
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleAnalyze();
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
        <div className="space-y-4">
          <label htmlFor="url-input" className="block text-lg font-medium text-gray-700">
            웹사이트 URL 입력
          </label>
          
          <div className="flex space-x-4">
            <input
              id="url-input"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="https://example.com"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-lg"
              disabled={isLoading}
            />
            
            <button
              onClick={handleAnalyze}
              disabled={isLoading}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed text-lg font-medium min-w-[120px]"
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  분석중...
                </div>
              ) : (
                '분석 시작'
              )}
            </button>
          </div>
          
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800">{error}</p>
            </div>
          )}
        </div>
      </div>

      {result && <SecurityReport data={result} />}
    </div>
  );
}