# reorganizar_galeria_v2.ps1
# Mueve la galeria oficial de mplsoccer a una subcarpeta _gallery/
# para no mezclarla con los notebooks didacticos.
#
# Como ejecutar:
#   cd "D:\PROYECTOS_venv\02_PROYECTOS\01_Python\datafutbol_ar\notebooks\00_aprendizaje_base"
#   powershell -ExecutionPolicy Bypass -File .\reorganizar_galeria_v2.ps1

$ErrorActionPreference = "Stop"
$base = "D:\PROYECTOS_venv\02_PROYECTOS\01_Python\datafutbol_ar\notebooks\00_aprendizaje_base\03_mplsoccer"

Write-Host ""
Write-Host "Reorganizando galeria mplsoccer..." -ForegroundColor Cyan
Write-Host "--------------------------------------------------"

# 1) Crear carpeta _gallery con sus subdirs
$galleryFolders = @(
    "_gallery",
    "_gallery\pitch_setup",
    "_gallery\pitch_plots",
    "_gallery\pizza_plots",
    "_gallery\radar",
    "_gallery\bumpy_charts",
    "_gallery\sonars",
    "_gallery\statsbomb",
    "_gallery\tutorials",
    "_archive\duplicados_py"
)
foreach ($f in $galleryFolders) {
    New-Item -ItemType Directory -Force -Path "$base\$f" | Out-Null
    Write-Host "  [OK] $f"
}

# Helper para mover archivos
function Move-IfExists {
    param($from, $to)
    if (Test-Path $from) {
        Move-Item $from $to -Force
        Write-Host "  [OK] $(Split-Path $from -Leaf)"
    }
}

# Helper para mover carpetas ENTERAS con su contenido
function Move-FolderIfExists {
    param($from, $to)
    if (Test-Path $from) {
        Get-ChildItem $from -File | ForEach-Object {
            Move-Item $_.FullName $to -Force
        }
        # Si quedo vacia la original, borrarla
        if ((Get-ChildItem $from).Count -eq 0) {
            Remove-Item $from -Force -Recurse
        }
        Write-Host "  [OK] contenido de $(Split-Path $from -Leaf) movido"
    }
}

# 2) Mover cada subcarpeta de la galeria a _gallery
Write-Host ""
Write-Host "Moviendo subcarpetas a _gallery/:" -ForegroundColor Yellow

Move-FolderIfExists "$base\pitch_setup" "$base\_gallery\pitch_setup"
Move-FolderIfExists "$base\pitch_plots" "$base\_gallery\pitch_plots"
Move-FolderIfExists "$base\pizza_plots" "$base\_gallery\pizza_plots"
Move-FolderIfExists "$base\radar" "$base\_gallery\radar"
Move-FolderIfExists "$base\bumpy_charts" "$base\_gallery\bumpy_charts"
Move-FolderIfExists "$base\sonars" "$base\_gallery\sonars"
Move-FolderIfExists "$base\statsbomb" "$base\_gallery\statsbomb"
Move-FolderIfExists "$base\tutorials" "$base\_gallery\tutorials"

# 3) Archivar los .py sueltos en raiz (son duplicados de los que estan en subcarpetas)
Write-Host ""
Write-Host "Archivando .py duplicados sueltos en raiz:" -ForegroundColor Yellow
Move-IfExists "$base\plot_bumpy.py" "$base\_archive\duplicados_py\plot_bumpy.py"
Move-IfExists "$base\plot_radar.py" "$base\_archive\duplicados_py\plot_radar.py"

Write-Host ""
Write-Host "--------------------------------------------------"
Write-Host "Reorganizacion de galeria completa." -ForegroundColor Green
Write-Host ""
Write-Host "Resultado:"
Write-Host "  03_mplsoccer/ ahora tiene SOLO los notebooks 01-05 + _gallery/"
Write-Host "  _gallery/ tiene los 48+ scripts de referencia oficial mplsoccer"
Write-Host "  _archive/duplicados_py/ tiene los 2 .py que estaban sueltos"
Write-Host ""
