param(
    [string]$Token = "",
    [string]$ExporterPath = "C:\Users\guilh\Downloads\DiscordChatExporter.Cli.win-x64"
)

if (-not $Token) {
    $envFile = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) ".env"
    if (Test-Path $envFile) {
        $envContent = Get-Content $envFile -Raw -Encoding UTF8
        if ($envContent -match 'DISCORD_TOKEN=(.+)') {
            $Token = $Matches[1].Trim()
        }
    }
}

if (-not $Token) {
    Write-Host "Token do Discord nao encontrado!" -ForegroundColor Red
    Write-Host "Crie um arquivo .env na mesma pasta com: DISCORD_TOKEN=seu_token_aqui" -ForegroundColor Yellow
    Write-Host "Ou execute: .\atualizar_ranking.ps1 -Token SEU_TOKEN" -ForegroundColor Yellow
    exit 1
}

$ErrorActionPreference = "Stop"
$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Exe = Join-Path $ExporterPath "DiscordChatExporter.Cli.exe"
$TempJson = Join-Path $RepoDir "temp_export.json"
$RankingJson = Join-Path $RepoDir "ranking.json"
$ChannelId = "1520758855129235456"

Write-Host "=== Atualizando Ranking haCARthon ===" -ForegroundColor Magenta

# 1. Exportar canal do Discord
Write-Host "[1/4] Exportando canal do Discord..." -ForegroundColor Cyan
if (-not (Test-Path $Exe)) {
    Write-Host "ERRO: DiscordChatExporter nao encontrado em: $Exe" -ForegroundColor Red
    exit 1
}

& $Exe export -c $ChannelId -t $Token -f Json -o $TempJson
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Falha ao exportar canal do Discord" -ForegroundColor Red
    exit 1
}

# 2. Processar JSON extraindo curtidas
Write-Host "[2/4] Processando curtidas..." -ForegroundColor Cyan
$raw = Get-Content $TempJson -Raw -Encoding UTF8 | ConvertFrom-Json
$messages = $raw.messages

$ranking = @()
foreach ($msg in $messages) {
    $temAnexo = ($msg.attachments | Measure-Object).Count -gt 0
    if (-not $temAnexo) { continue }

    $curtidas = 0
    foreach ($react in $msg.reactions) {
        if ($react.emoji.name -eq "👍" -or $react.emoji.code -eq "thumbsup") {
            $curtidas = $react.count
            break
        }
    }

    $autor = if ($msg.author.nickname) { $msg.author.nickname } else { $msg.author.name }
    $nick = $msg.author.name
    $texto = $msg.content -replace '\s+', ' '
    if ($texto.Length -gt 80) { $texto = $texto.Substring(0, 77) + "..." }
    if ([string]::IsNullOrWhiteSpace($texto)) { $texto = "(foto)" }

    $ranking += [PSCustomObject]@{
        autor    = $autor
        nick     = $nick
        curtidas = $curtidas
        resumo   = $texto
    }
}

# Ordenar por curtidas decrescente
$ranking = $ranking | Sort-Object -Property curtidas -Descending

$rankList = @()
$pos = 1
foreach ($item in $ranking) {
    $rankList += [PSCustomObject]@{
        posicao  = $pos
        autor    = $item.autor
        nick     = $item.nick
        curtidas = $item.curtidas
        resumo   = $item.resumo
    }
    $pos++
}

$output = [PSCustomObject]@{
    atualizadoEm = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffK")
    fonte        = "Discord - #📸-tô-no-hacarthon"
    ranking      = $rankList
}

$output | ConvertTo-Json -Depth 10 | Set-Content $RankingJson -Encoding UTF8
Write-Host "  -> $($rankList.Count) participantes no ranking" -ForegroundColor Green

# 3. Limpar arquivo temporário
Remove-Item $TempJson -Force -ErrorAction SilentlyContinue

# 4. Git commit e push
Write-Host "[3/4] Fazendo commit e push..." -ForegroundColor Cyan
Set-Location $RepoDir
git add ranking.json
$dataStr = (Get-Date).ToString("HH:mm")
git commit -m "atualiza ranking curtidas $dataStr"
if ($LASTEXITCODE -eq 0) {
    Write-Host "[4/4] Fazendo push para GitHub..." -ForegroundColor Cyan
    git push
    Write-Host ""
    Write-Host "=== Ranking atualizado com sucesso! ===" -ForegroundColor Green
    Write-Host "Aguardando ~1 min para o Vercel fazer deploy." -ForegroundColor Yellow
} else {
    Write-Host "Nenhuma mudanca para commitar (ranking ja atualizado)." -ForegroundColor Yellow
}
