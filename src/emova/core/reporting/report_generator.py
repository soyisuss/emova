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
        # Agrupar emociones por tarea
        task_emotions = {}
        for e in emotions:
            task_name = str(e.get("task", "-"))
            if task_name not in task_emotions:
                task_emotions[task_name] = []
            task_emotions[task_name].append(e)

        # Encabezados de la Tabla (sin Hora)
        data = [["Intervalo / Tarea", "Emoción Predominante", "Confianza Promedio"]]
        
        for task, items in task_emotions.items():
            emotion_counts = {}
            total_conf = 0.0
            valid_conf_count = 0
            
            for item in items:
                emo = str(item.get("emotion", "-"))
                emotion_counts[emo] = emotion_counts.get(emo, 0) + 1
                
                # Parsear confianza (removiendo % si existe)
                conf_str = str(item.get("confidence", "0")).replace('%', '').strip()
                try:
                    total_conf += float(conf_str)
                    valid_conf_count += 1
                except ValueError:
                    pass
                    
            predominant_emo = max(emotion_counts, key=emotion_counts.get) if emotion_counts else "-"
            avg_conf = (total_conf / valid_conf_count) if valid_conf_count > 0 else 0.0
            
            data.append([
                task, 
                predominant_emo, 
                f"{avg_conf:.1f}%"
            ])
            
        # Construir y pintar la tabla de ReportLab
        table = Table(data, colWidths=[200, 130, 130])
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
        # Extraer puntuaciones de tareas y cruzar con emociones si están disponibles
        tasks = session_data.get("tasks", [])
        if tasks:
            elements.append(Spacer(1, 5))
            elements.append(Paragraph("<b>Evaluación por Tarea y Análisis Emocional:</b>", styles['Heading3']))
            
            # Recalcular emociones predominantes para el análisis
            predominant_emotions = {}
            if emotions:
                for e in emotions:
                    t_name = str(e.get("task", "-"))
                    if t_name not in predominant_emotions:
                        predominant_emotions[t_name] = {}
                    emo = str(e.get("emotion", "-"))
                    predominant_emotions[t_name][emo] = predominant_emotions[t_name].get(emo, 0) + 1
            
            for idx, task in enumerate(tasks):
                task_title = task.get("title", f"Tarea {idx + 1}")
                task_score = survey.get(f"task_{idx}_ease")
                
                if task_score is not None:
                    # Buscar emoción predominante de esta tarea
                    pred_emo = "-"
                    if task_title in predominant_emotions and predominant_emotions[task_title]:
                        pred_emo = max(predominant_emotions[task_title], key=predominant_emotions[task_title].get)
                    
                    # Generar pequeño análisis
                    analysis = ""
                    if pred_emo != "-":
                        negative_emotions = ["Angry", "Disgust", "Fear", "Sad"]
                        positive_emotions = ["Happy", "Surprise"]
                        
                        is_negative = pred_emo in negative_emotions
                        is_positive = pred_emo in positive_emotions
                        
                        try:
                            score_val = int(task_score)
                            if score_val <= 2 and is_negative:
                                analysis = f"El usuario reportó alta dificultad y predominó la emoción negativa '{pred_emo}'. Esto sugiere frustración o confusión real."
                            elif score_val >= 4 and is_positive:
                                analysis = f"El usuario reportó facilidad y predominó una emoción positiva '{pred_emo}', lo cual es congruente con una buena usabilidad."
                            elif score_val >= 4 and is_negative:
                                analysis = f"A pesar de calificar la tarea como fácil, predominaron emociones negativas '{pred_emo}', lo que podría indicar un esfuerzo cognitivo no reportado."
                            elif score_val <= 2 and is_positive:
                                analysis = f"Curiosamente, el usuario reportó dificultad pero exhibió emociones positivas '{pred_emo}'. Podría indicar una tarea desafiante pero entretenida."
                            else:
                                analysis = f"La calificación fue de {score_val}/5 con una emoción predominante de '{pred_emo}'."
                        except ValueError:
                            analysis = f"Emoción predominante: '{pred_emo}'."
                    else:
                        analysis = "No se detectaron emociones suficientes durante esta tarea para realizar un análisis."

                    elements.append(Paragraph(f"• <b>{task_title}:</b> Calificación {task_score} / 5", normal_style))
                    elements.append(Paragraph(f"<i>Análisis:</i> {analysis}", normal_style))
                    elements.append(Spacer(1, 5))
            elements.append(Spacer(1, 10))

        elements.append(Paragraph("<b>Evaluación General:</b>", styles['Heading3']))
        questions = {
            "ease_of_use": "Facilidad de Uso Global",
            "navigation": "Navegación Intuitiva",
            "difficulty": "Facilidad para Completar Tareas",
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
