[CmdletBinding()]
param(
    [ValidateSet('status', 'health-check', 'build', 'start-all', 'stop-all', 'start', 'stop', 'restart', 'logs')]
    [string]$Action = 'status',
    [ValidateSet('xiaohongshu-mcp', 'webbridge-mcp', 'all')]
    [string]$Name = 'all'
)

$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ResearchRoot = (Resolve-Path (Join-Path $ScriptDir '..\..')).Path
$SocialHome = if ($env:SOCIAL_MCP_HOME) { $env:SOCIAL_MCP_HOME } elseif ($env:ROS_SOCIAL_HOME) { $env:ROS_SOCIAL_HOME } else { Join-Path $HOME '.researchos\social_mcp' }
$LogDir = Join-Path $SocialHome 'logs'
$PidDir = Join-Path $SocialHome 'pids'
New-Item -ItemType Directory -Path $LogDir,$PidDir -Force | Out-Null

function EnvOrDefault([string]$Name, [string]$Default) {
    $value = [Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrWhiteSpace($value)) { $value = [Environment]::GetEnvironmentVariable($Name, 'User') }
    if ([string]::IsNullOrWhiteSpace($value)) { return $Default }
    return $value
}

$KimiUrl = (EnvOrDefault 'SOCIAL_MCP_KIMI_URL' (EnvOrDefault 'ROS_WEBBRIDGE_URL' 'http://127.0.0.1:10086')).TrimEnd('/')
$KimiStatusUrl = "$KimiUrl/status"
$XhsRepo = EnvOrDefault 'SOCIAL_MCP_XHS_REPO' (Join-Path $ResearchRoot '..\rednote-mcp')
$XhsRepo = [IO.Path]::GetFullPath($XhsRepo)
$XhsPort = [int](EnvOrDefault 'SOCIAL_MCP_XHS_PORT' '18060')
$XhsAddress = "127.0.0.1:$XhsPort"
$XhsBin = EnvOrDefault 'SOCIAL_MCP_XHS_BIN' ''
if ([string]::IsNullOrWhiteSpace($XhsBin)) {
    $candidates = @(
        (Join-Path $XhsRepo 'bin\xhs-mcp.exe'),
        (Join-Path $XhsRepo 'bin\xhs-mcp'),
        (Join-Path $XhsRepo 'xiaohongshu-mcp.exe')
    )
    $XhsBin = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
$WebRepo = [IO.Path]::GetFullPath((EnvOrDefault 'SOCIAL_MCP_WEBBRIDGE_MCP_REPO' (Join-Path $ScriptDir 'webbridge_mcp')))
$WebPort = [int](EnvOrDefault 'SOCIAL_MCP_WEBBRIDGE_MCP_PORT' '18061')
$WebAddress = "127.0.0.1:$WebPort"
$WebBin = EnvOrDefault 'SOCIAL_MCP_WEBBRIDGE_MCP_BIN' (Join-Path $SocialHome 'bin\webbridge-mcp.exe')

function PortPid([int]$Port) {
    $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($connection) { return [int]$connection.OwningProcess }
    return $null
}

function Write-Log([string]$Message) { Write-Output "[$(Get-Date -Format s)] $Message" }

function Get-Status([string]$Label, [int]$Port) {
    $ownerPid = PortPid $Port
    if ($ownerPid) { Write-Log "$Label listening on :$Port (pid=$ownerPid)" } else { Write-Log "$Label not listening on :$Port" }
    return $ownerPid
}

function Build-WebBridge {
    $go = EnvOrDefault 'SOCIAL_MCP_GO' (EnvOrDefault 'GO_EXE' '')
    if ([string]::IsNullOrWhiteSpace($go)) {
        $goCommand = Get-Command go -ErrorAction SilentlyContinue
        if ($goCommand) { $go = $goCommand.Source }
    }
    if ([string]::IsNullOrWhiteSpace($go)) { throw 'Go not found; set SOCIAL_MCP_GO to a Go executable' }
    if (-not (Test-Path -LiteralPath $WebRepo)) { throw "webbridge-mcp repo not found: $WebRepo" }
    New-Item -ItemType Directory -Path (Split-Path -Parent $WebBin) -Force | Out-Null
    Write-Log "building webbridge-mcp -> $WebBin"
    & $go -C $WebRepo build -o $WebBin .
    if ($LASTEXITCODE -ne 0) { throw "webbridge-mcp build failed ($LASTEXITCODE)" }
}

function Set-XhsRuntimeEnvironment {
    if ([string]::IsNullOrWhiteSpace($env:XHS_CAMOUFOX_BIN)) {
        $candidate = Join-Path $XhsRepo 'bin\camoufox\camoufox.exe'
        if (Test-Path -LiteralPath $candidate) { $env:XHS_CAMOUFOX_BIN = $candidate }
    }
    if ([string]::IsNullOrWhiteSpace($env:PLAYWRIGHT_DRIVER_PATH)) {
        $candidate = Join-Path $XhsRepo '.playwright-driver'
        if (Test-Path -LiteralPath (Join-Path $candidate 'package\cli.js')) { $env:PLAYWRIGHT_DRIVER_PATH = $candidate }
    }
    if ([string]::IsNullOrWhiteSpace($env:COOKIES_PATH)) {
        $env:COOKIES_PATH = Join-Path $XhsRepo 'cookies.json'
    }
    if ([string]::IsNullOrWhiteSpace($env:PLAYWRIGHT_NODEJS_PATH)) {
        $node = EnvOrDefault 'PLAYWRIGHT_NODEJS_PATH' ''
        if (-not [string]::IsNullOrWhiteSpace($node)) { $env:PLAYWRIGHT_NODEJS_PATH = $node }
    }
    if ([string]::IsNullOrWhiteSpace($env:PLAYWRIGHT_NPM_PATH)) {
        $npm = EnvOrDefault 'PLAYWRIGHT_NPM_PATH' ''
        if (-not [string]::IsNullOrWhiteSpace($npm)) { $env:PLAYWRIGHT_NPM_PATH = $npm }
    }
}

function Start-WebBridge {
    $existing = PortPid $WebPort
    if ($existing) { Write-Log "webbridge-mcp already running on :$WebPort (pid=$existing)"; return }
    if (-not (Test-Path -LiteralPath $WebBin)) { Build-WebBridge }
    $logOut = Join-Path $LogDir 'webbridge-mcp.stdout.log'
    $logErr = Join-Path $LogDir 'webbridge-mcp.stderr.log'
    $proc = Start-Process -FilePath $WebBin -ArgumentList @('-port', $WebAddress) -WorkingDirectory $WebRepo -WindowStyle Hidden -RedirectStandardOutput $logOut -RedirectStandardError $logErr -PassThru
    Set-Content -LiteralPath (Join-Path $PidDir 'webbridge-mcp.pid') -Value $proc.Id
    Start-Sleep -Seconds 2
    if (-not (PortPid $WebPort)) { throw "webbridge-mcp did not bind :$WebPort; see $logErr" }
    Write-Log "webbridge-mcp started (pid=$($proc.Id))"
}

function Start-Xhs {
    $existing = PortPid $XhsPort
    if ($existing) { Write-Log "xiaohongshu-mcp already running on :$XhsPort (pid=$existing)"; return }
    if ([string]::IsNullOrWhiteSpace($XhsBin) -or -not (Test-Path -LiteralPath $XhsBin)) { throw "xiaohongshu-mcp binary not found; set SOCIAL_MCP_XHS_BIN (repo=$XhsRepo)" }
    Set-XhsRuntimeEnvironment
    $logOut = Join-Path $LogDir 'xiaohongshu-mcp.stdout.log'
    $logErr = Join-Path $LogDir 'xiaohongshu-mcp.stderr.log'
    $proc = Start-Process -FilePath $XhsBin -ArgumentList @('-headless=true', '-port', $XhsAddress) -WorkingDirectory $XhsRepo -WindowStyle Hidden -RedirectStandardOutput $logOut -RedirectStandardError $logErr -PassThru
    Set-Content -LiteralPath (Join-Path $PidDir 'xiaohongshu-mcp.pid') -Value $proc.Id
    Start-Sleep -Seconds 2
    if (-not (PortPid $XhsPort)) { throw "xiaohongshu-mcp did not bind :$XhsPort; see $logErr" }
    Write-Log "xiaohongshu-mcp started (pid=$($proc.Id))"
}

function Stop-Owned([string]$Service, [int]$Port) {
    $pidPath = Join-Path $PidDir "$Service.pid"
    if (-not (Test-Path -LiteralPath $pidPath)) { Write-Log "$Service is not managed by this runtime; leaving :$Port untouched"; return }
    $ownerPid = [int](Get-Content -LiteralPath $pidPath -Raw)
    $process = Get-Process -Id $ownerPid -ErrorAction SilentlyContinue
    if ($process) { Stop-Process -Id $ownerPid -Force }
    Remove-Item -LiteralPath $pidPath -Force
    Write-Log "$Service stopped (pid=$ownerPid)"
}

function Check-Health {
    $ok = $true
    try {
        $kimi = Invoke-RestMethod -Uri $KimiStatusUrl -TimeoutSec 3
        if ($kimi.running -and $kimi.extension_connected) { Write-Log 'Kimi WebBridge healthy' } else { Write-Log "Kimi WebBridge degraded: $($kimi | ConvertTo-Json -Compress)"; $ok = $false }
    } catch { Write-Log "Kimi WebBridge unreachable: $($_.Exception.Message)"; $ok = $false }
    foreach ($item in @(@{Name='xiaohongshu-mcp'; Port=$XhsPort; Url="http://127.0.0.1:$XhsPort/health"}, @{Name='webbridge-mcp'; Port=$WebPort; Url="http://127.0.0.1:$WebPort/health"})) {
        if (-not (PortPid $item.Port)) { Write-Log "$($item.Name) not listening"; $ok = $false; continue }
        try { $health = Invoke-RestMethod -Uri $item.Url -TimeoutSec 5; Write-Log "$($item.Name) health: $($health | ConvertTo-Json -Compress)" } catch { Write-Log "$($item.Name) health failed: $($_.Exception.Message)"; $ok = $false }
    }
    if (-not $ok) { exit 1 }
}

switch ($Action) {
    'status' { Get-Status 'xiaohongshu-mcp' $XhsPort; Get-Status 'webbridge-mcp' $WebPort; Write-Log "Kimi WebBridge endpoint: $KimiUrl"; break }
    'health-check' { Check-Health; break }
    'build' { Build-WebBridge; break }
    'start-all' { Start-Xhs; Start-WebBridge; break }
    'stop-all' { Stop-Owned 'xiaohongshu-mcp' $XhsPort; Stop-Owned 'webbridge-mcp' $WebPort; break }
    'start' { if ($Name -eq 'xiaohongshu-mcp') { Start-Xhs } elseif ($Name -eq 'webbridge-mcp') { Start-WebBridge } else { Start-Xhs; Start-WebBridge }; break }
    'stop' { if ($Name -eq 'xiaohongshu-mcp') { Stop-Owned 'xiaohongshu-mcp' $XhsPort } elseif ($Name -eq 'webbridge-mcp') { Stop-Owned 'webbridge-mcp' $WebPort } else { Stop-Owned 'xiaohongshu-mcp' $XhsPort; Stop-Owned 'webbridge-mcp' $WebPort }; break }
    'restart' { if ($Name -eq 'xiaohongshu-mcp') { Stop-Owned 'xiaohongshu-mcp' $XhsPort; Start-Xhs } elseif ($Name -eq 'webbridge-mcp') { Stop-Owned 'webbridge-mcp' $WebPort; Start-WebBridge } else { Stop-Owned 'xiaohongshu-mcp' $XhsPort; Stop-Owned 'webbridge-mcp' $WebPort; Start-Xhs; Start-WebBridge }; break }
    'logs' { $log = if ($Name -eq 'xiaohongshu-mcp') { Join-Path $LogDir 'xiaohongshu-mcp.stderr.log' } else { Join-Path $LogDir 'webbridge-mcp.stderr.log' }; Get-Content -LiteralPath $log -Wait }
}
