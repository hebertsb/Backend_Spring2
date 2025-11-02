"""
Utilidades para exportación de reportes a PDF y Excel.
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
from decimal import Decimal

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet
from typing import cast


class ExportadorReportesPDF:
    """
    Clase para generar reportes en formato PDF con estructura profesional.
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._crear_estilos_personalizados()
    
    def _crear_estilos_personalizados(self):
        """Crea estilos personalizados para el documento."""
        # Estilo para título principal
        self.styles.add(ParagraphStyle(
            name='TituloReporte',
            parent=self.styles['Title'],
            fontSize=20,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='SubtituloReporte',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para información
        self.styles.add(ParagraphStyle(
            name='InfoReporte',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7F8C8D'),
            spaceAfter=6
        ))
    
    def _formatear_valor(self, valor):
        """Formatea valores para mostrar en PDF."""
        if valor is None:
            return 'N/A'
        if isinstance(valor, Decimal):
            return f"Bs. {float(valor):,.2f}"
        if isinstance(valor, (int, float)):
            return f"{valor:,.2f}" if isinstance(valor, float) else f"{valor:,}"
        if isinstance(valor, datetime):
            return valor.strftime('%d/%m/%Y %H:%M')
        return str(valor)
    
    def generar_reporte_ventas_general(self, reporte_data, titulo="Reporte de Ventas General"):
        """
        Genera PDF para reporte de ventas general.
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
        story = []
        
        # Título
        story.append(Paragraph(titulo, self.styles['TituloReporte']))
        story.append(Spacer(1, 0.2*inch))
        
        # Información del período
        periodo = reporte_data.get('periodo', {})
        if periodo.get('fecha_inicio') or periodo.get('fecha_fin'):
            fecha_inicio = periodo.get('fecha_inicio', 'N/A')
            fecha_fin = periodo.get('fecha_fin', 'N/A')
            if isinstance(fecha_inicio, datetime):
                fecha_inicio = fecha_inicio.strftime('%d/%m/%Y')
            if isinstance(fecha_fin, datetime):
                fecha_fin = fecha_fin.strftime('%d/%m/%Y')
            
            periodo_texto = f"<b>Período:</b> {fecha_inicio} - {fecha_fin}"
            story.append(Paragraph(periodo_texto, self.styles['InfoReporte']))
            story.append(Spacer(1, 0.1*inch))
        
        fecha_generacion = f"<b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        story.append(Paragraph(fecha_generacion, self.styles['InfoReporte']))
        story.append(Spacer(1, 0.3*inch))
        
        # Métricas Generales
        metricas = reporte_data.get('metricas_generales', {})
        if metricas:
            story.append(Paragraph("Métricas Generales", self.styles['SubtituloReporte']))
            
            data_metricas = [
                ['Métrica', 'Valor'],
                ['Total Ventas', self._formatear_valor(metricas.get('total_ventas'))],
                ['Cantidad de Reservas', self._formatear_valor(metricas.get('cantidad_reservas'))],
                ['Ticket Promedio', self._formatear_valor(metricas.get('ticket_promedio'))],
                ['Total Pagado', self._formatear_valor(metricas.get('total_pagado'))],
            ]
            
            table_metricas = Table(data_metricas, colWidths=[3*inch, 2.5*inch])
            table_metricas.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')])
            ]))
            story.append(table_metricas)
            story.append(Spacer(1, 0.3*inch))
        
        # Top Paquetes
        top_paquetes = reporte_data.get('top_paquetes', [])
        if top_paquetes:
            story.append(Paragraph("Top Paquetes Más Vendidos", self.styles['SubtituloReporte']))
            
            data_paquetes = [['Paquete', 'Total Ventas', 'Cantidad']]
            for paquete in top_paquetes[:10]:
                data_paquetes.append([
                    paquete.get('paquete__nombre', 'N/A'),
                    self._formatear_valor(paquete.get('total_ventas')),
                    str(paquete.get('cantidad', 0))
                ])
            
            table_paquetes = Table(data_paquetes, colWidths=[3*inch, 1.5*inch, 1*inch])
            table_paquetes.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')])
            ]))
            story.append(table_paquetes)
            story.append(Spacer(1, 0.3*inch))
        
        # Top Servicios
        top_servicios = reporte_data.get('top_servicios', [])
        if top_servicios:
            story.append(Paragraph("Top Servicios Más Vendidos", self.styles['SubtituloReporte']))
            
            data_servicios = [['Servicio', 'Total Ventas', 'Cantidad']]
            for servicio in top_servicios[:10]:
                data_servicios.append([
                    servicio.get('servicio__titulo', 'N/A'),
                    self._formatear_valor(servicio.get('total_ventas')),
                    str(servicio.get('cantidad', 0))
                ])
            
            table_servicios = Table(data_servicios, colWidths=[3*inch, 1.5*inch, 1*inch])
            table_servicios.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E67E22')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')])
            ]))
            story.append(table_servicios)
            story.append(Spacer(1, 0.3*inch))
        
        # Top Clientes
        top_clientes = reporte_data.get('top_clientes', [])
        if top_clientes:
            story.append(PageBreak())
            story.append(Paragraph("Top Clientes", self.styles['SubtituloReporte']))
            
            data_clientes = [['Cliente', 'Total Gastado', 'Reservas']]
            for cliente in top_clientes[:15]:
                data_clientes.append([
                    cliente.get('cliente__nombre', 'N/A'),
                    self._formatear_valor(cliente.get('total_gastado')),
                    str(cliente.get('cantidad_reservas', 0))
                ])
            
            table_clientes = Table(data_clientes, colWidths=[3*inch, 1.5*inch, 1*inch])
            table_clientes.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9B59B6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')])
            ]))
            story.append(table_clientes)
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generar_reporte_clientes(self, reporte_data, titulo="Reporte de Clientes"):
        """
        Genera PDF para reporte de clientes.
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
        story = []
        
        # Título
        story.append(Paragraph(titulo, self.styles['TituloReporte']))
        story.append(Spacer(1, 0.2*inch))
        
        # Resumen
        resumen = reporte_data.get('resumen', {})
        fecha_generacion = f"<b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        story.append(Paragraph(fecha_generacion, self.styles['InfoReporte']))
        
        cantidad_clientes = reporte_data.get('cantidad_clientes', 0)
        story.append(Paragraph(f"<b>Total de clientes:</b> {cantidad_clientes}", self.styles['InfoReporte']))
        story.append(Spacer(1, 0.3*inch))
        
        # Tabla de clientes
        clientes = reporte_data.get('clientes', [])
        if clientes:
            story.append(Paragraph("Detalle de Clientes", self.styles['SubtituloReporte']))
            
            data_clientes = [[
                'Cliente', 'Teléfono', 'Total Gastado', 
                'Reservas', 'Ticket Prom.', 'Última Compra'
            ]]
            
            for cliente in clientes[:50]:  # Limitar a 50 clientes por página
                ultima_compra = cliente.get('ultima_compra')
                if isinstance(ultima_compra, datetime):
                    ultima_compra = ultima_compra.strftime('%d/%m/%Y')
                
                data_clientes.append([
                    cliente.get('cliente__nombre', 'N/A')[:25],
                    cliente.get('cliente__telefono', 'N/A'),
                    self._formatear_valor(cliente.get('total_gastado')),
                    str(cliente.get('cantidad_reservas', 0)),
                    self._formatear_valor(cliente.get('ticket_promedio')),
                    str(ultima_compra) if ultima_compra else 'N/A'
                ])
            
            table_clientes = Table(data_clientes, colWidths=[
                1.5*inch, 1*inch, 1.2*inch, 0.8*inch, 1*inch, 1*inch
            ])
            table_clientes.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')])
            ]))
            story.append(table_clientes)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generar_reporte_productos(self, reporte_data, titulo="Reporte de Productos"):
        """
        Genera PDF para reporte de productos.
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
        story = []
        
        # Título
        story.append(Paragraph(titulo, self.styles['TituloReporte']))
        story.append(Spacer(1, 0.2*inch))
        
        fecha_generacion = f"<b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        story.append(Paragraph(fecha_generacion, self.styles['InfoReporte']))
        story.append(Spacer(1, 0.3*inch))
        
        # Paquetes
        paquetes = reporte_data.get('paquetes', [])
        if paquetes:
            story.append(Paragraph("Rendimiento de Paquetes", self.styles['SubtituloReporte']))
            
            data_paquetes = [['Paquete', 'Precio USD', 'Precio BOB', 'Ventas BOB', 'Cant.', 'Conv. %']]
            for paquete in paquetes[:20]:
                data_paquetes.append([
                    paquete.get('paquete__nombre', 'N/A')[:25],
                    f"${float(paquete.get('paquete__precio_base_usd', 0)):,.2f}",
                    f"Bs. {float(paquete.get('paquete__precio_base_bob', 0)):,.2f}",
                    f"Bs. {float(paquete.get('ventas_totales_bob', 0)):,.2f}",
                    str(paquete.get('cantidad_vendida', 0)),
                    f"{float(paquete.get('tasa_conversion', 0)):.1f}%"
                ])
            
            table_paquetes = Table(data_paquetes, colWidths=[2*inch, 0.9*inch, 1.1*inch, 1.2*inch, 0.6*inch, 0.7*inch])
            table_paquetes.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 7.5),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')])
            ]))
            story.append(table_paquetes)
            story.append(Spacer(1, 0.3*inch))
        
        # Servicios
        servicios = reporte_data.get('servicios', [])
        if servicios:
            story.append(Paragraph("Rendimiento de Servicios", self.styles['SubtituloReporte']))
            
            data_servicios = [['Servicio', 'Cat.', 'USD', 'BOB', 'Ventas BOB', 'Cant.', 'Conv. %']]
            for servicio in servicios[:20]:
                data_servicios.append([
                    servicio.get('servicio__titulo', 'N/A')[:22],
                    servicio.get('servicio__categoria__nombre', 'N/A')[:12],
                    f"${float(servicio.get('servicio__precio_usd', 0)):,.2f}",
                    f"Bs. {float(servicio.get('servicio__precio_bob', 0)):,.0f}",
                    f"Bs. {float(servicio.get('ventas_totales_bob', 0)):,.2f}",
                    str(servicio.get('cantidad_vendida', 0)),
                    f"{float(servicio.get('tasa_conversion', 0)):.1f}%"
                ])
            
            table_servicios = Table(data_servicios, colWidths=[1.5*inch, 0.7*inch, 0.7*inch, 0.8*inch, 1.2*inch, 0.5*inch, 0.6*inch])
            table_servicios.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E67E22')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 7.5),
                ('FONTSIZE', (0, 1), (-1, -1), 6.5),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')])
            ]))
            story.append(table_servicios)
        
        doc.build(story)
        buffer.seek(0)
        return buffer


class ExportadorReportesExcel:
    """
    Clase para generar reportes en formato Excel con estructura profesional.
    """
    
    def __init__(self):
        self.color_header = 'FF3498DB'
        self.color_subtotal = 'FFECF0F1'
        self.border_style = Border(
            left=Side(style='thin', color='FFBDC3C7'),
            right=Side(style='thin', color='FFBDC3C7'),
            top=Side(style='thin', color='FFBDC3C7'),
            bottom=Side(style='thin', color='FFBDC3C7')
        )
    
    def _aplicar_estilo_header(self, ws, row_num, columns):
        """Aplica estilo a la fila de encabezado."""
        for col_num in range(1, columns + 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.fill = PatternFill(start_color=self.color_header, end_color=self.color_header, fill_type='solid')
            cell.font = Font(bold=True, color='FFFFFFFF', size=11)
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = self.border_style
    
    def _aplicar_estilo_datos(self, ws, start_row, end_row, columns):
        """Aplica estilo a las filas de datos."""
        for row_num in range(start_row, end_row + 1):
            for col_num in range(1, columns + 1):
                cell = ws.cell(row=row_num, column=col_num)
                cell.border = self.border_style
                cell.alignment = Alignment(vertical='center')
                
                # Alternar colores de fila
                if row_num % 2 == 0:
                    cell.fill = PatternFill(start_color=self.color_subtotal, end_color=self.color_subtotal, fill_type='solid')
    
    def _ajustar_ancho_columnas(self, ws):
        """Ajusta automáticamente el ancho de las columnas."""
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
    
    def generar_reporte_ventas_general(self, reporte_data, titulo="Reporte de Ventas General"):
        """
        Genera Excel para reporte de ventas general.
        """
        wb = Workbook()
        
        # Hoja 1: Resumen
        ws_resumen = cast(Worksheet, wb.active)
        ws_resumen.title = "Resumen"
        
        # Título
        ws_resumen['A1'] = titulo
        ws_resumen['A1'].font = Font(size=18, bold=True, color='FF2C3E50')
        ws_resumen.merge_cells('A1:D1')
        ws_resumen['A1'].alignment = Alignment(horizontal='center')
        
        # Información
        ws_resumen['A3'] = 'Fecha de generación:'
        ws_resumen['B3'] = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        periodo = reporte_data.get('periodo', {})
        if periodo.get('fecha_inicio'):
            ws_resumen['A4'] = 'Período desde:'
            fecha_inicio = periodo['fecha_inicio']
            if isinstance(fecha_inicio, datetime):
                ws_resumen['B4'] = fecha_inicio.strftime('%d/%m/%Y')
            else:
                ws_resumen['B4'] = str(fecha_inicio)
        
        if periodo.get('fecha_fin'):
            ws_resumen['A5'] = 'Período hasta:'
            fecha_fin = periodo['fecha_fin']
            if isinstance(fecha_fin, datetime):
                ws_resumen['B5'] = fecha_fin.strftime('%d/%m/%Y')
            else:
                ws_resumen['B5'] = str(fecha_fin)
        
        # Métricas Generales
        row = 7
        ws_resumen[f'A{row}'] = 'MÉTRICAS GENERALES'
        ws_resumen[f'A{row}'].font = Font(size=14, bold=True, color='FF34495E')
        ws_resumen.merge_cells(f'A{row}:B{row}')
        
        row += 2
        metricas = reporte_data.get('metricas_generales', {})
        
        # Encabezados
        ws_resumen[f'A{row}'] = 'Métrica'
        ws_resumen[f'B{row}'] = 'Valor'
        self._aplicar_estilo_header(ws_resumen, row, 2)
        
        row += 1
        start_data_row = row
        
        metricas_lista = [
            ('Total Ventas (Bs)', metricas.get('total_ventas', 0)),
            ('Cantidad de Reservas', metricas.get('cantidad_reservas', 0)),
            ('Ticket Promedio (Bs)', metricas.get('ticket_promedio', 0)),
            ('Total Pagado (Bs)', metricas.get('total_pagado', 0)),
        ]
        
        for nombre, valor in metricas_lista:
            ws_resumen[f'A{row}'] = nombre
            if isinstance(valor, Decimal):
                ws_resumen[f'B{row}'] = float(valor)
                ws_resumen[f'B{row}'].number_format = '#,##0.00'
            else:
                ws_resumen[f'B{row}'] = valor
            row += 1
        
        self._aplicar_estilo_datos(ws_resumen, start_data_row, row - 1, 2)
        
        # Hoja 2: Top Paquetes
        top_paquetes = reporte_data.get('top_paquetes', [])
        if top_paquetes:
            ws_paquetes = cast(Worksheet, wb.create_sheet("Top Paquetes"))
            
            ws_paquetes['A1'] = 'Top Paquetes Más Vendidos'
            ws_paquetes['A1'].font = Font(size=16, bold=True, color='FF27AE60')
            ws_paquetes.merge_cells('A1:D1')
            
            # Encabezados
            headers = ['Paquete', 'ID', 'Total Ventas (Bs)', 'Cantidad']
            for col_num, header in enumerate(headers, 1):
                ws_paquetes.cell(row=3, column=col_num, value=header)
            self._aplicar_estilo_header(ws_paquetes, 3, len(headers))
            
            # Datos
            for row_num, paquete in enumerate(top_paquetes, 4):
                ws_paquetes.cell(row=row_num, column=1, value=paquete.get('paquete__nombre', 'N/A'))
                ws_paquetes.cell(row=row_num, column=2, value=paquete.get('paquete__id', ''))
                
                total_ventas = paquete.get('total_ventas')
                if total_ventas:
                    ws_paquetes.cell(row=row_num, column=3, value=float(total_ventas))
                    ws_paquetes.cell(row=row_num, column=3).number_format = '#,##0.00'
                
                ws_paquetes.cell(row=row_num, column=4, value=paquete.get('cantidad', 0))
            
            self._aplicar_estilo_datos(ws_paquetes, 4, 3 + len(top_paquetes), len(headers))
            self._ajustar_ancho_columnas(ws_paquetes)
        
        # Hoja 3: Top Servicios
        top_servicios = reporte_data.get('top_servicios', [])
        if top_servicios:
            ws_servicios = cast(Worksheet, wb.create_sheet("Top Servicios"))
            
            ws_servicios['A1'] = 'Top Servicios Más Vendidos'
            ws_servicios['A1'].font = Font(size=16, bold=True, color='FFE67E22')
            ws_servicios.merge_cells('A1:D1')
            
            # Encabezados
            headers = ['Servicio', 'ID', 'Total Ventas (Bs)', 'Cantidad']
            for col_num, header in enumerate(headers, 1):
                ws_servicios.cell(row=3, column=col_num, value=header)
            self._aplicar_estilo_header(ws_servicios, 3, len(headers))
            
            # Datos
            for row_num, servicio in enumerate(top_servicios, 4):
                ws_servicios.cell(row=row_num, column=1, value=servicio.get('servicio__titulo', 'N/A'))
                ws_servicios.cell(row=row_num, column=2, value=servicio.get('servicio__id', ''))
                
                total_ventas = servicio.get('total_ventas')
                if total_ventas:
                    ws_servicios.cell(row=row_num, column=3, value=float(total_ventas))
                    ws_servicios.cell(row=row_num, column=3).number_format = '#,##0.00'
                
                ws_servicios.cell(row=row_num, column=4, value=servicio.get('cantidad', 0))
            
            self._aplicar_estilo_datos(ws_servicios, 4, 3 + len(top_servicios), len(headers))
            self._ajustar_ancho_columnas(ws_servicios)
        
        # Hoja 4: Top Clientes
        top_clientes = reporte_data.get('top_clientes', [])
        if top_clientes:
            ws_clientes = cast(Worksheet, wb.create_sheet("Top Clientes"))
            
            ws_clientes['A1'] = 'Top Clientes'
            ws_clientes['A1'].font = Font(size=16, bold=True, color='FF9B59B6')
            ws_clientes.merge_cells('A1:D1')
            
            # Encabezados
            headers = ['Cliente', 'ID', 'Total Gastado (Bs)', 'Cantidad Reservas']
            for col_num, header in enumerate(headers, 1):
                ws_clientes.cell(row=3, column=col_num, value=header)
            self._aplicar_estilo_header(ws_clientes, 3, len(headers))
            
            # Datos
            for row_num, cliente in enumerate(top_clientes, 4):
                ws_clientes.cell(row=row_num, column=1, value=cliente.get('cliente__nombre', 'N/A'))
                ws_clientes.cell(row=row_num, column=2, value=cliente.get('cliente__id', ''))
                
                total_gastado = cliente.get('total_gastado')
                if total_gastado:
                    ws_clientes.cell(row=row_num, column=3, value=float(total_gastado))
                    ws_clientes.cell(row=row_num, column=3).number_format = '#,##0.00'
                
                ws_clientes.cell(row=row_num, column=4, value=cliente.get('cantidad_reservas', 0))
            
            self._aplicar_estilo_datos(ws_clientes, 4, 3 + len(top_clientes), len(headers))
            self._ajustar_ancho_columnas(ws_clientes)
        
        self._ajustar_ancho_columnas(ws_resumen)
        
        # Guardar en buffer
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
    
    def generar_reporte_clientes(self, reporte_data, titulo="Reporte de Clientes"):
        """
        Genera Excel para reporte de clientes.
        """
        wb = Workbook()
        ws = cast(Worksheet, wb.active)
        ws.title = "Clientes"
        
        # Título
        ws['A1'] = titulo
        ws['A1'].font = Font(size=18, bold=True, color='FF2C3E50')
        ws.merge_cells('A1:G1')
        ws['A1'].alignment = Alignment(horizontal='center')
        
        # Información
        ws['A3'] = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        ws['A4'] = f"Total clientes: {reporte_data.get('cantidad_clientes', 0)}"
        
        # Encabezados
        headers = ['Cliente', 'Teléfono', 'Total Gastado (Bs)', 'Reservas', 
                   'Reservas Pagadas', 'Ticket Promedio (Bs)', 'Última Compra']
        for col_num, header in enumerate(headers, 1):
            ws.cell(row=6, column=col_num, value=header)
        self._aplicar_estilo_header(ws, 6, len(headers))
        
        # Datos
        clientes = reporte_data.get('clientes', [])
        for row_num, cliente in enumerate(clientes, 7):
            ws.cell(row=row_num, column=1, value=cliente.get('cliente__nombre', 'N/A'))
            ws.cell(row=row_num, column=2, value=cliente.get('cliente__telefono', 'N/A'))
            
            total_gastado = cliente.get('total_gastado')
            if total_gastado:
                ws.cell(row=row_num, column=3, value=float(total_gastado))
                ws.cell(row=row_num, column=3).number_format = '#,##0.00'
            
            ws.cell(row=row_num, column=4, value=cliente.get('cantidad_reservas', 0))
            ws.cell(row=row_num, column=5, value=cliente.get('reservas_pagadas', 0))
            
            ticket_promedio = cliente.get('ticket_promedio')
            if ticket_promedio:
                ws.cell(row=row_num, column=6, value=float(ticket_promedio))
                ws.cell(row=row_num, column=6).number_format = '#,##0.00'
            
            ultima_compra = cliente.get('ultima_compra')
            if isinstance(ultima_compra, datetime):
                ws.cell(row=row_num, column=7, value=ultima_compra.strftime('%d/%m/%Y'))
            else:
                ws.cell(row=row_num, column=7, value=str(ultima_compra) if ultima_compra else 'N/A')
        
        if clientes:
            self._aplicar_estilo_datos(ws, 7, 6 + len(clientes), len(headers))
        
        self._ajustar_ancho_columnas(ws)
        
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
    
    def generar_reporte_productos(self, reporte_data, titulo="Reporte de Productos"):
        """
        Genera Excel para reporte de productos.
        """
        wb = Workbook()
        
        # Hoja 1: Paquetes
        paquetes = reporte_data.get('paquetes', [])
        if paquetes:
            ws_paquetes = cast(Worksheet, wb.active)
            ws_paquetes.title = "Paquetes"
            
            ws_paquetes['A1'] = 'Rendimiento de Paquetes'
            ws_paquetes['A1'].font = Font(size=16, bold=True, color='FF27AE60')
            ws_paquetes.merge_cells('A1:F1')
            
            headers = ['Paquete', 'Precio Base (Bs)', 'Ventas Totales (Bs)', 
                      'Cantidad Vendida', 'Tasa Conversión (%)', '¿Personalizado?']
            for col_num, header in enumerate(headers, 1):
                ws_paquetes.cell(row=3, column=col_num, value=header)
            self._aplicar_estilo_header(ws_paquetes, 3, len(headers))
            
            for row_num, paquete in enumerate(paquetes, 4):
                ws_paquetes.cell(row=row_num, column=1, value=paquete.get('paquete__nombre', 'N/A'))
                
                # Intentar ambos nombres de campo para precio base
                precio_base = paquete.get('paquete__precio_base_bob') or paquete.get('paquete__precio_base')
                if precio_base:
                    ws_paquetes.cell(row=row_num, column=2, value=float(precio_base))
                    ws_paquetes.cell(row=row_num, column=2).number_format = '#,##0.00'
                
                # Intentar ambos nombres de campo para ventas totales
                ventas_totales = paquete.get('ventas_totales_bob') or paquete.get('ventas_totales')
                if ventas_totales:
                    ws_paquetes.cell(row=row_num, column=3, value=float(ventas_totales))
                    ws_paquetes.cell(row=row_num, column=3).number_format = '#,##0.00'
                
                ws_paquetes.cell(row=row_num, column=4, value=paquete.get('cantidad_vendida', 0))
                
                tasa_conversion = paquete.get('tasa_conversion', 0)
                ws_paquetes.cell(row=row_num, column=5, value=float(tasa_conversion))
                ws_paquetes.cell(row=row_num, column=5).number_format = '0.00'
                
                es_personalizado = paquete.get('paquete__es_personalizado', False)
                ws_paquetes.cell(row=row_num, column=6, value='Sí' if es_personalizado else 'No')
            
            self._aplicar_estilo_datos(ws_paquetes, 4, 3 + len(paquetes), len(headers))
            self._ajustar_ancho_columnas(ws_paquetes)
        
        # Hoja 2: Servicios
        servicios = reporte_data.get('servicios', [])
        if servicios:
            ws_servicios = cast(Worksheet, wb.create_sheet("Servicios"))
            
            ws_servicios['A1'] = 'Rendimiento de Servicios'
            ws_servicios['A1'].font = Font(size=16, bold=True, color='FFE67E22')
            ws_servicios.merge_cells('A1:F1')
            
            headers = ['Servicio', 'Categoría', 'Precio (USD)', 
                      'Ventas Totales (Bs)', 'Cantidad Vendida', 'Tasa Conversión (%)']
            for col_num, header in enumerate(headers, 1):
                ws_servicios.cell(row=3, column=col_num, value=header)
            self._aplicar_estilo_header(ws_servicios, 3, len(headers))
            
            for row_num, servicio in enumerate(servicios, 4):
                ws_servicios.cell(row=row_num, column=1, value=servicio.get('servicio__titulo', 'N/A'))
                ws_servicios.cell(row=row_num, column=2, value=servicio.get('servicio__categoria__nombre', 'N/A'))
                
                precio_usd = servicio.get('servicio__precio_usd')
                if precio_usd:
                    ws_servicios.cell(row=row_num, column=3, value=float(precio_usd))
                    ws_servicios.cell(row=row_num, column=3).number_format = '#,##0.00'
                
                # Intentar ambos nombres de campo para ventas totales
                ventas_totales = servicio.get('ventas_totales_bob') or servicio.get('ventas_totales')
                if ventas_totales:
                    ws_servicios.cell(row=row_num, column=4, value=float(ventas_totales))
                    ws_servicios.cell(row=row_num, column=4).number_format = '#,##0.00'
                
                ws_servicios.cell(row=row_num, column=5, value=servicio.get('cantidad_vendida', 0))
                
                tasa_conversion = servicio.get('tasa_conversion', 0)
                ws_servicios.cell(row=row_num, column=6, value=float(tasa_conversion))
                ws_servicios.cell(row=row_num, column=6).number_format = '0.00'
            
            self._aplicar_estilo_datos(ws_servicios, 4, 3 + len(servicios), len(headers))
            self._ajustar_ancho_columnas(ws_servicios)
        
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
