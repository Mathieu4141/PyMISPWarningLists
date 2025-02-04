#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import unittest

from glob import glob

from pymispwarninglists import WarningLists, tools


class TestPyMISPWarningLists(unittest.TestCase):

    def setUp(self):
        self.warninglists = WarningLists()

    def test_dump_warninglists(self):
        warninglists_from_files = {}
        for warninglist_file in glob(os.path.join(self.warninglists.root_dir_warninglists, '*', 'list.json')):
            with open(warninglist_file, mode='r', encoding="utf-8") as f:
                warninglist = json.load(f)
            warninglists_from_files[warninglist['name']] = warninglist
        for name, w in self.warninglists.items():
            out = w.to_dict()
            self.assertDictEqual(out, warninglists_from_files[w.name])

    def test_validate_schema_warninglists(self):
        self.warninglists.validate_with_schema()

    def test_json(self):
        for w in self.warninglists.values():
            w.to_json()

    def test_search(self):
        results = self.warninglists.search('8.8.8.8')
        self.assertEqual(results[0].name, 'List of known IPv4 public DNS resolvers')

    def test_slow_search(self):
        self.warninglists = WarningLists(True)
        results = self.warninglists.search('8.8.8.8')
        self.assertIn('List of known IPv4 public DNS resolvers', [r.name for r in results])
        results = self.warninglists.search('100.64.1.56')
        self.assertEqual(results[0].name, 'List of RFC 6598 CIDR blocks')
        results = self.warninglists.search('2001:DB8::34:1')
        self.assertEqual(results[0].name, 'List of RFC 3849 CIDR blocks')
        results = self.warninglists.search('1e100.net')
        self.assertTrue('List of known google domains' in [r.name for r in results])
        results = self.warninglists.search('blah.files.1drv.com')
        self.assertTrue('Top 10K most-used sites from Tranco' in [r.name for r in results])
        results = self.warninglists.search('arbitrary-domain-1e100.net')
        self.assertEqual(results, [])
        results = self.warninglists.search('phishing.co.uk')
        self.assertEqual(results, [])

    def test_fetch_xdg(self):
        tools.update_warninglists()
        self.assertTrue(tools.get_xdg_home_dir().exists())
        warninglists = WarningLists(from_xdg_home=True)
        self.assertEqual(len(warninglists), len(self.warninglists))
