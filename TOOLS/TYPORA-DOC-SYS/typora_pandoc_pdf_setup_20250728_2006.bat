# typora_pandoc_pdf_setup_20250728_2006.bat

@echo off
echo ═══════════════════════════════════════════════════════════════════
echo TYPORA-PANDOC PDF INTEGRATION SETUP
echo Time: 20:06 Pacific - July 28, 2025
echo ═══════════════════════════════════════════════════════════════════

echo.
echo Step 1: Downloading Pandoc...
echo Visiting: https://github.com/jgm/pandoc/releases/latest
echo Look for: pandoc-3.x.x-windows-x86_64.msi
echo.
pause

echo.
echo Step 2: Installing wkhtmltopdf for CSS-styled PDFs...
echo Visiting: https://wkhtmltopdf.org/downloads.html
echo Download: Windows 64-bit installer
echo.
pause

echo.
echo Step 3: Creating media folders for screenshots and files...
mkdir "C:\INDEX-PROJECT\media"
mkdir "C:\INDEX-PROJECT\media\screenshots"
mkdir "C:\INDEX-PROJECT\media\excel-charts"
mkdir "C:\INDEX-PROJECT\media\gui-captures"
mkdir "C:\INDEX-PROJECT\media\photos"
echo Media folders created successfully!

echo.
echo Step 4: Creating Typora CSS theme for perfect PDF output...
mkdir "C:\INDEX-PROJECT\typora-themes"
echo CSS theme folder created!

echo.
echo Step 5: Verifying installations...
echo Testing Pandoc installation:
pandoc --version
echo.
echo Testing wkhtmltopdf installation:
wkhtmltopdf --version

echo.
echo ═══════════════════════════════════════════════════════════════════
echo SETUP COMPLETE - Ready for Typora configuration
echo ═══════════════════════════════════════════════════════════════════
pause