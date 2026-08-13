GUIDE Mac Vision Fix 1.3.1
==========================

Purpose
-------
This patch fixes the Mac picture review error:

No vision model available (e.g. moondream, qwen2.5-vl)

The error can happen when GUIDE connects to a separately installed Mac Ollama
service instead of the Ollama engine and models stored on the GUIDE USB drive.

What This Updates
-----------------
- Guide (Mac).app/Contents/MacOS/launcher
- .internal/start-fallback.command
- BETA_TEST_PLAN.md, if present
- GUIDE_README.html, if present

The patch makes the Mac launcher start the bundled USB Ollama service first,
wait until a USB vision model is visible, and then open GUIDE.

How To Apply
------------
1. Quit GUIDE.
2. Quit the regular Ollama desktop app if it is open.
3. Plug in the GUIDE USB drive.
4. Unzip this patch if needed.
5. Double-click apply-mac-vision-fix.command.
6. If macOS blocks the script, right-click it, choose Open, then confirm.
7. Launch GUIDE from Guide (Mac).app on the USB.
8. Retest Review Picture.

Finder may show only README.txt and apply-mac-vision-fix.command. The patch
payload is stored in a hidden .patch-files folder inside this update.

Expected Result
---------------
After applying the patch, GUIDE should see at least one of these USB vision
models:

- moondream:latest
- huihui_ai/qwen2.5-vl-abliterated:7b-instruct

Notes
-----
This patch is for Mac users only.

It does not download models from the internet. It expects the vision models to
already exist on the GUIDE USB drive.
