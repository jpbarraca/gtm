# ⚡ Guitarix Tone Matcher

A simple vibe coded tool to dial in your virtual rig.

🎸 [Try the Live App Here](https://jpbarraca.github.io/gtm/)!

## 🤘 What is this?

Guitarix Tone Matcher is a standalone Progressive Web App (PWA) that acts as your personal AI guitar tech. By leveraging Google's Gemini AI, it translates your target guitar tone (e.g., "Tony Iommi", "Shoegaze", "Texas Blues") into a complete, ready-to-dial signal chain specifically designed for Guitarix, the open-source Linux virtual amplifier. It was developed as a tool to get a first approximation to a tone. YMMV!

Since this is a Vibe Coded tool, it prioritizes a slick, rock-inspired interface and runs entirely in your browser—no backend servers or databases required!

## ✨ Features

AI Rig Generation: Maps real-world analog gear to Guitarix's native digital modules.

Context Aware: Compensates for your physical guitar's specs (e.g., adjusting EQ if you are trying to play doom metal on a single-coil Strat).

Tone Vault: Save your favorite generated rigs straight to your browser's local storage.

NAM Fallback: If Guitarix native amps aren't enough for a highly specific modern tone, the AI will recommend a Neural Amp Modeler (NAM) profile to search for on ToneHunt/Tone3000.

Visual Pedalboard: See your signal chain laid out horizontally with dynamic, rotating knobs indicating exact parameter values.

## ⚙️ Basic Usage

Get an API Key: You will need a free Google Gemini API Key. You can grab one from Google AI Studio.

Open the App: Navigate to https://jpbarraca.github.io/gtm/. (You can also install it to your home screen or desktop as a PWA).

Configure Settings: Click the ⚙️ Settings button in the top right corner. Paste your Gemini API key and select your preferred AI model.

Dial it in: Select your Guitar Type, Pickup Configuration, and type in the tone or player you want to match.

Engage: Hit the "Engage" button. The AI will build your custom pedalboard and provide engineer's notes.

Save to Vault: Love the tone? Click 💾 Save Rig to keep it in your local Tone Vault for future reference.

## 🔒 Privacy Disclaimer

This app is a purely client-side PWA.

Your API Key is saved in your browser's localStorage and is only ever sent directly to Google's API endpoints to generate the tone.

Your Tone Vault is saved entirely in your browser's localStorage.
No data is ever sent to, or stored on, any third-party tracking servers or databases.
