# 用法（在任意目录执行均可）:
#   powershell -File "C:\Users\17659\design-competition-hub\scripts\push-to-github.ps1" -RemoteUrl "https://github.com/你的用户名/design-competition-hub.git"
# 首次 push 前请先在 GitHub 网页上创建空仓库（不要勾选 README）。
param(
    [Parameter(Mandatory = $true)]
    [string]$RemoteUrl
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
    [System.Environment]::GetEnvironmentVariable("Path", "User")

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "未找到 git，请先安装 Git for Windows 并重新打开终端。"
}

git remote get-url origin 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    git remote add origin $RemoteUrl
    Write-Host "已添加 remote origin"
} else {
    git remote set-url origin $RemoteUrl
    Write-Host "已更新 remote origin"
}

git push -u origin main
Write-Host "完成。"
