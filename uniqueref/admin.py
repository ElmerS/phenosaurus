from django.contrib import admin
from import_export import resources, widgets, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from import_export import widgets
from django.contrib.auth.models import Group
from import_export.fields import Field
from models import *
	
# class IPSDatapointResource to define that data can imported into class IPSDatapoint using import_export
class IPSDatapointResource(resources.ModelResource):

	pass_relscreen = fields.Field(column_name='relscreenname', attribute='relscreen', widget=ForeignKeyWidget(Screen,'name'))
	pass_relgene = fields.Field(column_name='relgenename', attribute='relgene', widget=ForeignKeyWidget(Gene,'name'))
	
	class Meta:
		model = IPSDatapoint	# Must be put into the class Datapoint (from oldref.model)
		skip_unchanged = True	# Skip if already exists
		report_skipped = True	# Perhaps this better be True?
		fields = ('id',
			'pass_relscreen', # Link to correct screen
			'pass_relgene', # Link to correct gene
			'low', 
			'lowtotal', 
			'high', 
			'hightotal', 
			'insertions',
			'lowcor', 
			'lowtotalcor', 
			'highcor', 
			'hightotalcor', 
			'pv', 
			'fcpv', 
			'mi',
		)

class IPSDatapointAdmin(ImportExportModelAdmin):
	def get_relgene(self, obj):
		return obj.relgene.name
	def get_relscreen(self, obj):
		return obj.relscreen.name
	get_relgene.short_description = 'Gene'
	get_relscreen.short_description = 'Associated Screen'
	resource_class = IPSDatapointResource
	list_display = ('id', 'get_relscreen', 'mi', 'fcpv', 'get_relgene')
    	pass

# class PSSDatapointResource to define that data can imported into class PSSDatapoint using import_export
class PSSDatapointResource(resources.ModelResource):

	pass_relscreen = fields.Field(column_name='relscreenname', attribute='relscreen', widget=ForeignKeyWidget(Screen,'name'))
	pass_relgene = fields.Field(column_name='relgenename', attribute='relgene', widget=ForeignKeyWidget(Gene,'name'))
	
	class Meta:
		model = PSSDatapoint	# Must be put into the class Datapoint (from oldref.model)
		skip_unchanged = True	# Skip if already exists
		report_skipped = True	# Perhaps this better be True?
		fields = ('id',
			  'pass_relscreen', # Link to correct screen
			  'pass_relgene', # Link to correct gene
			  'nm',
			  'tnm', 
		  	  'ct', 
			  'tct', 
			  'cct',
			  'ctct', 
			  'pv', 
			  'ti',
			  'fcpv', 
			  'mi',
			  'radius',
			  'seq',
		  )

class PSSDatapointAdmin(ImportExportModelAdmin):
	def get_relgene(self, obj):
		return obj.relgene.name
	def get_relscreen(self, obj):
		return obj.relscreen.name
	get_relgene.short_description = 'Gene'
	get_relscreen.short_description = 'Associated Screen'
	resource_class = PSSDatapointResource
	list_display = ('id', 'get_relscreen', 'fcpv', 'get_relgene')
    	pass


class SeqSummaryResource(resources.ModelResource):
	pass_relscreen = fields.Field(column_name='relscreenname', attribute='relscreen',
								  widget=ForeignKeyWidget(Screen, 'name'))

	class Meta:
		model = SeqSummary  # Must be put into the class Datapoint (from oldref.model)
		skip_unchanged = True  # Skip if already exists
		report_skipped = True  # Perhaps this better be True?
		fields = ('id',
				  'pass_relscreen',  # Link to correct screen
				  'high_dist',
				  'high_readsmappedtotophits',
				  'high_topreads_counts',
				  'high_totalmappedreads',
				  'high_totalreads',
				  'high_totaltopreads',
				  'high_totaluniquereads',
				  'low_dist',
				  'low_readsmappedtotophits',
				  'low_topreads_counts',
				  'low_totalmappedreads',
				  'low_totalreads',
				  'low_totaltopreads',
				  'low_totaluniquereads'
				  )

class SeqSummaryAdmin(ImportExportModelAdmin):
	def get_relscreen(self, obj):
		return obj.relscreen.name

	get_relscreen.short_description = 'Associated Screen'
	resource_class = SeqSummaryResource
	list_display = ('id', 'get_relscreen')
	pass


# calss GeneResoruce to define that data can be imported into class Gene using import_export
class GeneResource(resources.ModelResource):
	
	class Meta:
		model = Gene
		skip_unchanged = True
		report_skipped = True
		fields = ('id',
			  'name',
			  'description',
			  'chromosome',
			  'orientation',
		)

class GeneAdmin(ImportExportModelAdmin):
	list_display = ('name', 'chromosome', 'orientation', 'description')
	resource_class = GeneResource
	pass

# Class LocationResource to define
class LocationResource(resources.ModelResource):

        pass_relgene = fields.Field(column_name='relgenename', attribute='relgene', widget=ForeignKeyWidget(Gene,'name'))

	class Meta:
		model = Location
		skip_unchanged = True
		report_skipped = True
		fields = ('id',
			  'pass_relgene',
			  'startpos',
			  'endpos',
		)

class LocationAdmin(ImportExportModelAdmin):
        def get_relgene(self, obj):
                return obj.relgene.name
        get_relgene.short_description = 'Gene'
        resource_class = LocationResource
        list_display = ('id', 'get_relgene', 'startpos', 'endpos')
        pass

class ScreenPermissionsInline(admin.TabularInline):
	model = ScreenPermissions
	extra = 5

class ScreenAdmin(admin.ModelAdmin):
	inlines = (ScreenPermissionsInline,) # For the future it'd be nice if this would become a filter_vertical where multiple can be selected
	list_display = ('name', 'screentype', 'induced', 'knockout', 'description', 'celline', 'screen_date')

class UpdateHistoryAdmin(admin.ModelAdmin):
	list_display=('date', 'version', 'changes')

class CustomVariablesAdmin(admin.ModelAdmin):
	list_display=('custom_track_list_for_summary',)

class CustomTrackAdmin(admin.ModelAdmin):
	list_display = ('user', 'name', 'description', 'genelist')

class GroupAdmin(admin.ModelAdmin):
	inlines = (ScreenPermissionsInline,)

admin.site.register(Screen, ScreenAdmin)	
admin.site.register(Gene, GeneAdmin)
admin.site.register(IPSDatapoint, IPSDatapointAdmin)
admin.site.register(PSSDatapoint, PSSDatapointAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(CustomTracks, CustomTrackAdmin)
admin.site.unregister(Group) # To disable the standard form for modifying groups
admin.site.register(Group, GroupAdmin)
admin.site.register(UpdateHistory, UpdateHistoryAdmin)
admin.site.register(SeqSummary, SeqSummaryAdmin)
admin.site.register(CustomVariables, CustomVariablesAdmin)
