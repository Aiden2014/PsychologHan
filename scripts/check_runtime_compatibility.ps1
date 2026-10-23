<#
.SYNOPSIS
Checks compiled game/Unity member references without launching the game.
.DESCRIPTION
Uses the Mono.Cecil shipped with BepInEx 5. This detects binary API changes
which still compile from the same C# source (for example, a field becoming a
property). It does not replace in-game font/layout and Harmony verification.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string] $PluginPath,
    [Parameter(Mandatory = $true)][string] $ManagedDirectory,
    [Parameter(Mandatory = $true)][string] $CecilPath
)

$ErrorActionPreference = 'Stop'
try {
    $pluginFile = (Resolve-Path -LiteralPath $PluginPath).Path
    $managedPath = (Resolve-Path -LiteralPath $ManagedDirectory).Path
    $cecilFile = (Resolve-Path -LiteralPath $CecilPath).Path
    $null = [System.Reflection.Assembly]::LoadFrom($cecilFile)
    $resolver = [Mono.Cecil.DefaultAssemblyResolver]::new()
    # Never resolve against stale DLLs beside the plugin or in the current cwd.
    foreach ($directory in @($resolver.GetSearchDirectories())) {
        $resolver.RemoveSearchDirectory($directory)
    }
    $resolver.AddSearchDirectory($managedPath)
    $resolver.AddSearchDirectory((Split-Path -Parent $cecilFile))
    $reader = [Mono.Cecil.ReaderParameters]::new()
    $reader.AssemblyResolver = $resolver
    $assembly = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($pluginFile, $reader)
    $checked = 0
    $failures = 0
    try {
        foreach ($member in $assembly.MainModule.GetMemberReferences()) {
            if ($member.DeclaringType.Scope.Name -notmatch '^(Assembly-CSharp(?:-firstpass)?|UnityEngine(?:\..+)?|Unity\..+)$') {
                continue
            }
            $checked++
            try {
                if ($null -eq $member.Resolve()) {
                    Write-Output ('MISSING ' + $member.FullName)
                    $failures++
                }
            } catch {
                Write-Output ('UNRESOLVED ' + $member.FullName + ': ' + $_.Exception.Message)
                $failures++
            }
        }
        if ($checked -eq 0) {
            throw 'No game/Unity member references found; this is not a valid localization plugin check.'
        }
        Write-Output ("Checked {0} game/Unity member references; failures: {1}" -f $checked, $failures)
    } finally {
        $assembly.Dispose()
        $resolver.Dispose()
    }
    if ($failures -gt 0) { exit 1 }
} catch {
    Write-Error $_
    exit 1
}
