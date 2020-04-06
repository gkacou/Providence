from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


CHOIX_SEXE = (
    ('F', 'Féminin'),
    ('M', 'Masculin'),
    ('N', 'Non applicable'),
)
CLASSIFICATION_CAS = (
    ('S', 'Social'),
    ('M', 'Mission'),
)


class FamilleCommunaute(models.Model):
    """
    Grande famille de communauté chrétienne
    """
    nom = models.CharField(max_length=64, verbose_name="nom")

    class Meta:
        verbose_name = "groupe de communauté"
        ordering = ("nom",)

    def __str__(self):
        return self.nom


class Communaute(models.Model):
    """
    Communauté chrétienne
    """
    famille = models.ForeignKey(FamilleCommunaute, models.CASCADE, verbose_name="groupe")
    nom = models.CharField(max_length=64, verbose_name="nom de la communauté")

    class Meta:
        verbose_name = "communauté chrétienne"
        ordering = ("nom",)

    def __str__(self):
        return f"{self.famille} {self.nom}"


class ProvUser(AbstractUser):
    """
    Utilisateur de l'application
    """
    sexe = models.CharField(null=True, max_length=1, choices=CHOIX_SEXE)
    date_naissance = models.DateField(blank=True, null=True, verbose_name="date de naissance")
    telephone1 = models.CharField(default='', max_length=32, verbose_name="téléphone 1")
    telephone2 = models.CharField(blank=True, default='', max_length=32, verbose_name="téléphone 2")
    adresse = models.CharField(blank=True, default='', max_length=250, verbose_name="adresse géographique")
    date_adhesion = models.DateField(blank=True, null=True, verbose_name="date d'adhésion")
    communaute = models.ForeignKey(Communaute, models.SET_NULL, blank=True, null=True, verbose_name="église fréquentée")
    activite = models.CharField(blank=True, default='', max_length=64, verbose_name="secteur d'activité")
    profession = models.CharField(blank=True, default='', max_length=64)
    cotisation_social = models.PositiveIntegerField(blank=True, null=True, verbose_name="montant contribution social")
    cotisation_mission = models.PositiveIntegerField(blank=True, null=True, verbose_name="montant contribution mission")
    personne_physique = models.BooleanField(default=True)

    class Meta:
        verbose_name = "utilisateur"
        ordering = ("username",)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Membre(ProvUser):
    """
    Membre de Providence (classe proxy de la classe ProvUser)
    """
    class Meta:
        proxy = True
        verbose_name = "membre"
        ordering = ("-first_name",)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Reunion(models.Model):
    """
    Réunion de Providence
    """
    membre_hote = models.ForeignKey(
        ProvUser,
        models.CASCADE,
        related_name="reunions",
        limit_choices_to={'personne_physique': True},
        verbose_name="membre hôte"
    )
    date_reunion = models.DateField(verbose_name="date de la réunion")
    lieu_reunion = models.CharField(null=True, blank=True, max_length=128, verbose_name="lieu de la réunion")
    compte_rendu = models.TextField(null=True, blank=True, verbose_name="compte-rendu de la réunion")
    liste_presence = models.ManyToManyField(ProvUser, blank=True, related_name="presences", verbose_name="membres présents")

    class Meta:
        verbose_name = "réunion"
        ordering = ('-date_reunion',)

    def __str__(self):
        return f"{self.date_reunion.strftime('%d/%m/%Y')} - {self.membre_hote} ({self.lieu_reunion})"


class Entite(models.Model):
    """
    Entité à soutenir ou soutenue par Providence
    """
    SITUATION_MATRIMONIALE = (
        ('C', 'Célibataire'),
        ('M', 'Marié(e)'),
        ('D', 'Divorcé(e)'),
        ('V', 'Veuve / Veuf)'),
    )

    nom = models.CharField(null=True, blank=True, max_length=64)
    prenoms = models.CharField(max_length=64, null=True, blank=True, verbose_name="prénoms")
    sexe = models.CharField(null=True, blank=True, max_length=1, choices=CHOIX_SEXE)
    communaute = models.ForeignKey(Communaute, models.SET_NULL, blank=True, null=True, verbose_name="communauté fréquentée")
    situation_matrimoniale = models.CharField(max_length=1, blank=True, null=True, choices=SITUATION_MATRIMONIALE)
    profession = models.CharField(max_length=64, blank=True, null=True)
    fonction = models.CharField(max_length=64, blank=True, null=True)
    nb_enfants = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="nombre d'enfants")
    anciennete_foi = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="ancienneté dans la foi")

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.prenoms} {self.nom}"


class Beneficiaire(Entite):
    """
    Bénéficiaire de soutien de Providence (hérite de Entité)
    """
    class Meta:
        verbose_name = "bénéficiaire"


class NatureBesoin(models.Model):
    """
    Nature du besoin (Santé, Subsistance, Scolarité, ...)
    """
    libelle = models.CharField(max_length=20, verbose_name="libellé")
    classification = models.CharField(max_length=1, choices=CLASSIFICATION_CAS, verbose_name="classification")

    class Meta:
        verbose_name = "nature de demande"
        ordering = ('classification', 'libelle',)

    def __str__(self):
        return self.libelle


class Cas(Entite):
    """
    Cas présenté pour soutien par Providence
    """
    REMISE_DON = (
        ('O', 'Oui'),
        ('N', 'Non'),
        ('P', 'Partiellement'),
    )
    SUIVI_CAS = (
        ('O', 'Ouvert'),
        ('C', 'Clos'),
        ('R', 'Reconduit'),
        ('P', 'Reporté'),
    )

    soumis_par = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    reunion = models.ForeignKey(Reunion, models.CASCADE, blank=False, verbose_name="réunion")
    beneficiaire = models.ForeignKey(Beneficiaire, models.CASCADE, verbose_name="bénéficiaire")
    montant_sollicite = models.PositiveIntegerField(null=True, blank=True, verbose_name="montant solllicité")
    montant_alloue = models.PositiveIntegerField(null=True, blank=True, verbose_name="montant alloué")
    sollicitation_externe = models.PositiveIntegerField(null=True, blank=True, verbose_name="solllicitation hors Providence")
    classification = models.CharField(max_length=1, default='S', choices=CLASSIFICATION_CAS, verbose_name="classification du cas")
    nature = models.ManyToManyField(NatureBesoin, blank=True, verbose_name="nature(s) du cas")
    urgence = models.BooleanField(default=False, verbose_name="cas d'urgence ?")
    description = models.TextField(null=True, blank=True, verbose_name="exposé du cas")
    
    # Les champs suivants concernent le suivi du cas
    suivi = models.CharField(max_length=1, blank=True, null=True, default="O", choices=SUIVI_CAS, verbose_name="suivi du cas")
    don_remis = models.CharField(max_length=1, blank=True, null=True, choices=REMISE_DON, verbose_name="don remis ?")
    compte_rendu = models.TextField(null=True, blank=True, verbose_name="compte-rendu du cas")

    class Meta:
        verbose_name = "cas"
        verbose_name_plural = "cas"
        unique_together = ('reunion', 'beneficiaire')

    def save(self, *args, **kwargs):
        # Lors de la création d'un objet, copier les attributs du bénéficiaire
        if not self.pk:
            benef = self.beneficiaire
            self.nom = benef.nom
            self.prenoms = benef.prenoms
            self.sexe = benef.sexe
            self.communaute = benef.communaute
            self.situation_matrimoniale = benef.situation_matrimoniale
            self.profession = benef.profession
            self.fonction = benef.fonction
            self.nb_enfants = benef.nb_enfants
            self.anciennete_foi = benef.anciennete_foi
        super().save(*args, **kwargs)  # Procéder à la sauvegarde


class Cotisation(models.Model):
    """
    Cotisation mensuelle d'un membre pour le social et la mission
    """
    membre = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="membre")
    reunion = models.ForeignKey(Reunion, models.CASCADE, verbose_name="réunion")
    montant_social = models.PositiveIntegerField()
    social_libere = models.BooleanField(verbose_name="montant social libéré ?")
    montant_mission = models.PositiveIntegerField()
    mission_libere = models.BooleanField(verbose_name="montant mission libéré ?")

    class Meta:
        verbose_name = "cotisation mensuelle"


class AffectationNonLibere(models.Model):
    """
    Affectation des cotisations non libérées
    """
    cotisation = models.ForeignKey(
        Cotisation,
        on_delete=models.DO_NOTHING,
        verbose_name="cotisation"
    )
    cotisant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name="cotisants",
        verbose_name="cotisant"
    )
    somme = models.PositiveIntegerField(verbose_name="montant à récupérer")
    collecteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name="collecteurs",
        verbose_name="collecteur"
    )

    class Meta:
        verbose_name = "affectation cotisation non libérée"

