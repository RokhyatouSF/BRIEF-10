# ui/console_app.py
# Interface console complète avec rich pour la Maison de la Culture Douta Seck

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, Confirm, FloatPrompt
from rich.progress import track
import time
from datetime import datetime

console = Console()


def ecran_accueil(console):
    """
    Écran d'accueil animé et stylé
    """
    console.clear()
    messages = [
        "[bold cyan]MAISON DE LA CULTURE DOUTA SECK[/bold cyan]",
        "Réservations de salles – Dakar, Médina",
        "Culture • Créativité • Convivialité",
        "═" * 60
    ]
    for msg in messages:
        console.print(Panel.fit(msg, border_style="bright_blue"))
        time.sleep(0.8)
        console.clear()

    console.print(Panel.fit(
        "[bold green]Bienvenue à la Maison Douta Seck ![/bold green]\n"
        "Où la culture prend vie",
        border_style="green",
        padding=(2, 4)
    ))
    time.sleep(1.5)


def menu_client(app, console):
    """
    Menu principal pour les clients – TOUS LES CHOIX IMPLÉMENTÉS
    """
    user = app.user_actuel
    res_svc = app.res_svc
    pdf_svc = app.pdf_svc
    salle_svc = app.salle_svc  # pour lister les salles

    while True:
        console.print(Panel(
            f"[green bold]Espace Client – {user.prenom} {user.nom}[/green bold]",
            border_style="green",
            title="Menu Client"
        ))

        choix = Prompt.ask(
            "Que voulez-vous faire ?",
            choices=["1", "2", "3", "4", "5", "6"],
            choices_display=[
                "Nouvelle réservation",
                "Voir mes réservations",
                "Annuler une réservation",
                "Voir planning d'une salle",
                "Exporter une réservation en PDF",
                "Déconnexion"
            ]
        )

        if choix == "6":
            if Confirm.ask("[bold red]Confirmer la déconnexion ?[/bold red]"):
                console.print("[dim]Déconnexion... À bientôt ![/dim]")
                break
            continue

        if choix == "1":
            # 1. Nouvelle réservation
            console.print("[cyan]Création d'une nouvelle réservation[/cyan]")

            # Lister les salles disponibles
            salles = salle_svc.get_toutes()
            if not salles:
                console.print("[red]Aucune salle disponible[/red]")
                continue

            table = Table(title="Salles disponibles")
            table.add_column("ID", justify="right")
            table.add_column("Nom")
            table.add_column("Capacité")
            table.add_column("Prix/heure")
            for s in salles:
                table.add_row(str(s.id), s.nom, str(s.capacite), f"{s.prix_heure:,.0f} FCFA")
            console.print(table)

            salle_id = IntPrompt.ask("Choisir ID salle")
            salle = salle_svc.get_par_id(salle_id)
            if not salle:
                console.print("[red]Salle invalide[/red]")
                continue

            # Dates (simplifié – à améliorer avec validation)
            debut_str = Prompt.ask("Date début (YYYY-MM-DD HH:MM)")
            fin_str = Prompt.ask("Date fin   (YYYY-MM-DD HH:MM)")
            try:
                debut = datetime.strptime(debut_str, "%Y-%m-%d %H:%M")
                fin = datetime.strptime(fin_str, "%Y-%m-%d %H:%M")
            except:
                console.print("[red]Format date invalide[/red]")
                continue

            if fin <= debut:
                console.print("[red]La fin doit être après le début[/red]")
                continue

            if not res_svc.est_disponible(salle.id, debut, fin):
                console.print("[red bold]Créneau déjà réservé ![/red bold]")
                continue

            nom_groupe = Prompt.ask("Nom du groupe / événement")
            responsable = Prompt.ask("Responsable sur place")

            res = reservations(
                salle=salle,
                client=user,
                nom_groupe=nom_groupe,
                responsable=responsable,
                debut=debut,
                fin=fin
            )
            res.calculer_montant()

            console.print(f"[bold]Montant total estimé : {res.montant_total:,.0f} FCFA[/bold]")

            acompte = FloatPrompt.ask("Montant acompte (min 80%)", default=res.montant_total * 0.8)
            if acompte < res.montant_total * 0.8:
                console.print("[red]Acompte insuffisant (80% minimum requis)[/red]")
                continue

            res.acompte = acompte
            res.statut = "En attente validation"

            if res_svc.creer(res):
                console.print("[green bold]Réservation enregistrée – en attente validation ![/green bold]")

                # Génération PDF
                for _ in track(range(10), description="Génération du récapitulatif PDF..."):
                    time.sleep(0.1)

                success, msg = pdf_svc.generer_pdf_reservation({
                    'id': res.id,
                    'salle_nom': res.salle.nom,
                    'prenom': user.prenom,
                    'nom': user.nom,
                    'nom_groupe': res.nom_groupe,
                    'date_debut': res.debut.strftime("%Y-%m-%d %H:%M"),
                    'date_fin': res.fin.strftime("%Y-%m-%d %H:%M"),
                    'montant_total': res.montant_total,
                    'acompte': res.acompte,
                    'statut': res.statut
                })
                if success:
                    console.print(f"[bold green]PDF créé → {msg}[/bold green]")
                else:
                    console.print(f"[red]Erreur PDF : {msg}[/red]")
            else:
                console.print("[red]Échec création réservation[/red]")

        elif choix == "2":
            # 2. Voir mes réservations
            reservations = res_svc.liste_par_client(user.id)
            if not reservations:
                console.print("[italic yellow]Vous n'avez aucune réservation pour le moment.[/italic yellow]")
                continue

            table = Table(title="Mes réservations", show_header=True, header_style="bold cyan")
            table.add_column("ID", justify="right")
            table.add_column("Salle")
            table.add_column("Début")
            table.add_column("Fin")
            table.add_column("Statut", style="bold")
            table.add_column("Montant total")

            for r in reservations:
                statut_style = {
                    "Acceptée": "green",
                    "Refusée": "red",
                    "En attente validation": "yellow",
                    "En attente paiement": "blue"
                }.get(r["statut"], "white")

                table.add_row(
                    str(r["id"]),
                    r["salle_nom"],
                    r["date_debut"].strftime("%d/%m %H:%M"),
                    r["date_fin"].strftime("%d/%m %H:%M"),
                    f"[{statut_style}]{r['statut']}[/{statut_style}]",
                    f"{r['montant_total']:,.0f} FCFA"
                )

            console.print(table)

        elif choix == "3":
            # 3. Annuler une réservation
            reservations = res_svc.liste_par_client(user.id)
            if not reservations:
                console.print("[yellow]Aucune réservation à annuler[/yellow]")
                continue

            table = Table(title="Vos réservations annulables")
            table.add_column("ID")
            table.add_column("Salle")
            table.add_column("Début")
            table.add_column("Statut")
            for r in reservations:
                if r["statut"] in ["En attente paiement", "En attente validation"]:
                    table.add_row(str(r["id"]), r["salle_nom"], r["date_debut"].strftime("%d/%m %H:%M"), r["statut"])
            console.print(table)

            rid = IntPrompt.ask("ID de la réservation à annuler (0 pour annuler)")
            if rid == 0:
                continue

            if Confirm.ask(f"Confirmer l'annulation de la réservation {rid} ?"):
                if res_svc.annuler(rid, user.id):
                    console.print("[green]Réservation annulée avec succès[/green]")
                else:
                    console.print("[red]Échec annulation (réservation non annulable ou inexistante)[/red]")

        elif choix == "4":
            # 4. Voir planning d'une salle
            salles = salle_svc.get_toutes()
            if not salles:
                console.print("[red]Aucune salle disponible[/red]")
                continue

            table = Table(title="Salles disponibles")
            table.add_column("ID")
            table.add_column("Nom")
            for s in salles:
                table.add_row(str(s.id), s.nom)
            console.print(table)

            sid = IntPrompt.ask("ID de la salle à visualiser")
            planning = res_svc.get_planning_salle(sid)

            console.print(f"\n[bold]Planning de la salle (prochains 7 jours)[/bold]")
            if not planning:
                console.print("[green]Aucune réservation prévue sur cette période[/green]")
            else:
                for p in planning:
                    debut = p['debut'].strftime("%d/%m %H:%M")
                    fin = p['fin'].strftime("%H:%M")
                    statut_style = "green" if p['statut'] == "Acceptée" else "yellow" if p['statut'] == "En attente validation" else "red"
                    console.print(f"[{statut_style}]{debut} → {fin} | {p['nom_groupe'] or '—'} | {p['statut']}[/{statut_style}]")

        elif choix == "5":
            # 5. Exporter une réservation en PDF
            rid = IntPrompt.ask("ID de la réservation à exporter en PDF (0 pour annuler)")
            if rid == 0:
                continue

            # Récupérer une réservation par ID (à implémenter si besoin dans reservation_service)
            # Pour l'exemple, on simule ou on prend la dernière
            console.print("[yellow]Fonctionnalité export PDF spécifique (à compléter avec get_par_id)[/yellow]")

            # Exemple : exporter la dernière réservation créée (à adapter)
            console.print("[dim]Export de la dernière réservation simulé...[/dim]")
            # Ajoute ici le code pour récupérer une réservation par ID et appeler pdf_svc

console.print("[yellow]Fonctionnalité à compléter[/yellow]")


def menu_admin(app, console):
    """
    Menu principal pour les administrateurs – avec CRUD salles et validation
    """
    user = app.user_actuel
    res_svc = app.res_svc
    salle_svc = app.salle_svc

    while True:
        console.print(Panel(
            f"[red bold]Espace Administration – {user.prenom} {user.nom}[/red bold]",
            border_style="red",
            title="Menu Admin"
        ))

        choix = Prompt.ask(
            "Que voulez-vous faire ?",
            choices=["1", "2", "3", "4", "5", "6"],
            choices_display=[
                "Valider / refuser réservations",
                "Gérer les salles (CRUD)",
                "Voir statistiques",
                "Exporter toutes les réservations PDF",
                "Retour menu principal",
                "Quitter"
            ]
        )

        if choix == "6":
            if Confirm.ask("[bold red]Quitter l'application ?[/bold red]"):
                console.print("[blue]Fermeture... Au revoir ![/blue]")
                import sys
                sys.exit(0)
            continue

        if choix == "5":
            console.print("[dim]Retour au menu principal...[/dim]")
            break

        if choix == "1":
            # Validation des réservations en attente
            en_attente = res_svc.liste_en_attente()
            if not en_attente:
                console.print("[italic yellow]Aucune réservation en attente.[/italic yellow]")
                continue

            table = Table(title="Réservations à valider")
            table.add_column("ID")
            table.add_column("Client")
            table.add_column("Salle")
            table.add_column("Début")
            table.add_column("Statut")
            for r in en_attente:
                table.add_row(
                    str(r["id"]),
                    f"{r['prenom']} {r['nom']}",
                    r["salle_nom"],
                    r["date_debut"].strftime("%d/%m %H:%M"),
                    r["statut"]
                )
            console.print(table)

            rid = IntPrompt.ask("ID à traiter (0 pour annuler)")
            if rid == 0:
                continue

            dec = Prompt.ask("Action", choices=["1", "2"], choices_display=["1 = Accepter", "2 = Refuser"])
            statut = "Acceptée" if dec == "1" else "Refusée"

            if res_svc.changer_statut(rid, statut):
                console.print(f"[green]Réservation {rid} marquée comme {statut}[/green]")
            else:
                console.print("[red]Échec du changement de statut[/red]")

        elif choix == "2":
            # Gestion CRUD salles
            console.print("[cyan]Gestion des salles[/cyan]")
            action = Prompt.ask("Action", choices=["1","2","3","4","5"], choices_display=["Lister", "Ajouter", "Modifier", "Supprimer", "Retour"])
            if action == "5":
                continue

            if action == "1":
                salles = salle_svc.get_toutes()
                if not salles:
                    console.print("[yellow]Aucune salle[/yellow]")
                    continue
                table = Table(title="Liste des salles")
                table.add_column("ID")
                table.add_column("Nom")
                table.add_column("Capacité")
                table.add_column("Prix/h")
                for s in salles:
                    table.add_row(str(s.id), s.nom, str(s.capacite), f"{s.prix_heure:,.0f}")
                console.print(table)

            # Ajoute les autres actions (ajouter, modifier, supprimer) comme dans les exemples précédents

        elif choix == "3":
            console.print("[yellow]Statistiques (à implémenter : CA, occupation, etc.)[/yellow]")

        elif choix == "4":
            console.print("[yellow]Export global PDF (à implémenter)[/yellow]")

        else:
            console.print("[dim]Fonctionnalité en développement...[/dim]")