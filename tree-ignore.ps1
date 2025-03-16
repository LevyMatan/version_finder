# tree-ignore.ps1
param(
    [string]$Path = ".",
    [string[]]$Exclude = @(".pytest_cache", "venv", "build", "*.egg-info", "__pycache__"),
    [int]$MaxDepth = 5,  # Default maximum depth
    [int]$Indent = 0
)

function Show-Tree {
    param(
        [string]$CurrentPath,
        [string[]]$Exclude,
        [int]$MaxDepth,
        [int]$CurrentDepth,
        [int]$Indent
    )

    # Stop recursion if max depth is reached
    if ($CurrentDepth -ge $MaxDepth) {
        return
    }

    # Show directories, excluding specified patterns
    Get-ChildItem -LiteralPath $CurrentPath -Directory | Where-Object {
        foreach ($pattern in $Exclude) {
            if ($_.Name -like $pattern) { return $false }
        }
        return $true
    } | Sort-Object Name | ForEach-Object {
        Write-Host (" " * $Indent + "|-- " + $_.Name)
        Show-Tree -CurrentPath $_.FullName -Exclude $Exclude -MaxDepth $MaxDepth -CurrentDepth ($CurrentDepth + 1) -Indent ($Indent + 4)
    }

    # Show files in the current directory
    Get-ChildItem -LiteralPath $CurrentPath -File | Sort-Object Name | ForEach-Object {
        Write-Host (" " * ($Indent + 4) + "|-- " + $_.Name)
    }
}

Write-Host $Path
Show-Tree -CurrentPath $Path -Exclude $Exclude -MaxDepth $MaxDepth -CurrentDepth 0 -Indent 0
