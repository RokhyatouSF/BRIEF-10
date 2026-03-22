# database.py

import mysql.connector
from mysql.connector import Error as MySQLError

# Optionnel : si tu utilises rich pour les messages d'erreur
try:
    from rich.console import Console
    console = Console()
except ImportError:
    # Fallback si rich n'est pas installé
    class FakeConsole:
        def print(self, *args, **kwargs):
            print(*args)
    console = FakeConsole()


class Database:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",               # ← Mets ton mot de passe ici si besoin
                database="douta_seck",
                raise_on_warnings=True
            )
            print("Connexion MySQL établie avec succès")
        except MySQLError as err:
            print(f"Erreur de connexion à la base de données : {err}")
            raise

    def get_cursor(self):
        """Retourne un curseur avec résultats en dictionnaire"""
        return self.conn.cursor(dictionary=True)

    def commit(self):
        """Valide les modifications"""
        self.conn.commit()

    def close(self):
        """Ferme la connexion"""
        if self.conn and self.conn.is_connected():
            self.conn.close()
            print("Connexion MySQL fermée")

    def execute_safe(self, query: str, params=None, fetch: bool = False, fetchone: bool = False):
        """
        Exécute une requête de manière sécurisée avec gestion d'erreurs
        
        Args:
            query:   La requête SQL
            params:  Tuple ou dict de paramètres (protection contre injection SQL)
            fetch:   True si on veut récupérer tous les résultats (SELECT multiple)
            fetchone: True si on veut récupérer une seule ligne
        
        Returns:
            - True si INSERT/UPDATE/DELETE réussi
            - Liste de dicts si fetch=True
            - Dict si fetchone=True
            - None en cas d'erreur
        """
        cur = None
        try:
            cur = self.get_cursor()
            cur.execute(query, params or ())

            if fetch:
                return cur.fetchall()
            if fetchone:
                return cur.fetchone()
            
            # Pour INSERT/UPDATE/DELETE
            self.commit()
            return True

        except MySQLError as e:
            console.print(f"[bold red]Erreur MySQL {e.errno}: {e.msg}[/bold red]")
            console.print(f"[dim]Requête : {query[:200]}...[/dim]")
            if params:
                console.print(f"[dim]Paramètres : {params}[/dim]")
            self.conn.rollback()
            return None

        except Exception as e:
            console.print(f"[bold red]Erreur inattendue : {e}[/bold red]")
            self.conn.rollback()
            return None

        finally:
            if cur:
                try:
                    cur.close()
                except:
                    pass