[CmdletBinding()]
param(
    [string]$ProjectRoot,
    [string]$PythonPath,
    [string]$NssmPath,
    [string]$DiagnosticPath,
    [switch]$RepairExisting
)

$ErrorActionPreference = "Stop"
$serviceName = "Inseed"
$scriptProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if (-not $ProjectRoot) {
    $ProjectRoot = $scriptProjectRoot
}
if (-not $PythonPath) {
    $PythonPath = (Get-Command python.exe -ErrorAction Stop).Source
}
$wingetPackages = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages"
if (-not $NssmPath) {
    $nssmCommand = Get-Command nssm.exe -ErrorAction SilentlyContinue
    if ($nssmCommand) {
        $NssmPath = $nssmCommand.Source
    } else {
        $NssmPath = Get-ChildItem -LiteralPath $wingetPackages -Directory -Filter "NSSM.NSSM*" |
            ForEach-Object {
                Get-ChildItem -LiteralPath $_.FullName -Directory |
                    ForEach-Object {
                        Get-ChildItem -LiteralPath (Join-Path $_.FullName "win64") -Filter "nssm.exe" -ErrorAction SilentlyContinue
                    }
            } |
            Select-Object -First 1 -ExpandProperty FullName
    }
}

if (-not $NssmPath) {
    throw "NSSM was not found. Install it with: winget install --id NSSM.NSSM --scope user"
}

if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)) {
    $arguments = @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", "`"$PSCommandPath`"",
        "-ProjectRoot", "`"$ProjectRoot`"",
        "-PythonPath", "`"$PythonPath`"",
        "-NssmPath", "`"$NssmPath`""
    )
    if ($RepairExisting) {
        $arguments += "-RepairExisting"
    }
    $diagnosticPath = Join-Path $env:TEMP ("inseed-service-install-" + [Guid]::NewGuid().ToString("N") + ".log")
    $arguments += @("-DiagnosticPath", "`"$diagnosticPath`"")
    $elevated = Start-Process -FilePath "powershell.exe" -Verb RunAs -ArgumentList ($arguments -join " ") -Wait -PassThru
    if ($elevated.ExitCode -ne 0) {
        $details = Get-Content -LiteralPath $diagnosticPath -Raw -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $diagnosticPath -Force -ErrorAction SilentlyContinue
        throw "The elevated service installer failed with exit code $($elevated.ExitCode). $details"
    }
    Remove-Item -LiteralPath $diagnosticPath -Force -ErrorAction SilentlyContinue
    exit 0
}

trap {
    if ($DiagnosticPath) {
        $_ | Out-String | Add-Content -LiteralPath $DiagnosticPath
    }
    exit 1
}

$projectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$pythonPath = (Resolve-Path -LiteralPath $PythonPath).Path
$nssmPath = (Resolve-Path -LiteralPath $NssmPath).Path
$serviceRoot = Join-Path $env:ProgramData "InseedService"
$dataDirectory = Join-Path $serviceRoot "data"
$logDirectory = Join-Path $serviceRoot "logs"
$serviceNssmPath = Join-Path $serviceRoot "nssm.exe"
$envPath = Join-Path $projectRoot ".env"

function Add-LocalServiceAccess {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [System.Security.AccessControl.FileSystemRights]$Rights,
        [System.Security.AccessControl.InheritanceFlags]$InheritanceFlags = [System.Security.AccessControl.InheritanceFlags]::None
    )

    $acl = Get-Acl -LiteralPath $Path
    $rule = [System.Security.AccessControl.FileSystemAccessRule]::new(
        "NT AUTHORITY\LOCAL SERVICE",
        $Rights,
        $InheritanceFlags,
        [System.Security.AccessControl.PropagationFlags]::None,
        [System.Security.AccessControl.AccessControlType]::Allow
    )
    $acl.AddAccessRule($rule)
    Set-Acl -LiteralPath $Path -AclObject $acl
}

New-Item -ItemType Directory -Path $dataDirectory -Force | Out-Null
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null

$existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($existingService) {
    if (-not $RepairExisting) {
        throw "The $serviceName service already exists. Re-run with -RepairExisting to replace it."
    }
    if ($existingService.Status -ne "Stopped") {
        Stop-Service -Name $serviceName -Force
    }
    & $serviceNssmPath remove $serviceName confirm | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Could not remove the existing $serviceName service."
    }
}
Copy-Item -LiteralPath $nssmPath -Destination $serviceNssmPath -Force

if (-not (Test-Path -LiteralPath $envPath)) {
    $random = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $bytes = New-Object byte[] 48
    try {
        $random.GetBytes($bytes)
    } finally {
        $random.Dispose()
    }
    $secret = [Convert]::ToBase64String($bytes).TrimEnd("=").Replace("+", "-").Replace("/", "_")
    Set-Content -LiteralPath $envPath -Value "SECRET_KEY=$secret" -Encoding ASCII -NoNewline
}

$databasePath = Join-Path $projectRoot "inseed_db.db"
$serviceDatabasePath = Join-Path $dataDirectory "inseed_db.db"
if ((Test-Path -LiteralPath $databasePath) -and -not (Test-Path -LiteralPath $serviceDatabasePath)) {
    $backupCode = "import sqlite3; source=sqlite3.connect(r'$databasePath'); target=sqlite3.connect(r'$serviceDatabasePath'); source.backup(target); target.close(); source.close()"
    & $pythonPath -c $backupCode
    if ($LASTEXITCODE -ne 0) {
        throw "Could not copy the existing SQLite database to $serviceDatabasePath."
    }
}

$environmentLines = @(Get-Content -LiteralPath $envPath -ErrorAction SilentlyContinue)
if (-not ($environmentLines | Where-Object { $_ -match "^SQLALCHEMY_DATABASE_URI=" })) {
    $environmentLines += "SQLALCHEMY_DATABASE_URI=sqlite:///$($serviceDatabasePath.Replace('\', '/'))"
}
Set-Content -LiteralPath $envPath -Value $environmentLines -Encoding ASCII

$icacls = Join-Path $env:SystemRoot "System32\icacls.exe"
$pythonDirectory = Split-Path $pythonPath -Parent
$readInheritance = [System.Security.AccessControl.InheritanceFlags]::ContainerInherit -bor [System.Security.AccessControl.InheritanceFlags]::ObjectInherit
Add-LocalServiceAccess -Path $projectRoot -Rights ([System.Security.AccessControl.FileSystemRights]::ReadAndExecute) -InheritanceFlags $readInheritance
Add-LocalServiceAccess -Path $pythonDirectory -Rights ([System.Security.AccessControl.FileSystemRights]::ReadAndExecute) -InheritanceFlags $readInheritance
& $icacls $serviceRoot /grant "NT AUTHORITY\LOCAL SERVICE:(OI)(CI)(RX)" | Out-Null
& $icacls $dataDirectory /grant "NT AUTHORITY\LOCAL SERVICE:(OI)(CI)(M)" /T /C | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Could not grant LocalService access to the application data directory."
}
& $icacls $logDirectory /grant "NT AUTHORITY\LOCAL SERVICE:(OI)(CI)(M)" /T /C | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Could not grant LocalService access to the service logs."
}

& $serviceNssmPath install $serviceName $pythonPath "-m uvicorn app.main:app --host 127.0.0.1 --port 8001"
if ($LASTEXITCODE -ne 0) {
    throw "NSSM could not create the $serviceName service (exit code $LASTEXITCODE)."
}

$settings = @(
    @{ Name = "AppDirectory"; Values = @($projectRoot) },
    @{ Name = "DisplayName"; Values = @("Inseed local project workspace") },
    @{ Name = "Description"; Values = @("Local-only Inseed project and issue tracker.") },
    @{ Name = "Start"; Values = @("SERVICE_AUTO_START") },
    @{ Name = "ObjectName"; Values = @("NT AUTHORITY\LocalService", "") },
    @{ Name = "AppExit"; Values = @("Default", "Restart") },
    @{ Name = "AppRestartDelay"; Values = @("5000") },
    @{ Name = "AppEnvironmentExtra"; Values = @("PYTHONDONTWRITEBYTECODE=1") },
    @{ Name = "AppStdout"; Values = @((Join-Path $logDirectory "service-out.log")) },
    @{ Name = "AppStderr"; Values = @((Join-Path $logDirectory "service-error.log")) },
    @{ Name = "AppRotateFiles"; Values = @("1") },
    @{ Name = "AppRotateOnline"; Values = @("1") },
    @{ Name = "AppRotateBytes"; Values = @("10485760") }
)

foreach ($setting in $settings) {
    $values = $setting.Values
    & $serviceNssmPath set $serviceName $setting.Name @values
    if ($LASTEXITCODE -ne 0) {
        & $serviceNssmPath remove $serviceName confirm | Out-Null
        throw "NSSM could not apply service setting '$($setting.Name)'."
    }
}

& $serviceNssmPath start $serviceName
$startExitCode = $LASTEXITCODE

Start-Sleep -Seconds 2
$service = Get-Service -Name $serviceName
if ($service.Status -ne "Running") {
    throw "The $serviceName service did not start (status $($service.Status), NSSM exit code $startExitCode). Check the logs in $logDirectory."
}
Write-Output "Service status: $($service.Status)"
Write-Output "Local URL: http://127.0.0.1:8001/"
Write-Output "Service data and logs: $serviceRoot"
