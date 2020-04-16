import locale
from sys import platform
from django.contrib import admin
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.db.models import Count, Sum, F, Q
from django.forms import CheckboxSelectMultiple
from django.forms.widgets import TextInput
from django.contrib.postgres.aggregates import StringAgg
from django.utils.html import format_html
from django.urls import resolve

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
    VCotisationNonLiberee,
    AffectationNonLibere,
)
from .forms import CasCreationForm, CasChangeForm, CotisationChoiceField


if platform == "linux" or platform == "linux2":
    locale.setlocale( locale.LC_ALL, '')
elif platform == "darwin":
    locale.setlocale( locale.LC_ALL, 'fr_FR')
elif platform == "win32":
    locale.setlocale( locale.LC_ALL, 'French_France.1252')


def formatte_nombre(valeur, couleur=None, gras=False):
    """
    Formatte des valeurs de montant pour un affichage correct dans l'interface
    """
    style_couleur = f'color: {couleur};' if couleur else ''
    style_gras = f'font-weight: bold;' if gras else ''
    montant = f'{valeur:n}' if valeur is not None else '-'
    return format_html(f'<div style="{style_gras}{style_couleur}text-align: right;">{montant}</div>')


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
    formfield_overrides = {
        models.DecimalField: {'widget': TextInput(attrs={'class': 'text-right'})},
    }
    ordering = ('nom', 'prenoms')

    def get_queryset(self, request):
        return super().get_queryset(request)\
            .filter(classification='S')\
            .annotate(_natures=StringAgg("nature__libelle", ", "))\
            .order_by("-urgence")

    def nature_cas(self, obj):
        return obj._natures
    nature_cas.short_description = "Nature(s)"

    def montant_estime(self, obj):
        if obj.urgence:
            estime = obj.montant_sollicite
        else:
            urgence_social = obj.reunion.total_urgence_social()
            cotis_dispo = obj.reunion.cotisations_social() - urgence_social
            sollicite = obj.reunion.sollicite_social() - urgence_social
            estime = obj.montant_sollicite * cotis_dispo // sollicite
        return formatte_nombre(estime)
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
    formfield_overrides = {
        models.DecimalField: {'widget': TextInput(attrs={'class': 'text-right'})},
    }
    ordering = ('nom', 'prenoms')

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
        if obj.urgence:
            estime = obj.montant_sollicite
        else:
            urgence_mission = obj.reunion.total_urgence_mission()
            cotis_dispo = obj.reunion.cotisations_mission() - urgence_mission
            sollicite = obj.reunion.sollicite_mission() - urgence_mission
            estime = obj.montant_sollicite * cotis_dispo // sollicite
        return formatte_nombre(estime)
    montant_estime.short_description = "Montant estimé"

class CotisationInline(admin.TabularInline):
    model = Cotisation
    fields = ('membre', 'montant_social', 'social_libere', 'montant_mission', 'mission_libere',)
    max_num = 0
    can_delete = False
    readonly_fields = ('membre',)

class CotisationNonLibereInline(admin.TabularInline):
    model = VCotisationNonLiberee
    fields = ('membre', 'montant_social_fmt', 'social_libere', 'montant_mission_fmt', 'mission_libere',)
    max_num = 0
    extra = 0
    can_delete = False
    readonly_fields = ('membre', 'montant_social_fmt', 'social_libere', 'montant_mission_fmt', 'mission_libere',)

    def montant_social_fmt(self, obj):
        return formatte_nombre(obj.montant_social)
    montant_social_fmt.short_description = "Montant social"

    def montant_mission_fmt(self, obj):
        return formatte_nombre(obj.montant_mission)
    montant_mission_fmt.short_description = "Montant mission"

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

class AffectationNonLibereInline(admin.TabularInline):
    model = AffectationNonLibere
    extra = 0
    # form = AffectationNonLibereForm
    fields = (
        'reunion',
        'cotisation',
        'collecteur',
        'somme',
        'cas',
        'classification',
    )
    readonly_fields = ('classification',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cas')

    def classification(self, obj):
        return obj.cas.get_classification_display()
    # classification.short_description = "Classification"

    def get_parent_object_from_request(self, request):
        """
        Returns the parent object from the request or None.

        Note that this only works for Inlines, because the `parent_model`
        is not available in the regular admin.ModelAdmin as an attribute.
        """
        resolved = resolve(request.path_info)
        if resolved.kwargs:
            return self.parent_model.objects.get(pk=resolved.kwargs['object_id'])
        return None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "cotisation":
            return CotisationChoiceField(
                queryset=Cotisation.objects.filter(
                   Q(social_libere=False) | Q(mission_libere=False),
                    reunion=self.get_parent_object_from_request(request)
                )
            )
        
        if db_field.name == "cas":
            kwargs["queryset"] = Cas.objects.filter(
                reunion=self.get_parent_object_from_request(request)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Réunion
@admin.register(Reunion)
class ReunionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'nb_cas', 'total_sollicite',)
    readonly_fields = (
        'nb_cas',
        'total_sollicite',
        'total_soll_social',
        'total_soll_mission',
        'cotis_social',
        'cotis_mission',
        'disponible_social',
        'disponible_mission',
    )
    fieldsets = (
        ('Réunion', {
            'fields': (
                ('date_reunion', 'membre_hote', 'lieu_reunion', 'nb_cas',),
                ('total_soll_social', 'total_soll_mission',),
                ('cotis_social', 'cotis_mission'),
                ('disponible_social', 'disponible_mission',)
            ),
            'classes': (
                'baton-tabs-init',
                'baton-tab-inline-cotisations',
                'baton-tab-group-inline-cotisations_nl--inline-affectations',
                'baton-tab-fs-cr',
            ),
        }),
        ('Compte-rendu', {
            'fields': ('compte_rendu', 'liste_presence'),
            'classes': ('tab-fs-cr',),
        }),
    )
    inlines = (
        CasSocialInline,
        CasMissionInline,
        CotisationInline,
        CotisationNonLibereInline,
        AffectationNonLibereInline,
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _nb_cas=Count("cas_reunion"),
            _total_sollicite=Sum("cas_reunion__montant_sollicite"),
            _total_soll_social=Sum("cas_reunion__montant_sollicite", filter=Q(cas_reunion__classification='S')),
            _total_soll_mission=Sum("cas_reunion__montant_sollicite", filter=Q(cas_reunion__classification='M')),
        )
        return queryset

    def nb_cas(self, obj):
        return formatte_nombre(obj._nb_cas)
    nb_cas.short_description = "Nombre de cas"
    nb_cas.admin_order_field = "_nb_cas"

    def total_sollicite(self, obj):
        return formatte_nombre(obj._total_sollicite)
    total_sollicite.short_description = "Total sollicité"
    total_sollicite.admin_order_field = "_total_sollicite"

    def total_soll_social(self, obj):
        return formatte_nombre(obj._total_soll_social)
    total_soll_social.short_description = "Sollicité social"
    total_soll_social.admin_order_field = "_total_soll_social"

    def total_soll_mission(self, obj):
        return formatte_nombre(obj._total_soll_mission)
    total_soll_mission.short_description = "Sollicité mission"
    total_soll_mission.admin_order_field = "_total_soll_mission"

    def cotis_social(self, obj):
        return formatte_nombre(obj.cotisations_social())
    cotis_social.short_description = "Cotisations social"

    def cotis_mission(self, obj):
        return formatte_nombre(obj.cotisations_mission())
    cotis_mission.short_description = "Cotisations mission"

    def disponible_social(self, obj):
        affecte = obj.cas_reunion\
            .filter(classification='S')\
            .filter(urgence=False)\
            .aggregate(total=Sum('montant_alloue'))
        alloue = affecte['total'] if affecte['total'] else 0
        disponible = obj.cotisations_social() - obj.total_urgence_social() - alloue
        couleur = 'green' if disponible >= 0 else 'red'
        return formatte_nombre(disponible, couleur, gras=True)
    disponible_social.short_description = "Reliquat social"

    def disponible_mission(self, obj):
        affecte = obj.cas_reunion\
            .filter(classification='M')\
            .filter(urgence=False)\
            .aggregate(total=Sum('montant_alloue'))
        alloue = affecte['total'] if affecte['total'] else 0
        disponible = obj.cotisations_mission() - obj.total_urgence_mission() - alloue
        couleur = 'green' if disponible >= 0 else 'red'
        return formatte_nombre(disponible, couleur, gras=True)
    disponible_mission.short_description = "Reliquat mission"

    class Media:
        css = { "all" : ("admin/css/hide_admin_original.css",) }
