[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Plan,

    [Parameter(Mandatory = $true)]
    [string]$Output,

    [switch]$Force
)

$ErrorActionPreference = "Stop"
$skillDir = Split-Path -Parent $PSScriptRoot
$planPath = (Resolve-Path -LiteralPath $Plan).Path
$outputPath = [IO.Path]::GetFullPath($Output)

if ((Test-Path -LiteralPath $outputPath) -and -not $Force) {
    throw "Output already exists. Use -Force to replace it: $outputPath"
}

$planData = Get-Content -LiteralPath $planPath -Raw -Encoding utf8 | ConvertFrom-Json
$templateIds = @($planData.templates | ForEach-Object { $_.id } | Select-Object -Unique)
if ($templateIds.Count -ne 3) {
    throw "The plan must contain exactly three distinct templates."
}
if (-not $planData.slide_plan -or $planData.slide_plan.Count -lt 1) {
    throw "The plan does not contain a slide_plan."
}

$outputDir = Split-Path -Parent $outputPath
if (-not (Test-Path -LiteralPath $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

$powerPoint = $null
$presentation = $null
try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $presentation = $powerPoint.Presentations.Add(0)

    foreach ($item in $planData.slide_plan) {
        $sourcePath = Join-Path $skillDir ([string]$item.donor_asset)
        if (-not (Test-Path -LiteralPath $sourcePath)) {
            throw "Template asset not found: $sourcePath"
        }

        $assetSlide = [int]$item.donor_asset_slide
        [void]$presentation.Slides.InsertFromFile(
            $sourcePath,
            $presentation.Slides.Count,
            $assetSlide,
            $assetSlide
        )

        $copiedSlide = $presentation.Slides.Item($presentation.Slides.Count)
        $copiedSlide.Tags.Add("HFUT_TEMPLATE_ID", [string]$item.donor_template)
        $copiedSlide.Tags.Add("HFUT_ASSET_SLIDE", [string]$item.donor_asset_slide)
        $copiedSlide.Tags.Add("HFUT_SOURCE_FILE", [string]$item.original_source_file)
        $copiedSlide.Tags.Add("HFUT_SOURCE_SLIDE", [string]$item.original_source_slide)
        $copiedSlide.Tags.Add("HFUT_PURPOSE", [string]$item.purpose)
    }

    if (Test-Path -LiteralPath $outputPath) {
        Remove-Item -LiteralPath $outputPath -Force
    }
    $presentation.SaveAs($outputPath, 24)
    Write-Output "Created $outputPath with $($presentation.Slides.Count) slides from: $($templateIds -join ', ')"
}
finally {
    if ($presentation) {
        $presentation.Close()
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($presentation)
    }
    if ($powerPoint) {
        $powerPoint.Quit()
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($powerPoint)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
