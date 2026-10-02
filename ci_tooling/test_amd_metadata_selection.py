"""Only the verified delegated Polaris model/build selects the new payload."""
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from opencore_legacy_patcher.detections.device_probe import AMD
from opencore_legacy_patcher.sys_patch.patchsets.hardware.graphics.amd_polaris import AMDPolaris
from opencore_legacy_patcher.sys_patch.patchsets.hardware.graphics.amd_legacy_gcn import AMDLegacyGCN
from opencore_legacy_patcher.sys_patch.patchsets.base import PatchType


class Selection(unittest.TestCase):
    def test_delegated_payload_and_scope(self):
        computer = SimpleNamespace(real_model="MacBookPro13,3", cpu=SimpleNamespace(leafs=["AVX2"]),
                                   gpus=[SimpleNamespace(class_code=0x030000, arch=AMD.Archs.Polaris)])
        constants = SimpleNamespace(computer=computer)
        for major, build in [(23, "23H124"), (24, "24A335"), (24, "24H23"), (24, "24H99"), (25, "25A1")]:
            with self.subTest(major=major, build=build):
                baseline = AMDLegacyGCN(major, 6, build, constants)._model_specific_patches()["AMD Legacy GCN"]
                actual = AMDPolaris(major, 6, build, constants)._model_specific_patches()["AMD Polaris"]
                entries = actual[PatchType.OVERWRITE_SYSTEM_VOLUME]["/System/Library/Extensions"]
                expected = "12.5-24H23-metadata" if (major, build) == (24, "24H23") else "12.5"
                self.assertEqual(entries["AMDShared.bundle"], expected)
                entries["AMDShared.bundle"] = "12.5"
                self.assertEqual(actual, baseline)
        for model in ["MacBookPro14,3", "iMac18,2", "MacPro5,1"]:
            computer.real_model = model
            self.assertNotIn("12.5-24H23-metadata", str(AMDPolaris(24, 6, "24H23", constants)._model_specific_patches()))


if __name__ == "__main__":
    unittest.main()
