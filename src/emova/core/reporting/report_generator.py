import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(session_data, filepath="outputs/reports/report_emova.pdf"):
    """
    Generates a PDF report using the centralized session data.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    
    subtitle_style = styles['Heading2']
    subtitle_style.textColor = colors.HexColor("#7E38B7")
    
    normal_style = styles['Normal']
    
    elements = []
    
    # Document Title
    test_id = session_data.get("test_id", "NO_ID")
    elements.append(Paragraph(f"Reporte EMOVA - Prueba #{test_id}", title_style))
    elements.append(Spacer(1, 20))
    
    # Participant Section
    elements.append(Paragraph("Datos del Participante", subtitle_style))
    participant = session_data.get("participant", {})
    if participant:
        for key, value in participant.items():
            elements.append(Paragraph(f"<b>{key}:</b> {value}", normal_style))
    else:
        elements.append(Paragraph("No se registraron datos del participante.", normal_style))
        
    elements.append(Spacer(1, 20))
    
    # Tasks Section
    elements.append(Paragraph("Tareas Registradas", subtitle_style))
    tasks = session_data.get("tasks", [])
    if tasks:
        for i, task in enumerate(tasks, 1):
            title = task.get("title", "Sin título")
            desc = task.get("description", "Sin descripción")
            duration = task.get("duration_seconds", None)
            
            elements.append(Paragraph(f"<b>Tarea {i}:</b> {title}", styles['Heading3']))
            elements.append(Paragraph(desc, normal_style))
            
            if duration is not None:
                elements.append(Paragraph(f"<b>Tiempo de completitud:</b> {duration} segundos.", normal_style))
                
            elements.append(Spacer(1, 10))
    else:
        elements.append(Paragraph("No se registraron tareas.", normal_style))
        
    elements.append(Spacer(1, 20))
    
    # Seccion de Emociones Detectadas
    elements.append(Paragraph("Registro de Emociones Detectadas (IA)", subtitle_style))
    emotions = session_data.get("emotions", [])
    if emotions:
        elements.append(Spacer(1, 10))
        # Encabezados de la Tabla
        data = [["Intervalo / Tarea", "Hora", "Emoción", "Confianza"]]
        
        for e in emotions:
            data.append([
                str(e.get("task", "-")), 
                str(e.get("timestamp", "-")), 
                str(e.get("emotion", "-")), 
                str(e.get("confidence", "-"))
            ])
            
        # Construir y pintar la tabla de ReportLab
        table = Table(data, colWidths=[180, 80, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#7E38B7")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f3e5f5")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No detectamos rostros durante la prueba, o no se vinculó la red neuronal.", normal_style))
    
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Resultados de Encuesta de Usabilidad", subtitle_style))
    survey = session_data.get("survey", {})
    if survey:
        questions = {
            "ease_of_use": "Facilidad de Uso Global",
            "navigation": "Navegación Intuitiva",
            "clarity": "Claridad de Instrucciones",
            "efficiency": "Eficiencia en Tareas",
            "consistency": "Consistencia de la Interfaz",
            "error_recovery": "Recuperación de Errores",
            "visual_design": "Agrado Visual y Diseño",
            "satisfaction": "Satisfacción General"
        }
        
        for key, text in questions.items():
            val = survey.get(key, "-")
            elements.append(Paragraph(f"<b>{text}:</b> {val} / 5", normal_style))
            
        comments = survey.get("comments", "")
        if comments:
            elements.append(Spacer(1, 8))
            elements.append(Paragraph("<b>Comentarios Adicionales:</b>", normal_style))
            elements.append(Paragraph(comments, normal_style))
    else:
        elements.append(Paragraph("Aún no hay resultados de encuestas.", normal_style))
        
    # Build PDF
    doc.build(elements)
    print(f"PDF Report generated successfully at: {filepath}")
    return filepath
