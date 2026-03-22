from models.utilisateur import Utilisateur

class UtilisateurService:
    def __init__(self, db):
        self.db = db

    # CREATE
    def creer_client(self, prenom, nom, email, mdp):
        cur = self.db.cursor()
        cur.execute("SELECT id FROM utilisateurs WHERE email=%s", (email,))
        if cur.fetchone():
            return None, "Email déjà utilisé"

        hash_mdp = Utilisateur.hasher(mdp)
        cur.execute("""
            INSERT INTO utilisateurs (prenom, nom, email, mdp_hash, role)
            VALUES (%s, %s, %s, %s, 'client')
        """, (prenom, nom, email, hash_mdp))
        self.db.commit()
        return cur.lastrowid, "Compte créé"

    # READ
    def get_par_email_mdp(self, email, mdp):
        cur = self.db.cursor()
        cur.execute("""
            SELECT id, prenom, nom, mdp_hash, role
            FROM utilisateurs WHERE email = %s
        """, (email,))
        row = cur.fetchone()
        if not row:
            return None
        u = Utilisateur(**row, mdp_hash=row['mdp_hash'])
        return u if u.verifier_mdp(mdp) else None

    # UPDATE (exemple simple)
    def changer_mdp(self, user_id, ancien_mdp, nouveau_mdp):
        u = self.get_par_id(user_id)  # à implémenter si besoin
        if not u or not u.verifier_mdp(ancien_mdp):
            return False
        hash_nouveau = Utilisateur.hasher(nouveau_mdp)
        cur = self.db.cursor()
        cur.execute("UPDATE utilisateurs SET mdp_hash=%s WHERE id=%s", (hash_nouveau, user_id))
        self.db.commit()
        return True

    # DELETE (soft delete ou réel selon besoin)
    def supprimer_compte(self, user_id):
        cur = self.db.cursor()
        cur.execute("DELETE FROM utilisateurs WHERE id=%s", (user_id,))
        self.db.commit()
        return cur.rowcount > 0