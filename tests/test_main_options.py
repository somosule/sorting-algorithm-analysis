"""Tests for the command-line options that switch on the optional steps."""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import config
from main import _apply_options, _parse_args, _write_run_info

SWITCHES = ("RUN_BUBBLE_FULL", "RUN_MISSING_VALUES", "RUN_RECORD_LOOKUP")


class TestMainOptions(unittest.TestCase):
    def setUp(self):
        # Start every test with all three switches off, and put back the
        # real values afterwards so no other test is affected.
        for switch in SWITCHES:
            patcher = patch.object(config, switch, False)
            patcher.start()
            self.addCleanup(patcher.stop)

    def _switches(self):
        return {switch: getattr(config, switch) for switch in SWITCHES}

    def test_no_options_leaves_every_extra_off(self):
        _apply_options(_parse_args([]))
        self.assertEqual(self._switches(),
                         {switch: False for switch in SWITCHES})

    def test_each_option_switches_on_only_its_own_step(self):
        for option, switch in (("--bubble-check", "RUN_BUBBLE_FULL"),
                               ("--missing-values", "RUN_MISSING_VALUES"),
                               ("--record-lookup", "RUN_RECORD_LOOKUP")):
            with self.subTest(option=option):
                for name in SWITCHES:
                    setattr(config, name, False)
                _apply_options(_parse_args([option]))
                expected = {name: name == switch for name in SWITCHES}
                self.assertEqual(self._switches(), expected)

    def test_all_extras_switches_on_all_three(self):
        _apply_options(_parse_args(["--all-extras"]))
        self.assertEqual(self._switches(),
                         {switch: True for switch in SWITCHES})

    def test_a_switch_already_on_in_config_stays_on(self):
        config.RUN_RECORD_LOOKUP = True
        _apply_options(_parse_args([]))
        self.assertTrue(config.RUN_RECORD_LOOKUP)

    def test_run_info_records_the_extras(self):
        _apply_options(_parse_args(["--bubble-check", "--record-lookup"]))
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(config, "RESULTS_DIR", Path(directory)):
                path = _write_run_info()
            with open(path, newline="", encoding="utf-8") as file:
                settings = {row["setting"]: row["value"]
                            for row in csv.DictReader(file)}
        self.assertEqual(settings["extras_run"],
                         "bubble-check, record-lookup")


if __name__ == "__main__":
    unittest.main()
