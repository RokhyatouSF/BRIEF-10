# services/salle_service.py

from models.salle import Salle

class SalleService:
    """
    Service pour gérer les opérations CRUD sur les salles
    (Create, Read, Update, Delete)
    """
    
    def __init__(self, db):
        self.db = db

    def creer(self, nom: str, capacite: int, prix_heure: float) -> int | None:
        """
        Crée une nouvelle salle et retourne son ID
        """
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO salles (nom, capacite, prix_heure)
                VALUES (%s, %s, %s)
            """, (nom.strip(), capacite, prix_heure))
            self.db.commit()
            return cur.lastrowid
        except Exception as e:
            print(f"Erreur création salle : {e}")
            self.db.conn.rollback()
            return None

    def get_toutes(self) -> list[Salle]:
        """
        Retourne la liste de toutes les salles
        """
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT id, nom, capacite, prix_heure 
                FROM salles 
                ORDER BY nom
            """)
            rows = cur.fetchall()
            return [Salle(
                id=row['id'],
                nom=row['nom'],
                capacite=row['capacite'],
                prix_heure=row['prix_heure']
            ) for row in rows]
        except Exception as e:
            print(f"Erreur lecture salles : {e}")
            return []

    def get_par_id(self, salle_id: int) -> Salle | None:
        """
        Retourne une salle par son ID ou None si non trouvée
        """
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT id, nom, capacite, prix_heure 
                FROM salles 
                WHERE id = %s
            """, (salle_id,))
            row = cur.fetchone()
            if row:
                return Salle(
                    id=row['id'],
                    nom=row['nom'],
                    capacite=row['capacite'],
                    prix_heure=row['prix_heure']
                )
            return None
        except Exception as e:
            print(f"Erreur lecture salle {salle_id} : {e}")
            return None

    def modifier(self, salle_id: int, nom: str = None, capacite: int = None, prix_heure: float = None) -> bool:
        """
        Modifie les champs fournis d'une salle existante
        Retourne True si modification effectuée
        """
        if nom is None and capacite is None and prix_heure is None:
            return False  # rien à modifier

        updates = []
        params = []

        if nom is not None:
            updates.append("nom = %s")
            params.append(nom.strip())
        if capacite is not None:
            updates.append("capacite = %s")
            params.append(capacite)
        if prix_heure is not None:
            updates.append("prix_heure = %s")
            params.append(prix_heure)

        params.append(salle_id)

        query = f"UPDATE salles SET {', '.join(updates)} WHERE id = %s"

        try:
            cur = self.db.cursor()
            cur.execute(query, params)
            self.db.commit()
            return cur.rowcount > 0
        except Exception as e:
            print(f"Erreur modification salle {salle_id} : {e}")
            self.db.conn.rollback()
            return False

    def supprimer(self, salle_id: int) -> bool:
        """
        Supprime une salle (attention : peut échouer si liée à des réservations)
        Retourne True si suppression réussie
        """
        try:
            cur = self.db.cursor()
            cur.execute("DELETE FROM salles WHERE id = %s", (salle_id,))
            self.db.commit()
            return cur.rowcount > 0
        except Exception as e:
            print(f"Erreur suppression salle {salle_id} : {e}")
            self.db.conn.rollback()
            return False

    def existe(self, salle_id: int) -> bool:
        """Vérifie si une salle existe"""
        return self.get_par_id(salle_id) is not None