# main.py
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from database import Database
from services.utilisateur_service import UtilisateurService
from services.salle_service import SalleService
from services.reservation_service import ReservationService
from services.pdf_service import PdfService
from ui.console_app import ecran_accueil, menu_client, menu_admin

console = Console()

class Application:
    def __init__(self):
        self.db = Database()
        self.user_svc = UtilisateurService(self.db)
        self.salle_svc = SalleService(self.db)
        self.res_svc = ReservationService(self.db)
        self.pdf_svc = PdfService()
        self.user_actuel = None

    def run(self):
        ecran_accueil(console)

        while True:
            console.rule("Menu Principal", style="bright_blue")
            choix = Prompt.ask(
                "Choix",
                choices=["1", "2", "3"],
                choices_display=["S'inscrire (client)", "Se connecter", "Quitter"]
            )

            if choix == "1":
                self.user_svc.inscription_client(console)

            elif choix == "2":
                user = self.user_svc.connexion(console)
                if user:
                    self.user_actuel = user
                    console.print(f"\n[bold green]Bienvenue {user.prenom} {user.nom} ![/bold green]")
                    if user.role == "client":
                        menu_client(self, console)
                    elif user.role == "admin":
                        menu_admin(self, console)

            elif choix == "3":
                if Confirm.ask("[bold red]Vraiment quitter ?[/bold red]", default=False):
                    console.print("[blue]Au revoir et à bientôt ! 🎭[/blue]")
                    break

if __name__ == "__main__":
    try:
        app = Application()
        app.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Session terminée.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Erreur critique : {e}[/bold red]")
    finally:
        if hasattr(app, 'db'):
            app.db.close()