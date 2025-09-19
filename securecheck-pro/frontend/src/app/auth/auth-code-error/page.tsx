export default function AuthCodeError() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="text-6xl mb-6">⚠️</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-4">로그인 오류</h1>
        <p className="text-gray-600 mb-6">
          Google 로그인 중 오류가 발생했습니다. 다시 시도해 주세요.
        </p>
        <a
          href="/"
          className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
        >
          홈으로 돌아가기
        </a>
      </div>
    </div>
  )
}