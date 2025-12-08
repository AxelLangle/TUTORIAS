"""
Módulo de Generación de Reportes en PDF
Proporciona funciones para generar reportes de asesorías y tutorías en formato PDF
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
from io import BytesIO
import os

class PDFReportGenerator:
    """Generador de reportes PDF para asesorías y tutorías"""
    
    def __init__(self):
        self.page_size = letter
        self.margin = 0.5 * inch
        self.width = self.page_size[0] - 2 * self.margin
        self.height = self.page_size[1] - 2 * self.margin
        
    def _create_header(self, story, title, subtitle=""):
        """Crea el encabezado del reporte"""
        styles = getSampleStyleSheet()
        
        # Título principal
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#cc1313'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        story.append(Paragraph(title, title_style))
        story.append(Paragraph("Universidad Politécnica de Tecámac", subtitle_style))
        if subtitle:
            story.append(Paragraph(subtitle, subtitle_style))
        story.append(Spacer(1, 0.2*inch))
        
    def _create_info_table(self, story, info_dict):
        """Crea una tabla de información"""
        data = []
        for key, value in info_dict.items():
            data.append([f"{key}:", str(value)])
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0f7fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
    def _create_data_table(self, story, headers, data, title=""):
        """Crea una tabla de datos"""
        if title:
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'TableTitle',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.HexColor('#cc1313'),
                spaceAfter=8,
                fontName='Helvetica-Bold'
            )
            story.append(Paragraph(title, title_style))
        
        # Preparar datos de la tabla
        table_data = [headers] + data
        
        # Crear tabla
        col_widths = [self.width / len(headers)] * len(headers)
        table = Table(table_data, colWidths=col_widths)
        
        # Estilo de la tabla
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#cc1313')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
    def _create_summary_section(self, story, summary_dict):
        """Crea una sección de resumen"""
        styles = getSampleStyleSheet()
        
        summary_style = ParagraphStyle(
            'SummaryTitle',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#cc1313'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        
        story.append(Paragraph("RESUMEN", summary_style))
        
        for key, value in summary_dict.items():
            text = f"<b>{key}:</b> {value}"
            story.append(Paragraph(text, styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
    def _create_footer(self, story, tutor_name="", date_generated=None):
        """Crea el pie de página del reporte"""
        if date_generated is None:
            date_generated = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        styles = getSampleStyleSheet()
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("_" * 80, footer_style))
        
        if tutor_name:
            story.append(Paragraph(f"Tutor: {tutor_name}", footer_style))
        
        story.append(Paragraph(f"Reporte generado: {date_generated}", footer_style))
        story.append(Paragraph("Universidad Politécnica de Tecámac - Sistema de Asesorías y Tutorías", footer_style))
        
    def generate_student_report(self, student_data, tutorias, filename=None):
        """
        Genera un reporte PDF para un estudiante
        
        Args:
            student_data: Dict con información del estudiante {nombre, apellido_p, apellido_m, matricula, carrera, cuatrimestre}
            tutorias: Lista de tutorías del estudiante
            filename: Nombre del archivo (si es None, retorna BytesIO)
        
        Returns:
            BytesIO o ruta del archivo generado
        """
        if filename is None:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=self.page_size, 
                                   rightMargin=self.margin, leftMargin=self.margin,
                                   topMargin=self.margin, bottomMargin=self.margin)
        else:
            doc = SimpleDocTemplate(filename, pagesize=self.page_size,
                                   rightMargin=self.margin, leftMargin=self.margin,
                                   topMargin=self.margin, bottomMargin=self.margin)
        
        story = []
        
        # Encabezado
        self._create_header(story, "REPORTE DE TUTORÍAS INDIVIDUALES", 
                           f"Estudiante: {student_data.get('nombre', '')} {student_data.get('apellido_p', '')}")
        
        # Información del estudiante
        info_dict = {
            "Nombre Completo": f"{student_data.get('nombre', '')} {student_data.get('apellido_p', '')} {student_data.get('apellido_m', '')}",
            "Matrícula": student_data.get('matricula', 'N/A'),
            "Carrera": student_data.get('carrera', 'N/A'),
            "Cuatrimestre": student_data.get('cuatrimestre', 'N/A'),
        }
        self._create_info_table(story, info_dict)
        
        # Tabla de tutorías
        if tutorias:
            headers = ["Fecha", "Motivo", "Descripción", "Tutor"]
            data = []
            for tut in tutorias:
                data.append([
                    tut.get('fecha', 'N/A'),
                    tut.get('motivo', 'N/A'),
                    tut.get('descripcion', 'N/A')[:50] + "..." if len(tut.get('descripcion', '')) > 50 else tut.get('descripcion', 'N/A'),
                    tut.get('tutor', 'N/A')
                ])
            
            self._create_data_table(story, headers, data, "DETALLE DE TUTORÍAS")
        
        # Resumen
        summary_dict = {
            "Total de Tutorías": len(tutorias),
            "Período": f"{tutorias[0].get('fecha', 'N/A')} a {tutorias[-1].get('fecha', 'N/A')}" if tutorias else "N/A",
            "Motivos Principales": self._get_main_motives(tutorias),
        }
        self._create_summary_section(story, summary_dict)
        
        # Pie de página
        self._create_footer(story, tutor_name=student_data.get('tutor', ''))
        
        # Generar PDF
        doc.build(story)
        
        if filename is None:
            buffer.seek(0)
            return buffer
        return filename
    
    def generate_group_report(self, group_data, tutorias_grupales, filename=None):
        """
        Genera un reporte PDF para un grupo
        
        Args:
            group_data: Dict con información del grupo {grupo_nombre, carrera, cuatrimestre}
            tutorias_grupales: Lista de tutorías grupales
            filename: Nombre del archivo (si es None, retorna BytesIO)
        
        Returns:
            BytesIO o ruta del archivo generado
        """
        if filename is None:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=self.page_size,
                                   rightMargin=self.margin, leftMargin=self.margin,
                                   topMargin=self.margin, bottomMargin=self.margin)
        else:
            doc = SimpleDocTemplate(filename, pagesize=self.page_size,
                                   rightMargin=self.margin, leftMargin=self.margin,
                                   topMargin=self.margin, bottomMargin=self.margin)
        
        story = []
        
        # Encabezado
        self._create_header(story, "REPORTE DE TUTORÍAS GRUPALES",
                           f"Grupo: {group_data.get('grupo_nombre', '')}")
        
        # Información del grupo
        info_dict = {
            "Grupo": group_data.get('grupo_nombre', 'N/A'),
            "Carrera": group_data.get('carrera', 'N/A'),
            "Cuatrimestre": group_data.get('cuatrimestre', 'N/A'),
        }
        self._create_info_table(story, info_dict)
        
        # Tabla de tutorías grupales
        if tutorias_grupales:
            headers = ["Fecha", "Motivo", "Asistentes", "Descripción"]
            data = []
            for tut in tutorias_grupales:
                data.append([
                    tut.get('fecha', 'N/A'),
                    tut.get('motivo', 'N/A'),
                    tut.get('asistentes', 'N/A'),
                    tut.get('descripcion', 'N/A')[:40] + "..." if len(tut.get('descripcion', '')) > 40 else tut.get('descripcion', 'N/A'),
                ])
            
            self._create_data_table(story, headers, data, "DETALLE DE TUTORÍAS GRUPALES")
        
        # Resumen
        summary_dict = {
            "Total de Tutorías Grupales": len(tutorias_grupales),
            "Período": f"{tutorias_grupales[0].get('fecha', 'N/A')} a {tutorias_grupales[-1].get('fecha', 'N/A')}" if tutorias_grupales else "N/A",
            "Motivos Principales": self._get_main_motives(tutorias_grupales),
        }
        self._create_summary_section(story, summary_dict)
        
        # Pie de página
        self._create_footer(story)
        
        # Generar PDF
        doc.build(story)
        
        if filename is None:
            buffer.seek(0)
            return buffer
        return filename
    
    def generate_period_report(self, period_data, tutorias, filename=None):
        """
        Genera un reporte PDF para un período específico
        
        Args:
            period_data: Dict con información del período {start_date, end_date, carrera, cuatrimestre}
            tutorias: Lista de tutorías en el período
            filename: Nombre del archivo (si es None, retorna BytesIO)
        
        Returns:
            BytesIO o ruta del archivo generado
        """
        if filename is None:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=self.page_size,
                                   rightMargin=self.margin, leftMargin=self.margin,
                                   topMargin=self.margin, bottomMargin=self.margin)
        else:
            doc = SimpleDocTemplate(filename, pagesize=self.page_size,
                                   rightMargin=self.margin, leftMargin=self.margin,
                                   topMargin=self.margin, bottomMargin=self.margin)
        
        story = []
        
        # Encabezado
        self._create_header(story, "REPORTE DE TUTORÍAS POR PERÍODO",
                           f"Período: {period_data.get('start_date', '')} a {period_data.get('end_date', '')}")
        
        # Información del período
        info_dict = {
            "Fecha Inicio": period_data.get('start_date', 'N/A'),
            "Fecha Fin": period_data.get('end_date', 'N/A'),
            "Carrera": period_data.get('carrera', 'Todas'),
            "Cuatrimestre": period_data.get('cuatrimestre', 'Todos'),
        }
        self._create_info_table(story, info_dict)
        
        # Tabla de tutorías
        if tutorias:
            headers = ["Fecha", "Estudiante", "Motivo", "Tipo"]
            data = []
            for tut in tutorias:
                estudiante = f"{tut.get('nombre', '')} {tut.get('apellido_p', '')}"
                data.append([
                    tut.get('fecha', 'N/A'),
                    estudiante,
                    tut.get('motivo', 'N/A'),
                    tut.get('tipo', 'Individual'),
                ])
            
            self._create_data_table(story, headers, data, "DETALLE DE TUTORÍAS")
        
        # Resumen
        summary_dict = {
            "Total de Tutorías": len(tutorias),
            "Motivos Principales": self._get_main_motives(tutorias),
        }
        self._create_summary_section(story, summary_dict)
        
        # Pie de página
        self._create_footer(story)
        
        # Generar PDF
        doc.build(story)
        
        if filename is None:
            buffer.seek(0)
            return buffer
        return filename
    
    @staticmethod
    def _get_main_motives(tutorias, limit=3):
        """Obtiene los motivos principales de una lista de tutorías"""
        motives = {}
        for tut in tutorias:
            motivo = tut.get('motivo', 'N/A')
            motives[motivo] = motives.get(motivo, 0) + 1
        
        sorted_motives = sorted(motives.items(), key=lambda x: x[1], reverse=True)
        main_motives = ", ".join([f"{m[0]} ({m[1]})" for m in sorted_motives[:limit]])
        return main_motives if main_motives else "N/A"
