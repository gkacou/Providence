from django.contrib import admin
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.db.models import Count, Sum, F, Q
from django.forms import CheckboxSelectMultiple
from django.contrib.postgres.aggregates import StringAgg

from .models import (
    ProvUser,
    Membre,
    FamilleCommunaute,
    Communaute,
    Reunion,
    Beneficiaire,
    NatureBesoin,
    Cas,
    Cotisation,
)
from .forms import CasCreationForm, CasChangeForm


# Utilisateur Providence
@admin.register(ProvUser)
class ProvUserAdmin(UserAdmin):
    pass


# Membre Providence
@admin.register(Membre)
class ProvMembreAdmin(UserAdmin):
    model = Membre
    list_display = ('last_name', 'first_name', 'telephone1', 'telephone2', 'adresse', 'email')
    list_display_links = ('last_name', 'first_name',)
    fieldsets = (
        ('Identification', {'fields': ('username', 'password')}),
        ('Informations personnelles',
            {'fields': (
                ('last_name', 'first_name',),
                'email',
                'sexe',
                'date_naissance',
                ('telephone1', 'telephone2',),
                'adresse',
                'date_adhesion',
                'communaute',
                ('activite', 'profession',),
                ('cotisation_social', 'cotisation_mission',),
                'personne_physique',
            )}
        ),
    )
    radio_fields = {'sexe': admin.HORIZONTAL}

    # def get_queryset(self, *args, **kwargs):
    #     return Membre.objects.filter(is_superuser=False)


# Familles d'églises et églises
@admin.register(FamilleCommunaute)
class FamilleCommunauteAdmin(admin.ModelAdmin):
    pass

@admin.register(Communaute)
class CommunauteAdmin(admin.ModelAdmin):
    pass


# Bénéficiaire
@admin.register(Beneficiaire)
class BeneficiaireAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'nombre_cas')
    fieldsets = (
        (None, {
            'fields': (
                ('nom', 'prenoms', 'sexe'),
                ('situation_matrimoniale', 'nb_enfants'),
                ('anciennete_foi', 'communaute',),
                ('profession', 'fonction'),
            )
        }),
    )


class CasReunionListFilter(admin.SimpleListFilter):
    """
    Ce filtre retourne un sous-ensemble de cas, selon la réunion choisie
    """
    # Titre du filtre affiché dans le volet des filtres
    title = 'réunion'

    # Paramètre pour le filtre qui sera utilisé dans l'URL
    parameter_name = 'reunion'

    valeur_defaut = None

    def lookups(self, request, model_admin):
        """
        Retourne une liste de tuples. Le premier élément de chaque tuple
        est le code de la valeur du parèmtre d'URL (en l'occurrence 'reunion')
        Le second élément est le nom exploitable de la réunion
        """
        liste_reunions = []
        queryset = Reunion.objects.all()
        for reunion in queryset:
            liste_reunions.append(
                (str(reunion.pk), reunion.__str__())
            )
        return liste_reunions

    def queryset(self, request, queryset):
        """
        Retourne un queryset filtré selon la valeur fournie
        dans la querystring et récupérable via self.value()
        """
        # Filtrer le queryset selon la valeur demandée
        if self.value():
            return queryset.filter(reunion_id=self.value())
        return queryset

    def value(self):
        """
        Redéfinition de la méthode pour avoir une valeur par défaut
        """
        valeur = super(CasReunionListFilter, self).value()
        # if (valeur is None) and (self.valeur_defaut is None):
        #     # S'il existe au moins une réunion, retourne la plus récente, sinon None.
        #     reunion_recente = Reunion.objects.first()
        #     valeur = None if reunion_recente is None else reunion_recente.id
        #     self.valeur_defaut = valeur
        #     # else:
        #     #     valeur = self.valeur_defaut
        # return str(valeur) if valeur else None

        if valeur is None:
            if self.valeur_defaut is None:
                # S'il existe au moins une réunion, retourne la plus récente, sinon None.
                reunion_recente = Reunion.objects.first()
                valeur = None if reunion_recente is None else reunion_recente.id
                self.valeur_defaut = valeur
            else:
                valeur = self.valeur_defaut
        return str(valeur)

# Cas
@admin.register(Cas)
class CasAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'est_urgent', 'soumis_par', 'classification')
    list_filter = (CasReunionListFilter, 'classification',)
    form = CasChangeForm
    add_form = CasCreationForm
    fieldsets = (
        (None, {
            'fields': (
                ('soumis_par', 'reunion',),
                'urgence',
                ('nom', 'prenoms', 'sexe'),
                ('situation_matrimoniale', 'nb_enfants'),
                ('anciennete_foi', 'communaute',),
                ('profession', 'fonction'),
                ('montant_sollicite', 'sollicitation_externe', 'montant_alloue'),
                ('classification', 'nature'),
                ('description',),
            )
        }),
        ('Suivi du cas', {
            'fields': (
                'suivi',
                'don_remis',
                'compte_rendu',
            )
        })
    )
    add_fieldsets = (
        (None, {
            'fields': (
                'soumis_par',
                'reunion',
                'beneficiaire',
                'classification',
                'urgence',
            )
        }),
    )
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

    def get_changeform_initial_data(self, request):
        reunion = Reunion.objects.all()[0]  # Réunion la plus récente
        return {
            'soumis_par': request.user,
            'reunion' : reunion,
        }

    def get_readonly_fields(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return ('nom', 'prenoms', 'sexe', 'reunion', 'classification',)
        else:
            return []

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Utiliser un formulaire différent lors de la création
        """
        defaults = {}
        if obj is None:   # Si l'objet n'existe pas encore
            defaults['form'] = self.add_form

        defaults.update(kwargs)  # Transférer les autres paramètres dans defaults
        return super().get_form(request, obj, **defaults)

    def response_add(self, request, obj, post_url_continue=None):
        """
        Détermine la classe HttpResponse pour l'étape add_view.
        Il est personnalisé car la création des cas suit
        une logique similaire à celle de la création des utilisateurs
        """
        # Il faut permettre la poursuite de la modification du cas qui vient
        # d'être créé, donc le bouton 'Enregistrer' doit se comporter comme
        # le boutton 'Enregistrer et poursuivre la modif' sauf si :
        # * L'utilisateur a cliqué sur 'Enregistrer et ajouter un autre'
        # * Nous ajoutons un cas depuis un popup
        if '_addanother' not in request.POST and IS_POPUP_VAR not in request.POST:
            request.POST = request.POST.copy()
            request.POST['_continue'] = 1
        return super().response_add(request, obj, post_url_continue)



# Nature de besoin
@admin.register(NatureBesoin)
class NatureBesoinAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'classification')


# Cas (inline) pour affichage dans la page réunion
class CasSocialInline(admin.TabularInline):
    model = Cas
    # extra = 0
    max_num = 0
    can_delete = False
    fields = (
        'est_urgent',
        'nom',
        'prenoms',
        'soumis_par',
        'nature_cas',
        'montant_sollicite',
        'montant_estime',
        'montant_alloue',
    )
    readonly_fields = ('nom', 'prenoms', 'est_urgent', 'nature_cas', 'montant_estime')
    show_change_link = True
    verbose_name = 'social'
    verbose_name_plural = 'social'

    def get_queryset(self, request):
        return super().get_queryset(request)\
            .filter(classification='S')\
            .annotate(_natures=StringAgg("nature__libelle", ", "))\
            .order_by("-urgence")

    def nature_cas(self, obj):
        return obj._natures
    nature_cas.short_description = "Nature(s)"

    def montant_estime(self, obj):
        estime = obj.montant_sollicite * obj.reunion.cotisations_social() // obj.reunion.sollicite_social()
        return estime
    montant_estime.short_description = "Montant estimé"

class CasMissionInline(admin.TabularInline):
    model = Cas
    # extra = 0
    max_num = 0
    can_delete = False
    fields = (
        'est_urgent',
        'nom',
        'prenoms',
        'soumis_par',
        'nature_cas',
        'montant_sollicite',
        'montant_estime',
        'montant_alloue',
    )
    readonly_fields = ('nom', 'prenoms', 'est_urgent', 'nature_cas', 'montant_estime')
    show_change_link = True
    verbose_name = 'mission'
    verbose_name_plural = 'mission'

    def get_queryset(self, request):
        return super().get_queryset(request)\
            .filter(classification='M')\
            .annotate(
                _natures=StringAgg("nature__libelle", ", "),
            )\
            .order_by("-urgence")

    def nature_cas(self, obj):
        return obj._natures
    nature_cas.short_description = "Nature(s)"

    def montant_estime(self, obj):
        estime = obj.montant_sollicite * obj.reunion.cotisations_mission() // obj.reunion.sollicite_mission()
        return estime
    montant_estime.short_description = "Montant estimé"

class CotisationInline(admin.TabularInline):
    model = Cotisation
    fields = ('membre', 'montant_social', 'social_libere', 'montant_mission', 'mission_libere',)
    max_num = 0
    can_delete = False
    readonly_fields = ('membre',)

# Réunion
@admin.register(Reunion)
class ReunionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'nb_cas', 'total_sollicite',)
    readonly_fields = ('nb_cas', 'total_sollicite', 'cotisations_social', 'cotisations_mission',)
    fieldsets = (
        ('Réunion', {
            'fields': (
                'membre_hote',
                'date_reunion',
                ('lieu_reunion', 'nb_cas',),
                ('total_sollicite', 'cotisations_social', 'cotisations_mission')
            ),
            'classes': ('baton-tabs-init', 'baton-tab-inline-cotisations', 'baton-tab-fs-cr', ),
        }),
        # ('Cotisations', {
        #     'fields': ('compte_rendu', 'liste_presence'),
        #     'classes': ('tab-fs-cr',),
        # }),
        ('Compte-rendu', {
            'fields': ('compte_rendu', 'liste_presence'),
            'classes': ('tab-fs-cr',),
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _nb_cas=Count("cas_reunion"),
            _total_sollicite=Sum("cas_reunion__montant_sollicite"),
        )
        return queryset

    def nb_cas(self, obj):
        return obj._nb_cas
    nb_cas.short_description = "Nombre de cas"
    nb_cas.admin_order_field = "_nb_cas"

    def total_sollicite(self, obj):
        return obj._total_sollicite
    total_sollicite.short_description = "Total sollicité"
    total_sollicite.admin_order_field = "_total_sollicite"

    inlines = (CasSocialInline, CasMissionInline, CotisationInline,)