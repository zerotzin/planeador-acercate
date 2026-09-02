import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generar_pdf_rubricas(datos, archivo_salida="rubricas_quincenal.pdf"):
    """
    Genera el PDF de rúbricas con el formato exacto de Centro Comunitario Acércate:
    - Encabezado: [CENTRO COMUNITARIO ACÉRCATE] / RÚBRICA
    - Maestro (a): [Nombre] | Materia: [Materia]
    - Columnas: CRITERIO A EVALUAR | EXCELENTE (4) | BUENO (3) | EN PROCESO (2) | REQUIERE APOYO (1) | PUNTAJE
    """
    doc = SimpleDocTemplate(
        archivo_salida,
        pagesize=letter,
        leftMargin=34,
        rightMargin=34,
        topMargin=26,
        bottomMargin=26
    )

    styles = getSampleStyleSheet()

    style_school = ParagraphStyle(
        'SchoolTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        alignment=TA_CENTER
    )

    style_rubrica_title = ParagraphStyle(
        'RubricaTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=13,
        alignment=TA_CENTER
    )

    style_teacher_subject = ParagraphStyle(
        'TeacherSubject',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12
    )

    style_week_sub = ParagraphStyle(
        'WeekSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1b365d")
    )

    style_th = ParagraphStyle(
        'TableHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        alignment=TA_CENTER
    )

    style_th_num = ParagraphStyle(
        'TableHeadNum',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        alignment=TA_CENTER
    )

    style_crit = ParagraphStyle(
        'CritText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=8.5
    )

    style_desc = ParagraphStyle(
        'DescText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.5,
        leading=8,
        alignment=TA_LEFT
    )

    style_center = ParagraphStyle(
        'CenterText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9,
        alignment=TA_CENTER
    )

    style_total_lbl = ParagraphStyle(
        'TotalLbl',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        alignment=TA_RIGHT
    )

    story = []
    # Ancho disponible: 8.5*72 - 68 = 544 pt
    col_widths = [134, 85, 85, 85, 85, 50]

    nombre_centro = datos.get("nombre_centro", "CENTRO COMUNITARIO ACÉRCATE")
    fecha_periodo = datos.get("fecha_periodo", "Periodo Quincenal")
    materia = datos.get("materia", "Computación")
    maestro = datos.get("maestro", "Demart Flores Ornelas")
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

        # 1. Encabezado principal del Centro
        story.append(Paragraph(f"<b>{nombre_centro}</b>", style_school))
        story.append(Spacer(1, 2))
        story.append(Paragraph("<b>RÙBRICA DE EVALUACIÓN</b>", style_rubrica_title))
        story.append(Spacer(1, 6))

        # 2. Datos del Maestro, Materia, Grado y Periodo
        teacher_table_data = [
            [
                Paragraph(f"<b>Maestro (a):</b> {maestro}", style_teacher_subject),
                Paragraph(f"<b>Materia:</b> {materia}", ParagraphStyle('SubjRight', parent=style_teacher_subject, alignment=TA_RIGHT))
            ],
            [
                Paragraph(f"<b>Grado:</b> {grado_label}&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;<b>Fase:</b> Fase {fase_num}", style_teacher_subject),
                Paragraph(f"<b>Periodo:</b> {fecha_periodo}", ParagraphStyle('PerRight', parent=style_teacher_subject, alignment=TA_RIGHT))
            ]
        ]
        t_prof = Table(teacher_table_data, colWidths=[314, 210])
        t_prof.setStyle(TableStyle([
            ('LINEBELOW', (0,1), (-1,1), 1, colors.black),
            ('TOPPADDING', (0,0), (-1,-1), 1),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(t_prof)
        story.append(Spacer(1, 6))

        # 3. Tablas de rúbricas por sesión
        semanas = grade_info.get("semanas", [{}])
        for s_idx, sem in enumerate(semanas):
            pda_text = sem.get("pda", "")
            productos_text = sem.get("productos", "")
            eval_desc = sem.get("evaluacion", "")
            rubrica_items = sem.get("rubrica_niveles", None)

            # Rótulo de la sesión
            story.append(Paragraph(f"<b>SESIÓN {s_idx + 1} — PDA:</b> <font color='#333333'>{pda_text}</font>", style_week_sub))
            story.append(Paragraph(f"<b>Producto evaluable:</b> <font color='#333333'>{productos_text}</font>", style_desc))
            story.append(Spacer(1, 3))

            if not rubrica_items or not isinstance(rubrica_items, list):
                rubrica_items = [
                    {
                        "num": "1.-",
                        "criterio": "Logro del PDA y dominio técnico / conceptual",
                        "excelente": f"Demuestra con autonomía y precisión: {eval_desc}",
                        "bueno": "Cumple con el desempeño esperado requiriendo mínima orientación del docente.",
                        "en_proceso": "Muestra dificultad parcial para ejecutar la habilidad o responder a los retos de la sesión.",
                        "requiere_apoyo": "No logra realizar la actividad ni demostrar el aprendizaje aún con apoyo constante docente."
                    },
                    {
                        "num": "2.-",
                        "criterio": "Elaboración y calidad del producto o ejercicio",
                        "excelente": f"Entrega completa y correctamente: {productos_text}",
                        "bueno": "Entrega el producto/ejercicio con la mayoría de los requerimientos solicitados.",
                        "en_proceso": "Entrega el producto incompleto o con errores en el procedimiento.",
                        "requiere_apoyo": "No concluye ni presenta el producto o evidencia de la sesión."
                    },
                    {
                        "num": "3.-",
                        "criterio": "Seguimiento de normas, participación y cuidado de materiales",
                        "excelente": "Sigue las indicaciones paso a paso, participa reflexivamente y cuida los materiales del aula.",
                        "bueno": "Respeta las normas del espacio y sigue las indicaciones en su mayoría.",
                        "en_proceso": "Requiere constantes recordatorios para seguir instrucciones y colaborar de forma pacífica.",
                        "requiere_apoyo": "No respeta las normas de convivencia ni el cuidado de las instalaciones y materiales."
                    }
                ]

            table_data = [
                # Fila 0: Títulos
                [
                    Paragraph("<b>CRITERIO A EVALUAR</b>", style_th),
                    Paragraph("<b>EXCELENTE</b>", style_th),
                    Paragraph("<b>BUENO</b>", style_th),
                    Paragraph("<b>EN PROCESO</b>", style_th),
                    Paragraph("<b>REQUIERE APOYO</b>", style_th),
                    Paragraph("<b>PUNTAJE</b>", style_th)
                ],
                # Fila 1: Ponderación numérica (4, 3, 2, 1)
                [
                    "",
                    Paragraph("<b>4</b>", style_th_num),
                    Paragraph("<b>3</b>", style_th_num),
                    Paragraph("<b>2</b>", style_th_num),
                    Paragraph("<b>1</b>", style_th_num),
                    ""
                ]
            ]

            for item in rubrica_items:
                num = item.get("num", "")
                crit = item.get("criterio", "")
                c_lbl = f"<b>{num}</b> {crit}" if num else crit

                table_data.append([
                    Paragraph(c_lbl, style_crit),
                    Paragraph(item.get("excelente", ""), style_desc),
                    Paragraph(item.get("bueno", ""), style_desc),
                    Paragraph(item.get("en_proceso", ""), style_desc),
                    Paragraph(item.get("requiere_apoyo", ""), style_desc),
                    Paragraph("[ &nbsp; ]", style_center)
                ])

            table_data.append([
                Paragraph("<b>PUNTAJE TOTAL:</b>", style_total_lbl),
                "", "", "", "",
                Paragraph("<b>/ 12</b>", style_center)
            ])

            t_rub = Table(table_data, colWidths=col_widths)
            t_rub.setStyle(TableStyle([
                ('SPAN', (0,0), (0,1)),
                ('SPAN', (5,0), (5,1)),
                ('BOX', (0,0), (-1,-1), 0.75, colors.black),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
                ('VALIGN', (0,0), (-1,1), 'MIDDLE'),
                ('VALIGN', (0,2), (-1,-1), 'TOP'),
                ('VALIGN', (5,2), (5,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('LEFTPADDING', (0,0), (-1,-1), 3),
                ('RIGHTPADDING', (0,0), (-1,-1), 3),
                ('BACKGROUND', (0,0), (-1,1), colors.HexColor("#f0f0f0")),
                ('SPAN', (0,-1), (4,-1)),
                ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#f9f9f9")),
            ]))
            story.append(t_rub)

            if s_idx < len(semanas) - 1:
                story.append(Spacer(1, 10))

        if grade_idx < len(grados_data) - 1:
            story.append(PageBreak())

    doc.build(story)
    print(f"[OK] Archivo de Rúbricas generado exitosamente en: {os.path.abspath(archivo_salida)}")

if __name__ == "__main__":
    import sys
    ruta_json = sys.argv[1] if len(sys.argv) > 1 else "datos_planeacion_sep.json"
    ruta_rub = sys.argv[2] if len(sys.argv) > 2 else "rubricas_quincenal.pdf"

    if os.path.exists(ruta_json):
        with open(ruta_json, "r", encoding="utf-8") as f:
            datos = json.load(f)
        generar_pdf_rubricas(datos, ruta_rub)
    else:
        print(f"No se encontro {ruta_json}")
