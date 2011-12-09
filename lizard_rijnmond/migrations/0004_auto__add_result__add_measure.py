# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Result'
        db.create_table('lizard_rijnmond_result', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('time', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('measure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_rijnmond.Measure'], null=True, blank=True)),
        ))
        db.send_create_signal('lizard_rijnmond', ['Result'])

        # Adding model 'Measure'
        db.create_table('lizard_rijnmond_measure', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal('lizard_rijnmond', ['Measure'])


    def backwards(self, orm):
        
        # Deleting model 'Result'
        db.delete_table('lizard_rijnmond_result')

        # Deleting model 'Measure'
        db.delete_table('lizard_rijnmond_measure')


    models = {
        'lizard_rijnmond.measure': {
            'Meta': {'object_name': 'Measure'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'lizard_rijnmond.result': {
            'Meta': {'object_name': 'Result'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_rijnmond.Measure']", 'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'lizard_rijnmond.segment': {
            'Meta': {'object_name': 'Segment'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintainer': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'the_geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {})
        }
    }

    complete_apps = ['lizard_rijnmond']
