# services/pdf_service.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
from datetime import datetime
import qrcode
from io import BytesIO

class PdfService:
    @staticmethod
    def generer_pdf_reservation(data: dict, filename=None):
        if not data or 'id' not in data:
            return False, "Données invalides"

        filename = filename or f"reservation_{data['id']}_{datetime.now():%Y%m%d_%H%M}.pdf"

        doc = SimpleDocTemplate(filename, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        elements = []

        # QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(f"https://example.com/reservation/{data.get('id', 'demo')}")
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, "PNG")
        buffer.seek(0)
        elements.append(Image(buffer, width=5*cm, height=5*cm))
        elements.append(Spacer(1, 0.5*cm))

        # Tableau
        data_table = [
            ["N° Réservation", str(data.get('id', '—'))],
            ["Salle", data.get('salle_nom', '—')],
            ["Client", f"{data.get('prenom','')} {data.get('nom','')}"],
            ["Événement", data.get('nom_groupe', '—')],
            ["Période", f"{data.get('date_debut','—')} → {data.get('date_fin','—')}"],
            ["Montant total", f"{data.get('montant_total', 0):,.0f} FCFA"],
            ["Acompte", f"{data.get('acompte', 0):,.0f} FCFA"],
            ["Statut", data.get('statut', '—')]
        ]

        table = Table(data_table, colWidths=[9*cm, 9*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        elements.append(table)

        try:
            doc.build(elements)
            return True, filename
        except Exception as e:
            return False, str(e)