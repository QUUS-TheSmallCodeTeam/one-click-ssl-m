import { NextRequest, NextResponse } from 'next/server';
import { analysisResults } from '@/lib/analysis-storage';
import { generatePDFReport } from '@/lib/pdf-generator';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;

    console.log(`PDF download request for report ID: ${id}`);

    // Retrieve stored analysis result
    const analysisData = analysisResults.get(id);

    if (!analysisData) {
      console.error(`Analysis result not found for ID: ${id}`);
      return NextResponse.json(
        { error: `분석 결과가 존재하지 않습니다: ${id}` },
        { status: 404 }
      );
    }

    console.log(`Generating PDF for domain: ${analysisData.url}`);

    // Generate PDF
    const pdfBuffer = await generatePDFReport(analysisData);

    console.log(`PDF generated successfully: ${pdfBuffer.length} bytes`);

    // Create filename
    const domain = new URL(analysisData.url).hostname;
    const filename = `${domain}_security_report.pdf`;

    // Return PDF as response
    return new NextResponse(pdfBuffer, {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': `attachment; filename="${filename}"`,
        'Content-Length': pdfBuffer.length.toString(),
      },
    });

  } catch (error) {
    console.error('PDF generation error:', error);

    return NextResponse.json(
      {
        error: 'PDF 생성 중 오류가 발생했습니다',
        details: String(error)
      },
      { status: 500 }
    );
  }
}