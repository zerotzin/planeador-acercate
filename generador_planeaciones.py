import os
import re
import json
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generar_pdf_planeacion(datos, archivo_salida="planeacion_acercate.pdf", cache_dir=None):
    """
    Genera la planeación en formato horizontal (Landscape) de Centro Comunitario Acércate:
    - Encabezado institucional: CENTRO COMUNITARIO ACÉRCATE, Planeación, Grado, Fase, Campo formativo, Materia
    - 6 Columnas: PDA | Secuencia didáctica | T (min) | Materiales | Productos | Evaluación formativa
    - Compatible con cualquier materia, grados (Preescolar, Primaria, Secundaria) y número de sesiones
    """
    if cache_dir is None:
        cache_dir = os.path.join(os.path.dirname(archivo_salida), "capturas_cache")
    os.makedirs(cache_dir, exist_ok=True)

    # Carta horizontal: 792 x 612 pt
    doc = SimpleDocTemplate(
        archivo_salida,
        pagesize=landscape(letter),
        leftMargin=34,
        rightMargin=34,
        topMargin=26,
        bottomMargin=26
    )

    styles = getSampleStyleSheet()

    style_school_title = ParagraphStyle(
        'SchoolTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=14,
        alignment=TA_CENTER
    )

    style_meta_header = ParagraphStyle(
        'MetaHeader',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12
    )

    style_th = ParagraphStyle(
        'TableHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        alignment=TA_CENTER
    )

    style_body = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=8.8
    )

    style_time = ParagraphStyle(
        'TableTime',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9,
        alignment=TA_CENTER
    )

    story = []

    # Ancho total disponible en horizontal: 792 - 68 = 724 pt
    col_widths = [110, 274, 48, 76, 96, 120]

    nombre_centro = datos.get("nombre_centro", "CENTRO COMUNITARIO ACÉRCATE")
    fecha_periodo = datos.get("fecha_periodo", "Periodo Quincenal")
    campo_formativo = datos.get("campo_formativo", "Saberes y pensamiento científico")
    materia = datos.get("materia", "Computación")
    maestro = datos.get("maestro", "Demart Flores Ornelas")
    duracion = datos.get("duracion_sesion", "50")
    grados_data = datos.get("grados", [])

    for grade_idx, grade_info in enumerate(grados_data):
        grado_label = grade_info.get("grado_label", None)
        grado_num = grade_info.get("grado", grade_idx + 1)
        fase_num = grade_info.get("fase", 3 if grado_num <= 2 else (4 if grado_num <= 4 else 5))
        
        if not grado_label:
            nombres_grados = {1: "Primero", 2: "Segundo", 3: "Tercero", 4: "Cuarto", 5: "Quinto", 6: "Sexto"}
            nivel = grade_info.get("nivel", "Primaria")
            grado_str = nombres_grados.get(grado_num, f"{grado_num}º")
            grado_label = f"{grado_str} de {nivel}"

        semanas = grade_info.get("semanas", [{}])
        total_sesiones = len(semanas)

        for s_idx, sem in enumerate(semanas):
            pda_text = sem.get("pda", "")
            secuencia_text = sem.get("secuencia", "").replace("\n", "<br/>")
            tiempos_text = sem.get("tiempos", "5 min<br/><br/>10 min<br/><br/>25 min<br/><br/>10 min").replace("\n", "<br/>")
            materiales_text = sem.get("materiales", sem.get("material", "Computadora, software correspondiente e internet")).replace("\n", "<br/>")
            productos_text = sem.get("productos", "").replace("\n", "<br/>")
            evaluacion_text = sem.get("evaluacion", "").replace("\n", "<br/>")

            # 1. Encabezado institucional de Centro Comunitario Acércate
            story.append(Paragraph(f"<b>{nombre_centro}</b>", style_school_title))
            story.append(Spacer(1, 4))

            meta_data = [
                [
                    Paragraph(f"Planeación del {fecha_periodo}.", style_meta_header),
                    Paragraph(f"Maestro(a): &nbsp;<u>&nbsp;{maestro}&nbsp;</u>", ParagraphStyle('TeachR', parent=style_meta_header, alignment=TA_RIGHT))
                ],
                [
                    Paragraph(f"Grado: &nbsp;<u>&nbsp;{grado_label}&nbsp;</u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Fase: &nbsp;<u>&nbsp;Fase {fase_num}&nbsp;</u>", style_meta_header),
                    Paragraph(f"Materia: &nbsp;<u>&nbsp;{materia}&nbsp;</u>", ParagraphStyle('SubjR', parent=style_meta_header, alignment=TA_RIGHT))
                ],
                [
                    Paragraph(f"Campo formativo: &nbsp;<u>&nbsp;&nbsp;{campo_formativo}&nbsp;&nbsp;</u>", style_meta_header),
                    Paragraph(f"<b>Sesión {s_idx + 1} de {total_sesiones}</b>", ParagraphStyle('SesR', parent=style_meta_header, alignment=TA_RIGHT))
                ]
            ]
            t_meta = Table(meta_data, colWidths=[460, 264])
            t_meta.setStyle(TableStyle([
                ('TOPPADDING', (0,0), (-1,-1), 1),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(t_meta)
            story.append(Spacer(1, 6))

            # 2. Tabla Principal de 6 columnas
            table_data = [
                # Encabezados
                [
                    Paragraph("<b>PDA</b>", style_th),
                    Paragraph("<b>Secuencia didáctica</b>", style_th),
                    Paragraph(f"<b>T<br/>({duracion} min)</b>", style_th),
                    Paragraph("<b>Materiales</b>", style_th),
                    Paragraph("<b>Productos</b>", style_th),
                    Paragraph("<b>Evaluación formativa</b>", style_th)
                ],
                # Contenido
                [
                    Paragraph(pda_text, style_body),
                    Paragraph(secuencia_text, style_body),
                    Paragraph(tiempos_text, style_time),
                    Paragraph(materiales_text, style_body),
                    Paragraph(productos_text, style_body),
                    Paragraph(evaluacion_text, style_body)
                ]
            ]

            t_main = Table(table_data, colWidths=col_widths)
            t_main.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 0.75, colors.black),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f0f0f0")),
                ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
                ('VALIGN', (0,1), (-1,1), 'TOP'),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('LEFTPADDING', (0,0), (-1,-1), 4),
                ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(t_main)

            # Salto de página entre sesiones
            if not (grade_idx == len(grados_data) - 1 and s_idx == len(semanas) - 1):
                story.append(PageBreak())

    doc.build(story)
    print(f"[OK] Archivo PDF generado exitosamente en: {os.path.abspath(archivo_salida)}")

if __name__ == "__main__":
    import sys
    ruta_json = sys.argv[1] if len(sys.argv) > 1 else "datos_planeacion_sep.json"
    ruta_pdf = sys.argv[2] if len(sys.argv) > 2 else "planeacion_acercate.pdf"

    if os.path.exists(ruta_json):
        with open(ruta_json, "r", encoding="utf-8") as f:
            datos = json.load(f)
        generar_pdf_planeacion(datos, ruta_pdf)
    else:
        print(f"No se encontro {ruta_json}")
