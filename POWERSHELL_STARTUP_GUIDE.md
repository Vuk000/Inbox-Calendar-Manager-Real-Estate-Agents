# Quick Start Guide - PowerShell vs Command Prompt

## ⚠️ PowerShell vs Command Prompt - Important Difference!

### PowerShell (PowerShell.exe or Terminal in VS Code)

PowerShell requires the `.\` prefix for security reasons. It will NOT execute scripts from the current directory without it.

**✅ Correct:**
```powershell
.\start_app.ps1
.\start_app.bat
```

**❌ Wrong (will give error):**
```powershell
start_app.bat
start_app.ps1
```

**Error you'll see:**
```
start_app.bat : The term 'start_app.bat' is not recognized...
Suggestion: Use ".\start_app.bat"
```

### Command Prompt (cmd.exe)

Command Prompt does NOT require the `.\` prefix.

**✅ Correct:**
```cmd
start_app.bat
```

**Also works:**
```cmd
.\start_app.bat
```

## Which Terminal Am I Using?

**PowerShell:**
- Prompt shows: `PS C:\...>`
- Usually blue/purple background
- VS Code Terminal by default uses PowerShell on Windows

**Command Prompt:**
- Prompt shows: `C:\...>`
- Usually black background
- Old-style Windows terminal

## Recommended Solution

**For PowerShell users (most common):**
```powershell
.\start_app.ps1
```

**For Command Prompt users:**
```cmd
start_app.bat
```

**Or double-click `start_app.bat` in File Explorer** - This works regardless of terminal type!

