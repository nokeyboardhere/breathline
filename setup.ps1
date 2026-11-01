
$ErrorActionPreference = "Stop"

$projectPath = $PSScriptRoot
$mainPath = Join-Path $projectPath "main.py"
$pngPath = Join-Path $projectPath "icon.png"
$icoPath = Join-Path $projectPath "icon.ico"

if (-not (Test-Path $mainPath)) {
    throw "main.py was not found in the project folder."
}

# Find the Python installation.
$python = (Get-Command python -ErrorAction Stop).Source
$pythonw = Join-Path (Split-Path $python) "pythonw.exe"

if (-not (Test-Path $pythonw)) {
    $command = Get-Command pythonw.exe -ErrorAction SilentlyContinue
    if ($command) {
        $pythonw = $command.Source
    }
    else {
        throw "pythonw.exe was not found."
    }
}

# Convert icon.png to a Windows .ico file.
if (Test-Path $pngPath) {
    Add-Type -AssemblyName System.Drawing

    $source = [System.Drawing.Image]::FromFile($pngPath)
    $bitmap = [System.Drawing.Bitmap]::new(256, 256)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)

    try {
        $graphics.Clear([System.Drawing.Color]::Transparent)
        $graphics.InterpolationMode = "HighQualityBicubic"

        $scale = [Math]::Min(256 / $source.Width, 256 / $source.Height)
        $width = [int]($source.Width * $scale)
        $height = [int]($source.Height * $scale)
        $x = [int]((256 - $width) / 2)
        $y = [int]((256 - $height) / 2)

        $graphics.DrawImage($source, $x, $y, $width, $height)

        $memory = [System.IO.MemoryStream]::new()
        $bitmap.Save($memory, [System.Drawing.Imaging.ImageFormat]::Png)
        $pngBytes = $memory.ToArray()

        $file = [System.IO.File]::Create($icoPath)
        $writer = [System.IO.BinaryWriter]::new($file)

        # ICO header and image directory entry.
        $writer.Write([UInt16]0)
        $writer.Write([UInt16]1)
        $writer.Write([UInt16]1)
        $writer.Write([byte]0)
        $writer.Write([byte]0)
        $writer.Write([byte]0)
        $writer.Write([byte]0)
        $writer.Write([UInt16]1)
        $writer.Write([UInt16]32)
        $writer.Write([UInt32]$pngBytes.Length)
        $writer.Write([UInt32]22)
        $writer.Write($pngBytes)

        $writer.Close()
        $memory.Dispose()
    }
    finally {
        $graphics.Dispose()
        $bitmap.Dispose()
        $source.Dispose()
    }
}

# Create the desktop shortcut.
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Breathline.lnk"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)

$shortcut.TargetPath = $pythonw
$shortcut.Arguments = "`"$mainPath`""
$shortcut.WorkingDirectory = $projectPath

if (Test-Path $icoPath) {
    $shortcut.IconLocation = "$icoPath,0"
}

$shortcut.Description = "Breathline breathing app"
$shortcut.Save()

Write-Host "Breathline desktop shortcut created successfully."

