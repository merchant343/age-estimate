param([string]$Url='http://127.0.0.1:8000',[int]$DurationSec=90,[string]$LogPath='verification_logs/deploy.csv',[string]$SummaryPath='verification_logs/deploy-summary.md')
$ErrorActionPreference='Continue'; $dir=Split-Path -Parent $LogPath; New-Item -ItemType Directory -Force -Path $dir | Out-Null
$img=Join-Path $dir 'fixed-test.png'; [IO.File]::WriteAllBytes($img,[Convert]::FromBase64String('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='))
$rows=@(); $startAll=[DateTimeOffset]::UtcNow; $previous=$null; $maxGap=0
for($i=0;$i -lt $DurationSec;$i++){
  $s=[DateTimeOffset]::UtcNow; $sw=[Diagnostics.Stopwatch]::StartNew(); $tmp=[IO.Path]::GetTempFileName(); $status=0; $ok=$false; $version='unknown'
  try{$status=[int](& curl.exe -sS -o $tmp -w '%{http_code}' -F "file=@$img;type=image/png" -F 'region=kr' "$Url/api/analyze"); $body=Get-Content $tmp -Raw; $json=$body|ConvertFrom-Json; $version=[string]$json.model_version; $ok=($status -eq 200 -and $json.estimated_age_range)}catch{$body=$_.Exception.Message}
  $sw.Stop(); $e=[DateTimeOffset]::UtcNow; if($previous){$gap=($s-$previous).TotalSeconds; if($gap -gt $maxGap){$maxGap=$gap}}; $previous=$s
  $row=[pscustomobject]@{start_utc=$s.ToString('o');end_utc=$e.ToString('o');response_ms=$sw.ElapsedMilliseconds;status=$status;analysis_ok=$ok;model_version=$version}; $rows+=$row; Write-Output ($row|ConvertTo-Json -Compress); Remove-Item $tmp -Force -ErrorAction SilentlyContinue; $sleep=[Math]::Max(0,1000-$sw.ElapsedMilliseconds); Start-Sleep -Milliseconds $sleep
}
$rows | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $LogPath
$success=($rows|Where-Object analysis_ok).Count; $failed=$rows.Count-$success; @("# Deployment verification","","- URL: $Url","- Window UTC: $($startAll.ToString('o')) - $([DateTimeOffset]::UtcNow.ToString('o'))","- Requests: $($rows.Count) (success $success, failed $failed)","- Target interval: 1 second","- Maximum observed gap: $([math]::Round($maxGap,3)) seconds","- Unobserved gaps: any gap over 2 seconds is unverified","- Versions observed: $((($rows|Select-Object -ExpandProperty model_version -Unique) -join ', '))","- Synthetic fixed image: yes","","Observed requests are not a proof of zero downtime outside this window.") | Set-Content -Encoding UTF8 -Path $SummaryPath
