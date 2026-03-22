# Maison de la Culture Douta Seck - Système de Réservation de Salles


**Un système de gestion moderne et intuitif des réservations de salles pour la Maison de la Culture Douta Seck (Dakar, Médina).**

Ce projet est une application console professionnelle développée en **Python** avec une interface utilisateur riche (grâce à la bibliothèque `rich`), une base de données MySQL, un système d'authentification sécurisé, génération de PDF avec QR code, et une expérience utilisateur soignée.

## Fonctionnalités principales

### Espace Client
- Inscription et connexion sécurisée (mot de passe hashé avec bcrypt)
- Création de réservation avec vérification de disponibilité en temps réel
- Calcul automatique du montant total et acompte minimum (80 %)
- Visualisation de l'historique des réservations avec statuts colorés
- Annulation de réservation (si encore en attente)
- Consultation du planning sommaire d'une salle (7 jours)
- Génération et téléchargement d'un récapitulatif PDF professionnel (avec QR code)

### Espace Administrateur
- Validation / refus des réservations en attente
- Gestion complète des salles (CRUD : Créer, Lire, Mettre à jour, Supprimer)
- Liste des réservations en attente avec informations client
- Export PDF individuel ou global (à venir)
- Statistiques futures (taux d'occupation, CA estimé, etc.)

### Fonctionnalités premium
- Écran d'accueil animé avec messages stylés
- Barre de progression pendant les opérations longues
- Messages chaleureux et personnalisés
- Couleurs et emojis par statut (✅ Acceptée, ⏳ En attente, ❌ Refusée)
- Génération de PDF avec QR code dynamique

## Technologies utilisées

- **Python 3.10+**
- **MySQL** (base de données relationnelle)
- **mysql-connector-python**
- **rich** → interface console moderne et colorée
- **reportlab** → génération PDF professionnelle
- **qrcode[pil]** → QR code intégré dans les PDF
- **bcrypt** → hachage sécurisé des mots de passe

## Prérequis

- Python 3.10 ou supérieur
- MySQL 8.0+ installé et lancé
- Créer une base de données nommée `douta_seck`

## Installation

1. Cloner le projet

```bash
git clone https://github.com/ton-pseudo/projet-douta-seck.git
cd projet-douta-seck
