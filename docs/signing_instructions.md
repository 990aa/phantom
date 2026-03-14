# Self-Signing Instructions for Phantom AI

This guide explains how to set up self-signing for both Windows and Android so you can install and run the apps without warning screens on devices.

## Important Note on Storage
**DO NOT** commit your `.keystore` or `.pfx` files to GitHub. Keep them in a safe, offline backup location (e.g., a encrypted USB drive or a secure password manager's file vault). If you lose these, you will not be able to update your apps on F-Droid or WinGet with the same signature.

---

## Android (APK)

F-Droid compatible signing uses a standard Java Keystore. We set the validity to 25 years (9125 days) to ensure it doesn't expire soon.

1. **Generate a Keystore:**
   Run this command. Replace `my-phantom-key` with a unique alias if you have other apps.
   ```bash
   keytool -genkey -v -keystore phantom_v1.keystore -alias phantom_alias -keyalg RSA -keysize 2048 -validity 9125
   ```
   *Note: Use a strong password. This will not affect keys generated for other apps as long as the filename (`phantom_v1.keystore`) and alias are unique.*

2. **Base64 Encode for GitHub Actions:**
   ```bash
   base64 -w 0 phantom_v1.keystore > keystore.b64
   ```

3. **Required GitHub Secrets:**
   - `ANDROID_KEYSTORE_BASE64`: Content of `keystore.b64`
   - `ANDROID_STORE_PASSWORD`: Your keystore password
   - `ANDROID_KEY_ALIAS`: `phantom_alias`
   - `ANDROID_KEY_PASSWORD`: Your key password

---

## Windows (Tauri / WinGet)

For Windows, self-signing avoids the "Windows SmartScreen" blue warning.

1. **Generate a Self-Signed Certificate:**
   Run PowerShell as Administrator. We set the expiry to 10 years.
   ```powershell
   $cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=990aa" -KeyExportPolicy Exportable -KeySpec Signature -HashAlgorithm sha256 -KeyLength 2048 -CertStoreLocation "Cert:\CurrentUser\My" -NotAfter (Get-Date).AddYears(10)
   $pwd = ConvertTo-SecureString -String "YOUR_SAFE_PASSWORD" -Force -AsPlainText
   Export-PfxCertificate -Cert $cert -FilePath "phantom_win_v1.pfx" -Password $pwd
   ```

2. **Base64 Encode for GitHub Actions:**
   ```powershell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("phantom_win_v1.pfx")) | Out-File -FilePath "cert_b64.txt"
   ```

3. **Required GitHub Secrets:**
   - `WINDOWS_CERTIFICATE_BASE64`: Content of `cert_b64.txt`
   - `WINDOWS_CERTIFICATE_PASSWORD`: "YOUR_SAFE_PASSWORD"

---

## Backup Strategy
1. Copy `phantom_v1.keystore` and `phantom_win_v1.pfx` to your secure backup.
2. Store the passwords in a password manager.
3. Delete the local files from your workspace after encoding to prevent accidental leakage.
