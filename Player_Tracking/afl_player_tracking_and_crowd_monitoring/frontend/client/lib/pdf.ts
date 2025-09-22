import { PDFDocument, StandardFonts, rgb } from "pdf-lib";

export interface UploadMeta {
  id: string;
  original_filename: string;
  created_at: string;
}

function wrapText(text: string, maxWidth: number, font: any, size: number) {
  const words = text.split(/\s+/);
  const lines: string[] = [];
  let line = "";
  for (const w of words) {
    const test = line ? line + " " + w : w;
    const width = font.widthOfTextAtSize(test, size);
    if (width > maxWidth && line) {
      lines.push(line);
      line = w;
    } else {
      line = test;
    }
  }
  if (line) lines.push(line);
  return lines;
}

export async function buildAnalysisPdf(params: {
  title: string;
  upload: UploadMeta;
  section: string;
  data: unknown;
}): Promise<Blob> {
  const { title, upload, section, data } = params;
  const pdf = await PDFDocument.create();
  pdf.setTitle(title);
  pdf.setSubject(section);
  pdf.setAuthor("AFL Analytics");

  const font = await pdf.embedFont(StandardFonts.Helvetica);
  const fontBold = await pdf.embedFont(StandardFonts.HelveticaBold);

  let page = pdf.addPage();
  let { width, height } = page.getSize();
  const margin = 50;
  const contentWidth = width - margin * 2;
  let y = height - margin;

  const drawLine = (t: string, f: any, size: number, color = rgb(0, 0, 0)) => {
    const lines = wrapText(t, contentWidth, f, size);
    for (const ln of lines) {
      if (y < margin + size) {
        page = pdf.addPage();
        ({ width, height } = page.getSize());
        y = height - margin;
      }
      page.drawText(ln, { x: margin, y, size, font: f, color });
      y -= size + 4;
    }
  };

  // Header
  drawLine(title, fontBold, 20);
  const createdAt = upload.created_at ? new Date(upload.created_at).toLocaleString() : "";
  drawLine(`Upload: ${upload.original_filename} • Created: ${createdAt}`, font, 10, rgb(0.35, 0.35, 0.35));
  y -= 6;
  drawLine(section, fontBold, 14);

  // Body
  const body = data ? JSON.stringify(data, null, 2) : "Not available";
  const paragraphs = body.split("\n");
  for (const p of paragraphs) {
    drawLine(p, font, 10);
  }

  const bytes = await pdf.save();
  return new Blob([bytes], { type: "application/pdf" });
}
