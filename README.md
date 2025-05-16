# DRK Multi-Lang - Multilingual Darmoshark Driver Translator

![Badge](https://hitscounter.dev/api/hit?url=https%3A%2F%2Fgithub.com%2FXanixsl%2FRussifier-Drk&label=Visitors&icon=people&color=%23c5b3e6)
[![Download Count](https://hitscounter.dev/api/hit?url=https%3A%2F%2Fgithub.com%2FXanixsl%2FRussifier-Drk%2Freleases%2Flatest%2Fdownload%2FDRK.exe&label=Downloads&color=0078D7)](https://github.com/Xanixsl/Russifier-Drk/releases/latest/download/DRK.exe)
[![Latest Version](https://img.shields.io/github/v/release/Xanixsl/Russifier-Drk?label=Latest%20Version&style=flat-square)](https://github.com/Xanixsl/Russifier-Drk/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square&logo=opensourceinitiative&logoColor=white)](https://opensource.org/licenses/MIT)

<img src="https://github.com/user-attachments/assets/0f139f68-0bd6-4068-b7e9-9480534085d2" alt="DRK Multi-Lang Screenshot" width="650"/>

## 🚀 About the Program

**DRK Multi-Lang** is an automatic translation tool for **Darmoshark** mouse drivers (models **M3, M3s, N3**) that supports 20+ languages.

🔗 **Official Website:** [https://russifier-drk.ru/](https://russifier-drk.ru/)  
*(Note: The website currently has a standard version in Russian and English. Other languages are planned to be supported in the future)*

## ✨ Key Features

✔ Fully automatic translation process  
✔ Security: All files remain on your PC  
✔ Ability to roll back to default settings  
✔ Modern UI with transparency effects  
✔ Supports driver versions 1.6.5 - 1.8.2.9  
✔ 20+ language translations available  

🔒 **Important:** The program does NOT collect or send your data! All files are stored strictly on your computer.

## 🌍 Supported Languages
English | Russian | Ukrainian | Belarusian | Kazakh | Polish | Czech | Slovak  
Bulgarian | Serbian | Armenian | Georgian | Romanian | Latvian | Lithuanian  
Estonian | Turkish | German | French | Spanish | and more...

⚠ **Translation Notice:**  
I am not a native speaker of all these languages and cannot guarantee 100% translation accuracy. All translations were performed using translators and AI systems for better precision. Some minor text overlapping or truncation (like "Exam...") may occur in the mouse driver interface after translation.

## 📥 Installation

1. Download the latest version:
   - [Download DRK_MultiLang.exe](https://github.com/Xanixsl/Russifier-Drk/releases/latest/download/DRK.exe)
   - [All versions](https://github.com/Xanixsl/Russifier-Drk/releases)

2. Run as Administrator

## 🛠 How It Works

<img src="https://github.com/user-attachments/assets/56ab3c34-8fef-425c-881f-381c5d78617c" alt="DRK Multi-Lang Screenshot" width="650"/>

1. Locates mouse driver (`DeviceDriver.exe`)
2. Finds language folder (`language`)
3. Replaces default files with translated versions
4. Saves path in cache for quick rollback

## 🔄 Switching Languages

1. Wait until DRK Multi-Lang launches the mouse driver
2. Go to the bottom tab in driver settings
3. Select **English** from dropdown list

> **Note:** The translation only works when English is selected in the driver settings.

## 📂 About Cache System
<img src="https://github.com/user-attachments/assets/34478cde-6cee-4914-8df6-a51628710985" alt="DRK Multi-Lang Screenshot" width="750"/>

Cache is temporary storage that:
- Remembers driver location (`DeviceDriver.exe`)
- Speeds up subsequent launches
- Enables quick rollback

To access TEMP folder (where cache is stored):

<img src="https://github.com/user-attachments/assets/1bad9a28-585d-47e6-94fa-b7b247df1825" alt="DRK Multi-Lang Screenshot" width="550"/>

1. Press `Win + R`
2. Type `%temp%`
3. Press `Enter`

## 💻 Technical Details

Built with:
- Python + PyQt5 for modern UI
- psutil for process management
- ctypes for admin rights

## 📜 License

MIT License - see [LICENSE](LICENSE) file.

## ☕ Support the Project

If you find this tool useful, consider supporting development:

[![DonationAlerts](https://img.shields.io/badge/Donate-DonationAlerts-red?style=for-the-badge)](https://www.donationalerts.com/r/saylont)  
[![Boosty](https://img.shields.io/badge/Donate-Boosty-8A2BE2?style=for-the-badge)](https://boosty.to/saylontoff/donate)  

*Even small support motivates further development!*
