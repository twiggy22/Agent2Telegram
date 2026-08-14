import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent2telegram.instance_lock import InstanceAlreadyRunning, acquire


class InstanceLockTests(unittest.TestCase):
    def test_same_config_cannot_be_acquired_twice(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = {
                "AGENT2TELEGRAM_CONFIG": str(Path(tmp) / "config.json"),
                "AGENT2TELEGRAM_STATE": str(Path(tmp) / "state"),
            }
            with patch.dict(os.environ, env, clear=False):
                first = acquire()
                try:
                    with self.assertRaises(InstanceAlreadyRunning):
                        acquire()
                finally:
                    first.close()

    def test_different_configs_can_run_together(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = str(Path(tmp) / "state")
            with patch.dict(os.environ, {"AGENT2TELEGRAM_STATE": state}, clear=False):
                with patch.dict(os.environ, {"AGENT2TELEGRAM_CONFIG": str(Path(tmp) / "one.json")}, clear=False):
                    first = acquire()
                try:
                    with patch.dict(os.environ, {"AGENT2TELEGRAM_CONFIG": str(Path(tmp) / "two.json")}, clear=False):
                        second = acquire()
                    second.close()
                finally:
                    first.close()


if __name__ == "__main__":
    unittest.main()
