from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Count, Sum, F, Q, Value
from django.db.models.functions import Concat
from django.conf import settings
from django.utils.html import format_html

from tinymce import HTMLField

CHOIX_SEXE = (
    ('F', 'Féminin'),
    ('M', 'Masculin'),
    ('N', 'Non applicable'),
)
CLASSIFICATION_CAS = (
    ('S', 'Social'),
    ('M', 'Mission'),
)


class Communaute(models.Model):
    """
    Famille de communauté chrétienne
    """
    nom = models.CharField(max_length=128, unique=True, verbose_name="nom court")
    nom_long = models.CharField(max_length=128, blank=True, null=True, verbose_name="nom long")

    class Meta:
        verbose_name = "communauté"
        ordering = ("nom",)
        indexes = [
            models.Index(fields=['nom'], name='comm_nom_idx'),
            models.Index(fields=['nom_long'], name='comm_nom_long_idx'),
        ]

    def __str__(self):
        return self.nom


# class Communaute(models.Model):
#     """
#     Communauté chrétienne
#     """
#     famille = models.ForeignKey(FamilleCommunaute, models.CASCADE, verbose_name="groupe")
#     nom = models.CharField(max_length=128, verbose_name="nom de la communauté")

#     class Meta:
#         verbose_name = "communauté chrétienne"
#         verbose_name_plural = "communautés chrétiennes"
#         ordering = ("famille", "nom",)

#     def nom_comunaute(self):
#         return f"{self.famille} {self.nom}"
#     nom_comunaute.admin_order_field = Concat('famille', Value(' '), 'nom')
#     nom_comunaute.short_description = "Communauté"

#     def __str__(self):
#         return f"{self.famille} {self.nom}"


class ProvUser(AbstractUser):
    """
    Utilisateur de l'application
    """
    sexe = models.CharField(null=True, max_length=1, choices=CHOIX_SEXE)
    date_naissance = models.DateField(blank=True, null=True, verbose_name="date de naissance")
    telephone1 = models.CharField(blank=True, null=True, default='', max_length=32, verbose_name="téléphone 1")
    telephone2 = models.CharField(blank=True, null=True, default='', max_length=32, verbose_name="téléphone 2")
    adresse = models.CharField(blank=True, null=True, default='', max_length=250, verbose_name="adresse géographique")
    date_adhesion = models.DateField(blank=True, null=True, verbose_name="date d'adhésion")
    communaute = models.ForeignKey(Communaute, models.SET_NULL, blank=True, null=True, verbose_name="église fréquentée")
    eglise_locale = models.CharField(blank=True, null=True, default='', max_length=128, verbose_name="église locale")
    activite = models.CharField(blank=True, null=True, default='', max_length=128, verbose_name="secteur d'activité")
    profession = models.CharField(blank=True, null=True, default='', max_length=128)
    cotisation_social = models.PositiveIntegerField(blank=True, null=True, verbose_name="montant contribution social")
    cotisation_mission = models.PositiveIntegerField(blank=True, null=True, verbose_name="montant contribution mission")
    personne_physique = models.BooleanField(default=True)
    peut_cotiser = models.BooleanField(default=True, verbose_name="peut cotiser")

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
        ordering = ("last_name", "first_name",)

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
    compte_rendu = HTMLField(null=True, blank=True, verbose_name="compte-rendu de la réunion")
    liste_presence = models.ManyToManyField(ProvUser, blank=True, related_name="presences", verbose_name="membres présents")

    class Meta:
        verbose_name = "réunion"
        ordering = ('-date_reunion',)

    def nombre_cas(self):
        return self.cas_reunion.count()
    nombre_cas.short_description = "Nombre de cas"

    def sollicite_social(self):
        somme = self.cas_reunion.filter(classification='S').\
            aggregate(social=Sum('montant_sollicite'))
        return somme['social']
    sollicite_social.short_description = "Sollicité social"

    def sollicite_mission(self):
        somme = self.cas_reunion.filter(classification='M').\
            aggregate(mission=Sum('montant_sollicite'))
        return somme['mission']
    sollicite_mission.short_description = "Sollicité mission"

    def total_urgence_social(self):
        somme = self.cas_reunion\
            .filter(classification='S')\
            .filter(urgence=True)\
            .aggregate(social=Sum('montant_sollicite'))
        total = somme['social'] if somme['social'] else 0
        return total
    total_urgence_social.short_description = "Urgence social"

    def total_urgence_mission(self):
        somme = self.cas_reunion\
            .filter(classification='M')\
            .filter(urgence=True)\
            .aggregate(mission=Sum('montant_sollicite'))
        total = somme['mission'] if somme['mission'] else 0
        return total
    total_urgence_mission.short_description = "Urgence mission"

    def total_cotisation(self):
        return self.cotisations.aggregate(
            total_social=Sum('montant_social'),
            total_mission=Sum('montant_mission')
        )

    # @property
    def cotisations_social(self):
        return self.total_cotisation()['total_social']
    cotisations_social.short_description = "Cotisations social"

    # @property
    def cotisations_mission(self):
        return self.total_cotisation()['total_mission']
    cotisations_mission.short_description = "Cotisations mission"

    def save(self, *args, **kwargs):
        # Après la création d'une réunion, générer les cotisations des membres
        nouvelle_reunion = self.pk is None
        super().save(*args, **kwargs)  # Procéder à la sauvegarde

        if nouvelle_reunion:
            for membre_prov in Membre.objects.filter(peut_cotiser=True):
                social = membre_prov.cotisation_social if membre_prov.cotisation_social else 0
                mission = membre_prov.cotisation_mission if membre_prov.cotisation_mission else 0
                cotis = Cotisation.objects.create(
                    membre=membre_prov,
                    reunion=self,
                    montant_social=social,
                    montant_mission=mission
                )

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
    sexe = models.CharField(null=True, max_length=1, choices=CHOIX_SEXE)
    communaute = models.ForeignKey(Communaute, models.SET_NULL, blank=True, null=True, verbose_name="communauté fréquentée")
    eglise_locale = models.CharField(blank=True, null=True, default='', max_length=128, verbose_name="église locale")
    situation_matrimoniale = models.CharField(max_length=1, blank=True, null=True, choices=SITUATION_MATRIMONIALE)
    profession = models.CharField(max_length=64, blank=True, null=True)
    fonction = models.CharField(max_length=64, blank=True, null=True)
    nb_enfants = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="nombre d'enfants")
    anciennete_foi = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="ancienneté dans la foi")

    class Meta:
        abstract = True

    def __str__(self):
        prenom = self.prenoms if self.prenoms else ""
        return f"{prenom} {self.nom}"


class Beneficiaire(Entite):
    """
    Bénéficiaire de soutien de Providence (hérite de Entité)
    """

    def nombre_cas(self):
        return self.cas_beneficiaire.count()
    nombre_cas.short_description = "Nombre de cas"

    class Meta:
        verbose_name = "bénéficiaire"
        indexes = [
            models.Index(fields=['nom'], name='benef_nom_idx'),
            models.Index(fields=['prenoms'], name='benef_prenoms_idx'),
        ]


class NatureBesoin(models.Model):
    """
    Nature du besoin (Santé, Subsistance, Scolarité, ...)
    """
    libelle = models.CharField(max_length=20, verbose_name="libellé")
    classification = models.CharField(max_length=1, choices=CLASSIFICATION_CAS, verbose_name="classification")

    class Meta:
        verbose_name = "nature de besoin"
        verbose_name_plural = "natures de besoins"
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
        ('A', 'Annulé'),
    )

    soumis_par = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    reunion = models.ForeignKey(Reunion, models.CASCADE, blank=False, related_name="cas_reunion", verbose_name="réunion")
    beneficiaire = models.ForeignKey(Beneficiaire, models.CASCADE, related_name="cas_beneficiaire", verbose_name="bénéficiaire")
    montant_sollicite = models.PositiveIntegerField(null=True, blank=True, default=0, verbose_name="montant solllicité")
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
        # Si le cas est un cas d'urgence, le montant affecté est automatiquement égal
        # au montant sollicité
        if self.urgence:
            self.montant_alloue = self.montant_sollicite

        # Lors de la création d'un cas, recopier les attributs du bénéficiaire
        if not self.pk:
            benef = self.beneficiaire
            self.nom = benef.nom
            self.prenoms = benef.prenoms
            self.sexe = benef.sexe
            self.communaute = benef.communaute
            self.eglise_locale = benef.eglise_locale
            self.situation_matrimoniale = benef.situation_matrimoniale
            self.profession = benef.profession
            self.fonction = benef.fonction
            self.nb_enfants = benef.nb_enfants
            self.anciennete_foi = benef.anciennete_foi
        super().save(*args, **kwargs)  # Procéder à la sauvegarde

    def est_urgent(self):
        return format_html("&#x2714") if self.urgence else "-"
    est_urgent.short_description = "Cas d'urgence"

    def montant_estime(self):
        pass


class Cotisation(models.Model):
    """
    Cotisation mensuelle d'un membre pour le social et la mission
    """
    membre = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="membre")
    reunion = models.ForeignKey(Reunion, models.CASCADE, related_name="cotisations", verbose_name="réunion")
    montant_social = models.PositiveIntegerField(default=0)
    social_libere = models.BooleanField(default=False, verbose_name="montant social libéré ?")
    montant_mission = models.PositiveIntegerField(default=0)
    mission_libere = models.BooleanField(default=False, verbose_name="montant mission libéré ?")

    class Meta:
        verbose_name = "cotisation du mois"
        verbose_name_plural = "cotisations du mois"

    def __str__(self):
        return ''


# def cotisation_non_liberee(reunion):
#     return Q(reunion=reunion) & Q(social_libere=False) | Q(mission_libere=False)

class AffectationNonLibere(models.Model):
    """
    Affectation des cotisations non libérées
    """
    reunion = models.ForeignKey(
        Reunion,
        on_delete=models.CASCADE,
        related_name="affectations",
        verbose_name="réunion"
    )
    cotisation = models.ForeignKey(
        Cotisation,
        on_delete=models.CASCADE,
        verbose_name="cotisation de"
    )
    collecteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name="collecteurs",
        limit_choices_to={'personne_physique': True},
        verbose_name="Collecté par"
    )
    somme = models.PositiveIntegerField(verbose_name="montant à récupérer")
    cas = models.ForeignKey(
        Cas,
        on_delete=models.CASCADE,
        related_name='affectation_cas',
    )

    class Meta:
        verbose_name = "affectation de cotisation non libérée"
        verbose_name_plural = "affectations des cotisations non libérées"

    def __str__(self):
        return f"{self.cotisation.membre}"


class VueCotisationNonLiberee(models.Model):
    """
    Cotisation mensuelle non libérée (Vue de base de données)
    """
    id = models.IntegerField(primary_key=True, verbose_name="identifiant")
    membre = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        null=True, blank=True,
        db_column="membre_id",
        verbose_name="membre"
    )
    reunion = models.ForeignKey(
        Reunion,
        on_delete=models.DO_NOTHING,
        null=True, blank=True,
        related_name="cotisations_nl",
        db_column="reunion_id",
        verbose_name="réunion"
    )
    montant_social = models.PositiveIntegerField(null=True, blank=True,)
    social_libere = models.BooleanField(null=True, blank=True,verbose_name="montant social libéré ?")
    montant_mission = models.PositiveIntegerField(null=True, blank=True,)
    mission_libere = models.BooleanField(null=True, blank=True,verbose_name="montant mission libéré ?")
    reste_cotis_social = models.IntegerField(null=True, blank=True, verbose_name="reste social")
    reste_cotis_mission = models.IntegerField(null=True, blank=True, verbose_name="reste mission")

    class Meta:
        managed = False
        db_table = "v_cotisation_non_liberee"
        verbose_name = "cotisation du mois non libérée"
        verbose_name_plural = "cotisations du mois non libérées"

    def __str__(self):
        return ""
