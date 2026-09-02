import os
import json
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas para numeración de páginas automática en la esquina inferior derecha"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        page_text = f"{self._pageNumber}"
        self.drawRightString(792 - 34, 18, page_text)
        self.restoreState()

def generar_pdf_plano_didactico(datos, archivo_salida="plano_didactico.pdf"):
    """
    Genera el documento oficial 'PLANO DIDÁCTICO' para Primaria General (NEM SEP 2022)
    siguiendo la plantilla institucional de Centro Comunitario Acércate.
    """
    # Dimensiones carta horizontal: 792 x 612 pt (márgenes 34 pt) -> ancho imprimible: 724 pt
    doc = SimpleDocTemplate(
        archivo_salida,
        pagesize=landscape(letter),
        leftMargin=34,
        rightMargin=34,
        topMargin=22,
        bottomMargin=24
    )

    styles = getSampleStyleSheet()

    style_school_center = ParagraphStyle(
        'SchoolCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=11.5,
        alignment=TA_CENTER
    )

    style_bold_center = ParagraphStyle(
        'BoldCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=11.5,
        alignment=TA_CENTER
    )

    style_meta_list = ParagraphStyle(
        'MetaList',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5
    )

    style_box_cell = ParagraphStyle(
        'BoxCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=8.8
    )

    style_box_cell_center = ParagraphStyle(
        'BoxCellCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=8.8,
        alignment=TA_CENTER
    )

    style_th = ParagraphStyle(
        'TableHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9,
        alignment=TA_CENTER
    )

    style_th_mod = ParagraphStyle(
        'TableHeadMod',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=6.5,
        leading=8,
        alignment=TA_CENTER
    )

    style_body = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.8,
        leading=8.2
    )

    style_center = ParagraphStyle(
        'CenterCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.8,
        leading=8.2,
        alignment=TA_CENTER
    )

    style_eval = ParagraphStyle(
        'EvalBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.8,
        leading=8.2
    )

    style_firmas_title = ParagraphStyle(
        'FirmaTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        alignment=TA_CENTER
    )

    style_firmas_name = ParagraphStyle(
        'FirmaName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        alignment=TA_CENTER
    )

    story = []

    # Datos generales
    nombre_centro = datos.get("nombre_centro", "CENTRO COMUNITARIO ACÉRCATE")
    ciclo_escolar = datos.get("ciclo_escolar", "2025-2026")
    grado_str = datos.get("grado_str", "SEXTO GRADO")
    fecha_entrega = datos.get("fecha_entrega", "05/junio/2026")
    periodo_abarca = datos.get("periodo_abarca", "Del 08 al 19 de junio")
    fase_grado = datos.get("fase_grado", "5/ 6°")
    problematica = datos.get("problematica", "¿Por qué cambian los materiales y cómo podemos cuidar nuestra salud y el ambiente?")
    campos_formativos = datos.get("campos_formativos", ["Pensamiento Científico", "De lo humano y lo comunitario"])
    contenidos = datos.get("contenidos", ["Cambios permanentes en los materiales y sus implicaciones en la vida diaria."])
    ejes_articuladores = datos.get("ejes_articuladores", ["Pensamiento crítico", "vida saludable", "inclusión", "interculturalidad"])
    perfil_egreso = datos.get("perfil_egreso", "")
    maestro = datos.get("maestro", "Demart Flores Ornelas")
    reviso_nombre = datos.get("reviso", "Mayra Sánchez")
    vobo_nombre = datos.get("vobo", "Supervisión escolar")

    # 1. ENCABEZADO SUPERIOR CENTRADO
    story.append(Paragraph(nombre_centro, style_school_center))
    story.append(Paragraph(ciclo_escolar, style_school_center))
    story.append(Paragraph(grado_str.upper(), style_bold_center))
    story.append(Paragraph("PLANO DIDÁCTICO", style_bold_center))
    story.append(Spacer(1, 3))

    # 2. METADATOS EN FORMA DE LISTA VERTICAL (Izquierda)
    meta_list_text = f"""Fecha de entrega: {fecha_entrega}<br/>Periodo que abarca: {periodo_abarca}<br/>Fase/ grado: {fase_grado}"""
    story.append(Paragraph(meta_list_text, style_meta_list))
    story.append(Spacer(1, 4))

    # 3. TABLA DE DATOS INICIALES (Exacta a la imagen institucional)
    # Preparar campos y contenidos en columnas
    if isinstance(campos_formativos, str):
        campos_list = [c.strip() for c in campos_formativos.split(",") if c.strip()]
    else:
        campos_list = list(campos_formativos)

    if isinstance(contenidos, str):
        contenidos_list = [c.strip() for c in contenidos.split("\n") if c.strip()]
    else:
        contenidos_list = list(contenidos)

    # Si hay 2 campos (lo estándar):
    # Col 0 (Encabezado lateral): 154 pt
    # Col 1 (Campo 1): 285 pt
    # Col 2 (Campo 2): 285 pt
    # Total: 154 + 285 + 285 = 724 pt
    c1_nombre = campos_list[0] if len(campos_list) > 0 else "Pensamiento Científico"
    c2_nombre = campos_list[1] if len(campos_list) > 1 else ""

    c1_cont = contenidos_list[0] if len(contenidos_list) > 0 else ""
    c2_cont = contenidos_list[1] if len(contenidos_list) > 1 else ""

    ejes_txt = ", ".join(ejes_articuladores) if isinstance(ejes_articuladores, list) else str(ejes_articuladores)
    perfil_txt = f" {perfil_egreso}" if perfil_egreso else ""

    if c2_nombre:
        # Estructura de 3 columnas
        t_box_widths = [154, 285, 285]
        box_table_data = [
            # Fila 0: Problemática (abarca las 3 columnas)
            [
                Paragraph(f"Problemática/ situación detonadora: {problematica}", style_box_cell),
                "", ""
            ],
            # Fila 1: Campo(s) Formativo (s)
            [
                Paragraph("Campo(s) Formativo (s)", style_box_cell),
                Paragraph(c1_nombre, style_box_cell_center),
                Paragraph(c2_nombre, style_box_cell_center)
            ],
            # Fila 2: Contenido
            [
                Paragraph("Contenido:", style_box_cell),
                Paragraph(c1_cont, style_box_cell),
                Paragraph(c2_cont, style_box_cell)
            ],
            # Fila 3: Ejes articuladores
            [
                Paragraph(f"Ejes articuladores: {ejes_txt}", style_box_cell),
                "", ""
            ],
            # Fila 4: Perfil de egreso
            [
                Paragraph(f"¿Qué rasgos del perfil de Egreso se favorecen?{perfil_txt}", style_box_cell),
                "", ""
            ]
        ]
        box_table_style = TableStyle([
            ('SPAN', (0,0), (2,0)), # Problemática abarca todo
            ('SPAN', (0,3), (2,3)), # Ejes abarca todo
            ('SPAN', (0,4), (2,4)), # Perfil abarca todo
            ('BOX', (0,0), (-1,-1), 0.75, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 2.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
            ('LEFTPADDING', (0,0), (-1,-1), 3),
            ('RIGHTPADDING', (0,0), (-1,-1), 3),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white]),
        ])
    else:
        # Estructura de 2 columnas si solo hay 1 campo formativo
        t_box_widths = [154, 570]
        box_table_data = [
            [Paragraph(f"Problemática/ situación detonadora: {problematica}", style_box_cell), ""],
            [Paragraph("Campo(s) Formativo (s)", style_box_cell), Paragraph(c1_nombre, style_box_cell_center)],
            [Paragraph("Contenido:", style_box_cell), Paragraph(c1_cont, style_box_cell)],
            [Paragraph(f"Ejes articuladores: {ejes_txt}", style_box_cell), ""],
            [Paragraph(f"¿Qué rasgos del perfil de Egreso se favorecen?{perfil_txt}", style_box_cell), ""]
        ]
        box_table_style = TableStyle([
            ('SPAN', (0,0), (1,0)),
            ('SPAN', (0,3), (1,3)),
            ('SPAN', (0,4), (1,4)),
            ('BOX', (0,0), (-1,-1), 0.75, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 2.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
            ('LEFTPADDING', (0,0), (-1,-1), 3),
            ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ])

    t_box = Table(box_table_data, colWidths=t_box_widths)
    t_box.setStyle(box_table_style)
    story.append(t_box)
    story.append(Spacer(1, 4))

    # 4. TABLA PRINCIPAL DE SESIONES Y ACTIVIDADES
    # Ancho total: 724 pt
    # Col 0 (PDA): 116 pt
    # Col 1 (Secuencia Didáctica): 262 pt
    # Col 2 (Tiempo): 42 pt
    # Col 3 (Modalidad): 42 pt (Ajustada para que no corte la palabra Modalidad)
    # Col 4 (Producto): 96 pt
    # Col 5 (Evaluación/Indicadores): 166 pt
    col_widths_main = [116, 262, 42, 42, 96, 166]

    filas_tabla = [
        # Encabezado
        [
            Paragraph("<b>PDA</b>", style_th),
            Paragraph("<b>Secuencia Didáctica</b>", style_th),
            Paragraph("<b>Tiempo</b>", style_th),
            Paragraph("<b>Modalidad</b>", style_th_mod),
            Paragraph("<b>Producto</b>", style_th),
            Paragraph("<b>Evaluación/Indicadores</b>", style_th)
        ]
    ]

    bloques_actividades = datos.get("bloques", [])

    for b in bloques_actividades:
        pda_b = b.get("pda", "").replace("\n", "<br/>")
        sec_b = b.get("secuencia", "").replace("\n", "<br/>")
        t_b = b.get("tiempo", "10min").replace("\n", "<br/>")
        mod_b = b.get("modalidad", "G").replace("\n", "<br/>")
        prod_b = b.get("producto", "").replace("\n", "<br/>")
        eval_b = b.get("evaluacion", "").replace("\n", "<br/>")

        filas_tabla.append([
            Paragraph(pda_b, style_body),
            Paragraph(sec_b, style_body),
            Paragraph(t_b, style_center),
            Paragraph(mod_b, style_center),
            Paragraph(prod_b, style_body),
            Paragraph(eval_b, style_eval)
        ])

    t_main = Table(filas_tabla, colWidths=col_widths_main, repeatRows=1)
    t_main.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
        ('VALIGN', (0,1), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_main)
    story.append(Spacer(1, 14))

    # 5. PIE DE FIRMAS (Al final del documento)
    firmas_data = [
        [
            Paragraph("Elaboro", style_firmas_title),
            Paragraph("Reviso", style_firmas_title),
            Paragraph("VoBo", style_firmas_title)
        ],
        [
            Paragraph(f"{maestro}", style_firmas_name),
            Paragraph(f"{reviso_nombre}", style_firmas_name),
            Paragraph(f"{vobo_nombre}", style_firmas_name)
        ]
    ]
    t_firmas = Table(firmas_data, colWidths=[240, 244, 240])
    t_firmas.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (0,0), 0.75, colors.black),
        ('LINEABOVE', (1,0), (1,0), 0.75, colors.black),
        ('LINEABOVE', (2,0), (2,0), 0.75, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(KeepTogether([t_firmas]))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Archivo Plano Didáctico generado exitosamente en: {os.path.abspath(archivo_salida)}")

if __name__ == "__main__":
    import sys
    ruta_json = sys.argv[1] if len(sys.argv) > 1 else "datos_plano_ejemplo.json"
    ruta_pdf = sys.argv[2] if len(sys.argv) > 2 else "plano_didactico.pdf"

    if os.path.exists(ruta_json):
        with open(ruta_json, "r", encoding="utf-8") as f:
            datos = json.load(f)
        generar_pdf_plano_didactico(datos, ruta_pdf)
    else:
        print(f"No se encontro {ruta_json}")
