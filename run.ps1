param(
    [string]$appPath
)

if ($null -eq $appPath)
{
    break
}

# Now $appPath contains the passed path which you can use in the script
Write-Host "Received app path: $appPath"

$settings = ".\settings.json"

$data = Get-Content $settings -Raw | ConvertFrom-Json

$applications = $data.applications | Where-Object { $_.folder -eq $appPath }

if ($null -ne $applications)
{
    # Change to the application folder
    Set-Location -Path $appPath

    # Run the dotnet command
    dotnet $applications.dll
}
else
{
    Write-Host "Application not found in settings.json"
}