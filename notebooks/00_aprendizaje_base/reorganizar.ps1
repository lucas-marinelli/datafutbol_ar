# reorganizar.ps1 -- Mueve los notebooks a la nueva estructura
# Como ejecutar (una sola vez):
#   1. Abri PowerShell
#   2. cd "D:\PROYECTOS_venv\02_PROYECTOS\01_Python\datafutbol_ar\notebooks\00_aprendizaje_base"
#   3. powershell -ExecutionPolicy Bypass -File .\reorganizar.ps1

$ErrorActionPreference = "Stop"
$base = "D:\PROYECTOS_venv\02_PROYECTOS\01_Python\datafutbol_ar\notebooks\00_aprendizaje_base"

Write-Host ""
Write-Host "Reorganizando notebooks de 00_aprendizaje_base/" -ForegroundColor Cyan
Write-Host "-----------------------------------------------"

# 1) Crear carpetas (no falla si ya existen)
Write-Host "Creando carpetas..." -ForegroundColor Yellow
$folders = @(
    "01_python_pandas",
    "02_matplotlib",
    "03_mplsoccer",
    "04_statsbomb",
    "05_visualizaciones_futbol",
    "06_scraping",
    "_archive\duplicados"
)
foreach ($f in $folders) {
    New-Item -ItemType Directory -Force -Path "$base\$f" | Out-Null
    Write-Host "  [OK] $f"
}

# Funcion helper para mover archivos solo si existen
function Move-IfExists {
    param($from, $to)
    if (Test-Path $from) {
        Move-Item $from $to
        $nombreArchivo = Split-Path $from -Leaf
        $carpetaDestino = Split-Path $to -Parent | Split-Path -Leaf
        $nombreDestino = Split-Path $to -Leaf
        Write-Host "  [OK] $nombreArchivo -> $carpetaDestino\$nombreDestino"
    } else {
        $nombreArchivo = Split-Path $from -Leaf
        Write-Host "  [SKIP] ya movido o no existe: $nombreArchivo" -ForegroundColor DarkGray
    }
}

# 2) PANDAS
Write-Host ""
Write-Host "01_python_pandas/" -ForegroundColor Yellow
Move-IfExists "$base\pandas_1.ipynb" "$base\01_python_pandas\01_introduccion.ipynb"
Move-IfExists "$base\pandas_2.ipynb" "$base\01_python_pandas\02_seleccion_filtrado.ipynb"
Move-IfExists "$base\pandas_3.ipynb" "$base\01_python_pandas\03_manipulacion.ipynb"
Move-IfExists "$base\pandas_4.ipynb" "$base\01_python_pandas\04_agrupacion.ipynb"
Move-IfExists "$base\pandas_5.ipynb" "$base\01_python_pandas\05_visualizacion_basica.ipynb"
Move-IfExists "$base\pandas_6_JOIN_revisar.ipynb" "$base\01_python_pandas\06_joins.ipynb"

# 3) MATPLOTLIB
Write-Host ""
Write-Host "02_matplotlib/" -ForegroundColor Yellow
Move-IfExists "$base\matplotlib_1.ipynb" "$base\02_matplotlib\01_introduccion.ipynb"

# 4) MPLSOCCER
Write-Host ""
Write-Host "03_mplsoccer/" -ForegroundColor Yellow
Move-IfExists "$base\01_introduccion_mplsoccer.ipynb" "$base\03_mplsoccer\01_introduccion.ipynb"
Move-IfExists "$base\02_plot_pitches.ipynb" "$base\03_mplsoccer\02_pitches.ipynb"
Move-IfExists "$base\03_plot_pitch_types.ipynb" "$base\03_mplsoccer\03_tipos_de_pitch.ipynb"
Move-IfExists "$base\07_dashboards.ipynb" "$base\03_mplsoccer\04_dashboards.ipynb"

# 5) STATSBOMB
Write-Host ""
Write-Host "04_statsbomb/" -ForegroundColor Yellow
Move-IfExists "$base\04_plot_statsbomb_data.ipynb" "$base\04_statsbomb\01_carga_eventos.ipynb"
Move-IfExists "$base\10_statsbomb.ipynb" "$base\04_statsbomb\02_explorar_partidos.ipynb"

# 6) VISUALIZACIONES FUTBOL
Write-Host ""
Write-Host "05_visualizaciones_futbol/" -ForegroundColor Yellow
Move-IfExists "$base\05_mapas_de_tiros.ipynb" "$base\05_visualizaciones_futbol\01_mapas_tiros.ipynb"
Move-IfExists "$base\06_mapas_de_calor.ipynb" "$base\05_visualizaciones_futbol\02_mapas_calor.ipynb"
Move-IfExists "$base\09_mapas_de_pases.ipynb" "$base\05_visualizaciones_futbol\03_pass_network.ipynb"
Move-IfExists "$base\radar.ipynb" "$base\05_visualizaciones_futbol\04_radar.ipynb"
Move-IfExists "$base\08_filtrado_pases.ipynb" "$base\05_visualizaciones_futbol\05_filtrado_pases.ipynb"

# 7) SCRAPING
Write-Host ""
Write-Host "06_scraping/" -ForegroundColor Yellow
Move-IfExists "$base\scrapeo.ipynb" "$base\06_scraping\01_scraping_basico.ipynb"
Move-IfExists "$base\joins_REVconfede.ipynb" "$base\06_scraping\02_joins_dataframes.ipynb"

# 8) ARCHIVAR DUPLICADOS
Write-Host ""
Write-Host "_archive/duplicados/ (notebooks duplicados a revisar despues)" -ForegroundColor Yellow
Move-IfExists "$base\int_mplsoccer.ipynb" "$base\_archive\duplicados\int_mplsoccer.ipynb"
Move-IfExists "$base\mplsoccer_2.ipynb" "$base\_archive\duplicados\mplsoccer_2.ipynb"
Move-IfExists "$base\mplsoccer_3.ipynb" "$base\_archive\duplicados\mplsoccer_3.ipynb"
Move-IfExists "$base\statsbomb1.ipynb" "$base\_archive\duplicados\statsbomb1.ipynb"
Move-IfExists "$base\mapas_de_tiros.ipynb" "$base\_archive\duplicados\mapas_de_tiros.ipynb"

Write-Host ""
Write-Host "-----------------------------------------------"
Write-Host "Reorganizacion completa." -ForegroundColor Green
Write-Host ""
Write-Host "Proximos pasos:"
Write-Host "  - Revisar la nueva estructura con: tree /F"
Write-Host "  - Cuando tengas tiempo, abrir _archive\duplicados\ y comparar con la version oficial"
Write-Host "  - Si los duplicados son iguales o peores, borrarlos definitivamente"
Write-Host ""
