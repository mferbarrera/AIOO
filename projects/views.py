from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User,Group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.core.mail import send_mail
from django.core.serializers import serialize
from django.apps import apps
from django.views.generic.edit import CreateView
from projects import models as pm
from projects import forms as fm
from projects.models import Country
import json,secrets,sys,decimal,re


# Form test

# General info

def get_user_profile(request):
	return pm.UserProfile.objects.get(user=request.user)

def get_project_list(request):
	owner=pm.UserProfile.objects.get(user=request.user)
	return pm.Project.objects.filter(owner__in=owner.getareaowners())

def get_project_cards(request):
	owner=pm.UserProfile.objects.get(user=request.user)
	cards=pm.Project.status_card(owner)
	return cards

# Users admin

def Dashboard(request):
	return render(request,'dashboard/index.html')

def About(request):
	return render(request,'about/index.html')


def Login(request):
	invalid_user=False
	if request.method=="POST":
		user = authenticate(request,username=request.POST.get('username'),password=request.POST.get('password'))
		print(request.POST)
		if user is not None:
			if user.is_active:
				login(request,user)
				print("success!")
				return redirect('/home/')
			else:
				invalid_user=True
		else:
			print("invalid User")
			invalid_user=True
	return render(request,'sb-admin/login.html',{'invalid_user':invalid_user})


def Logout(request):
	logout(request)
	return redirect('/login/')

def Register(request):
	if request.method=="POST":
		requestpost=request.POST.dict()
		requestpost.pop('csrfmiddlewaretoken')
		newuserequest=pm.RequestUser.objects.create(**requestpost)
		return redirect('/login/')
	countrylist=pm.Country.objects.all()
	companylist=pm.Company.objects.all()
	arealist=pm.CompanyFamilyArea.objects.all()
	return render(request,'sb-admin/register.html', {'countrylist':countrylist, 'companylist':companylist,'arealist':arealist})

@login_required
def ProjectPost(request):
	form = fm.ProjectForm()
	if request.method=="POST":
		projectpost=request.POST.dict()
		print(projectpost)
		projectpost.pop('csrfmiddlewaretoken')
		projectuser=pm.UserProfile.objects.get(user__username=request.user.username)
		projectpost['country']=pm.Country.objects.get(id=projectpost['country'])
		projectpost['wbs']=pm.WBS.objects.get(id=projectpost['wbs'])
		projectpost['pds']=pm.ProjectDeliverableSchema.objects.get(id=projectpost['pds'])
		newproject=pm.Project.objects.create(**projectpost)
		newproject.owner.add(projectuser)
		newproject.createstructure()
		return redirect('/home/')
	return render(request,'sb-admin/project_post.html', {'form':form,'userprofile': get_user_profile(request)})


@login_required
def ProjectUpdate(request,id):
	updateproject=pm.Project.objects.get(id=id)
	form = fm.ProjectForm(request.POST or None,instance=updateproject)
	if request.method=="POST":
		form.save()
		return redirect('/home/')
	else:
		return render(request,'sb-admin/project_post.html', {'form':form,'userprofile': get_user_profile(request)})

# Ajax
def AjaxRouter(data):
	model=eval('pm.'+data['model'])
	ajaxresult=False
	if (data['method']=='update'):
		print(data)
		key_name=data['key']
		for item in eval(data['data']):
			key_value=item[key_name]
			item.pop(key_name)
			obj=model.objects.filter(**{key_name:key_value}).update(**item)
		ajaxresult=True
	if (data['method']=='autocomplete'):
		queryfilter=eval(data['filter'])
		queryvalues=eval(data['values'])
		ajaxresult=json.dumps(list(model.objects.filter(**queryfilter).values(*queryvalues)[:20]))
	if (data['method']=='updateevents'):
		print(data)
		key_name=data['key']
		for item in eval(data['events']):
			key_value=item[key_name]
			item.pop(key_name)
			obj=model.objects.filter(**{key_name:key_value}).update(**item)
		
		ajaxresult=True
	return ajaxresult



def Ajax(request):
	ajaxresponse="Error"
	if request.method=="POST":
		if request.is_ajax():
			data=request.POST.dict()
			data.pop('CSRF')
			ajaxresult=AjaxRouter(data)
			if ajaxresult:
				return HttpResponse("200 OK")
	if request.method=="GET":
		if request.is_ajax():
			data=request.GET.dict()
			ajaxresult=AjaxRouter(data)
			return JsonResponse(eval(ajaxresult),safe=False)
	return HttpResponse("Error")

# Scheduler

@login_required
def Home(request):
	return render(request,'sb-admin/index.html',{'projects_list': get_project_list(request),'project_cards':get_project_cards(request),'userprofile': get_user_profile(request)})

@login_required
def Nodes(request,pid):
	locationsobj=[]
	project=pm.Project.objects.get(pid=pid)
	locations=pm.ProjectLocation.byproject(pid)
	for location in locations:
		form=fm.ProjectLocationForm(None,instance=location)
		for field in form.fields.keys():
			if field=='planningref':
				form.fields[field].widget.attrs={'class':'form-control location_autocomplete', 'style':'background-color: #fcf8e3;', 'id':field, 'row_id':location.id,'field_value':''}
			else:
				form.fields[field].widget.attrs={'class':'form-control', 'style':'background-color: #fcf8e3;', 'id':field, 'row_id':location.id, 'field_value':''}
			

		locationsobj.append({'value':location,'form': form})
	
	return render(request,'sb-admin/projectlocation.html',{'projects_list': get_project_list(request),'locationsobj': locationsobj,'project':project,'userprofile': get_user_profile(request)})

@login_required
def Locations(request,pid):
	project=pm.Project.objects.get(pid=pid)
	return render(request,'sb-admin/test_autocomplete.html',{'projects_list': get_project_list(request),'project':project,'userprofile': get_user_profile(request)})	

@login_required
def Scheduler(request,pid):
	form=fm.ProjectEventForm()
	project=pm.Project.objects.get(pid=pid)
	project_resources=json.dumps(project.resources())
	project_events=json.dumps(project.events())
	project_startdate=project.startdate().strftime("%Y-%m-%d")	
	return render(request,'sb-admin/scheduler_template.html',{ 'projects_list': get_project_list(request),'project_resources' : project_resources, 'project_events': project_events, 'project_startdate': project_startdate, 'form':form ,'userprofile': get_user_profile(request)})

@login_required
def Kanban(request):
	user=pm.UserProfile.objects.get(user=request.user)
	project_kanban=pm.Project.kanban(user)
	return render(request,'sb-admin/project_kanban.html',{ 'projects_list': get_project_list(request), 'project_kanban': project_kanban,'userprofile': get_user_profile(request) })

# Forms

def CountryView(CreateView):
	template_name ='sb-admin/test_form.html'
	model = Country
	fields = ('name','isoname','isocurrency')



# Excel Middleware

CRUD = {'create':0b1000, 'readall':0b0100, 'read':0b0100,'update':0b0010,'delete':0b0001}


def ExcelMiddleware(request):
	#
	# Initialize json_data for processing
	#   json_data: Is data source from Excel Application
	#   json_answ: Is the answer from middleware
	#   json_row : Is the input and output from row processing of each data row in json_data
	#


	json_data={}
	json_answ={}
	json_answ['api']={'apiname': u'Excel Middleware \U0001F41D','copyright':'(C)2015-2025 Bee888.io', 'author': 'Manuel F. Barrera', 'about' : 'On each transaction you accept the terms and conditions described at http://xlsmw.bee888.io:8969/about/'}
	json_answ['error']=''
	json_answ['data']=[]

	try:
		# Try to load json_data
		#json_data = json.loads(request.body.decode('utf-8'))
		json_data = eval(request.body)
		api_isvalid=pm.ApiExcelForms.apivalid(json_data['api']['apiname'],json_data['api']['apikey'])
		api_command=pm.ApiExcelCommands.objects.filter(api__apiname=json_data['api']['apiname'],routing_key=json_data['api']['routing_key'])[0]
		userprofile=pm.UserProfile.objects.filter(user__username=json_data['api']['username'])[0]

		print(api_isvalid, userprofile.level, api_command.level, userprofile.profile & api_command.profile)
		
		# Check if application, user and command is valid
		if api_isvalid and userprofile.level>=api_command.level and userprofile.profile & api_command.profile and api_command.enabled and type(json_data['data']['rows']).__name__=='list':

		# Work with each row in data of json_data 
		# The data will be formated: { rowid: id, action: method, field1:value1, field2:value2, ... fieldN:valueN }
			print("Aplication and user profile is valid")
			if request.method=="GET" and json_data['api']['routing_key']=='getcsrf':
				get_token(request)
				print ("CSRF Token, generated")
			for json_row_data in json_data['data']['rows']:
				json_row={}
				if json_row_data['action'] in CRUD:
					json_row['api']=json_data['api']
					json_row['data']=json_row_data
					json_row['userprofile']=userprofile
					json_row['api_command']=api_command
					row_command=api_command.classname
					#try:
					jpl_crud=eval(row_command)
					json_row=jpl_crud['data']

			# For rows action field will be used for error notification
					#except:
					#	print("FAIL")
					#	json_row={}
					#	json_row['rowid']=json_row_data['rowid']
					#	json_row['action']=':error %'%sys.exc_info()[0]
				else:
					json_row['rowid']=json_row_data['rowid']
					json_row['action']=':%s is not enabled'%json_row_data['action']
				
				
				if json_row_data['action']=='readall':
					json_answ['data']=json_row
				else:
					json_answ['data'].append(json_row)		

		else:
			# Append global error transaction
			if not api_isvalid:
				json_answ['error']+=":Invalid App"
			if not userprofile.user.is_authenticated:
				json_answ['error']+=":User auth required"
			if not api_command.enabled:
				json_answ['error']+=":Command disabled"
			if not type(json_data['data']).__name__== 'list':
				json_answ['error']+=':Invalid Data format'
	except:
		json_answ['error']=r":json.loads fail, %s"%sys.exc_info()[0]
		print(sys.exc_info())
	
	return JsonResponse(json_answ)


class ExcelMiddlewareValidateUser():
	def create(json_data):
		json_answ={'rowid': json_data['rowid'], 'rowerror':'not implemented', 'action':':invalid'}
		return json_answ

	def read(json_data):
		
		json_answ={'rowid': json_data['data']['rowid'], 'rowerror':'', 'action':':unauthorized', 'uservalid':False}
		print("call works!")
		try:
			username=json_data['api']['username']
			print(username)
			password=json_data['api']['password']
			print(password)
			user=authenticate(username=username,password=password)
			print(user)
			if user is not None:
				json_answ['action']=':authorized'
				json_answ['uservalid']=True
				print("authorized")

		except:
			json_answ['error']=':error, %s'%sys.exc_info()[0]

		return json_answ

	def update(json_data):
		json_answ={'rowid': json_data['rowid'], 'rowerror':'not implemented', 'action':':invalid'}
		return json_answ

	def delete(json_data):
		json_answ={'rowid': json_data['rowid'], 'rowerror':'not implemented', 'action':':invalid'}
		return json_answ





class JPLCRUD:
	JPLSX = {
		'forwarding'	: {
			'xmcapexio' : {
				'capexio' : {
					'fields' : {
						'create' : ['structure','country','linenumber','colorlabel','classification','capexio','capexamx','businessarea','macro','project','subproject','iopriority','AB','SAP','vendor','projectlabel','metric','units','unitarycost','ammount','support','owner'],
						'read'	 : ['country','linenumber'],
						'update' : ['structure','country','linenumber','colorlabel','classification','capexio','capexamx','businessarea','macro','project','subproject','iopriority','AB','SAP','vendor','projectlabel','metric','units','unitarycost','ammount','support','owner'],
						'readall': ['structure'],
					},
					'related' : {
						'structure'	: {'type': 'many_to_one', 'model' : 'capexstructure', 'field' : 'name', 'filters' : {'structure':'name'}},
						'country' 	: {'type': 'many_to_one', 'model' : 'country', 'field' : 'isoname', 'filters' : {'country':'isoname'}}
					},
					'choices' : {
						'colorlabel' : {'B':'Blue','G':'Grey','W':'White'} 
					}
				}
			}
		}
	}



	def __init__(self,json_data):
		# Populate class models from projects
		self.JPLSX['models']={}
		projects = apps.get_app_config('projects')
		for class_name, class_object in projects.models.items():
			class_alias = re.findall(r"\.(\w+)\'",str(class_object))[0]
			if not '_' in class_alias:
				self.JPLSX['models'][class_name]=eval('pm.%s'%class_alias)
		projects 		= None
		self.rowid 		= json_data['data']['rowid']
		self.json_data 	= json_data['data']['fields']
		self.routing_key= json_data['api']['routing_key']
		self.action 	= json_data['data']['action']
		self.modelname  = json_data['data']['model']['name']
		self.keymodel 	= self.JPLSX['models'][self.modelname]
		self.keyrelated = json_data['data']['model']['related']
		self.FIELDS 	= self.JPLSX['forwarding'][self.routing_key][self.modelname]['fields']
		self.RELATED 	= self.JPLSX['forwarding'][self.routing_key][self.modelname]['related']
		self.CHOICES 	= self.JPLSX['forwarding'][self.routing_key][self.modelname]['choices']
		self.json_answ  = {}

	
	def serializeitem(self,item):
		json_item={}
		for f in item._meta.get_fields():
			field_evalue=None
			if f.is_relation and f.name in self.RELATED:
				field_evalue='item.%s.%s'%(f.name,self.RELATED[f.name]['field'])
			if not f.is_relation:
				field_evalue='item.%s'%f.name
			if field_evalue:
				json_item[f.name]=eval(field_evalue)
		return json_item

	def getkwargs(self,action):
		field_kwargs={'fields':{},'valid':True,'error':''}
		for f in self.FIELDS[action]:
			if f in self.json_data:
				if f in self.RELATED:
					json_related_args={}
					json_related_args[self.RELATED[f]['field']]=self.json_data[f]
					if self.RELATED[f]['type']=='many_to_one':
						field_kwargs['fields'][f]=self.JPLSX['models'][self.RELATED[f]['model']].objects.select_related().filter(**json_related_args)[0]
				else:
					field_kwargs['fields'][f]=self.json_data[f]
			else:
				if action!='readall':
					field_kwargs['valid']=False
					field_kwargs['error']+=''
		return field_kwargs

	def dataappendrow(self,rowid,item):
		self.json_answ['data'].append({'rowid':rowid, 'fields': self.serializeitem(item),'valid': True, 'error': ''})

	def router(self):
		self.json_answ={'data':[]}
		if self.action=='create':
			field_kwargs=self.getkwargs(self.action)['fields']
			item=self.keymodel(**field_kwargs)
			item.save()
			self.dataappendrow(self.rowid,item)
		if self.action=='read':
			field_kwargs=self.getkwargs(self.action)['fields']
			item=self.keymodel.objects.filter(**field_kwargs)[0]
			self.dataappendrow(self.rowid,item)
		if self.action=='update':
			field_kwargs=self.getkwargs('read')['fields']
			item=self.keymodel.objects.filter(**field_kwargs)[0]
			field_kwargs=self.getkwargs(self.action)['fields']
			item(**field_kwargs)
			item.save()
			self.dataappendrow(self.rowid,item)
		if self.action=='readall':
			rowid=0
			field_kwargs=self.getkwargs(self.action)['fields']
			if len(field_kwargs.keys()):
				items=self.keymodel.objects.select_related().filter(**field_kwargs)
			else:
				items=self.keymodel.objects.select_related().all()
			for item in items:
				rowid+=1
				self.dataappendrow(rowid,item)

		return self.json_answ
