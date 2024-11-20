# Get all .json files in cache directory
$files = Get-ChildItem -Path "cache" -Filter "*.json"

foreach ($file in $files) {
    # Get original name without extension
    $origName = $file.BaseName
    
    # Calculate SHA1 hash
    $sha1 = New-Object System.Security.Cryptography.SHA1CryptoServiceProvider
    $hash = [System.BitConverter]::ToString(
        $sha1.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($origName))
    ).Replace("-", "").ToLower()
    
    # New filename with hash
    $newPath = Join-Path $file.Directory.FullName "$hash.json"
    
    # Rename file if new name is different
    if ($file.FullName -ne $newPath) {
        Move-Item -Path $file.FullName -Destination $newPath -Force
        Write-Host "Renamed $($file.Name) to $hash.json"
    }
}