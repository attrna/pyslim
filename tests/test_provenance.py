"""
Test cases for provenance handling.
"""
from __future__ import print_function
from __future__ import division

import pyslim
import msprime
import tests
import unittest
import random
import json
import tskit

# *Note:* it is now deprecated to extract information from provenance,
# but we still need to do it, to be able to load old file versions.

_slim_v3_3_1_example = r'''
{
    "environment": {
        "os": {
            "machine": "x86_64",
            "node": "skua",
            "release": "4.19.0-2-amd64",
            "system": "Linux",
            "version": "#1 SMP Debian 4.19.16-1 (2019-01-17)"
        }
    },
    "metadata": {
        "individuals": {
            "flags": {
                "16": {
                    "description": "the individual was alive at the time the file was written",
                    "name": "SLIM_TSK_INDIVIDUAL_ALIVE"
                },
                "17": {
                    "description": "the individual was requested by the user to be remembered",
                    "name": "SLIM_TSK_INDIVIDUAL_REMEMBERED"
                },
                "18": {
                    "description": "the individual was in the first generation of a new population",
                    "name": "SLIM_TSK_INDIVIDUAL_FIRST_GEN"
                }
            }
        }
    },
    "parameters": {
        "command": [
            "slim",
            "recipe_WF.slim"
        ],
        "model": "initialize()\n{\n    setSeed(23);\n    initializeTreeSeq();\n    initializeMutationRate(1e-2);\n    initializeMutationType(\"m1\", 0.5, \"f\", -0.1);\n    initializeGenomicElementType(\"g1\", m1, 1.0);\n    initializeGenomicElement(g1, 0, 99);\n    initializeRecombinationRate(1e-2);\n}\n\n1 { \n    sim.addSubpop(\"p1\", 10);\n}\n\n10 {\n    sim.treeSeqOutput(\"recipe_WF.trees\");\n    catn(\"Done.\");\n    sim.simulationFinished();\n}\n",
        "model_type": "WF",
        "seed": 1701990081340
    },
    "schema_version": "1.0.0",
    "slim": {
        "file_version": "0.3",
        "generation": 10
    },
    "software": {
        "name": "SLiM",
        "version": "3.3.1"
    }
}	
'''

_slim_v3_1_example = r'''
{
    "environment": {
        "os": {
            "machine": "x86_64",
            "node": "d93-172.uoregon.edu",
            "release": "17.6.0",
            "system": "Darwin",
            "version": "Darwin Kernel Version 17.6.0: Tue May  8 15:22:16 PDT 2018; root:xnu-4570.61.1~1/RELEASE_X86_64"
        }
    },
    "metadata": {
        "individuals": {
            "flags": {
                "16": {
                    "description": "the individual was alive at the time the file was written",
                    "name": "SLIM_TSK_INDIVIDUAL_ALIVE"
                },
                "17": {
                    "description": "the individual was requested by the user to be remembered",
                    "name": "SLIM_TSK_INDIVIDUAL_REMEMBERED"
                },
                "18": {
                    "description": "the individual was in the first generation of a new population",
                    "name": "SLIM_TSK_INDIVIDUAL_FIRST_GEN"
                }
            }
        }
    },
    "parameters": {
        "command": [],
        "model": "initialize() {\n\tinitializeTreeSeq();\n\tinitializeMutationRate(1e-7);\n\tinitializeMutationType(\"m1\", 0.5, \"f\", 0.0);\n\tinitializeGenomicElementType(\"g1\", m1, 1.0);\n\tinitializeGenomicElement(g1, 0, 99999);\n\tinitializeRecombinationRate(1e-8);\n}\n1 {\n\tsim.addSubpop(\"p1\", 500);\n}\n2000 late() { sim.treeSeqOutput(\"~/Desktop/junk.trees\"); }\n",
        "model_type": "WF",
        "seed": 1783301962445
    },
    "schema_version": "1.0.0",
    "slim": {
        "file_version": "0.2",
        "generation": 2000
    },
    "software": {
        "name": "SLiM",
        "version": "3.1"
    }
}
'''

_slim_v3_0_example = '''
{"program": "SLiM", "version": "3.0", "file_version": "0.1", "model_type": "WF", "generation": 10, "remembered_node_count": 0}
'''

old_provenance_examples = [_slim_v3_0_example, _slim_v3_1_example, _slim_v3_3_1_example]


class TestProvenance(tests.PyslimTestCase):

    def get_0_1_slim_examples(self):
        for filename in ['tests/examples/recipe_WF.v3.0.trees',
                         'tests/examples/recipe_nonWF.v3.0.trees']:
            with self.assertWarns(Warning):
                yield tskit.load(filename)

    def get_0_2_slim_examples(self):
        for filename in ['tests/examples/recipe_WF.v3.2.trees',
                         'tests/examples/recipe_nonWF.v3.2.trees']:
            with self.assertWarns(Warning):
                yield tskit.load(filename)

    def get_0_3_slim_examples(self):
        for filename in ['tests/examples/recipe_WF.v3.3.1.trees',
                         'tests/examples/recipe_nonWF.v3.3.1.trees']:
            with self.assertWarns(Warning):
                yield tskit.load(filename)

    def get_0_4_slim_examples(self):
        for filename in ['tests/examples/recipe_WF.v3.4.trees',
                         'tests/examples/recipe_nonWF.v3.4.trees']:
            with self.assertWarns(Warning):
                yield tskit.load(filename)

    def test_get_provenance(self):
        for ts in self.get_slim_examples(WF=True):
            with self.assertWarns(Warning):
                prov = ts.slim_provenance
            self.assertEqual(prov.model_type, "WF")
            self.assertEqual(prov, pyslim.get_provenance(ts))
            self.assertEqual(prov, pyslim.get_provenance(ts.tables))
        for ts in self.get_slim_examples(nonWF=True):
            with self.assertWarns(Warning):
                prov = ts.slim_provenance
            self.assertEqual(prov.model_type, "nonWF")
            self.assertEqual(prov, pyslim.get_provenance(ts))
            self.assertEqual(prov, pyslim.get_provenance(ts.tables))

    def test_get_all_provenances(self):
        for ts in self.get_slim_examples(WF=True):
            rts = self.run_msprime_restart(ts, WF=True)
            provenances = rts.slim_provenances
            self.assertEqual(len(provenances), 2)
            with self.assertWarns(Warning):
                last_prov = ts.slim_provenance
            self.assertEqual(last_prov, provenances[0])
            # mrts = pyslim.SlimTreeSequence(msprime.mutate(rts, rate=0.001))
            j = 0
            for p in rts.provenances():
                is_slim, _ = pyslim.slim_provenance_version(p)
                if is_slim:
                    sp = pyslim.parse_provenance(p)
                    self.assertEqual(provenances[j], sp)
                    j += 1
                else:
                    with self.assertRaises(ValueError):
                        pyslim.parse_provenance(p)

    def test_provenance_creation(self):
        record = pyslim.make_pyslim_provenance_dict()
        tskit.provenance.validate_provenance(record)

        record = pyslim.make_slim_provenance_dict("nonWF", 100)
        tskit.provenance.validate_provenance(record)

    def test_upgrade_provenance_errors(self):
        ts = msprime.simulate(10)
        # test bad input
        with self.assertRaises(ValueError):
            pyslim.upgrade_slim_provenance(ts.tables)

    def test_upgrade_provenance(self):
        ts = msprime.simulate(10)
        for record_text in old_provenance_examples:
            record = json.loads(record_text)
            prov = tskit.Provenance(timestamp='2018-08-25T14:59:13', record=json.dumps(record))
            is_slim, version = pyslim.slim_provenance_version(prov)
            self.assertTrue(is_slim)
            if 'file_version' in record:
                self.assertEqual(version, "0.1")
            else:
                self.assertEqual(version, record['slim']['file_version'])
            tables = ts.dump_tables()
            tables.provenances.add_row(json.dumps(record))
            pyslim.upgrade_slim_provenance(tables) # modifies the tables
            new_ts = tables.tree_sequence()
            self.assertEqual(new_ts.num_provenances, 3)
            is_slim, version = pyslim.slim_provenance_version(new_ts.provenance(2))
            self.assertTrue(is_slim)
            self.assertEqual(version, "0.4")
            new_record = json.loads(new_ts.provenance(2).record)
            if 'model_type' in record:
                self.assertEqual(record['model_type'], new_record['parameters']['model_type'])
                self.assertEqual(record['generation'], new_record['slim']["generation"])
            else:
                self.assertEqual(
                        record['parameters']['model_type'],
                        new_record['parameters']['model_type'])
                self.assertEqual(record['slim']['generation'], new_record['slim']["generation"])

    def test_convert_0_1_files(self):
        for ts in self.get_0_1_slim_examples():
            pts = pyslim.SlimTreeSequence(ts)
            self.assertEqual(ts.num_provenances, 1)
            self.assertEqual(pts.num_provenances, 2)
            self.assertEqual(ts.provenance(0).record, pts.provenance(0).record)
            record = json.loads(ts.provenance(0).record)
            self.assertTrue(isinstance(pts.metadata, dict))
            self.assertTrue('SLiM' in pts.metadata)
            self.assertEqual(record['model_type'], pts.metadata['SLiM']['model_type'])
            self.assertEqual(record['generation'], pts.metadata['SLiM']["generation"])
            self.assertListEqual(list(ts.samples()), list(pts.samples()))
            self.assertArrayEqual(ts.tables.nodes.flags, pts.tables.nodes.flags)
            samples = list(ts.samples())
            t = ts.first()
            pt = pts.first()
            for _ in range(20):
                u = random.sample(samples, 1)[0]
                self.assertEqual(t.parent(u), pt.parent(u))
                if t.parent(u) != tskit.NULL:
                    self.assertEqual(t.branch_length(u), pt.branch_length(u))

    def test_convert_0_2_files(self):
        for ts in self.get_0_2_slim_examples():
            pts = pyslim.SlimTreeSequence(ts)
            self.assertEqual(ts.num_provenances, 1)
            self.assertEqual(pts.num_provenances, 2)
            self.assertEqual(ts.provenance(0).record, pts.provenance(0).record)
            record = json.loads(ts.provenance(0).record)
            self.assertTrue(isinstance(pts.metadata, dict))
            self.assertTrue('SLiM' in pts.metadata)
            self.assertEqual(record['parameters']['model_type'],
                             pts.metadata['SLiM']['model_type'])
            self.assertEqual(record['slim']['generation'],
                             pts.metadata['SLiM']["generation"])
            self.assertListEqual(list(ts.samples()), list(pts.samples()))
            self.assertArrayEqual(ts.tables.nodes.flags, pts.tables.nodes.flags)
            samples = list(ts.samples())
            t = ts.first()
            pt = pts.first()
            for _ in range(20):
                u = random.sample(samples, 1)[0]
                self.assertEqual(t.parent(u), pt.parent(u))
                if t.parent(u) != tskit.NULL:
                    self.assertEqual(t.branch_length(u), pt.branch_length(u))

    def test_convert_0_3_files(self):
        for ts in self.get_0_3_slim_examples():
            pts = pyslim.SlimTreeSequence(ts)
            self.assertEqual(ts.num_provenances, 1)
            self.assertEqual(pts.num_provenances, 2)
            self.assertEqual(ts.provenance(0).record, pts.provenance(0).record)
            record = json.loads(ts.provenance(0).record)
            self.assertTrue(isinstance(pts.metadata, dict))
            self.assertTrue('SLiM' in pts.metadata)
            self.assertEqual(record['parameters']['model_type'],
                             pts.metadata['SLiM']['model_type'])
            self.assertEqual(record['slim']['generation'],
                             pts.metadata['SLiM']["generation"])
            self.assertListEqual(list(ts.samples()), list(pts.samples()))
            self.assertArrayEqual(ts.tables.nodes.flags, pts.tables.nodes.flags)
            samples = list(ts.samples())
            t = ts.first()
            pt = pts.first()
            for _ in range(20):
                u = random.sample(samples, 1)[0]
                self.assertEqual(t.parent(u), pt.parent(u))
                if t.parent(u) != tskit.NULL:
                    self.assertEqual(t.branch_length(u), pt.branch_length(u))

    def test_convert_0_4_files(self):
        # Note that with version 0.5 and above, we *don't* get information from
        # provenance, we get it from top-level metadata
        for ts in self.get_0_4_slim_examples():
            pts = pyslim.SlimTreeSequence(ts)
            self.assertEqual(ts.num_provenances, 1)
            self.assertEqual(pts.num_provenances, 2)
            self.assertEqual(ts.provenance(0).record, pts.provenance(0).record)
            record = json.loads(ts.provenance(0).record)
            self.assertTrue(isinstance(pts.metadata, dict))
            self.assertTrue('SLiM' in pts.metadata)
            self.assertEqual(record['parameters']['model_type'],
                             pts.metadata['SLiM']['model_type'])
            self.assertEqual(record['slim']['generation'],
                             pts.metadata['SLiM']['generation'])
            self.assertListEqual(list(ts.samples()), list(pts.samples()))
            self.assertArrayEqual(ts.tables.nodes.flags, pts.tables.nodes.flags)
            samples = list(ts.samples())
            t = ts.first()
            pt = pts.first()
            for _ in range(20):
                u = random.sample(samples, 1)[0]
                self.assertEqual(t.parent(u), pt.parent(u))
                if t.parent(u) != tskit.NULL:
                    self.assertEqual(t.branch_length(u), pt.branch_length(u))



