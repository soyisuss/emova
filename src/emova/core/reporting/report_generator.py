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
    elements.append(Paragraph("Reporte de Prueba de Usabilidad EMOVA", title_style))
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
    
    # Placeholder for Emotions & Survey
    elements.append(Paragraph("Emociones (Próximamente)", subtitle_style))
    elements.append(Paragraph("Aún no hay datos emocionales recopilados.", normal_style))
    
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Resultados de la Encuesta (Próximamente)", subtitle_style))
    elements.append(Paragraph("Aún no hay resultados de encuestas.", normal_style))
        
    # Build PDF
    doc.build(elements)
    print(f"PDF Report generated successfully at: {filepath}")
    return filepath
