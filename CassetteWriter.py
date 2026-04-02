#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 10:36:53 2026

@author: l3g0b0y
"""

import tkinter as tk
from tkinter import ttk, filedialog as fd, messagebox as msg
import numpy as np
import sounddevice as sd
import wave

# ---------------- AUDIO ENCODING ---------------- #

def file_to_audio(file_path):
    with open(file_path, "rb") as f:
        data = f.read()

    sample_rate = 44100
    duration = 0.01

    audio = []

    for byte in data:
        for i in range(8):
            bit = (byte >> i) & 1
            freq = 2000 if bit else 1000

            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = np.sin(2 * np.pi * freq * t)

            audio.extend(tone)

    return np.array(audio), sample_rate


# ---------------- AUDIO STEGANOGRAPHY ---------------- #

def hide_audio(cover_path, secret_path, output_path):
    with wave.open(cover_path, 'rb') as cover:
        params = cover.getparams()
        cover_frames = bytearray(cover.readframes(cover.getnframes()))

    with wave.open(secret_path, 'rb') as secret:
        secret_frames = bytearray(secret.readframes(secret.getnframes()))

    if len(secret_frames) > len(cover_frames):
        raise ValueError("Secret audio too large!")

    for i in range(len(secret_frames)):
        cover_frames[i] = (cover_frames[i] & 0b11111110) | (secret_frames[i] & 1)

    with wave.open(output_path, 'wb') as out:
        out.setparams(params)
        out.writeframes(cover_frames)


# ---------------- UPLOADER ---------------- #

def Uploader(w):
    file_path = fd.askopenfilename(
        title="Upload code",
        filetypes=[("Code files", "*.c *.cpp *.bin"), ("All files", "*.*")]
    )

    if not file_path:
        return

    EACw = tk.Toplevel(w)
    EACw.title("Cassette Upload")
    EACw.geometry("450x400")

    tk.Label(EACw, text="Selected File:", font=("Arial", 10, "bold")).pack()
    tk.Label(EACw, text=file_path, wraplength=400).pack(pady=5)

    # ---------------- DEVICE SELECTOR ---------------- #

    devices = sd.query_devices()
    device_names = [f"{i}: {d['name']}" for i, d in enumerate(devices)]

    selected_device = tk.StringVar(value=device_names[0])

    tk.Label(EACw, text="Select Output Device:").pack(pady=5)
    device_menu = ttk.Combobox(EACw, values=device_names, textvariable=selected_device)
    device_menu.pack(fill="x", padx=20)

    # ---------------- AUDIO FILES ---------------- #

    cover_audio = tk.StringVar(value="No cover selected")
    secret_audio = tk.StringVar(value="No secret selected")

    def select_cover():
        path = fd.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if path:
            cover_audio.set(path)

    def select_secret():
        path = fd.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if path:
            secret_audio.set(path)

    tk.Label(EACw, text="Cover Audio").pack()
    tk.Label(EACw, textvariable=cover_audio, wraplength=400).pack()
    ttk.Button(EACw, text="Select Cover", command=select_cover).pack(pady=5)

    tk.Label(EACw, text="Secret Audio").pack()
    tk.Label(EACw, textvariable=secret_audio, wraplength=400).pack()
    ttk.Button(EACw, text="Select Secret", command=select_secret).pack(pady=5)

    # ---------------- PROGRESS ---------------- #

    progress = ttk.Progressbar(EACw, length=350)
    progress.pack(pady=15)

    status = tk.Label(EACw, text="Ready", fg="green")
    status.pack()

    # ---------------- ENCRYPT BUTTON ---------------- #

    def encrypt_audio():
        try:
            if cover_audio.get() == "No cover selected" or secret_audio.get() == "No secret selected":
                msg.showerror("Error", "Select both audio files!")
                return

            output = "encrypted.wav"
            hide_audio(cover_audio.get(), secret_audio.get(), output)

            msg.showinfo("Done", f"Encrypted audio saved as {output}")

        except Exception as e:
            msg.showerror("Error", str(e))

    ttk.Button(EACw, text="Encrypt Audio", command=encrypt_audio).pack(pady=5)

    # ---------------- START UPLOAD ---------------- #

    def start_upload():
        try:
            status.config(text="Encoding...", fg="orange")
            EACw.update_idletasks()

            audio, sr = file_to_audio(file_path)

            # Set selected device
            device_index = int(selected_device.get().split(":")[0])
            sd.default.device = device_index

            status.config(text="Playing to cassette...", fg="blue")

            total = len(audio)
            chunk = sr // 10

            sd.play(audio, sr, blocking=False)

            for i in range(0, total, chunk):
                progress["value"] = (i / total) * 100
                EACw.update_idletasks()

            sd.wait()
            progress["value"] = 100

            status.config(text="Done!", fg="green")
            msg.showinfo("Success", "Written to cassette 🎵")

        except Exception as e:
            msg.showerror("Error", str(e))

    ttk.Button(EACw, text="Start Recording", command=start_upload).pack(pady=10)


# ---------------- MAIN UI ---------------- #

w = tk.Tk()
w.title("Cassette Programmer Pro")
w.geometry("800x400")

sidebar = ttk.Frame(w, width=200)
sidebar.pack(side="left", fill="y")

ttk.Label(sidebar, text="Program Tape", font=("Arial", 16, "bold")).pack(pady=20)

ttk.Button(
    sidebar,
    text="Upload",
    command=lambda: Uploader(w)
).pack(pady=10, padx=20, fill="x")

main = ttk.Frame(w)
main.pack(side="right", expand=True, fill="both")

tk.Label(main, text="Cassette System", font=("Arial", 18)).pack(pady=50)

w.mainloop()