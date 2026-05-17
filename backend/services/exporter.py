from pathlib import Path
from datetime import datetime
import re

EXPORT_BASE = Path('./exports')


class DocumentExporter:
    def __init__(self, project: dict, analysis_result: dict):
        self.project = project
        self.results = analysis_result.get('results', {})
        self.docs    = analysis_result.get('documentation', {})
        EXPORT_BASE.mkdir(parents=True, exist_ok=True)

    def to_markdown(self) -> str:
        return self.docs.get('full_markdown', '# Sin documentación generada')

    def to_html(self) -> str:
        md = self.to_markdown()
        project_name = self.project.get('name', 'Proyecto')

        html_body = md
        html_body = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html_body, flags=re.MULTILINE)
        html_body = re.sub(r'^### (.+)$',  r'<h3>\1</h3>', html_body, flags=re.MULTILINE)
        html_body = re.sub(r'^## (.+)$',   r'<h2>\1</h2>', html_body, flags=re.MULTILINE)
        html_body = re.sub(r'^# (.+)$',    r'<h1>\1</h1>', html_body, flags=re.MULTILINE)
        html_body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_body)
        html_body = re.sub(r'\*(.+?)\*',      r'<em>\1</em>',        html_body)
        html_body = re.sub(r'`([^`]+)`', r'<code>\1</code>', html_body)
        html_body = re.sub(r'```[\w]*\n(.*?)```', r'<pre><code>\1</code></pre>', html_body, flags=re.DOTALL)

        def convert_table(m):
            rows = m.group(0).strip().split('\n')
            out = '<table>\n'
            for i, row in enumerate(rows):
                if re.match(r'\|[-| :]+\|', row):
                    continue
                cells = [c.strip() for c in row.split('|') if c.strip()]
                tag = 'th' if i == 0 else 'td'
                out += '<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>\n'
            return out + '</table>\n'
        html_body = re.sub(r'(\|.+\|\n)+', convert_table, html_body)
        html_body = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html_body, flags=re.MULTILINE)
        html_body = re.sub(r'^\- (.+)$', r'<li>\1</li>', html_body, flags=re.MULTILINE)
        html_body = re.sub(r'(<li>.*?</li>\n?)+', r'<ul>\g<0></ul>', html_body, flags=re.DOTALL)
        html_body = html_body.replace('---', '<hr>')
        html_body = re.sub(r'\n\n+', '</p><p>', html_body)
        html_body = '<p>' + html_body + '</p>'

        score = self.results.get('quality_score', 0)
        score_color = '#10b981' if score >= 70 else '#f59e0b' if score >= 40 else '#ef4444'

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{project_name} — Documentación Técnica</title>
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;700;800&display=swap');
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --bg: #0f172a; --surface: #1e293b; --border: #334155;
    --accent: #38bdf8; --accent2: #818cf8; --accent3: #34d399;
    --text: #cbd5e1; --muted: #64748b; --white: #f1f5f9;
  }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; line-height: 1.7; }}
  .container {{ max-width: 960px; margin: 0 auto; padding: 3rem 2rem; }}
  .doc-header {{ background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 2.5rem; margin-bottom: 3rem; position: relative; overflow: hidden; }}
  .doc-header::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, var(--accent), var(--accent2), var(--accent3)); }}
  .doc-header h1 {{ font-size: 2rem; font-weight: 800; color: var(--white); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem; }}
  .doc-header .subtitle {{ color: var(--muted); font-size: 0.9rem; font-family: 'JetBrains Mono', monospace; }}
  .stats-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 1.5rem; }}
  .stat {{ background: var(--bg); border: 1px solid var(--border); border-radius: 10px; padding: 1rem; text-align: center; }}
  .stat .val {{ font-size: 1.8rem; font-weight: 800; color: var(--white); }}
  .stat .lbl {{ font-size: 0.7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.2rem; font-family: 'JetBrains Mono', monospace; }}
  .quality-badge {{ display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.4rem 1rem; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 100px; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: {score_color}; margin-top: 1rem; }}
  h1 {{ font-size: 1.8rem; font-weight: 800; color: var(--white); margin: 2.5rem 0 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--accent); }}
  h2 {{ font-size: 1.4rem; font-weight: 700; color: var(--white); margin: 2rem 0 0.75rem; padding-left: 0.75rem; border-left: 3px solid var(--accent2); }}
  h3 {{ font-size: 1.1rem; font-weight: 700; color: var(--accent); margin: 1.5rem 0 0.5rem; }}
  h4 {{ font-size: 1rem; font-weight: 600; color: var(--text); margin: 1rem 0 0.4rem; }}
  p {{ margin: 0.75rem 0; }}
  code {{ background: rgba(56,189,248,0.08); border: 1px solid rgba(56,189,248,0.15); padding: 0.15rem 0.45rem; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; color: var(--accent); }}
  pre {{ background: #0d1b2a; border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem; overflow-x: auto; margin: 1rem 0; }}
  pre code {{ background: none; border: none; padding: 0; color: #a8d8f0; font-size: 0.85rem; }}
  table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.9rem; }}
  th {{ background: var(--surface); color: var(--white); padding: 0.7rem 1rem; text-align: left; font-weight: 600; border: 1px solid var(--border); }}
  td {{ padding: 0.6rem 1rem; border: 1px solid var(--border); color: var(--text); }}
  tr:nth-child(even) td {{ background: rgba(255,255,255,0.02); }}
  blockquote {{ border-left: 3px solid var(--accent3); padding: 0.75rem 1rem; background: rgba(52,211,153,0.05); border-radius: 0 8px 8px 0; margin: 1rem 0; color: var(--accent3); font-style: italic; }}
  ul {{ padding-left: 1.5rem; margin: 0.5rem 0; }}
  li {{ margin: 0.3rem 0; }}
  hr {{ border: none; border-top: 1px solid var(--border); margin: 2.5rem 0; }}
  strong {{ color: var(--white); font-weight: 700; }}
  em {{ color: var(--accent2); font-style: italic; }}
  .toc {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; }}
  .toc h3 {{ color: var(--white); margin: 0 0 1rem; display: flex; align-items: center; gap: 0.5rem; }}
  .toc ol {{ padding-left: 1.5rem; }}
  .toc li {{ margin: 0.4rem 0; }}
  .toc a {{ color: var(--accent); text-decoration: none; }}
  .toc a:hover {{ text-decoration: underline; }}
  .doc-footer {{ margin-top: 4rem; padding-top: 2rem; border-top: 1px solid var(--border); text-align: center; color: var(--muted); font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; }}
  .doc-footer span {{ color: var(--accent); }}
  .material-icons {{ font-size: 1.2em; vertical-align: middle; }}
  .material-symbols-outlined {{ font-size: 1.2em; vertical-align: middle; }}
</style>
</head>
<body>
<div class="container">
  <div class="doc-header">
    <h1><span class="material-icons">description</span> {project_name}</h1>
    <div class="subtitle">Documentación Técnica Profesional · Generado {datetime.utcnow().strftime('%d/%m/%Y %H:%M')} UTC</div>
    <div class="quality-badge">Score de Calidad: {score}/100</div>
    <div class="stats-row">
      <div class="stat"><div class="val">{self.results.get('total_files', 0)}</div><div class="lbl">Archivos</div></div>
      <div class="stat"><div class="val">{len(self.results.get('functions', []))}</div><div class="lbl">Funciones</div></div>
      <div class="stat"><div class="val">{len(self.results.get('classes', []))}</div><div class="lbl">Clases</div></div>
      <div class="stat"><div class="val">{len(self.results.get('endpoints', []))}</div><div class="lbl">Endpoints</div></div>
    </div>
  </div>
  <div class="toc">
    <h3><span class="material-icons">list</span> Tabla de Contenidos</h3>
    <ol>
      <li><a href="#sec1">Resumen del Proyecto</a></li>
      <li><a href="#sec2">Arquitectura y Diseño</a></li>
      <li><a href="#sec3">Documentación de API</a></li>
      <li><a href="#sec4">Clases y Objetos</a></li>
      <li><a href="#sec5">Funciones</a></li>
      <li><a href="#sec6">Modelos de Datos</a></li>
      <li><a href="#sec7">Guía de Despliegue</a></li>
      <li><a href="#sec8">Reporte de Calidad</a></li>
    </ol>
  </div>
  <div class="content">{html_body}</div>
  <div class="doc-footer">Generado por <span>AutoDocs AI</span> · {datetime.utcnow().strftime('%Y-%m-%d')}</div>
</div>
</body>
</html>"""

    # ── PDF: WeasyPrint → ReportLab → HTML fallback ──────────────────────────
    def to_pdf(self) -> str:
        html_content = self.to_html()
        output_path = EXPORT_BASE / f"{self.project['_id']}_docs.pdf"
        html_path   = EXPORT_BASE / f"{self.project['_id']}_docs.html"

        # Always save HTML as backup
        html_path.write_text(html_content, encoding='utf-8')

        # 1st attempt: WeasyPrint (best visual quality)
        try:
            from weasyprint import HTML
            HTML(string=html_content).write_pdf(str(output_path))
            if output_path.exists() and output_path.stat().st_size > 1000:
                print(f"[PDF] WeasyPrint generado exitosamente: {output_path.stat().st_size} bytes")
                return str(output_path)
            else:
                print(f"[PDF] WeasyPrint generó archivo inválido o muy pequeño")
        except Exception as e:
            print(f"[PDF] Error en WeasyPrint: {str(e)}")

        # 2nd attempt: ReportLab (always works, no system deps)
        try:
            pdf_path = self._pdf_with_reportlab(str(output_path))
            if pdf_path and Path(pdf_path).exists() and Path(pdf_path).stat().st_size > 1000:
                print(f"[PDF] ReportLab generado exitosamente: {Path(pdf_path).stat().st_size} bytes")
                return pdf_path
            else:
                print(f"[PDF] ReportLab generó archivo inválido o muy pequeño")
        except Exception as e:
            print(f"[PDF] Error en ReportLab: {str(e)}")

        # Final fallback: HTML (but rename to .pdf to avoid confusion)
        print(f"[PDF] Ambos métodos fallaron, usando HTML como fallback")
        return str(html_path)

    def _pdf_with_reportlab(self, output_path: str) -> str:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer,
            Table, TableStyle, HRFlowable,
        )
        from reportlab.lib.enums import TA_CENTER

        project_name = self.project.get('name', 'Proyecto')
        score  = self.results.get('quality_score', 0)
        md     = self.to_markdown()

        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm,
            title=f"{project_name} — Documentación Técnica",
            author="AutoDocs AI",
        )

        base = getSampleStyleSheet()
        def S(name, parent='Normal', **kw):
            return ParagraphStyle(name, parent=base[parent], **kw)

        styles = {
            'title': S('T', 'Title',   fontSize=24, textColor=colors.HexColor('#0f172a'), spaceAfter=8, alignment=TA_CENTER),
            'sub':   S('Su','Normal',  fontSize=10, textColor=colors.HexColor('#64748b'), spaceAfter=16, alignment=TA_CENTER),
            'h1':    S('H1','Heading1',fontSize=18, textColor=colors.HexColor('#0f172a'), spaceBefore=20, spaceAfter=8),
            'h2':    S('H2','Heading2',fontSize=14, textColor=colors.HexColor('#1e293b'), spaceBefore=16, spaceAfter=6),
            'h3':    S('H3','Heading3',fontSize=12, textColor=colors.HexColor('#334155'), spaceBefore=12, spaceAfter=4),
            'h4':    S('H4','Heading4',fontSize=10, textColor=colors.HexColor('#475569'), spaceBefore=10,  spaceAfter=3),
            'body':  S('Bo','Normal',  fontSize=10, textColor=colors.HexColor('#334155'), leading=15, spaceAfter=5),
            'code':  S('Co','Code',    fontSize=8, textColor=colors.HexColor('#0c4a6e'),
                       backColor=colors.HexColor('#f0f9ff'), borderPad=4,
                       fontName='Courier', leading=12, spaceAfter=8),
            'quote': S('Qu','Normal',  fontSize=10, textColor=colors.HexColor('#166534'),
                       leftIndent=15, backColor=colors.HexColor('#f0fdf4'), spaceAfter=8),
            'location': S('Loc','Normal', fontSize=8, textColor=colors.HexColor('#64748b'),
                          leftIndent=10, spaceAfter=4),
        }

        story = []
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(f"[DOC] {project_name}", styles['title']))
        story.append(Paragraph("Documentación Técnica · AutoDocs AI · " +
                                datetime.utcnow().strftime('%d/%m/%Y'), styles['sub']))

        # Stats table
        row1 = [str(self.results.get('total_files', 0)),
                str(len(self.results.get('functions', []))),
                str(len(self.results.get('classes', []))),
                str(len(self.results.get('endpoints', [])))]
        row2 = ['Archivos', 'Funciones', 'Clases', 'Endpoints']
        t = Table([row1, row2], colWidths=[3.5*cm]*4)
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
            ('FONTSIZE',      (0,0), (-1,0), 18),
            ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
            ('BACKGROUND',    (0,1), (-1,1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR',     (0,1), (-1,1), colors.HexColor('#64748b')),
            ('FONTSIZE',      (0,1), (-1,1), 7),
            ('FONTNAME',      (0,1), (-1,1), 'Helvetica'),
            ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
            ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
            ('BOX',           (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('INNERGRID',     (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING',    (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3*cm))

        score_color = colors.HexColor('#16a34a') if score >= 70 else \
                      colors.HexColor('#ca8a04') if score >= 40 else colors.HexColor('#dc2626')
        score_style = S('Sc', 'Normal', fontSize=10, textColor=score_color,
                        alignment=TA_CENTER, spaceBefore=4, spaceAfter=10)
        story.append(Paragraph(f"Score de Calidad: {score}/100", score_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
        story.append(Spacer(1, 0.4*cm))

        # Parse markdown → ReportLab elements
        in_code = False
        code_buf = []

        def flush_code():
            if code_buf:
                txt = '\n'.join(code_buf).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                # Agregar borde y mejor formato para bloques de código
                from reportlab.platypus import Table, TableStyle
                code_text = txt.replace('\n', '<br/>').replace(' ', '&nbsp;')
                code_para = Paragraph(code_text, styles['code'])
                story.append(code_para)
                story.append(Spacer(1, 0.3*cm))
                code_buf.clear()

        def safe_para(text, style):
            """Escape XML-unsafe chars and apply inline bold/code."""
            text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'\*(.+?)\*',     r'<i>\1</i>', text)
            text = re.sub(r'`([^`]+)`',
                          r'<font name="Courier" color="#0369a1" size="8">\1</font>', text)
            # Manejar ubicación del código
            if text.strip().startswith('**Ubicación:**'):
                text = text.replace('**Ubicación:**', '<b>Ubicación:</b>')
                style = styles['location']
            if text.strip().startswith('**Ejemplo de código:**'):
                text = text.replace('**Ejemplo de código:**', '<b>Ejemplo de código:</b>')
            if text.strip():
                try:
                    story.append(Paragraph(text, style))
                except Exception:
                    story.append(Paragraph(re.sub(r'<[^>]+>', '', text), style))

        for line in md.split('\n'):
            if line.strip().startswith('```'):
                if in_code:
                    flush_code()
                    in_code = False
                else:
                    in_code = True
                continue
            if in_code:
                code_buf.append(line)
                continue
            if line.strip() == '---':
                story.append(HRFlowable(width="100%", thickness=0.5,
                                        color=colors.HexColor('#e2e8f0')))
                story.append(Spacer(1, 0.2*cm))
            elif line.startswith('#### '):
                safe_para(line[5:], styles['h4'])
            elif line.startswith('### '):
                safe_para(line[4:], styles['h3'])
            elif line.startswith('## '):
                safe_para(line[3:], styles['h2'])
            elif line.startswith('# '):
                safe_para(line[2:], styles['h1'])
            elif line.startswith('> '):
                safe_para(line[2:], styles['quote'])
            elif line.startswith(('- ', '* ')):
                safe_para('• ' + line[2:], styles['body'])
            elif line.strip() == '':
                story.append(Spacer(1, 0.15*cm))
            else:
                safe_para(line, styles['body'])

        if in_code:
            flush_code()

        story.append(Spacer(1, 1*cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0')))
        story.append(Paragraph("Generado automáticamente por AutoDocs AI", styles['sub']))

        doc.build(story)
        return output_path