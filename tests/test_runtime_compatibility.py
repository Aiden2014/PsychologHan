"""Exercise the binary checker with generated assemblies, without a game install."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[1]


class RuntimeCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pwsh = shutil.which("pwsh")
        configured = os.environ.get("PSYCHOLOGHAN_CECIL_PATH")
        candidates = [Path(configured)] if configured else sorted(
            (Path.home() / ".nuget/packages/mono.cecil").glob(
                "*/lib/netstandard2.0/Mono.Cecil.dll"
            ), reverse=True
        )
        if not cls.pwsh or not candidates or not candidates[0].is_file():
            raise unittest.SkipTest(
                "Requires PowerShell 7 and Mono.Cecil (NuGet cache or PSYCHOLOGHAN_CECIL_PATH)"
            )
        cls.cecil = candidates[0]
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name)
        fixture = cls.root / "fixture.ps1"
        fixture.write_text(r'''
param([string] $Root, [string] $Cecil)
$ErrorActionPreference = 'Stop'
$null = [Reflection.Assembly]::LoadFrom($Cecil)
$version = [Version]::new(1, 0, 0, 0)
$api = [Mono.Cecil.AssemblyDefinition]::CreateAssembly(
    [Mono.Cecil.AssemblyNameDefinition]::new('Unity.TestApi', $version),
    'Unity.TestApi', [Mono.Cecil.ModuleKind]::Dll)
$module = $api.MainModule
$asset = [Mono.Cecil.TypeDefinition]::new('TMPro', 'TMP_Asset',
    [Mono.Cecil.TypeAttributes]::Public, $module.TypeSystem.Object)
$module.Types.Add($asset)
$getter = [Mono.Cecil.MethodDefinition]::new('get_material',
    [Mono.Cecil.MethodAttributes]::Public, $module.TypeSystem.String)
$asset.Methods.Add($getter)
$property = [Mono.Cecil.PropertyDefinition]::new('material',
    [Mono.Cecil.PropertyAttributes]::None, $module.TypeSystem.String)
$property.GetMethod = $getter
$asset.Properties.Add($property)
$scene = [Mono.Cecil.TypeDefinition]::new('UnityEngine', 'Scene',
    [Mono.Cecil.TypeAttributes]::Public, $module.TypeSystem.Object)
$module.Types.Add($scene)
$handle = [Mono.Cecil.MethodDefinition]::new('get_handle',
    [Mono.Cecil.MethodAttributes]::Public, $module.TypeSystem.Int64)
$scene.Methods.Add($handle)
$null = New-Item -ItemType Directory -Path (Join-Path $Root 'Managed')
$api.Write((Join-Path $Root 'Managed/Unity.TestApi.dll'))

foreach ($legacy in @($true, $false)) {
    $name = if ($legacy) { 'LegacyPlugin' } else { 'RebuiltPlugin' }
    $plugin = [Mono.Cecil.AssemblyDefinition]::CreateAssembly(
        [Mono.Cecil.AssemblyNameDefinition]::new($name, $version),
        $name, [Mono.Cecil.ModuleKind]::Dll)
    $pm = $plugin.MainModule
    $scope = [Mono.Cecil.AssemblyNameReference]::new('Unity.TestApi', $version)
    $pm.AssemblyReferences.Add($scope)
    $assetRef = [Mono.Cecil.TypeReference]::new('TMPro', 'TMP_Asset', $pm, $scope)
    $sceneRef = [Mono.Cecil.TypeReference]::new('UnityEngine', 'Scene', $pm, $scope)
    $type = [Mono.Cecil.TypeDefinition]::new('Test', 'Plugin',
        [Mono.Cecil.TypeAttributes]::Public, $pm.TypeSystem.Object)
    $pm.Types.Add($type)
    $method = [Mono.Cecil.MethodDefinition]::new('Probe',
        [Mono.Cecil.MethodAttributes]::Public, $pm.TypeSystem.Void)
    $type.Methods.Add($method)
    $il = $method.Body.GetILProcessor()
    $il.Emit([Mono.Cecil.Cil.OpCodes]::Ldnull)
    if ($legacy) {
        $field = [Mono.Cecil.FieldReference]::new('material', $pm.TypeSystem.String, $assetRef)
        $il.Emit([Mono.Cecil.Cil.OpCodes]::Ldfld, $field)
    } else {
        $get = [Mono.Cecil.MethodReference]::new('get_material', $pm.TypeSystem.String, $assetRef)
        $get.HasThis = $true
        $il.Emit([Mono.Cecil.Cil.OpCodes]::Callvirt, $get)
    }
    $il.Emit([Mono.Cecil.Cil.OpCodes]::Pop)
    $il.Emit([Mono.Cecil.Cil.OpCodes]::Ldnull)
    $returnType = if ($legacy) { $pm.TypeSystem.Int32 } else { $pm.TypeSystem.Int64 }
    $getHandle = [Mono.Cecil.MethodReference]::new('get_handle', $returnType, $sceneRef)
    $getHandle.HasThis = $true
    $il.Emit([Mono.Cecil.Cil.OpCodes]::Callvirt, $getHandle)
    $il.Emit([Mono.Cecil.Cil.OpCodes]::Pop)
    $il.Emit([Mono.Cecil.Cil.OpCodes]::Ret)
    $plugin.Write((Join-Path $Root ($name + '.dll')))
    $plugin.Dispose()
}
$api.Dispose()
''', encoding="utf-8")
        result = subprocess.run(
            [cls.pwsh, "-NoProfile", "-File", str(fixture),
             "-Root", str(cls.root), "-Cecil", str(cls.cecil)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)

    def check_plugin(self, name, managed="Managed"):
        return subprocess.run(
            [self.pwsh, "-NoProfile", "-File",
             str(PROJECT / "scripts/check_runtime_compatibility.ps1"),
             "-PluginPath", str(self.root / name),
             "-ManagedDirectory", str(self.root / managed),
             "-CecilPath", str(self.cecil)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )

    def test_old_binary_detects_field_to_property_and_return_type_changes(self):
        result = self.check_plugin("LegacyPlugin.dll")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("MISSING System.String TMPro.TMP_Asset::material", result.stdout)
        self.assertIn("MISSING System.Int32 UnityEngine.Scene::get_handle()", result.stdout)
        self.assertIn("failures: 2", result.stdout)

    def test_rebuilt_binary_resolves_current_api(self):
        result = self.check_plugin("RebuiltPlugin.dll")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Checked 2 game/Unity member references; failures: 0", result.stdout)

    def test_missing_dependency_is_a_failure(self):
        (self.root / "EmptyManaged").mkdir(exist_ok=True)
        result = self.check_plugin("RebuiltPlugin.dll", managed="EmptyManaged")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("UNRESOLVED", result.stdout)


if __name__ == "__main__":
    unittest.main()
