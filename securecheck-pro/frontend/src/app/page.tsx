import { SecurityAnalyzer } from '@/components/SecurityAnalyzer';
import AuthButton from '@/components/AuthButton';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-end mb-8">
          <AuthButton />
        </div>

        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            원클릭SSL
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            웹사이트 URL을 입력하면 종합 보안 분석 보고서를 자동으로 생성합니다
          </p>
        </div>
        
        <SecurityAnalyzer />
        
        <div className="mt-16 text-center">
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-3xl mb-4">🔒</div>
              <h3 className="text-lg font-semibold mb-2">SSL 분석</h3>
              <p className="text-gray-600">인증서 상태, 보안 등급, 취약점을 종합 분석</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-3xl mb-4">📊</div>
              <h3 className="text-lg font-semibold mb-2">비즈니스 영향</h3>
              <p className="text-gray-600">매출 손실, ROI 계산, 개선 우선순위 제시</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-3xl mb-4">📄</div>
              <h3 className="text-lg font-semibold mb-2">PDF 보고서</h3>
              <p className="text-gray-600">경영진용 요약부터 개발자용 상세 가이드까지</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
