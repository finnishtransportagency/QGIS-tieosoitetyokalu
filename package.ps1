<#
.SYNOPSIS
    Rakentaa julkaisukelpoisen ZIP-paketin Tieosoitetyokalu-QGIS-pluginista.

.DESCRIPTION
    Kokoaa pluginin tiedostot eksplisiittisen sisallytyslistan perusteella,
    tarkistaa etta kaikki pakolliset tiedostot ovat olemassa ja kirjoittaa
    ZIP-paketin joka lapaisee plugins.qgis.org:n validoinnin.

    Skripti ei generoi johdettuja tiedostoja. Se olettaa etta resources.py on
    kaannetty resources.qrc:sta ja i18n/*.qm .ts-tiedostoista (ks. translate.bat).
    Jos ne puuttuvat, skripti keskeytyy virheeseen.

.PARAMETER Version
    Paketin versio ZIP-tiedostonimessa. Oletuksena metadata.txt:n version-kentta.

.PARAMETER OutputDir
    Hakemisto johon ZIP kirjoitetaan. Oletus: zip_build (on .gitignoressa).

.PARAMETER Force
    Ylikirjoita olemassa oleva ZIP-tiedosto.

.PARAMETER DryRun
    Nayta mita paketoitaisiin, mutta ala kirjoita ZIP-tiedostoa.

.PARAMETER CheckUrls
    Tarkista metadata.txt:n homepage-, tracker- ja repository-linkit HTTP HEAD
    -pyynnolla. plugins.qgis.org tekee saman palvelinpuolella.

.PARAMETER SkipPolicyChecks
    Ohita julkaisupolitiikan tarkistukset (versionumeron kasvu, changelog,
    QGIS-versiohaarukan eheys). Kayta vain sisaisiin valijulkaisuihin.

.PARAMETER ValidateOnly
    Validoi olemassa oleva ZIP-tiedosto rakentamatta uutta. Kayta esimerkiksi
    aiemman julkaisun tarkistamiseen.

.EXAMPLE
    .\package.ps1 -DryRun
    Listaa paketoitavat tiedostot kirjoittamatta ZIP-tiedostoa.

.EXAMPLE
    .\package.ps1
    Rakentaa zip_build\Tieosoitetyokalu-<versio>.zip ja validoi sen.
#>

[CmdletBinding()]
param(
    [string] $Version,
    [string] $OutputDir = 'zip_build',
    [switch] $Force,
    [switch] $DryRun,
    [switch] $CheckUrls,
    [switch] $SkipPolicyChecks,
    [string] $ValidateOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Invoke-WebRequestin edistymispalkki sotkisi tulosteen (-CheckUrls).
$ProgressPreference = 'SilentlyContinue'

# ZIP-kasittely tarvitsee molemmat kokoonpanot .NET Frameworkissa:
#   System.IO.Compression              -> ZipArchive, ZipArchiveMode, CompressionLevel
#   System.IO.Compression.FileSystem   -> ZipFile, ZipFileExtensions
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

# ---------------------------------------------------------------------------
# Vakiot
# ---------------------------------------------------------------------------

# Pluginin hakemiston nimi ZIPin sisalla. Taman TAYTYY pysya samana, koska
# plugins.qgis.org tunnistaa jo julkaistun pluginin talla nimella
# (package_name). Nimen muutos saisi paketin nayttamaan uudelta pluginilta,
# jolloin siihen sovellettaisiin PEP 8 -nimeamissaantoa ja se hylattaisiin.
$script:PluginDirName = 'Tieosoitetyokalu'

$script:RepoRoot  = $PSScriptRoot
$script:PluginDir = Join-Path $script:RepoRoot $script:PluginDirName

# plugins.qgis.org: PLUGIN_MAX_UPLOAD_SIZE, julkaisuohjeissa mainittu 20 MB.
$script:MaxPackageBytes = 20MB

# ---------------------------------------------------------------------------
# Tulostusapurit
# ---------------------------------------------------------------------------

function Write-Step {
    param([string] $Message)
    Write-Host ''
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Write-Ok {
    param([string] $Message)
    Write-Host "    [OK]  $Message" -ForegroundColor Green
}

function Write-Warn2 {
    param([string] $Message)
    Write-Host "    [VAR] $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string] $Message)
    Write-Host "          $Message" -ForegroundColor DarkGray
}

function Write-Fail {
    param([string] $Message)
    Write-Host "    [EI]  $Message" -ForegroundColor Red
}

# ---------------------------------------------------------------------------
# metadata.txt:n jasennys
# ---------------------------------------------------------------------------

function ConvertFrom-MetadataText {
    <#
    .SYNOPSIS
        Jasentaa metadata.txt:n [general]-osion jarjestetyksi hajautustauluksi.

    .DESCRIPTION
        Noudattaa samoja saantoja kuin Pythonin configparser, jota
        plugins.qgis.org kayttaa:
          - vain [general]-osion avaimet luetaan
          - # ja ; aloittavat kommenttirivin
          - sisennetyt rivit ovat edellisen arvon jatkoa (esim. about=)
          - tyhja rivi paattaa monirivisen arvon
          - avainten kirjainkoko sailyy (parser.optionxform = str)
    #>
    param(
        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [AllowEmptyString()]
        [AllowNull()]
        [string[]] $Lines
    )

    $lines          = $Lines
    $metadata       = [ordered]@{}
    $currentSection = $null
    $currentKey     = $null

    foreach ($line in $lines) {
        # Tyhja rivi paattaa monirivisen arvon.
        if ([string]::IsNullOrWhiteSpace($line)) {
            $currentKey = $null
            continue
        }

        $trimmed = $line.Trim()

        if ($trimmed.StartsWith('#') -or $trimmed.StartsWith(';')) {
            continue
        }

        if ($trimmed -match '^\[(.+)\]$') {
            $currentSection = $Matches[1].Trim()
            $currentKey     = $null
            continue
        }

        # Sisennetty rivi jatkaa edellista arvoa.
        if (($line[0] -eq ' ' -or $line[0] -eq "`t") -and $currentKey) {
            $metadata[$currentKey] = $metadata[$currentKey] + "`n" + $trimmed
            continue
        }

        if ($trimmed -match '^([^=:]+?)\s*[=:]\s*(.*)$') {
            if ($currentSection -eq 'general') {
                $currentKey            = $Matches[1].Trim()
                $metadata[$currentKey] = $Matches[2].Trim()
            } else {
                $currentKey = $null
            }
            continue
        }

        $currentKey = $null
    }

    if (-not $currentSection) {
        throw "metadata.txt:sta ei loytynyt yhtaan osiota. [general]-osio on pakollinen."
    }

    if ($metadata.Count -eq 0) {
        throw "metadata.txt:sta ei loytynyt [general]-osiota tai se on tyhja."
    }

    return $metadata
}

function Read-PluginMetadata {
    <#
    .SYNOPSIS
        Lukee ja jasentaa metadata.txt:n levylta UTF-8:na, kuten QGIS:n
        dokumentaatio vaatii.
    #>
    param(
        [Parameter(Mandatory)] [string] $Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "metadata.txt ei loydy polusta: $Path"
    }

    $lines = [System.IO.File]::ReadAllLines($Path, [System.Text.Encoding]::UTF8)
    return ConvertFrom-MetadataText -Lines $lines
}

function Get-MetadataValue {
    <#
    .SYNOPSIS
        Palauttaa metadata-avaimen arvon tai $null jos avain puuttuu.
        Set-StrictMode estaisi puuttuvan avaimen suoran lukemisen.
    #>
    param(
        [Parameter(Mandatory)] $Metadata,
        [Parameter(Mandatory)] [string] $Key
    )

    if ($Metadata.Contains($Key)) {
        return $Metadata[$Key]
    }
    return $null
}

# ---------------------------------------------------------------------------
# Paketin sisallytyslista
# ---------------------------------------------------------------------------

# Hakemistokohtaiset sisallytyshahmot. Hahmot (eivat kovakoodatut tiedostonimet)
# varmistavat etta uudet dialogit ja moduulit tulevat mukaan ilman etta tata
# skriptia tarvitsee muistaa paivittaa. Juuritasolla kaytetaan tarkkoja nimia,
# jotta kehitystyokalujen tiedostot eivat paady pakettiin.
$script:IncludeRules = @(
    @{
        Directory = ''
        Patterns  = @(
            '__init__.py'       # classFactory, QGIS:n sisaankaynti
            'metadata.txt'      # pakollinen
            'main_icon.png'     # metadata.txt:n icon= viittaa tahan levylla
            'Osoitetyokalu.py'  # paaluokka
            'LayerHandler.py'
            'resources.py'      # kaannetyt ikonit, importoidaan ajossa
        )
    }
    @{ Directory = 'CustomExceptions'; Patterns = @('*.py') }
    @{ Directory = 'dialogs';          Patterns = @('*.py', '*.ui') }  # .ui ladataan uic.loadUiType:lla ajossa
    @{ Directory = 'libs';             Patterns = @('*.py') }
    @{ Directory = 'i18n';             Patterns = @('*.qm') }          # kaannetyt kaannokset, ei .ts
)

# Tiedostot jotka kopioidaan pakettiin eri nimella tai eri paikasta.
# Source on suhteessa repon juureen, Entry suhteessa plugin-hakemistoon ZIPissa.
$script:RemappedFiles = @(
    @{
        Source = 'Tieosoitetyokalu\LICENSE.txt'
        Entry  = 'LICENSE'
        Reason = 'plugins.qgis.org vaatii paatteettoman LICENSE-tiedoston (pakollinen 3.6.2024 alkaen)'
    }
    @{
        Source = 'README.md'
        Entry  = 'README.md'
        Reason = 'julkaisuohjeen dokumentaatiovaatimus; sijaitsee repon juuressa'
    }
)

# Tiedostot joiden TAYTYY olla paketissa. Erillinen lista sisallytyshahmoista,
# jotta puuttuva tiedosto huomataan heti eika vasta QGIS:ssa. Erityisen tarkeaa
# resources.py:lle ja *.qm:lle, jotka eivat ole versionhallinnassa.
$script:RequiredEntries = @(
    '__init__.py'
    'metadata.txt'
    'LICENSE'
    'README.md'
    'main_icon.png'
    'Osoitetyokalu.py'
    'LayerHandler.py'
    'resources.py'
    'CustomExceptions/VkmApiException.py'
    'CustomExceptions/VkmRequestException.py'
    'dialogs/Ajoradat_dialog.py'
    'dialogs/Ajoradat_dialog.ui'
    'dialogs/DeleteLayer_dialog.py'
    'dialogs/DeleteLayer_dialog.ui'
    'dialogs/PopUp_dialog.py'
    'dialogs/PopUp_dialog.ui'
    'dialogs/SearchForm_dialog.py'
    'dialogs/SearchForm_dialog.ui'
    'dialogs/Settings_dialog.py'
    'dialogs/Settings_dialog.ui'
    'dialogs/ShowCoordinates_dialog.py'
    'dialogs/ShowCoordinates_dialog.ui'
    'libs/process_widgets.py'
    'libs/vkm_api_requests.py'
    'i18n/Osoitetyokalu_en.qm'
    'i18n/Osoitetyokalu_sv.qm'
)

# Turvaverkko: naiden hahmojen osuminen kerattyyn listaan on aina virhe.
# Kyse ei ole "naita ei sisallyteta" -listasta (sen hoitaa $IncludeRules) vaan
# tarkistuksesta joka pysayttaa paketoinnin jos jotain menee pieleen.
$script:ForbiddenEntryPatterns = @(
    @{ Pattern = '\.pyc';            Reason = 'plugins.qgis.org hylkaa paketin jos polku sisaltaa .pyc' }
    @{ Pattern = '__pycache__';      Reason = 'Pythonin valimuistihakemisto, ei kuulu pakettiin' }
    @{ Pattern = '(^|/)logs(/|$)';   Reason = 'ajonaikainen lokihakemisto; sisaltaa kehittajan kyselyhistorian' }
    @{ Pattern = '\.log$';           Reason = 'lokitiedosto' }
    @{ Pattern = '(^|/)\.env$';      Reason = 'ymparistomuuttujatiedosto, voi sisaltaa salaisuuksia' }
    @{ Pattern = '\.(key|pem|pfx|p12)$'; Reason = 'avain- tai sertifikaattitiedosto' }
    @{ Pattern = '(^|/)\.git(/|$)';  Reason = 'versionhallinnan metadata' }
    @{ Pattern = '\.\.';             Reason = 'plugins.qgis.org hylkaa polkutiedon sisaltavat merkinnat' }
)

# Tiedostot ja hakemistot jotka jatetaan tarkoituksella pois. Naista ei
# varoiteta. Kaikesta muusta plugin-hakemiston sisallosta joka ei paady
# pakettiin varoitetaan, jotta uusi moduuli ei jaa huomaamatta pois.
$script:KnownExcludedPatterns = @(
    '__pycache__'
    '(^|/)logs(/|$)'
    '(^|/)tool_icons(/|$)'   # kaannetty resources.py:hyn, ei lueta levylta
    '\.qrc$'                 # lahdetiedosto resources.py:lle
    '\.ts$'                  # lahdetiedosto .qm:lle
    '\.pro$'                 # pylupdate-projektitiedosto
    '(^|/)pb_tool\.cfg$'
    '(^|/)pylintrc$'
    '(^|/)translate\.bat$'
    '(^|/)LICENSE\.txt$'     # korvattu paatteettomalla LICENSE-merkinnalla
)

function Get-PackageFileList {
    <#
    .SYNOPSIS
        Kerää paketoitavat tiedostot sisallytyshahmojen ja uudelleenkohdistusten
        perusteella.

    .OUTPUTS
        Objektit joilla SourcePath (absoluuttinen), Entry (suhteellinen polku
        plugin-hakemistossa, /-erottimin) ja Length.
    #>
    [CmdletBinding()]
    param()

    $collected = [ordered]@{}

    foreach ($rule in $script:IncludeRules) {
        $searchDir = if ($rule.Directory) {
            Join-Path $script:PluginDir $rule.Directory
        } else {
            $script:PluginDir
        }

        if (-not (Test-Path -LiteralPath $searchDir -PathType Container)) {
            Write-Verbose "Sisallytyshahmon hakemisto puuttuu, ohitetaan: $searchDir"
            continue
        }

        foreach ($pattern in $rule.Patterns) {
            $found = @(Get-ChildItem -LiteralPath $searchDir -Filter $pattern -File -ErrorAction SilentlyContinue)

            foreach ($file in $found) {
                $entry = if ($rule.Directory) {
                    "$($rule.Directory)/$($file.Name)"
                } else {
                    $file.Name
                }
                $entry = $entry.Replace('\', '/')

                if (-not $collected.Contains($entry)) {
                    $collected[$entry] = [pscustomobject]@{
                        SourcePath = $file.FullName
                        Entry      = $entry
                        Length     = $file.Length
                    }
                }
            }
        }
    }

    foreach ($remap in $script:RemappedFiles) {
        $sourcePath = Join-Path $script:RepoRoot $remap.Source

        if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
            # Puuttuminen raportoidaan pakollisten tiedostojen tarkistuksessa.
            Write-Verbose "Uudelleenkohdistettu lahde puuttuu: $sourcePath"
            continue
        }

        $entry = $remap.Entry.Replace('\', '/')
        $collected[$entry] = [pscustomobject]@{
            SourcePath = (Get-Item -LiteralPath $sourcePath).FullName
            Entry      = $entry
            Length     = (Get-Item -LiteralPath $sourcePath).Length
        }
    }

    return @($collected.Values | Sort-Object Entry)
}

function Assert-RequiredEntries {
    <#
    .SYNOPSIS
        Keskeyttaa jos yksikin pakollinen tiedosto puuttuu. Kaikki puuttuvat
        listataan kerralla, jotta korjaus onnistuu yhdella kierroksella.
    #>
    param(
        [Parameter(Mandatory)] [AllowEmptyCollection()] [array] $Files
    )

    $present = @($Files | ForEach-Object { $_.Entry })
    $missing = @($script:RequiredEntries | Where-Object { $present -notcontains $_ })

    if ($missing.Count -eq 0) {
        Write-Ok "Kaikki $($script:RequiredEntries.Count) pakollista tiedostoa loytyvat"
        return
    }

    Write-Fail "Pakollisia tiedostoja puuttuu ($($missing.Count) kpl):"
    foreach ($entry in $missing) {
        Write-Host "            - $script:PluginDirName/$entry" -ForegroundColor Red
    }

    # Kohdennettu ohje yleisimpiin syihin: nama artefaktit eivat ole
    # versionhallinnassa, joten ne puuttuvat puhtaasta checkoutista.
    if ($missing -match '\.qm$') {
        Write-Host ''
        Write-Warn2 'Kaannokset (*.qm) eivat ole versionhallinnassa (.gitignore: *.qm).'
        Write-Warn2 'Generoi ne ennen paketointia, esim. Tieosoitetyokalu\translate.bat'
    }
    if ($missing -contains 'resources.py') {
        Write-Host ''
        Write-Warn2 'resources.py generoidaan resources.qrc:sta:'
        Write-Warn2 '  pyrcc5 -o resources.py resources.qrc'
    }
    if ($missing -contains 'LICENSE') {
        Write-Host ''
        Write-Warn2 'LICENSE luodaan LICENSE.txt:sta paketointivaiheessa. Tarkista etta'
        Write-Warn2 'Tieosoitetyokalu\LICENSE.txt on olemassa.'
    }

    throw "Paketointi keskeytetty: $($missing.Count) pakollista tiedostoa puuttuu."
}

function Assert-NoForbiddenEntries {
    <#
    .SYNOPSIS
        Turvaverkko: keskeyttaa jos kerattyyn listaan on paatynyt tiedosto joka
        kaataisi plugins.qgis.org:n validoinnin tai vuotaisi arkaluontoista dataa.
    #>
    param(
        [Parameter(Mandatory)] [AllowEmptyCollection()] [array] $Files
    )

    $violations = @()

    foreach ($file in $Files) {
        foreach ($rule in $script:ForbiddenEntryPatterns) {
            if ($file.Entry -match $rule.Pattern) {
                $violations += [pscustomobject]@{
                    Entry  = $file.Entry
                    Reason = $rule.Reason
                }
            }
        }
    }

    if ($violations.Count -eq 0) {
        Write-Ok 'Kiellettyja tiedostoja ei loytynyt'
        return
    }

    Write-Fail "Kiellettyja tiedostoja kerattyna ($($violations.Count) kpl):"
    foreach ($violation in $violations) {
        Write-Host "            - $($violation.Entry): $($violation.Reason)" -ForegroundColor Red
    }

    throw 'Paketointi keskeytetty: kerattyyn listaan paatyi kiellettyja tiedostoja.'
}

function Write-UncollectedFileWarnings {
    <#
    .SYNOPSIS
        Varoittaa plugin-hakemiston tiedostoista jotka eivat paady pakettiin
        eivatka ole tunnetulla poissulkulistalla.

    .DESCRIPTION
        Tama on skriptin tarkein yllapidettavyystarkistus: ilman sita uusi
        alihakemisto (esim. Tieosoitetyokalu\widgets) jaisi hiljaisesti pois
        paketista ja plugin kaatuisi vasta kayttajan QGIS:ssa.
    #>
    param(
        [Parameter(Mandatory)] [AllowEmptyCollection()] [array] $Files
    )

    $collectedEntries = @($Files | ForEach-Object { $_.Entry })
    $prefixLength     = $script:PluginDir.Length + 1

    $allFiles = @(Get-ChildItem -LiteralPath $script:PluginDir -Recurse -File -Force)

    $unexpected = @()

    foreach ($file in $allFiles) {
        $relative = $file.FullName.Substring($prefixLength).Replace('\', '/')

        if ($collectedEntries -contains $relative) {
            continue
        }

        $isKnown = $false
        foreach ($pattern in $script:KnownExcludedPatterns) {
            if ($relative -match $pattern) {
                $isKnown = $true
                break
            }
        }

        if (-not $isKnown) {
            $unexpected += $relative
        }
    }

    if ($unexpected.Count -eq 0) {
        Write-Ok 'Plugin-hakemistossa ei ole tuntemattomia tiedostoja'
        return
    }

    Write-Warn2 "Plugin-hakemistossa on $($unexpected.Count) tiedostoa joita ei paketoida"
    Write-Warn2 'eika ole tunnetulla poissulkulistalla. Tarkista sisallytyshahmot:'
    foreach ($relative in $unexpected) {
        Write-Host "            ? $relative" -ForegroundColor Yellow
    }
}

# ---------------------------------------------------------------------------
# ZIP-paketin kirjoitus
# ---------------------------------------------------------------------------

function New-PluginPackage {
    <#
    .SYNOPSIS
        Kirjoittaa ZIP-paketin annetusta tiedostolistasta.

    .DESCRIPTION
        Kayttaa .NET:n ZipArchive-rajapintaa ja asettaa jokaisen merkinnan nimen
        eksplisiittisesti /-erottimin.

        Miksi ei Compress-Archive: sen merkintanimet riippuvat PowerShell-
        versiosta ja kayttojarjestelman polkuerottimesta. plugins.qgis.org
        paattelee pluginin nimen tekemalla namelist[0].index("/"), ja QGIS:n
        asennin etsii lyhimman metadata.txt-polun. Kenoviivat merkintanimissa
        rikkovat molemmat. Eksplisiittiset nimet poistavat taman riippuvuuden,
        ja Test-PluginPackage varmistaa tuloksen viela erikseen.

        Uudelleenkohdistukset (LICENSE.txt -> LICENSE, juuren README.md)
        hoituvat merkintanimen kautta, joten valiaikaista staging-hakemistoa ei
        tarvita eika siivottavaa jaa.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [AllowEmptyCollection()] [array] $Files,
        [Parameter(Mandatory)] [string] $DestinationPath
    )

    $destinationDir = Split-Path -Parent $DestinationPath
    if ($destinationDir -and -not (Test-Path -LiteralPath $destinationDir -PathType Container)) {
        New-Item -ItemType Directory -Path $destinationDir -Force | Out-Null
        Write-Info "Luotiin hakemisto: $destinationDir"
    }

    if (Test-Path -LiteralPath $DestinationPath) {
        Remove-Item -LiteralPath $DestinationPath -Force
    }

    $archive = $null
    $succeeded = $false

    try {
        $archive = [System.IO.Compression.ZipFile]::Open(
            $DestinationPath,
            [System.IO.Compression.ZipArchiveMode]::Create
        )

        foreach ($file in $Files) {
            # Merkintanimi: aina PluginDirName/<suhteellinen polku>, /-erottimin.
            $entryName = '{0}/{1}' -f $script:PluginDirName, $file.Entry.Replace('\', '/')

            [void][System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
                $archive,
                $file.SourcePath,
                $entryName,
                [System.IO.Compression.CompressionLevel]::Optimal
            )
        }

        $succeeded = $true
    }
    finally {
        if ($archive) {
            $archive.Dispose()
        }

        # Vajaa ZIP on pahempi kuin ei ZIPia lainkaan: se voisi paatya
        # julkaisuun. Poistetaan keskeytyneen ajon jaljet.
        if (-not $succeeded -and (Test-Path -LiteralPath $DestinationPath)) {
            Remove-Item -LiteralPath $DestinationPath -Force -ErrorAction SilentlyContinue
            Write-Fail 'Keskenerainen ZIP-tiedosto poistettiin.'
        }
    }

    return (Get-Item -LiteralPath $DestinationPath)
}

# ---------------------------------------------------------------------------
# Valmiin paketin validointi
# ---------------------------------------------------------------------------

# plugins.qgis.org: PLUGIN_REQUIRED_METADATA.
$script:RequiredMetadataKeys = @(
    'name'
    'description'
    'version'
    'qgisMinimumVersion'
    'author'
    'email'
    'about'
    'tracker'
    'repository'
)

function Get-ZipEntryText {
    <#
    .SYNOPSIS
        Lukee ZIP-merkinnan sisallon UTF-8-merkkijonona.
    #>
    param(
        [Parameter(Mandatory)] $Archive,
        [Parameter(Mandatory)] [string] $EntryName
    )

    $entry = $Archive.GetEntry($EntryName)
    if (-not $entry) {
        throw "ZIP-merkintaa ei loydy: $EntryName"
    }

    $stream = $entry.Open()
    try {
        $reader = New-Object System.IO.StreamReader($stream, [System.Text.Encoding]::UTF8)
        try {
            return $reader.ReadToEnd()
        }
        finally {
            $reader.Dispose()
        }
    }
    finally {
        $stream.Dispose()
    }
}

function Test-PluginPackage {
    <#
    .SYNOPSIS
        Validoi valmiin ZIP-paketin plugins.qgis.org:n saantojen mukaan.

    .DESCRIPTION
        Toistaa QGIS-Django-repon plugins/validator.py:n kovat tarkistukset
        paikallisesti, jotta virheet loytyvat ennen uploadia. Lukee paketin
        takaisin levylta, eli tarkistaa todellisen artefaktin eika sita mita
        skripti luuli kirjoittavansa.

        Kaikki havainnot kerataan ja raportoidaan kerralla, jotta korjaus
        onnistuu yhdella kierroksella.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $Path
    )

    $failures = @()
    $checks   = @()

    $zipItem = Get-Item -LiteralPath $Path

    # 1. Paketin koko.
    if ($zipItem.Length -le $script:MaxPackageBytes) {
        $checks += "Koko $([math]::Round($zipItem.Length / 1MB, 2)) MB <= $($script:MaxPackageBytes / 1MB) MB"
    } else {
        $failures += "Paketti on liian suuri: $([math]::Round($zipItem.Length / 1MB, 2)) MB, raja $($script:MaxPackageBytes / 1MB) MB."
    }

    $archive = [System.IO.Compression.ZipFile]::OpenRead($Path)

    try {
        $entryNames = @($archive.Entries | ForEach-Object { $_.FullName })

        if ($entryNames.Count -eq 0) {
            $failures += 'Paketti on tyhja.'
            throw 'ABORT'
        }

        # 2. Merkintanimet kayttavat /-erotinta.
        # plugins.qgis.org paattelee pluginin nimen namelist[0].index("/")-
        # kutsulla ja QGIS:n asennin etsii lyhimman metadata.txt-polun.
        # Kenoviivat rikkovat molemmat.
        $backslashEntries = @($entryNames | Where-Object { $_.Contains('\') })
        if ($backslashEntries.Count -eq 0) {
            $checks += 'Kaikki merkintanimet kayttavat /-erotinta'
        } else {
            $failures += "Merkintanimissa on kenoviivoja ($($backslashEntries.Count) kpl), esim. '$($backslashEntries[0])'."
        }

        # 3. Turvallisuustarkistukset joilla validator hylkaa paketin.
        $pycEntries = @($entryNames | Where-Object { $_.Contains('.pyc') })
        if ($pycEntries.Count -eq 0) {
            $checks += 'Yhdessakaan merkintanimessa ei ole .pyc-osumaa'
        } else {
            $failures += "Merkintanimissa on .pyc-osumia ($($pycEntries.Count) kpl), esim. '$($pycEntries[0])'. plugins.qgis.org hylkaa paketin."
        }

        $traversalEntries = @($entryNames | Where-Object { $_.Contains('..') -or $_.StartsWith('/') -or $_.StartsWith('\') })
        if ($traversalEntries.Count -eq 0) {
            $checks += 'Ei polkutietoa sisaltavia merkintanimia'
        } else {
            $failures += "Merkintanimissa on polkutietoa ($($traversalEntries.Count) kpl), esim. '$($traversalEntries[0])'."
        }

        # 4. Tasmalleen yksi ylatason hakemisto.
        $topLevel = @($entryNames | ForEach-Object { $_.Split('/')[0] } | Sort-Object -Unique)

        if ($topLevel.Count -eq 1) {
            $checks += "Yksi ylatason hakemisto: $($topLevel[0])"
        } else {
            $failures += "Paketissa on $($topLevel.Count) ylatason kohdetta: $($topLevel -join ', '). Sallittu vain yksi."
        }

        $packageName = $topLevel[0]

        # 5. Ylatason hakemiston nimi vastaa jo julkaistua package_namea.
        if ($packageName -eq $script:PluginDirName) {
            $checks += "package_name on odotettu: $script:PluginDirName"
        } else {
            $failures += "Ylatason hakemisto on '$packageName', odotettiin '$script:PluginDirName'. Nimen muutos saisi paketin nayttamaan uudelta pluginilta."
        }

        # 6. Nimi on kelvollinen Python-tunniste.
        # plugins.qgis.org:n regex ^[A-Za-z][A-Za-z0-9-_]+$ paastaisi lapi myos
        # valiviivan, mutta hakemiston nimesta tulee Python-paketin nimi, eika
        # valiviivallista nimea voi importata. Paketti lapaisisi uploadin ja
        # kaatuisi vasta kayttajan QGIS:ssa.
        if ($packageName -match '^[A-Za-z_][A-Za-z0-9_]*$') {
            $checks += 'package_name on kelvollinen Python-tunniste'
        } else {
            $failures += "Ylatason hakemisto '$packageName' ei ole kelvollinen Python-tunniste. Valiviivat ja pisteet estavat pluginin latautumisen."
        }

        # 7. Pakolliset tiedostot paketissa.
        foreach ($required in @('__init__.py', 'metadata.txt', 'LICENSE')) {
            $entryName = "$packageName/$required"
            if ($entryNames -contains $entryName) {
                $checks += "$required loytyy"
            } else {
                $failures += "Paketista puuttuu $entryName."
            }
        }

        # 8. metadata.txt jasentyy ja pakolliset kentat ovat paikallaan.
        $metadataEntryName = "$packageName/metadata.txt"
        if ($entryNames -contains $metadataEntryName) {
            $metadataText = Get-ZipEntryText -Archive $archive -EntryName $metadataEntryName

            try {
                $packagedMetadata = ConvertFrom-MetadataText -Lines ($metadataText -split "`r?`n")

                $missingKeys = @($script:RequiredMetadataKeys | Where-Object { -not $packagedMetadata.Contains($_) -or -not $packagedMetadata[$_] })

                if ($missingKeys.Count -eq 0) {
                    $checks += "Pakolliset metadata-kentat ($($script:RequiredMetadataKeys.Count) kpl) paikallaan"
                } else {
                    $failures += "metadata.txt:sta puuttuu pakollisia kenttia: $($missingKeys -join ', ')."
                }

                # 9. Ikoni on paketissa. Validator lukee sen ZIPista ja QGIS:n
                #    lisaosahallinta nayttaa sen listauksessa.
                $iconValue = Get-MetadataValue $packagedMetadata 'icon'
                if ($iconValue) {
                    $iconPath  = $iconValue -replace '^\./', ''
                    $iconEntry = "$packageName/$($iconPath.Replace('\', '/'))"

                    if ($entryNames -contains $iconEntry) {
                        $checks += "Ikoni loytyy: $iconPath"
                    } else {
                        $failures += "metadata.txt:n icon=$iconValue viittaa tiedostoon jota ei ole paketissa ($iconEntry)."
                    }
                } else {
                    $checks += 'Ikonia ei ole maaritelty (valinnainen)'
                }
            }
            catch {
                $failures += "metadata.txt:n jasennys paketista epaonnistui: $($_.Exception.Message)"
            }
        }
    }
    catch {
        if ($_.Exception.Message -ne 'ABORT') {
            throw
        }
    }
    finally {
        $archive.Dispose()
    }

    foreach ($check in $checks) {
        Write-Ok $check
    }

    if ($failures.Count -gt 0) {
        Write-Host ''
        Write-Fail "Validointi hylkasi paketin ($($failures.Count) havaintoa):"
        foreach ($failure in $failures) {
            Write-Host "            - $failure" -ForegroundColor Red
        }
        throw "Paketti ei lapaise plugins.qgis.org:n validointia: $($failures.Count) havaintoa."
    }
}

# ---------------------------------------------------------------------------
# Julkaisupolitiikan tarkistukset
# ---------------------------------------------------------------------------

# QGIS:n dokumentaation sallimat category-arvot.
$script:AllowedCategories = @('Raster', 'Vector', 'Database', 'Mesh', 'Web')

# QGIS-versio josta lahtien plugin listautuu "QGIS 4 Ready" -listalle.
# Lahde: https://plugins.qgis.org/docs/migrate-qgis4
$script:Qgis4Threshold = [version] '4.0'

function Get-LastReleasedVersion {
    <#
    .SYNOPSIS
        Paattelee edellisen julkaistun version repon git-tageista.

    .DESCRIPTION
        Aiemmin tama oli kovakoodattu vakio, joka olisi pitanyt paivittaa kasin
        jokaisen julkaisun jalkeen. Unohtunut paivitys olisi tehnyt
        versiotarkistuksesta hyodyttoman huomaamatta. Git-tagit ovat jo
        olemassa oleva julkaisukirjanpito (v1.3.2, v1.3.1, ...), joten ne
        pidetaan totuuden lahteena.

        Palauttaa $null jos gitia ei ole tai tageja ei loydy; tallon
        versiotarkistus ohitetaan varoituksella.
    #>
    [CmdletBinding()]
    param()

    try {
        $gitCommand = Get-Command git -ErrorAction SilentlyContinue
        if (-not $gitCommand) { return $null }

        # Natiivikomennon stderr ei saa keskeyttaa suoritusta.
        $previousPreference = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        try {
            $tags = & git -C $script:RepoRoot tag --list 2>$null
        }
        finally {
            $ErrorActionPreference = $previousPreference
        }

        if (-not $tags) { return $null }

        # Hyvaksytaan vain puhtaat julkaisutagit (v1.3.2 tai 1.3.2).
        # Esijulkaisutagit kuten 1.2.1-ALPHA.1 jatetaan huomiotta.
        $versions = @(
            $tags |
                ForEach-Object { $_.Trim() } |
                Where-Object { $_ -match '^v?\d+(\.\d+)+$' } |
                ForEach-Object { ConvertTo-ComparableVersion ($_ -replace '^v', '') } |
                Where-Object { $_ }
        )

        if ($versions.Count -eq 0) { return $null }

        return ($versions | Sort-Object -Descending)[0]
    }
    catch {
        return $null
    }
}

function ConvertTo-ComparableVersion {
    <#
    .SYNOPSIS
        Muuntaa pisteellisen versiomerkkijonon [version]-tyypiksi vertailua
        varten. Palauttaa $null jos muoto ei kelpaa.
    #>
    param([string] $Text)

    if (-not $Text) { return $null }
    if ($Text -notmatch '^\d+(\.\d+)*$') { return $null }

    # [version] vaatii vahintaan kaksi osaa (esim. "4" ei kelpaa).
    $normalized = $Text
    if ($Text -notmatch '\.') { $normalized = "$Text.0" }

    try { return [version] $normalized } catch { return $null }
}

function Test-ReleasePolicy {
    <#
    .SYNOPSIS
        Tarkistaa julkaisukelpoisuuden asiat joita plugins.qgis.org:n
        validaattori ei tarkista mutta jotka kaatavat hyvaksynnan tai rikkovat
        kayttajien asennukset.

    .DESCRIPTION
        Virheet keskeyttavat paketoinnin, varoitukset eivat. Kaikki havainnot
        raportoidaan kerralla.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $Metadata,
        [Parameter(Mandatory)] [string] $PackageVersion
    )

    $errors   = @()
    $warnings = @()
    $passed   = @()

    # --- QGIS-versiohaarukka ------------------------------------------------
    # plugins.qgis.org paattelee yhteensopivuuden pelkastaan
    # qgisMinimumVersion- ja qgisMaximumVersion-kentista. Jos maksimia ei ole
    # asetettu, haarukka paattyy minimin paaversion .99-numeroon.
    # Lahde: https://plugins.qgis.org/docs/migrate-qgis4
    #
    # Skripti EI ota kantaa siihen mika paaversio on "oikea": QGIS 4:lle
    # rajattu julkaisu on taysin kelvollinen valinta. Jokainen julkaistu versio
    # kantaa oman haarukkansa, joten uudempi QGIS 4 -only -versio ei poista
    # aiempaa QGIS 3 -versiota kayttajilta. Tarkistetaan siis vain etta
    # haarukka on hyvin muodostettu ja raportoidaan mihin se johtaa.
    $minVersionText = Get-MetadataValue $Metadata 'qgisMinimumVersion'
    $maxVersionText = Get-MetadataValue $Metadata 'qgisMaximumVersion'

    $minVersion = ConvertTo-ComparableVersion $minVersionText
    $maxVersion = ConvertTo-ComparableVersion $maxVersionText

    if (-not $minVersion) {
        $errors += "qgisMinimumVersion ('$minVersionText') ei ole kelvollinen pisteellinen versionumero."
    } elseif ($maxVersionText -and -not $maxVersion) {
        $errors += "qgisMaximumVersion ('$maxVersionText') ei ole kelvollinen pisteellinen versionumero."
    } elseif ($maxVersion -and $maxVersion -lt $minVersion) {
        $errors += "qgisMaximumVersion ($maxVersionText) on pienempi kuin qgisMinimumVersion ($minVersionText). Plugin ei listautuisi yhdellekaan QGIS-versiolle."
    } else {
        $effectiveMax = if ($maxVersion) {
            $maxVersionText
        } else {
            "$($minVersion.Major).99 (paatelty)"
        }

        $passed += "QGIS-yhteensopivuus $minVersionText - $effectiveMax"

        # Onko tama julkaisu QGIS 4 -yhteensopiva? Ehto on sama kuin
        # plugins.qgis.orgin "QGIS 4 Ready" -listalla.
        $qgis4Ready = ($minVersion -ge $script:Qgis4Threshold) -or
                      ($maxVersion -and $maxVersion -ge $script:Qgis4Threshold)

        if ($qgis4Ready) {
            $passed += 'Listautuu QGIS 4 Ready Plugins -listalle'
        }

        if ($minVersion -ge $script:Qgis4Threshold) {
            # QGIS 4 -only. Taysin kelvollinen, mutta kannattaa tietaa etta
            # QGIS 3 -kayttajat jaavat aiempaan julkaistuun versioon.
            if (-not $maxVersion) {
                $warnings += "qgisMaximumVersion puuttuu. Haarukaksi paatellaan $minVersionText - $($minVersion.Major).99, mika on tassa oikea, mutta plugins.qgis.orgin ohje suosittelee asettamaan sen eksplisiittisesti (qgisMaximumVersion=4.99)."
            }
            $warnings += "QGIS 4 -only -julkaisu (minimi $minVersionText). QGIS 3.x -kayttajat eivat nae tata versiota vaan jaavat viimeisimpaan QGIS 3 -yhteensopivaan julkaisuun. Varmista etta se on tarkoitus."
        } elseif (-not $maxVersion) {
            $warnings += "qgisMaximumVersion puuttuu. Haarukaksi paatellaan $minVersionText - $($minVersion.Major).99, joten plugin ei listaudu QGIS 4:lle. Aseta qgisMaximumVersion=4.99 jos QGIS 4 -tuki on tarkoitus."
        }
    }

    # Poistettu lippu: supportsQt6 ei ole enaa kaytossa QGIS-ytimessa.
    if ($Metadata.Contains('supportsQt6')) {
        $warnings += 'supportsQt6 on metadata.txt:ssa, mutta lippu on poistettu QGIS-ytimesta eika sita enaa tunnisteta. Se voi poistaa.'
    }

    # --- Versionumero -------------------------------------------------------
    # Edellinen julkaisu paatellaan git-tageista, ei kovakoodatusta vakiosta.
    $newVersion  = ConvertTo-ComparableVersion $PackageVersion
    $lastVersion = Get-LastReleasedVersion

    if (-not $newVersion) {
        $errors += "version ('$PackageVersion') ei ole kelvollinen pisteellinen versionumero."
    } elseif (-not $lastVersion) {
        $warnings += 'Edellista julkaisua ei voitu paatella git-tageista, joten versionumeron kasvua ei tarkistettu.'
    } elseif ($newVersion -le $lastVersion) {
        $errors += "version on $PackageVersion, mutta repossa on jo julkaisutagi $lastVersion. Uuden version taytyy olla suurempi, koska plugins.qgis.org ei hyvaksy saman versionumeron uudelleenlatausta."
    } else {
        $passed += "version $PackageVersion on suurempi kuin edellinen julkaisutagi $lastVersion"
    }

    # --- Changelog ----------------------------------------------------------
    # Hyvaksymisohje vaatii changelogin nimenomaan paivityksilta.
    $changelogText = Get-MetadataValue $Metadata 'changelog'

    if (-not $changelogText) {
        $errors += 'changelog puuttuu metadata.txt:sta. plugins.qgis.org:n hyvaksymisohje vaatii sen paivityksilta, jotta kayttajat nakevat mika versioiden valilla muuttui.'
    } elseif ($changelogText -notmatch [regex]::Escape($PackageVersion)) {
        $errors += "changelog ei mainitse versiota $PackageVersion."
    } else {
        $passed += "changelog mainitsee version $PackageVersion"
    }

    # --- Experimental- ja deprecated-liput ----------------------------------
    $experimental = Get-MetadataValue $Metadata 'experimental'

    # Kokeellinen lippu on kelvollinen valinta, esimerkiksi juuri migratoidulle
    # julkaisulle, joten se ei keskeyta paketointia. Seuraus on kuitenkin syyta
    # tietaa, koska se rajaa nakyvyytta merkittavasti.
    if ($experimental -and $experimental.ToString().ToLower() -in @('true', '1')) {
        $warnings += 'experimental=True. Plugin nakyy vain kayttajille jotka ovat erikseen sallineet kokeelliset lisaosat lisaosahallinnan asetuksista. Aseta experimental=False kun julkaisu on tarkoitettu kaikille.'
    } else {
        $passed += 'experimental=False'
    }

    $deprecated = Get-MetadataValue $Metadata 'deprecated'
    if ($deprecated -and $deprecated.ToString().ToLower() -in @('true', '1')) {
        $warnings += 'deprecated=True. Tama merkitsee KOKO pluginin vanhentuneeksi, ei vain tata versiota.'
    }

    # --- Kategoria ----------------------------------------------------------
    $category = Get-MetadataValue $Metadata 'category'

    # Kelvoton category ei esta latausta, mutta se on QGIS:n dokumentaation
    # vastainen ja kentta jaa vaikutuksettomaksi.
    if (-not $category) {
        $warnings += 'category puuttuu. Plugin sijoittuu oletuksena Lisaosat-valikkoon.'
    } elseif ($script:AllowedCategories -notcontains $category) {
        $warnings += "category='$category' ei ole QGIS:n dokumentaation sallima arvo, joten kentta jaa vaikutuksettomaksi. Sallitut: $($script:AllowedCategories -join ', ')."
    } else {
        $passed += "category=$category"
    }

    # --- Tekija (validaattorin saanto) --------------------------------------
    $author = Get-MetadataValue $Metadata 'author'
    if ($author -and $author.Contains('/')) {
        $errors += "author='$author' sisaltaa kenoviivan. plugins.qgis.org hylkaa taman."
    } else {
        $passed += "author=$author"
    }

    # --- Tagit --------------------------------------------------------------
    $tags = Get-MetadataValue $Metadata 'tags'
    if (-not $tags) {
        $warnings += 'tags puuttuu. Tagit parantavat pluginin loydettavyytta.'
    } else {
        $tagList = @($tags -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
        if ($tagList.Count -le 1) {
            $warnings += "tags sisaltaa vain $($tagList.Count) tagin ('$tags'). Kuvaavammat tagit parantavat loydettavyytta."
        } else {
            $passed += "tags ($($tagList.Count) kpl)"
        }
    }

    # --- Raportointi --------------------------------------------------------
    foreach ($item in $passed)   { Write-Ok $item }
    foreach ($item in $warnings) { Write-Warn2 $item }

    if ($errors.Count -gt 0) {
        Write-Host ''
        Write-Fail "Julkaisupolitiikan tarkistus hylkasi paketin ($($errors.Count) havaintoa):"
        foreach ($item in $errors) {
            Write-Host "            - $item" -ForegroundColor Red
        }
        Write-Host ''
        Write-Info 'Korjaa Tieosoitetyokalu\metadata.txt tai ohita tarkistukset'
        Write-Info 'parametrilla -SkipPolicyChecks (vain sisaisiin valijulkaisuihin).'
        throw "Julkaisupolitiikan tarkistus ei mennyt lapi: $($errors.Count) havaintoa."
    }
}

function Test-MetadataUrls {
    <#
    .SYNOPSIS
        Tarkistaa metadata.txt:n linkit HTTP HEAD -pyynnolla.

    .DESCRIPTION
        plugins.qgis.org tekee saman palvelinpuolella ja hylkaa paketin jos
        linkki ei vastaa tai on jaanyt Plugin Builderin oletusarvoksi
        (http://bugs, http://repo, http://homepage).
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $Metadata
    )

    $urlKeys = @('homepage', 'tracker', 'repository')
    $placeholders = @('http://bugs', 'http://repo', 'http://homepage')
    $errors = @()

    foreach ($key in $urlKeys) {
        $url = Get-MetadataValue $Metadata $key

        if (-not $url) {
            if ($key -eq 'homepage') {
                Write-Warn2 "$key puuttuu (valinnainen, mutta suositeltu)."
            } else {
                $errors += "$key puuttuu. Se on pakollinen kentta."
            }
            continue
        }

        $isPlaceholder = $false
        foreach ($placeholder in $placeholders) {
            if ($url.StartsWith($placeholder)) { $isPlaceholder = $true; break }
        }

        if ($isPlaceholder) {
            $errors += "$key='$url' on Plugin Builderin oletusarvo. plugins.qgis.org hylkaa sen."
            continue
        }

        try {
            $response = Invoke-WebRequest -Uri $url -Method Head -UseBasicParsing -TimeoutSec 20
            if ([int]$response.StatusCode -ge 400) {
                $errors += "$key='$url' vastasi HTTP $([int]$response.StatusCode)."
            } else {
                Write-Ok "$key vastasi HTTP $([int]$response.StatusCode)"
            }
        }
        catch {
            # Osa palvelimista ei tue HEAD-metodia; yritetaan GET.
            try {
                $response = Invoke-WebRequest -Uri $url -Method Get -UseBasicParsing -TimeoutSec 20
                if ([int]$response.StatusCode -ge 400) {
                    $errors += "$key='$url' vastasi HTTP $([int]$response.StatusCode)."
                } else {
                    Write-Ok "$key vastasi HTTP $([int]$response.StatusCode) (GET; HEAD ei tuettu)"
                }
            }
            catch {
                $errors += "$key='$url' ei vastannut: $($_.Exception.Message)"
            }
        }
    }

    if ($errors.Count -gt 0) {
        Write-Host ''
        Write-Fail "Linkkitarkistus hylkasi paketin ($($errors.Count) havaintoa):"
        foreach ($item in $errors) {
            Write-Host "            - $item" -ForegroundColor Red
        }
        throw "Linkkitarkistus ei mennyt lapi: $($errors.Count) havaintoa."
    }
}

# ---------------------------------------------------------------------------
# Paaohjelma
# ---------------------------------------------------------------------------

Write-Host ''
Write-Host 'Tieosoitetyokalu - QGIS-pluginin paketointi' -ForegroundColor White
Write-Host ('-' * 62) -ForegroundColor DarkGray

if ($ValidateOnly) {
    if (-not (Test-Path -LiteralPath $ValidateOnly -PathType Leaf)) {
        throw "ZIP-tiedostoa ei loydy: $ValidateOnly"
    }

    $validatePath = (Get-Item -LiteralPath $ValidateOnly).FullName

    Write-Step 'Validoidaan olemassa oleva paketti'
    Write-Info $validatePath
    Write-Host ''

    Test-PluginPackage -Path $validatePath

    Write-Host ''
    Write-Host ('-' * 62) -ForegroundColor DarkGray
    Write-Host 'Paketti lapaisi validoinnin.' -ForegroundColor Green
    Write-Host ''
    exit 0
}

Write-Step 'Luetaan pluginin metadata'

if (-not (Test-Path -LiteralPath $script:PluginDir -PathType Container)) {
    throw "Plugin-hakemistoa ei loydy: $script:PluginDir"
}

$metadataPath = Join-Path $script:PluginDir 'metadata.txt'
$metadata     = Read-PluginMetadata -Path $metadataPath

$metadataVersion = Get-MetadataValue $metadata 'version'
if (-not $metadataVersion) {
    throw "metadata.txt:n [general]-osiosta puuttuu pakollinen kentta 'version'."
}

# -Version vaikuttaa vain tiedostonimeen; poikkeama raportoidaan.
$packageVersion = if ($Version) { $Version } else { $metadataVersion }

Write-Ok "metadata.txt jasennetty, $($metadata.Count) kenttaa"
Write-Info "Plugin       : $(Get-MetadataValue $metadata 'name')"
Write-Info "package_name : $script:PluginDirName"
Write-Info "Versio       : $packageVersion"

if ($Version -and $Version -ne $metadataVersion) {
    Write-Warn2 "-Version ($Version) eroaa metadata.txt:n arvosta ($metadataVersion)."
    Write-Warn2 'plugins.qgis.org kayttaa metadata.txt:n versiota, ei tiedostonimea.'
}

$qgisMaximum = Get-MetadataValue $metadata 'qgisMaximumVersion'
$changelog   = Get-MetadataValue $metadata 'changelog'

Write-Info "QGIS minimi  : $(Get-MetadataValue $metadata 'qgisMinimumVersion')"
Write-Info "QGIS maksimi : $(if ($qgisMaximum) { $qgisMaximum } else { '(ei asetettu)' })"
Write-Info "Ikoni        : $(Get-MetadataValue $metadata 'icon')"
Write-Info "Kategoria    : $(Get-MetadataValue $metadata 'category')"
Write-Info "Experimental : $(Get-MetadataValue $metadata 'experimental')"
Write-Info "Deprecated   : $(Get-MetadataValue $metadata 'deprecated')"
Write-Info "Changelog    : $(if ($changelog) { 'on' } else { 'PUUTTUU' })"

# ---------------------------------------------------------------------------

Write-Step 'Kerataan paketoitavat tiedostot'

$packageFiles = Get-PackageFileList

if ($packageFiles.Count -eq 0) {
    throw 'Yhtaan paketoitavaa tiedostoa ei loytynyt. Tarkista plugin-hakemiston polku.'
}

$totalBytes = ($packageFiles | Measure-Object -Property Length -Sum).Sum

Write-Ok "$($packageFiles.Count) tiedostoa, yhteensa $([math]::Round($totalBytes / 1KB, 1)) KB"

Write-Host ''
foreach ($file in $packageFiles) {
    $sizeText = '{0,8:N0} B' -f $file.Length
    Write-Host ('          {0}  {1}/{2}' -f $sizeText, $script:PluginDirName, $file.Entry) -ForegroundColor Gray
}

# ---------------------------------------------------------------------------

Write-Step 'Tarkistetaan tiedostolista'

Assert-RequiredEntries -Files $packageFiles
Assert-NoForbiddenEntries -Files $packageFiles
Write-UncollectedFileWarnings -Files $packageFiles

# ---------------------------------------------------------------------------

if ($SkipPolicyChecks) {
    Write-Step 'Julkaisupolitiikan tarkistukset'
    Write-Warn2 'Ohitettu (-SkipPolicyChecks). Paketti ei valttamatta ole'
    Write-Warn2 'julkaisukelpoinen plugins.qgis.org:iin.'
} else {
    Write-Step 'Tarkistetaan julkaisukelpoisuus'
    Test-ReleasePolicy -Metadata $metadata -PackageVersion $packageVersion
}

if ($CheckUrls) {
    Write-Step 'Tarkistetaan metadata.txt:n linkit'
    Test-MetadataUrls -Metadata $metadata
}

# ---------------------------------------------------------------------------

# Tiedostonimi on versioitu GitHub Releasea varten. ZIPin sisalla ylatason
# hakemisto on aina versioimaton, koska siita tulee Python-paketin nimi.
$zipFileName    = '{0}-{1}.zip' -f $script:PluginDirName, $packageVersion
$outputDirPath  = if ([System.IO.Path]::IsPathRooted($OutputDir)) {
    $OutputDir
} else {
    Join-Path $script:RepoRoot $OutputDir
}
$zipPath = Join-Path $outputDirPath $zipFileName

if ($DryRun) {
    Write-Step 'Kuivaharjoitus'
    Write-Ok 'Tarkistukset lapaisty. ZIP-tiedostoa ei kirjoitettu (-DryRun).'
    Write-Info "Kirjoitettaisiin: $zipPath"
    Write-Host ''
    exit 0
}

if ((Test-Path -LiteralPath $zipPath) -and -not $Force) {
    throw "ZIP-tiedosto on jo olemassa: $zipPath`nKayta -Force jos haluat ylikirjoittaa sen."
}

Write-Step 'Kirjoitetaan ZIP-paketti'

$zipFile = New-PluginPackage -Files $packageFiles -DestinationPath $zipPath

Write-Ok "$zipFileName kirjoitettu"
Write-Info "Polku : $zipPath"
Write-Info "Koko  : $([math]::Round($zipFile.Length / 1KB, 1)) KB (pakkaamaton $([math]::Round($totalBytes / 1KB, 1)) KB)"

# ---------------------------------------------------------------------------

Write-Step 'Validoidaan paketti plugins.qgis.org:n saantojen mukaan'

Test-PluginPackage -Path $zipPath

Write-Host ''
Write-Host ('-' * 62) -ForegroundColor DarkGray
Write-Host "VALMIS: $zipPath" -ForegroundColor Green
Write-Host ''
