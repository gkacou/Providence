from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


CHOIX_SEXE = (
    ('F', 'Féminin'),
    ('M', 'Masculin'),
    ('N', 'Non applicable'),
)


class FamilleCommunauté(models.Model):
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
    famille = models.ForeignKey(FamilleCommunauté, models.CASCADE, verbose_name="groupe")
    nom = models.CharField(max_length=64, verbose_name="nom de la communauté")

    class Meta:
        verbose_name = "communauté chrétienne"
        ordering = ("nom",)

    def __str__(self):
        return self.nom


class ProvUser(AbstractUser):
    """
    Utilisateur de l'application
    """
    sexe = models.CharField(null=True, max_length=1, choices=CHOIX_SEXE)
    date_naissance = models.DateField(blank=True, null=True, verbose_name="date de naissance")
    telephone1 = models.CharField(default='', max_length=14, verbose_name="téléphone 1")
    telephone2 = models.CharField(blank=True, default='', max_length=14, verbose_name="téléphone 2")
    adresse = models.CharField(blank=True, default='', max_length=250, verbose_name="adresse géographique")
    date_adhesion = models.DateField(blank=True, null=True, verbose_name="date d'adhésion")
    communaute = models.ForeignKey(Communaute, models.SET_NULL, blank=True, null=True, verbose_name="église fréquentée")
    activite = models.CharField(blank=True, default='', max_length=64, verbose_name="secteur d'activité")
    profession = models.CharField(blank=True, default='', max_length=64)
    cotisation_social = models.PositiveIntegerField(blank=True, null=True, verbose="montant contribution social")
    cotisation_mission = models.PositiveIntegerField(blank=True, null=True, verbose="montant contribution mission")

    class Meta:
        verbose_name = "utilisateur"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Membre(ProvUser):
    """
    Membre de Providence (classe proxy de la classe ProvUser)
    """
    class Meta:
        proxy = True
        verbose_name = "membre"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Reunion(models.Model):
    """
    Réunion de Providence
    """
    membre_hote = models.ForeignKey(ProvUser, models.CASCADE, verbose_name="membre hôte")
    date_reunion = models.DateField(verbose_name="date de la réunion")
    lieu_reunion = models.CharField(max_length=128, verbose_name="lieu de la réunion")
    compte_rendu = models.TextField(verbose_name="compte-rendu de la réunion")
    liste_presence = models.ManyToManyField(ProvUser, models.DO_NOTHING, verbose_name="membres présents")

    class Meta:
        verbose_name = "réunion"

    def __str__(self):
        return self.membre_hote


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

    nom = models.CharField(max_length=64)
    prenoms = models.CharField(max_length=64, null=True, blank=True, verbose_name="prénoms")
    sexe = models.CharField(null=True, blank=True, max_length=1, choices=CHOIX_SEXE)
    communaute = models.ForeignKey(Communaute, models.SET_NULL, blank=True, null=True, verbose_name="communauté fréquentée")
    situation_matrimoniale = models.CharField(max_length=1, blank=True, null=True, choices=SITUATION_MATRIMONIALE)
    profession = models.CharField(max_length=64, blank=True, null=True)
    fonction = models.CharField(max_length=64, blank=True, null=True)
    nb_enfants = models.PositiveSmallIntegerField(verbose_name="nombre d'enfants")
    anciennete_foi = models.PositiveSmallIntegerField(verbose_name="ancienneté dans la foi")

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

    class Meta:
        verbose_name = "nature de demande"
        ordering = ('libelle')

    def __str__(self):
        return self.libelle


class Cas(Entite):
    """
    Cas présenté pour soutien par Providence
    """
    CLASSIFICATION_CAS = (
        ('S', 'Social'),
        ('M', 'Mission'),
    )
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
    reunion = models.ForeignKey(Reunion, models.CASCADE, verbose_name="réunion")
    beneficiaire = models.ForeignKey(Beneficiaire, models.CASCADE, verbose_name="bénéficiaire")
    montant_sollicite = models.PositiveIntegerField(verbose_name="montant solllicité")
    montant_alloue = models.PositiveIntegerField(verbose_name="montant alloué")
    sollicitation_externe = models.PositiveIntegerField(verbose_name="solllicitation hors Providence")
    classification = models.CharField(max_length=1, choices=CLASSIFICATION_CAS, verbose_name="classification du cas")
    nature = models.ManyToManyField(NatureBesoin, models.DO_NOTHING, verbose_name="nature(s) du cas")
    urgence = models.BooleanField(default=False, verbose_name="cas d'urgence ?")
    description = models.TextField(verbose_name="exposé du cas")
    
    # Les champs suivants concernent le suivi du cas
    suivi = models.CharField(max_length=1, blank=True, null=True, default="O", choices=SUIVI_CAS, verbose_name="suivi du cas")
    don_remis = models.CharField(max_length=1, blank=True, null=True, choices=REMISE_DON, verbose_name="don remis ?")
    compte_rendu = models.TextField(verbose_name="compte-rendu du cas")

    class Meta:
        verbose_name = "cas"


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
