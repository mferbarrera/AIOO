from django import forms
from projects import models as pm

class ExampleForm(forms.Form):
    like_website = forms.TypedChoiceField(
        label = "Do you like this website?",
        choices = ((1, "Yes"), (0, "No")),
        coerce = lambda x: bool(int(x)),
        widget = forms.RadioSelect,
        initial = '1',
        required = True,
    )

    favorite_food = forms.CharField(
        label = "What is your favorite food?",
        max_length = 80,
        required = True,
    )

    favorite_color = forms.CharField(
        label = "What is your favorite color?",
        max_length = 80,
        required = True,
    )

    favorite_number = forms.IntegerField(
        label = "Favorite number",
        required = False,
    )

    notes = forms.CharField(
        label = "Additional notes or feedback",
        required = False,
    )

class ProjectForm(forms.ModelForm):

    def wizard(self):
        structure = [
            {
                'id': 1,
                'name': 'Paso 1',
                'label': 'General',
                'reference': 'Información general',
                'fields' : [
                    [self['year'],self['country']],
                    [self['ptype'],self['priority']],
                ],
            },
            {
                'id': 2,
                'name': 'Paso 2',
                'label': 'Titulo',
                'reference': 'Titulo del proyecto',
                'fields': [
                    [self['name'],self['reference']],
                    [self['label']]
                ]
            },
            {
                'id': 3,
                'name': 'Paso 3',
                'label': 'Objetivos',
                'reference': 'Justificación y objetivos del proyecto',
                'fields': [
                    [self['objective'],self['justify']],
                    [self['background']]
                ]
            },
            {
                'id': 4,
                'name': 'Paso 4',
                'label': 'WBS/Entregables',
                'reference': 'WBS y entregables',
                'fields': [
                    [self['wbs'],self['pds']],
                    [self['totallocations']]
                ]

            },
        ]
        return structure


    class Meta:
        model   = pm.Project
        fields  = ('year','ptype','name','reference','objective','justify','background','country','label','priority','wbs','pds','totallocations')
        widgets = {
            'summary': forms.Textarea(attrs={'rows':2,'cols':15}),
        }

class ProjectLocationForm(forms.ModelForm):
    location__id=forms.CharField(required=False)

    class Meta:
        model   = pm.ProjectLocation
        fields  = ('planningref','location__id','nodetype','priority')

class ProjectEventForm(forms.ModelForm):
    #start       = forms.DateField(widget=forms.SelectDateWidget())
    #end         = forms.DateField(widget=forms.SelectDateWidget())
    eventid     = forms.IntegerField()

    class Meta:
        model   = pm.ProjectEvent
        fields  = ('eventid','description','progress','start','end')