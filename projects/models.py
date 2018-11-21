#from djongo import models
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime,timedelta
from datetime import date as ddate
from django.utils import timezone
import os, secrets, uuid, json, calendar


# Shared Choices
STAGE_SLOT_RANGE=range(-5,12)

ISO3166 = (
	('GT', 'Guatemala'),
	('SV', 'El Salvador'),
	('HN', 'Honduras'),
	('NI', 'Nicaragua'),
	('CR', 'Costa Rica'),
	('PA', 'Panama'),
)

ISO3166_REGIONTYPE = (
	('AR','Región autónoma'),
	('DE','Departamento'),
	('IR','Región indigena'),
	('PR','Provincia')
)

ISO4217 = (
	('USD', 'Dollar'),
	('GTQ', 'Quetzal'),
	('HNL', 'Lempira'),
	('NIO', 'Cordoba'),
	('CRC', 'Colon'),
	('PAB', 'Balboa'),
)

ICC2010_ALLOCATION = (
	('EXW', 'Ex Works'),
	('FCA', 'Free CArrier'),
	('CPT', 'Carriage Paid To'),
	('CIP', 'Carriage An Insurance Paid to'),
	('DAT', 'Delivered At Terminal'),
	('DAP', 'Delivered At Place'),
	('DDP', 'Delivered Duty Paid'),

)

ICC2010_RISK = (
	('FAS', 'Free Alongside Ship'),
	('FOB', 'Free on Board'),
	('CFR', 'Cost and Freight'),
	('CIF', 'Cost, Insurance & Freight')
)

# Shared Tools

def GetImagePath(instance,filename):

	return os.path.join('photos', str(instance.id), filename)

def GetSerialModel(KMODEL,SERIALCHOICES,RELATED):

	json_model = {}
	for f in KMODEL._meta.get_fields():
		if not (f.many_to_many or f.one_to_many or f.many_to_one):
			value=eval('KMODEL.%s'%f.name)
			if f.name in SERIALCHOICES:
				value=SERIALCHOICES[f.name][value]
			json_model[f.name]=value
		else:
			fname=f.name
			if f.many_to_one:
				fname=RELATED['many_to_one'][f.name]['name']
				value=eval('KMODEL.%s.%s'%(f.name,RELATED['many_to_one'][f.name]['value']))
				json_model[fname]=value
	return json_model


# Create your models here.

# Units models

class Units(models.Model):
	UNITSCHOICES = (
		('km','Kilometros'),
		('m','Metros'),
		('cm','Centimetros'),
		('in','Pulgadas'),
		('Puertos','Puertos'),
		('SFP','SFP'),
		('Tarjetas','Tarjetas'),
		('Chasis','Chasis'),
		('Rack','Rack'),
		('Switch','Switch'),
		('Router','Router'),
		('Servidor','Servidor')
	)
	UNITTYPE = (
		('LN','Longitud'),
		('WG','Peso'),
		('NE','Equipo de red'),
		('SW','Software'),
		('LI','Licencia'),
		('SR','Servicio')
	)

	name  	= models.CharField(max_length=100,choices=UNITSCHOICES)
	utype 	= models.CharField(max_length=2,choices=UNITTYPE)

	def __str__(self):
		return self.name

# Location models

class Country(models.Model):

	name = models.CharField(max_length=100)
	isoname = models.CharField(max_length=2,choices=ISO3166)
	isocurrency = models.CharField(max_length=3,choices=ISO4217)

	def __str__(self):
		return self.name

class Region(models.Model):
	name 	  = models.CharField(max_length=100)
	isotype   = models.CharField(max_length=2,choices=ISO3166_REGIONTYPE)
	isoname   = models.CharField(max_length=6)
	country   = models.ForeignKey(Country, on_delete=models.CASCADE)

	def __str__(self):
		return '%s, %s'%(self.isoname,self.name)

class City(models.Model):
	name = models.CharField(max_length=100)
	region = models.ForeignKey(Region, on_delete=models.CASCADE)

	def __str__(self):
		return '%s, %s %s'%(self.name,self.region.name,self.region.country.isoname) 

class Company(models.Model):
	COMPANYCLASS = (
		('O','Propietario'),		
		('P','Proveedor'),
		('V','Virtual'),
	)

	name         = models.CharField(max_length=100)
	address      = models.CharField(max_length=100)
	companyclass = models.CharField(max_length=1,choices=COMPANYCLASS)
	countries    = models.ManyToManyField(Country)
	contact      = models.ForeignKey(User,on_delete=models.CASCADE)

	def __str__(self):
		return self.name

class CompanyFamilyArea(models.Model):
	AREAFAMILYCHOICES = (
		('PLAFJA','Planificación'),
		('PROFJA','Proyectos'),
		('PLAINF','Planificación infraestructura'),
		('PROINF','Proyectos infraestructura'),
		('CONINF','Construcción infraestructura'),
		('COMPRA','Compras'),
		('IMPLAN','Implantación'),
		('PROVDR','Proveedor venta'),
		('PROINF','Proveedor implementación')
	)

	company = models.ForeignKey(Company,on_delete=models.CASCADE)
	name 	= models.CharField(max_length=6,choices=AREAFAMILYCHOICES)

	def __str__(self):
		return self.get_name_display()

class CompanyArea(models.Model):
	
	company = models.ForeignKey(Company,on_delete=models.CASCADE)
	name    = models.CharField(max_length=100)
	family  = models.ForeignKey(CompanyFamilyArea,on_delete=models.CASCADE,blank=True,null=True)

	def __str__(self):
		return u'%s/%s'%(self.company.name,self.name)

class UserProfile(models.Model):
	LEVELCHOICES = (
		(1,'Silver'),
		(10,'Gold'),
		(100,'Platinum'),
		(1000,'Rhodium'),
		(10000,'Diamond'),
		(100000,'Endohedral'),
		(1000000,'Antimatter')
	)

	user      = models.ForeignKey(User,on_delete=models.CASCADE)
	area      = models.ForeignKey(CompanyArea,on_delete=models.CASCADE)
	country   = models.ForeignKey(Country,on_delete=models.CASCADE)
	level     = models.IntegerField(default=1,choices=LEVELCHOICES)
	profile   = models.IntegerField(default=0)
	phone     = models.CharField(max_length=20,default="")
	phone_alt = models.CharField(max_length=20,default="") 

	def __str__(self):
		return r'%s %s %s'%(self.user.username,self.user.first_name,self.user.last_name)

	def getareaowners(self):
		users=[]
		if self.level<1000:
			users=UserProfile.objects.filter(area=self.area, level__lte=self.level)
		if self.level>=1000:
			users=UserProfile.objects.filter(area__family=self.area.family, level__lte=self.level)
		return users

class RequestUser(models.Model):
	username     = models.CharField(max_length=20,default="")
	first_name	 = models.CharField(max_length=100,default="")
	last_name    = models.CharField(max_length=100,default="")
	email  	  	 = models.EmailField(max_length=254,default="")
	phone 		 = models.CharField(max_length=20)
	phone_alt	 = models.CharField(max_length=20)
	company      = models.CharField(max_length=20,default="CLARO")
	area         = models.CharField(max_length=100,default="Planificación fija")
	country      = models.CharField(max_length=2,default="GT")
	created      = models.DateTimeField(auto_now=True,editable=False)
	authorized   = models.BooleanField(default=False)
	authorizedby = models.ForeignKey(UserProfile,on_delete=models.CASCADE,null=True,blank=True)
	status   	 = models.CharField(max_length=100,default="")
	acceptterms	 = models.BooleanField(default=True)

	def __str__(self):
		return r'%s %s %s'%(self.created.isoformat(),self.username,self.company)

	def save(self,*args, **kwargs):

		if self.authorized:
			try:
				if User.objects.get(username=self.username) is None:
					userpassword = secrets.token_urlsafe(10)
					user = User.objects.create_user()
					user.save()
					user.set_password(userpassword)
					

			except:
				self.authorized=False
		super(RequestUser, self).save(*args, **kwargs)

		



class Product(models.Model):

	partnumber  = models.CharField(max_length=150)
	sapcode     = models.CharField(max_length=50)
	description = models.CharField(max_length=100)
	vendor      = models.ForeignKey(Company,on_delete=models.CASCADE)
	created     = models.DateField(auto_now_add=True,editable=False)
	updated     = models.DateTimeField(auto_now=True,editable=False)
	enabled     = models.BooleanField(default=True)

	def __str__(self):
		return self.partnumber

# CAPEX Models


class CAPEXStructure(models.Model):

	VALIDYEARS = (
		(2019,'Año en curso'),
		(2020,'Año siguiente')
	)

	STRUCTURETYPE = (
		('S','Structure'),
		('T','Transaction')
	)


	year            = models.IntegerField(choices=VALIDYEARS)
	name            = models.CharField(max_length=10,editable=False)
	reference       = models.CharField(max_length=100)
	created         = models.DateField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)
	structuretype   = models.CharField(max_length=1,choices=STRUCTURETYPE)
	enabled         = models.BooleanField(default=False)

	def save(self, *args, **kwargs):
		if not self.name:
			try:
				laststructure=CAPEXStructure.objects.filter(year=self.year,structuretype=self.structuretype).order_by('-name')[0]
				structureid='{:03d}'.format(int(laststructure.name[1:4])+1)
				self.name=r'R%s%s-%s'%(structureid,self.structuretype,str(self.year)[2:])
			except:
				self.name=r'R%s%s-%s'%("001",self.structuretype,str(self.year)[2:])

		super(CAPEXStructure, self).save(*args, **kwargs)			

	def __str__(self):
		return r'%s'%(self.name)

class CAPEXIO(models.Model):
	LABELCHOICES = (
		('B','Blue'),
		('G','Grey'),
		('W','White'),
		('Y','Yellow')
	)

	structure       = models.ForeignKey(CAPEXStructure,on_delete=models.CASCADE)
	country         = models.ForeignKey(Country,on_delete=models.CASCADE)
	linenumber		= models.IntegerField(default=10)
	colorlabel		= models.CharField(max_length=1,default="Y",choices=LABELCHOICES)
	classification  = models.CharField(max_length=20,blank=True,null=True)
	capexio         = models.CharField(max_length=10,blank=True,null=True)
	capexamx        = models.CharField(max_length=10,blank=True,null=True)
	businessarea    = models.CharField(max_length=10,blank=True,null=True)
	macro           = models.CharField(max_length=10,blank=True,null=True)
	project         = models.CharField(max_length=50,blank=True,null=True)
	subproject      = models.CharField(max_length=50,blank=True,null=True)
	iopriority      = models.CharField(max_length=10,blank=True,null=True)
	AB              = models.CharField(max_length=10,blank=True,null=True)
	SAP             = models.CharField(max_length=20,blank=True,null=True)
	vendor          = models.CharField(max_length=10,blank=True,null=True)
	projectlabel    = models.CharField(max_length=140,blank=True,null=True)
	metric			= models.CharField(max_length=100,default="#Unidades")
	units			= models.DecimalField(max_digits=20,decimal_places=2,default=0)
	unitarycost		= models.DecimalField(max_digits=20,decimal_places=2,default=0)
	ammount			= models.DecimalField(max_digits=20,decimal_places=2,default=0)
	support         = models.CharField(max_length=300,blank=True,null=True)
	owner           = models.CharField(max_length=100,blank=True,null=True)
	
	def __str__(self):
		return r'%s@%s.%s'%(self.capexio,self.structure.name,self.country.isoname)




# Projects Model

class WBS(models.Model):

	name 		 = models.CharField(max_length=100)
	enabled		 = models.BooleanField(default=True)

	def __str__(self):
		return self.name

	def create_goals(self):
		stages=Stage.objects.filter(wbs=self)
		if not StageGoal.objects.filter(stage__in=stages):
			for stage in stages:
				for slot in STAGE_SLOT_RANGE:
					StageGoal.objects.create(stage=stage,slot=slot,goal=0)

	def delete_goals(self):
		stages=Stage.objects.filter(wbs=self)
		for stagegoal in StageGoal.objects.filter(stage__in=stages):
			stagegoal.delete()
		

class Stage(models.Model):
	NODETYPECHOICES = (
		('G','Global'),
		('S','Sitio')
	)

	ntype 		  = models.CharField(max_length=1,choices=NODETYPECHOICES)
	nlevel		  = models.IntegerField(default=10)
	ntitle   	  = models.CharField(max_length=100)
	nuuid 		  = models.UUIDField(default=uuid.uuid4,blank=True)
	wbs 	 	  = models.ForeignKey(WBS,on_delete=models.CASCADE)
	deliverable	  = models.CharField(max_length=200)
	areafamily    = models.ForeignKey(CompanyFamilyArea,on_delete=models.CASCADE)

	def __str__(self):
		return r'%d %s %s/%s'%(self.nlevel,self.ntype,self.ntitle,self.areafamily.name)

	def startdate(self,year):
		startslot=StageGoal.objects.filter(goal=0,stage=self).order_by('slot')[0].slot
		startmonth=startslot if startslot>0 else 13+startslot
		startyear =int(year) if startslot>0 else int(year)-1
		return datetime(startyear,startmonth,1,8,0,0)

	def enddate(self,year):
		endslot=StageGoal.objects.filter(goal=100,stage=self).order_by('-slot')[0].slot
		endmonth=endslot if endslot>0 else endslot+13
		endyear =int(year) if endslot>0 else int(year)-1
		endday = calendar.monthrange(endyear,endmonth)[1]
		return datetime(endyear,endmonth,endday,18,0,0)


class StageGoal(models.Model):
	stage    	  = models.ForeignKey(Stage,on_delete=models.CASCADE)
	slot 	      = models.IntegerField(default=0)
	goal     	  = models.DecimalField(max_digits=5,decimal_places=2)


class ProjectDeliverableSchema(models.Model):
	name 		  = models.CharField(max_length=100)
	enabled 	  = models.BooleanField(default=True)

	def __str__(self):
		return self.name

class Deliverable(models.Model):
	NODETYPECHOICES = (
		('G','Global'),
		('S','Sitio')
	)

	DELIVERABLETYPECHOICES = (
		('S','Servicio'),
		('D','Documentos'),
		('C','Consultoría'),
		('H','Hardware'),
		('L','Licencias'),
		('S','Software'),
		('M','Materiales')

	)

	pds 	      = models.ForeignKey(ProjectDeliverableSchema,on_delete=models.CASCADE)
	dtype 		  = models.CharField(max_length=1,choices=NODETYPECHOICES)
	dlevel	      = models.IntegerField(default=10)
	dtitle	 	  = models.CharField(max_length=100)
	areafamily    = models.ForeignKey(CompanyFamilyArea,on_delete=models.CASCADE)

class Location(models.Model):
	LOCATIONCLASS=(
		('W','Bodega'),
		('O','Sitio propio'), 
		('A','Bodega Proveedor'), 
		('V','Sitio Virtual'), 
		('R','Sitio arrendado'),
		('C','Celda'),
		('P','Poste')
	)
	name          = models.CharField(max_length=100)
	company       = models.ForeignKey(Company,on_delete=models.CASCADE)
	city          = models.ForeignKey(City, on_delete=models.CASCADE)
	address       = models.CharField(max_length=200,blank=True,null=True)
	locationclass = models.CharField(max_length=1,choices=LOCATIONCLASS)
	uuid          = models.UUIDField(default=uuid.uuid4,editable=False)
	nemonic       = models.CharField(max_length=10,blank=True,null=True)
	sapsite       = models.CharField(max_length=10,blank=True,null=True)
	sapcenter     = models.CharField(max_length=10,blank=True,null=True)
	lat           = models.FloatField(blank=True,null=True)
	lon           = models.FloatField(blank=True,null=True)

	def __str__(self):
		return r'%s,%s %s'%(self.name,self.city,self.city.region.country.isoname)


class Project(models.Model):
	PROJECTTYPE=(
		('AC','Acceso'),
		('AM','AMX'),
		('AP','Aplicaciones'),
		('CO','Core'),
		('DI','Distribución'),
		('LB','Laboratorio'),
		('VI','Video')
	)

	YEARS=(
		(2019,'2019'),
		(2020,'2020')
	)

	STATUS = (
		('DP','Diseño'),
		('QP','Cotización'),
		('QA','SAP-Compras'),
		('IP','Implementación'),
		('CP','Capitalizado'),
		('PR','Rechazado')
	)

	LABEL = (
		('Normal','Normal'),
		('Multimedia','Multimedia'),
		('IP+Fotónico','IP+Fotónico'),
	)

	pid             = models.CharField(max_length=8,editable=False)
	year 	 		= models.IntegerField("Año de ejecución",choices=YEARS)
	created         = models.DateField(auto_now_add=True,editable=False)
	updated         = models.DateTimeField(auto_now=True,editable=False)
	ptype           = models.CharField("Tipo de proyecto",max_length=2,choices=PROJECTTYPE)
	name            = models.CharField("Titulo",max_length=200)
	reference       = models.CharField("Referencia",max_length=200,blank=True)
	owner		    = models.ManyToManyField(UserProfile,verbose_name="Tripulación")
	country         = models.ForeignKey(Country,on_delete=models.CASCADE,verbose_name="Pais")
	label           = models.CharField("Etiqueta",max_length=100,default="Normal",choices=LABEL)
	priority        = models.IntegerField("Prioridad",default=100)
	objective       = models.TextField("Objetivo",max_length=5000,default="#Objetivo")
	justify         = models.TextField("Justificación",max_length=5000,default="#Justificación")
	status			= models.CharField("Estatus",max_length=2,choices=STATUS,default='DP')
	wbs				= models.ForeignKey(WBS,on_delete=models.CASCADE,verbose_name="WBS")
	background 		= models.TextField("Antecedentes",max_length=5000,default="#Antecedentes",blank=True,null=True)
	totallocations  = models.IntegerField("Total de sitios",default=0)
	structure 		= models.BooleanField(default=False,editable=False)
	pds             = models.ForeignKey(ProjectDeliverableSchema,on_delete=models.CASCADE,verbose_name="Entregables")


	def status_icon(self):
		STATUSICONS = {
			'DP':'fa-drafting-compass',
			'QP':'fa-rocket',
			'QA':'fa-shopping-basket',
			'IP':'fa-paper-plane',
			'CP':'fa-money-bill',
			'PR':'fa-ban'
		}
		if self.status:
			icon=STATUSICONS[self.status]
		else:
			icon='fa-forumbee'
		return icon

	def kanban(user):
		status_list=dict(Project.STATUS)
		projects=Project.objects.filter(owner__in=user.getareaowners())
		kanban_list=[]
		for status_key in status_list:
			board={
				'id': status_key,
				'title': status_list[status_key],
				'class': 'bg-warning',
				'item' : []
			}
			for project in projects.filter(status=status_key):
				board['item'].append({ 'id': project.id, 'title': project.pid,'pid':project.pid, 'content': project.name, 'reference': project.reference, 'toggle':'popover'})
			kanban_list.append(board)
			kanban={'statuslist': list(status_list), 'structure': kanban_list}
		return kanban

	def status_card(user):
		
		dashboardcard = [
			{
				'status':'bg-success',
				'icon': 'fa-check-circle',
				'count': 0
			},
			{
				'status': 'bg-warning',
				'icon': 'fa-exclamation-circle',
				'count':0
			},
			{
				'status': 'bg-danger',
				'icon': 'fa-life-ring',
				'count':0
			},
			{
				'status': 'bg-primary',
				'icon': 'fa-tasks',
				'count': Project.objects.filter(owner__in=user.getareaowners()).count()
			}

		]

		return dashboardcard

	def save(self, *args, **kwargs):
		if not self.pid:	
			projectyear=self.year
			if self.ptype:
				try:
					projects=Project.objects.filter(ptype=self.ptype,year=projectyear).order_by('-pid')[0]
					pindex=int(projects.pid[2:5])+1
				except:
					pindex=1

				pindex='{:03d}'.format(pindex)
				self.pid=r'%s%s-%s'%(self.ptype,pindex,str(projectyear)[2:])
			else:
				self.full_clean()

		super(Project, self).save(*args, **kwargs)

	def createstructure(self):
		print("Creating loctions...")
		if (not self.structure) and (int(self.totallocations)>0):
			for k in range(0,int(self.totallocations)):
				ProjectLocation.objects.create(planningref="Sitio "+'{:04d}'.format(k+1),project=self)
		if (not self.structure):
			stages=Stage.objects.filter(wbs=self.wbs).order_by('nlevel')
			event=ProjectEvent
			locations=ProjectLocation.objects.filter(project=self)
			planning=[True,False]
			print("Sites created, creating events...")
			for p in planning:
				for s in stages:
					startdate=timezone.make_aware(s.startdate(self.year))
					enddate=timezone.make_aware(s.enddate(self.year))
					if s.ntype=="S":
						for k in locations:
							ProjectEvent.objects.create(stage=s,projectnode=k,project=self,start=startdate,end=enddate,planning=p)
					else:
						ProjectEvent.objects.create(stage=s,project=self,start=startdate,end=enddate,planning=p)
			self.structure=True
			self.save()		

	def title(self):
		return r'%s %s'%(self.pid,self.reference)


	def resources(self):
		resource=[]
		for k in Stage.objects.filter(wbs=self.wbs).order_by('nlevel'):
			k_resource = {'id': '','title': '', 'taskname': k.ntitle, 'children': []}
			k_resource['id']=str(k.id)
			k_resource['title']=k.ntitle
			if k.ntype=='S':
				for j in ProjectLocation.objects.filter(project=self).order_by('planningref'):
					j_resource={'id': '','title': '', 'taskname': k.ntitle, 'children': []}
					j_resource['id']=str(k.id)+"::"+str(j.id)
					j_resource['title']=j.planningref
					k_resource['children'].append(j_resource)
			resource.append(k_resource)
		return resource

	def events(self):
		json_events = []
		ProjectEvents=ProjectEvent.objects.filter(project=self).order_by('stage__nlevel','planning')
		for k in ProjectEvents:
			resourceid=str(k.stage.id)
			if k.stage.ntype=='S':
				resourceid+="::"+str(k.projectnode.id)
			json_event = {'id': k.id, 'resourceId': resourceid, 'start': k.start.isoformat(), 'end': k.end.isoformat(), 'title': k.name, 'color': k.color(), 'progress': k.progress, 'editable': not k.planning }
			json_events.append(json_event)
		return json_events

	def __str__(self):
		return r'%s'%(self.pid)

	def startdate(self):
		return StageGoal.objects.filter(stage__wbs=self.wbs).order_by('slot')[0].stage.startdate(self.year)

	def enddate(self):
		return StageGoal.objects.filter(stage__wbs=self.wbs).order_by('-slot')[0].stage.enddate(self.year)


class ProjectLocation(models.Model):
	NODETYPECHOICES = (
		('IND','Existente indoor'),
		('OUT','Existente outdoor'),
		('BNW','Nuevo construido/con permisos'),
		('UCP','Nuevo en construcción/con permisos'),
		('DWC','Nuevo definido/sin permisos'),
		('TBD','Nodo pendiente de definir'),
		('WHS','Bodega'),
		('WPR','Bodega proveedor')
	)

	nodeuuid    = models.UUIDField(default=uuid.uuid4,editable=False)
	planningref = models.CharField(max_length=100)
	location 	= models.ForeignKey(Location,on_delete=models.CASCADE,blank=True,null=True)
	project 	= models.ForeignKey(Project,on_delete=models.CASCADE)
	nodetype    = models.CharField(max_length=3,choices=NODETYPECHOICES,default='TBD')
	priority    = models.IntegerField(default=10)

	def save(self, *args, **kwargs):
		if self.location:
			self.planningref=self.location.name
		super(ProjectLocation,self).save(*args,**kwargs)

	def __str__(self):
		return r'%s/%s'%(self.project.pid,self.planningref)

	def isphysical(self):
		return True if not self.nodetype in ['TBD','WHS','WPR'] else False
		
	def byproject(pid):
		project=Project.objects.get(pid=pid)
		locations=ProjectLocation.objects.filter(project=project).order_by('planningref')
		return locations



class ProjectEvent(models.Model):
	TASKSYSTEMS = (
		('SM','Service Manage'),
		('SP','SAP'),
		('BP','BProjects')
	)

	stage 			= models.ForeignKey(Stage,on_delete=models.CASCADE)
	projectnode     = models.ForeignKey(ProjectLocation,on_delete=models.CASCADE,blank=True,null=True)
	name 			= models.CharField("Titulo",max_length=100,blank=True)
	taskid			= models.CharField(max_length=100,blank=True)
	system	        = models.CharField(max_length=2,choices=TASKSYSTEMS,default='BP')
	description     = models.TextField("Descripción",max_length=1000,blank=True)
	project         = models.ForeignKey(Project,on_delete=models.CASCADE)
	start	  	    = models.DateTimeField("Fecha de inicio")
	end 		    = models.DateTimeField("Fecha de fin")
	progress		= models.FloatField("Avance",default=0)
	planning 		= models.BooleanField(default=False)


	def color(self):
		linearprogress=0
		today = timezone.now()
		if self.planning:
			taskcolor='#007bff' #Primary
		else:
			if today>=self.start:
				if self.start==self.end:
					linearprogress=1
				else:
					linearprogress=(today-self.start)/(self.end-self.start)
				taskcolor='#ffc107' #Orange
				if self.progress<0.9*linearprogress:
					taskcolor='#dc3545' #Danger
				if self.progress>=linearprogress:
					taskcolor='#289745' #Green
			else:
				taskcolor='#6c757d' #Secondary
		return taskcolor

	def __str__(self):
		return r'%s-%s'%(self.project.pid,self.name)

	def save(self, *args, **kwargs):
		if not self.taskid:
			self.taskid=str(uuid.uuid4())
		if not self.name:
			self.name=self.stage.ntitle
			if self.planning:
				self.name="Planificado "+self.name
			else:
				self.name="Real "+self.name
			if self.stage.ntype=='S':
				self.name+="/"+self.projectnode.planningref
		super(ProjectEvent,self).save(*args,**kwargs)
		EventLog=ProjectEventLog(event=self,progress=self.progress,start=self.start,end=self.end)
		EventLog.save()


class ProjectEventLog(models.Model):
	event           = models.ForeignKey(ProjectEvent,on_delete=models.CASCADE)
	updated			= models.DateField(auto_now_add=True,editable=False)
	progress		= models.FloatField()
	start			= models.DateTimeField()
	end             = models.DateTimeField()

class DeliverableEvent(models.Model):

	deliverable     = models.ForeignKey(Deliverable,on_delete=models.CASCADE)
	deliverableid   = models.UUIDField(default=uuid.uuid4,editable=False)
	project         = models.ForeignKey(Project,on_delete=models.CASCADE)
	projectnode     = models.ForeignKey(ProjectLocation,on_delete=models.CASCADE,blank=True,null=True)
	delivered 	    = models.BooleanField(default=False)
	dateplanned     = models.DateField()
	datedelivered   = models.DateField()
	quantity        = models.DecimalField(max_digits=10,decimal_places=2)
	units           = models.ForeignKey(Units,on_delete=models.CASCADE)
	comments 		= models.TextField(max_length=1000,default="#Comentarios")
	crowd			= models.ManyToManyField(UserProfile)

	def __str__(self):
		return r'%s %s'%(self.project.pid,self.delivered)	

class ProjectQuote(models.Model):
	ITEMCLASSCHOICES = (
		('HW','Hardware'),
		('SW','Licencias'),
		('TX','Impuestos'),
		('SH','Transporte'),
		('IF','Infraestructura'),
		('SR','Servicios')
	)

	INCOTERMCHOICES = (
		('EXW','EXW'),
		('FCA','FCA'),
		('FAS','FAS'),
		('FOB','FOB'),
		('CFR','CFR'),
		('CIF','CIF'),
		('CPT','CPT'),
		('CIP','CIP'),
		('DAT','DAT'),
		('DAP','DAP'),
		('DDP','DDP')
	)
	
	token          = models.UUIDField(default=uuid.uuid4,editable=False)
	created        = models.DateField(auto_now_add=True,editable=False)
	updated        = models.DateTimeField(auto_now=True,editable=False)
	itemclass      = models.CharField(max_length=2,choices=ITEMCLASSCHOICES)
	vendor         = models.ForeignKey(Company,on_delete=models.CASCADE)
	partnumber     = models.ForeignKey(Product,on_delete=models.CASCADE,blank=True,null=True)
	description    = models.CharField(max_length=140)
	quantity       = models.DecimalField(max_digits=20,decimal_places=2)
	units		   = models.ForeignKey(Units,on_delete=models.CASCADE,blank=True,null=True)
	incoterm	   = models.CharField(max_length=3,choices=INCOTERMCHOICES)
	amount 	   	   = models.DecimalField(max_digits=20,decimal_places=2)



class CAPEXTransaction(models.Model):

	TRANSACTIONSCHOICES =(
		('REQ','Requerimiento'),
		('APR','Autorizado'),
		('SOL','Solicitud de compra'),
		('PRC','Comprometido'),
		('CAP','Capitalizado'),
		('COV','Carry Over'),
		('TRF','Transferencia')
	)

	token      = models.UUIDField(default=uuid.uuid4, editable=False)
	structure  = models.ForeignKey(CAPEXStructure,on_delete=models.CASCADE)
	created    = models.DateField(auto_now_add=True)
	updated    = models.DateTimeField(auto_now=True)
	value      = models.DecimalField(max_digits=20,decimal_places=2)	
	project    = models.ForeignKey(Project,on_delete=models.CASCADE)
	reference  = models.TextField(max_length=200)
	enabled    = models.BooleanField(default=False)

	def save(self, *args, **kwargs):
		self.token=secrets.token_urlsafe(32)
		super(CAPEXTransaction,self).save(*args,**kwargs)

	def __str__(self):
		return self.token



#  EXCEL Middleware


class ApiExcelForms(models.Model):

	apiname    = models.CharField(max_length=64,blank=True,null=True)
	apikey     = models.CharField(max_length=64,blank=True,null=True)
	created    = models.DateField(auto_now_add=True)
	reference  = models.CharField(max_length=100)
	enabled    = models.BooleanField(default=False)

	def save(self, *args, **kwargs):
		if not self.apiname:
			self.apiname=r'XLS%s'%(secrets.token_urlsafe(7))
			self.apikey=secrets.token_urlsafe(32)
		super(ApiExcelForms, self).save(*args, **kwargs)


	def apivalid(apiname,apikey):
		apienabled=False
		try:
			api=ApiExcelForms.objects.filter(apiname=apiname,apikey=apikey)[0]
			if api.enabled:
				apienabled=True
		except:
			pass
		return apienabled

	def __str__(self):
		return self.reference

class ApiExcelCommands(models.Model):

	CRUDOPTIONS = (
		(0b0000,'----'),
		(0b0100,'-R--'),
		(0b1100,'CR--'),
		(0b1110,'CRU-'),
		(0b1111,'CRUD')
	)

	PROFILEOPTIONS = (
		(0b00000,'---- ---- ---- ---- ----'),
		(0b00001,'---- ---- ---- ---- EINF'),
		(0b00010,'---- ---- ---- PINF ----'),
		(0b00100,'---- ---- EING ---- ----'),
		(0b01000,'---- PING ---- ---- ----'),
		(0b10000,'BYND ---- ---- ---- ----'),
		(0b11111,'- ANY BODY CAN USE THIS-')

	)

	REQUESTOPTIONS = (
		('POST','POST'),
		('GET','GET')
	)

	LEVELCHOICES = (
		(1,'Silver'),
		(10,'Gold'),
		(100,'Platinum'),
		(1000,'Rhodium'),
		(10000,'Diamond'),
		(100000,'Endohedral'),
		(1000000,'Antimatter')
	)


	api         = models.ForeignKey(ApiExcelForms,on_delete=models.CASCADE)
	routing_key = models.CharField(max_length=100)
	classname   = models.TextField(max_length=200)
	method      = models.TextField(max_length=10,choices=REQUESTOPTIONS,default="GET")
	level       = models.IntegerField(default=0,choices=LEVELCHOICES)
	profile     = models.IntegerField(default=0,choices=PROFILEOPTIONS)
	crud        = models.IntegerField(choices=CRUDOPTIONS)
	enabled		= models.BooleanField(default=True)
	mailsubject = models.CharField(max_length=200,blank=True,null=True)
	mailtext    = models.TextField(max_length=1000,blank=True,null=True)

	def __str__(self):
		return self.routing_key
