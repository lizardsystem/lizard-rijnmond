# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Area'
        db.create_table('lizard_rijnmond_area', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('maintainer', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('the_geom', self.gf('django.contrib.gis.db.models.fields.LineStringField')()),
        ))
        db.send_create_signal('lizard_rijnmond', ['Area'])


    def backwards(self, orm):
        
        # Deleting model 'Area'
        db.delete_table('lizard_rijnmond_area')


    models = {
        'lizard_rijnmond.area': {
            'Meta': {'object_name': 'Area'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintainer': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'the_geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {})
        }
    }

    complete_apps = ['lizard_rijnmond']
