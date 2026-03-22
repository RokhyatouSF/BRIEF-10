# services/reservation_service.py
# Service complet pour gérer les réservations (CRUD + logique métier)

from models.reservation import Reservation
from datetime import datetime, timedelta

class ReservationService:
    def __init__(self, db):
        self.db = db

    def est_disponible(self, salle_id: int, debut: datetime, fin: datetime) -> bool:
        """Vérifie si le créneau est libre pour la salle donnée"""
        try:
            cur = self.db.get_cursor()  # ← Utilise get_cursor() comme dans ta classe Database
            cur.execute("""
                SELECT COUNT(*) as cnt 
                FROM reservations
                WHERE salle_id = %s
                  AND statut IN ('En attente validation', 'Acceptée')
                  AND NOT (date_fin <= %s OR date_debut >= %s)
            """, (salle_id, fin, debut))
            
            result = cur.fetchone()
            return result['cnt'] == 0 if result else True
        except Exception as e:
            print(f"[ERREUR] Vérification disponibilité : {e}")
            return False
        finally:
            if 'cur' in locals():
                cur.close()

    def creer(self, reservation: Reservation) -> bool:
        """Crée une nouvelle réservation et met à jour l'objet avec l'ID généré"""
        try:
            cur = self.db.get_cursor()
            cur.execute("""
                INSERT INTO reservations
                (salle_id, client_id, nom_groupe, responsable, date_debut, date_fin,
                 montant_total, acompte, statut)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                reservation.salle.id,
                reservation.client.id,
                reservation.nom_groupe,
                reservation.responsable,
                reservation.debut,
                reservation.fin,
                reservation.montant_total,
                reservation.acompte,
                reservation.statut
            ))
            
            self.db.commit()
            reservation.id = cur.lastrowid
            return reservation.id is not None
        except Exception as e:
            print(f"[ERREUR] Création réservation : {e}")
            self.db.conn.rollback()
            return False
        finally:
            if 'cur' in locals():
                cur.close()

    def liste_par_client(self, client_id: int) -> list[dict]:
        """Liste toutes les réservations d'un client"""
        try:
            cur = self.db.get_cursor()
            cur.execute("""
                SELECT r.*, s.nom as salle_nom
                FROM reservations r
                JOIN salles s ON r.salle_id = s.id
                WHERE r.client_id = %s
                ORDER BY r.date_debut DESC
            """, (client_id,))
            result = cur.fetchall()
            return result
        except Exception as e:
            print(f"[ERREUR] Liste réservations client : {e}")
            return []
        finally:
            if 'cur' in locals():
                cur.close()

    def liste_en_attente(self) -> list[dict]:
        """Liste les réservations en attente de validation (pour admin)"""
        try:
            cur = self.db.get_cursor()
            cur.execute("""
                SELECT r.*, u.prenom, u.nom, s.nom as salle_nom
                FROM reservations r
                JOIN utilisateurs u ON r.client_id = u.id
                JOIN salles s ON r.salle_id = s.id
                WHERE r.statut = 'En attente validation'
                ORDER BY r.date_debut
            """)
            result = cur.fetchall()
            return result
        except Exception as e:
            print(f"[ERREUR] Liste réservations en attente : {e}")
            return []
        finally:
            if 'cur' in locals():
                cur.close()

    def changer_statut(self, res_id: int, nouveau_statut: str) -> bool:
        """Change le statut d'une réservation (Acceptée / Refusée / Annulée)"""
        if nouveau_statut not in ["Acceptée", "Refusée", "Annulée"]:
            print(f"Statut invalide : {nouveau_statut}")
            return False

        try:
            cur = self.db.get_cursor()
            cur.execute("""
                UPDATE reservations 
                SET statut = %s 
                WHERE id = %s
            """, (nouveau_statut, res_id))
            
            self.db.commit()
            return cur.rowcount > 0
        except Exception as e:
            print(f"[ERREUR] Changement statut : {e}")
            self.db.conn.rollback()
            return False
        finally:
            if 'cur' in locals():
                cur.close()

    def annuler(self, res_id: int, client_id: int) -> bool:
        """Annule (supprime) une réservation si elle est encore modifiable"""
        try:
            cur = self.db.get_cursor()
            cur.execute("""
                DELETE FROM reservations
                WHERE id = %s 
                  AND client_id = %s
                  AND statut IN ('En attente paiement', 'En attente validation')
            """, (res_id, client_id))
            
            self.db.commit()
            return cur.rowcount > 0
        except Exception as e:
            print(f"[ERREUR] Annulation réservation : {e}")
            self.db.conn.rollback()
            return False
        finally:
            if 'cur' in locals():
                cur.close()

    def get_planning_salle(self, salle_id: int, jours: int = 7) -> list[dict]:
        """Retourne les réservations sur les X prochains jours pour une salle"""
        try:
            debut_periode = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            fin_periode = debut_periode + timedelta(days=jours)

            cur = self.db.get_cursor()
            cur.execute("""
                SELECT date_debut AS debut, date_fin AS fin, statut, nom_groupe
                FROM reservations
                WHERE salle_id = %s
                  AND date_debut < %s
                  AND date_fin > %s
                ORDER BY date_debut
            """, (salle_id, fin_periode, debut_periode))
            
            result = cur.fetchall()
            return result
        except Exception as e:
            print(f"[ERREUR] Planning salle {salle_id} : {e}")
            return []
        finally:
            if 'cur' in locals():
                cur.close()