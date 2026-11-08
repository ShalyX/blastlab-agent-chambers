"""Web Chamber acceptance tests: explicit config, truthful reports, public proof,
public-run rate limits and preserved owner authorization."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from copy import deepcopy

from web_chamber import catalog, expected_total, report_from_run, validate_config
from verify_public_evidence import verify
from evidence_export import parse_run

import control_api as gateway
from test_control_api import GatewayTests


class ChamberContractTests(unittest.TestCase):
    def test_catalog_reports_one_executable_chamber(self):
        c=catalog()
        self.assertEqual([x['id'] for x in c['chambers'] if x['state']=='available'],['web'])
        self.assertEqual(len(c['missions']),2)
        self.assertEqual(len(c['scenarios']),5)
        self.assertTrue(any(e['id']=='live' and not e['public'] for e in c['engines']))

    def test_rejects_arbitrary_source_and_non_string_ids(self):
        for mission,scenario in [
            ('https://malicious.site','clean'),('inventory_value','cat ../../'),
            (True,'clean'),('inventory_value',[]),('',''),(None, 'compound')]:
            with self.assertRaises(ValueError):
                validate_config(mission,scenario)

    def test_mission_valuations_are_distinct(self):
        rows=[{'name':'mugs','available':4,'unit_price_cents':1200},
              {'name':'plates','available':3,'unit_price_cents':800}]
        self.assertEqual(expected_total(rows,'inventory_value'),7200)
        self.assertEqual(expected_total(rows,'low_stock_exposure'),2400)

    def test_public_export_self_verified_and_tamper_detected(self):
        p=Path(__file__).resolve().parent/'artifacts'/'vultr-vm-20261104'
        if not (p/'trace.jsonl').exists():
            self.skipTest('Historical raw Vultr run not available on this host')
        run=parse_run(p,'live')
        result=verify(run)
        self.assertTrue(result['verified'])
        self.assertEqual(result['events'],41)
        self.assertFalse(run['proof']['original_log_independently_verifiable_from_public_export'])
        wrong=deepcopy(run)
        wrong['events'][15]['title']='Fabricated compromise!'
        with self.assertRaisesRegex(ValueError,'Tampered public event'):
            verify(wrong)

    def test_report_source_labels_and_untested_scope(self):
        run={
          'origin':'scripted-fixture','is_model_driven':False,
          'mission_id':'low_stock_exposure','scenario':'receipt_forgery',
          'summary':{'acceptance_passed':True,'completed':True,'reset_verified':True,
                     'supervisor_sentinel_unchanged':True},
          'events':[
           {'kind':'page_observation','detail':{}},
           {'kind':'policy_decision','detail':{'decision':'deny','tool':'finish'}},
           {'kind':'sandbox_destroyed','detail':{'container_absent':True,'workspace_removed':True}},
           {'kind':'sandbox_destroyed','detail':{'container_absent':True,'workspace_removed':True}},
          ]
        }
        report=report_from_run(run)
        self.assertEqual(report['verdict'],'CONTROLLED TEST PASSED')
        self.assertEqual(report['policy_denial_count'],1)
        self.assertEqual(report['attempted_by_source'],'SCRIPTED FIXTURE')
        self.assertEqual(report['mission_id'],'low_stock_exposure')
        self.assertIn('Other four Chambers',report['untested'])


class PublicGatewayTests(GatewayTests):
    # Extend inherited endpoint fixture and tests without invoking real Docker.
    def test_public_catalog_and_history_not_owner_gated(self):
        status,body=self.request('GET','/api/catalog')
        self.assertEqual(status,200)
        self.assertEqual(len(body['chambers']),5)
        status,body=self.request('GET','/api/history')
        self.assertEqual(status,200)
        self.assertIn('runs',body)

    def test_public_scripted_start_requires_safe_origin_and_config(self):
        data={'mission':'low_stock_exposure','scenario':'role_spoof'}
        status,_=self.request('POST','/api/demo-runs',data)
        self.assertEqual(status,403)
        status,_=self.request('POST','/api/demo-runs',
            {'mission':'inventory_value','scenario':'exfil_bait','url':'https://evil.example'},
            {'Origin':'https://blastlab.example'})
        self.assertEqual(status,400)
        with patch.object(gateway,'run_task',lambda *_: None):
            status,job=self.request('POST','/api/demo-runs',data,
                                    {'Origin':'https://blastlab.example'})
        self.assertEqual(status,202)
        self.assertEqual(job['mode'],'scripted')
        self.assertEqual(job['mission'],'low_stock_exposure')
        self.assertEqual(job['scenario'],'role_spoof')
        status,poll=self.request('GET',job['poll_url'])
        self.assertEqual(status,200)
        self.assertEqual(poll['status'],'queued')
        self.assertNotIn('owner_token',poll)
        status,_=self.request('GET','/api/jobs/'+job['job_id'])
        self.assertEqual(status,401)

    def test_public_does_not_start_live_model(self):
        for bad in [
            {'mode':'live','mission':'inventory_value','scenario':'clean'},
            {'mission':'inventory_value','scenario':'../../escape'},
            {'mission':'inventory_value','scenario':'clean','command':'rm -rf /'},
        ]:
            status,_=self.request('POST','/api/demo-runs',bad,
                {'Origin':'https://blastlab.example'})
            self.assertEqual(status,400)

    def test_public_hourly_budget(self):
        gateway.MAX_PUBLIC_PER_HOUR=1
        self.addCleanup(setattr,gateway,'MAX_PUBLIC_PER_HOUR',4)
        with patch.object(gateway,'run_task',lambda *_:None):
            status,_=self.request('POST','/api/demo-runs',
                                  {'mission':'inventory_value','scenario':'clean'},
                                  {'Origin':'https://blastlab.example'})
        self.assertEqual(status,202)
        # Release the fake active job to reach the public budget gate.
        with gateway.JOB_LOCK:gateway.ACTIVE_JOB=None
        status,_=self.request('POST','/api/demo-runs',
                              {'mission':'inventory_value','scenario':'clean'},
                              {'Origin':'https://blastlab.example'})
        self.assertEqual(status,429)


if __name__=='__main__':
    unittest.main()
