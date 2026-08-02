from pathlib import Path
import re
import unittest


PROJECT = Path(__file__).resolve().parents[1]


class Task4StructureTests(unittest.TestCase):
    def test_game_patches_use_typed_harmony_annotation_patches(self):
        patches = (PROJECT / "GamePatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn("[HarmonyPatch(typeof(global::GameManager), nameof(global::GameManager.addMe)", patches)
        self.assertIn("[HarmonyPatch(typeof(global::GameManager), nameof(global::GameManager.addSpeaker)", patches)
        self.assertIn("[HarmonyPatch(typeof(global::GameManager), nameof(global::GameManager.updateClientsSection))]", patches)
        self.assertIn('[HarmonyPatch(typeof(global::DeathRunes), "setRunes")]', patches)
        self.assertGreaterEqual(patches.count("[HarmonyPrefix]"), 2)
        self.assertGreaterEqual(patches.count("[HarmonyPostfix]"), 2)
        self.assertIn("global::GameManager __instance", patches)
        self.assertIn("global::DeathRunes __instance", patches)

    def test_production_patches_do_not_use_reflection_registration_or_field_helpers(self):
        patches = (PROJECT / "GamePatches.cs").read_text(encoding="utf-8-sig")

        forbidden_tokens = [
            "TypeByName",
            "AccessTools.",
            "GetFieldValue",
            "GetText(",
            "SetText(",
            "object __instance",
        ]
        for token in forbidden_tokens:
            with self.subTest(token=token):
                self.assertNotIn(token, patches)

        self.assertIsNone(re.search(r"\bharmony\.Patch\s*\(", patches))

    def test_plugin_uses_patchall_and_keeps_unpatchself(self):
        plugin = (PROJECT / "Plugin.cs").read_text(encoding="utf-8-sig")

        self.assertIn("harmony.PatchAll();", plugin)
        self.assertIn("harmony.UnpatchSelf();", plugin)
        self.assertNotIn("GamePatches.Apply", plugin)

    def test_csproj_references_target_unity_2021_managed_assemblies(self):
        csproj = (PROJECT / "PsychologHan.csproj").read_text(encoding="utf-8-sig")

        self.assertNotIn("UnityEngine.Modules", csproj)
        self.assertNotIn("UnityEngine.TextCoreModule", csproj)
        self.assertNotIn(r"D:\SteamLibrary\steamapps\common\Psycholog", csproj)

        expected_references = [
            "Assembly-CSharp.dll",
            "UnityEngine.dll",
            "UnityEngine.CoreModule.dll",
            "UnityEngine.UI.dll",
            "UnityEngine.UIModule.dll",
            "Unity.TextMeshPro.dll",
            "UnityEngine.TextRenderingModule.dll",
        ]
        for dll_name in expected_references:
            with self.subTest(dll_name=dll_name):
                self.assertIn(r"$(GamePath)\Psycholog_Data\Managed\\".replace("\\\\", "\\") + dll_name, csproj)

        self.assertGreaterEqual(csproj.count("<Private>false</Private>"), len(expected_references))
