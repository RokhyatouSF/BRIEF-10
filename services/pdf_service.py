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
    def generer_pdf_reservation(res_data: dict, filename=None):
        if not res_data or 'id' not in res_data:
            return False, "Données invalides"

        if filename is None:
            filename = f"reservation_{res_data['id']}_{datetime.now():%Y%m%d_%H%M}.pdf"

        doc = SimpleDocTemplate(filename, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("MAISON DE LA CULTURE DOUTA SECK", styles['Title']))
        elements.append(Paragraph("Avenue Blaise Diagne x Rue 25 – Médina – Dakar", styles['Normal']))
        elements.append(Spacer(1, 0.6*cm))

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data("https://github.com/rokhyatou/projet-douta-seck")  
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img_qr.save(buffer, format="PNG")
        buffer.seek(0)

        qr_img = Image(buffer, width=5*cm, height=5*cm)
        elements.append(qr_img)
        elements.append(Spacer(1, 0.4*cm))

        data = [
            ["N° Réservation", str(res_data.get('id', '—'))],
            ["Salle", res_data.get('salle_nom', '—')],
            ["Client", f"{res_data.get('prenom','')} {res_data.get('nom','')}"],
            ["Événement", res_data.get('nom_groupe', '—')],
            ["Période", f"{res_data.get('date_debut','—')} → {res_data.get('date_fin','—')}"],
            ["Montant total", f"{res_data.get('montant_total', 0):,.0f} FCFA"],
            ["Acompte", f"{res_data.get('acompte', 0):,.0f} FCFA"],
            ["Solde restant", f"{res_data.get('montant_total', 0) - res_data.get('acompte', 0):,.0f} FCFA"],
            ["Statut", res_data.get('statut', '—')],
        ]

        table = Table(data, colWidths=[9*cm, 9*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 1*cm))
        elements.append(Paragraph(f"Généré le {datetime.now():%d/%m/%Y %H:%M} – Document officiel", styles['Italic']))

        try:
            doc.build(elements)
            return True, filename
        except Exception as e:
            return False, str(e)
