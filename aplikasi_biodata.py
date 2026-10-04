import tkinter as tk
from tkinter import messagebox
import datetime
import random
import logging
import os
import re

# Konfigurasi Log Aplikasi (menyimpan aktivitas ke dalam file .log)
logging.basicConfig(
    filename='aplikasi_biodata.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- Helper Validation Functions ---
# File untuk fitur "Remember Me" (disimpan di folder yang sama dengan script)
FILE_REMEMBER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "remember_me.txt")

# Format email: nama@domain.tld
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")

# Format telepon Indonesia: awalan 08 / +62 / 62, lalu 8, digit 1-9, dan 7-10 digit lagi
# Contoh valid: 081234567890, +6281234567890, 6281234567890
TELEPON_REGEX = re.compile(r"^(\+62|62|0)8[1-9][0-9]{7,10}$")


def normalisasi_telepon(teks):
    """Membersihkan karakter non-numerik pada string telepon."""
    return re.sub(r"[\s\-().]", "", teks)


def parse_tanggal(teks):
    """Mengonversi string tanggal ke format date, mengembalikan None apabila gagal mem-parsing."""
    try:
        return datetime.datetime.strptime(teks.strip().replace("/", "-"), "%d-%m-%Y").date()
    except ValueError:
        return None


def pesan_error_nim(teks):
    teks = teks.strip()
    if teks and not teks.isdigit():
        return "NIM harus berisi angka"
    return ""


def pesan_error_email(teks):
    teks = teks.strip()
    if teks and not EMAIL_REGEX.match(teks):
        return "Format email tidak valid (contoh: nama@email.com)"
    return ""


def pesan_error_telepon(teks):
    teks = normalisasi_telepon(teks)
    if teks and not TELEPON_REGEX.match(teks):
        return "Format salah (contoh: 081234567890 atau +6281234567890)"
    return ""


def pesan_error_tanggal(teks):
    teks = teks.strip()
    if not teks:
        return ""
    tanggal = parse_tanggal(teks)
    if tanggal is None:
        return "Gunakan format DD-MM-YYYY (contoh: 17-08-2004)"
    if tanggal > datetime.date.today():
        return "Tanggal lahir tidak boleh di masa depan"
    if tanggal.year < 1900:
        return "Tahun lahir tidak valid"
    return ""


# Membuat kelas utama aplikasi yang mewarisi dari tk.Tk
class AplikasiBiodata(tk.Tk):
    # Metode __init__ adalah constructor yang akan dijalankan saat objek dibuat
    def __init__(self):
        super().__init__()
        self.title("Aplikasi Biodata Mahasiswa")
        self.geometry("600x820")
        self.resizable(True, True)

        # Database user sederhana (dalam aplikasi nyata, ini akan di database)
        self.users_db = {
            "admin": "123",
            "user1": "password1",
            "mahasiswa": "123456"
        }

        # Warna background per user
        self.warna_user = {
            "admin": "orange",
            "user1": "lightblue",
            "mahasiswa": "lightgreen",
        }
        # Simpan warna default window (aman untuk semua OS)
        self.warna_default = self.cget("bg")

        # Status login
        self.current_user = None

        # Status tampil/sembunyi password
        self.password_terlihat = False

        # Atribut untuk manajemen frame
        self.frame_aktif = None

        # Buat tampilan
        self._buat_tampilan_login()
        self._buat_tampilan_biodata()

        # Muat username terakhir bila Remember Me pernah dipakai
        self._muat_username_tersimpan()

        # Tampilkan frame login di awal
        self._pindah_ke(self.frame_login)

        # praktikum 5.4
        # Log aplikasi start
        logging.info("Aplikasi dimulai")

    # TAMPILAN LOGIN
    def _buat_tampilan_login(self):
        # Latar belakang biru muda yang profesional
        self.frame_login = tk.Frame(master=self, bg="#e3f2fd", padx=20, pady=100)

        # Konfigurasi grid untuk frame login agar terpusat
        self.frame_login.grid_columnconfigure(0, weight=1)
        self.frame_login.grid_columnconfigure(1, weight=2)
        self.frame_login.grid_columnconfigure(2, weight=0)

        # Judul Login
        tk.Label(
            self.frame_login,
            text="HALAMAN LOGIN",
            font=("Arial", 16, "bold"),
            bg="#e3f2fd"
        ).grid(row=0, column=0, columnspan=3, pady=20)

        # Input Username
        tk.Label(
            self.frame_login,
            text="Username:",
            font=("Arial", 12),
            bg="#e3f2fd"
        ).grid(row=1, column=0, sticky="W", pady=5)

        self.entry_username = tk.Entry(self.frame_login, font=("Arial", 12))
        self.entry_username.grid(row=1, column=1, columnspan=2, pady=5, sticky="EW")

        # Input Password
        tk.Label(
            self.frame_login,
            text="Password:",
            font=("Arial", 12),
            bg="#e3f2fd"
        ).grid(row=2, column=0, sticky="W", pady=5)

        self.entry_password = tk.Entry(
            self.frame_login,
            font=("Arial", 12),
            show="*"
        )
        self.entry_password.grid(row=2, column=1, pady=5, sticky="EW")

        # --- Show/Hide Password ---
        self.btn_toggle_password = tk.Button(
            self.frame_login,
            text="Tampilkan",
            font=("Arial", 9),
            width=10,
            command=self._toggle_password
        )
        self.btn_toggle_password.grid(row=2, column=2, padx=(5, 0), pady=5)

        # --- Remember Me ---
        self.var_remember = tk.IntVar(value=0)
        self.check_remember = tk.Checkbutton(
            self.frame_login,
            text="Ingat username saya",
            variable=self.var_remember,
            font=("Arial", 10),
            bg="#e3f2fd"
        )
        self.check_remember.grid(row=3, column=1, columnspan=2, sticky="W")

        # Tombol Login
        self.btn_login = tk.Button(
            self.frame_login,
            text="Login",
            font=("Arial", 12, "bold"),
            command=self._coba_login
        )
        self.btn_login.grid(row=4, column=0, columnspan=3, pady=20, sticky="EW")

        # Keyboard shortcuts untuk login
        self.entry_username.bind("<Return>", lambda e: self.entry_password.focus_set())
        self.entry_password.bind("<Return>", lambda e: self._coba_login())

    # FITUR: SHOW/HIDE PASSWORD
    def _toggle_password(self):
        """Mengganti visibilitas teks pada kolom password antara karakter * dan teks biasa."""
        self.password_terlihat = not self.password_terlihat
        if self.password_terlihat:
            self.entry_password.config(show="")
            self.btn_toggle_password.config(text="Sembunyikan")
        else:
            self.entry_password.config(show="*")
            self.btn_toggle_password.config(text="Tampilkan")

    def _sembunyikan_password(self):
        """Memaksa kolom password untuk menyembunyikan karakternya."""
        self.password_terlihat = False
        self.entry_password.config(show="*")
        self.btn_toggle_password.config(text="Tampilkan")

    # FITUR: REMEMBER ME
    def _simpan_username(self, username):
        """Merekam username ke dalam penyimpanan lokal agar bisa digunakan kembali di sesi selanjutnya."""
        try:
            with open(FILE_REMEMBER, "w", encoding="utf-8") as f:
                f.write(username)
        except OSError as e:
            logging.error(f"Gagal menyimpan remember me: {e}")

    def _hapus_username_tersimpan(self):
        """Membersihkan data login yang tersimpan dari lokal disk."""
        try:
            if os.path.exists(FILE_REMEMBER):
                os.remove(FILE_REMEMBER)
        except OSError as e:
            logging.error(f"Gagal menghapus remember me: {e}")

    def _muat_username_tersimpan(self):
        """Mengecek ketersediaan data login yang disimpan dan menerapkannya pada kolom input."""
        try:
            if os.path.exists(FILE_REMEMBER):
                with open(FILE_REMEMBER, "r", encoding="utf-8") as f:
                    username = f.read().strip()
                if username:
                    self.entry_username.delete(0, tk.END)
                    self.entry_username.insert(0, username)
                    self.var_remember.set(1)
                    return
        except OSError as e:
            logging.error(f"Gagal memuat remember me: {e}")
        self.var_remember.set(0)

    # TAMPILAN BIODATA
    def format_tanggal_otomatis(self, *args):
        """Memformat input tanggal secara otomatis menjadi pola tanggal-bulan-tahun sembari user mengetik."""
        # Hapus semua karakter non-angka
        raw = "".join(filter(str.isdigit, self.var_tgl_lahir.get()))
        # Batasi panjang maksimal 8 digit (DDMMYYYY)
        raw = raw[:8]
        
        formatted = ""
        if len(raw) > 0:
            formatted += raw[:2]
        if len(raw) > 2:
            formatted += "-" + raw[2:4]
        if len(raw) > 4:
            formatted += "-" + raw[4:]

        if self.var_tgl_lahir.get() != formatted:
            self.var_tgl_lahir.set(formatted)
            # Kembalikan kursor ke posisi paling belakang
            self.after(10, lambda: self.entry_tgl.icursor(tk.END))

    def _buat_tampilan_biodata(self):
        # --- Variabel Kontrol Tkinter ---
        self.var_nama = tk.StringVar()
        self.var_nim = tk.StringVar()
        self.var_jurusan = tk.StringVar()
        self.var_tgl_lahir = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_telepon = tk.StringVar()
        self.var_jk = tk.StringVar(value="Pria")
        self.var_setuju = tk.IntVar()

        # Aktifkan trace untuk validasi real-time dan auto-formatting
        self.var_tgl_lahir.trace_add("write", self.format_tanggal_otomatis)
        
        self.var_nama.trace_add("write", self.validate_form)
        self.var_nim.trace_add("write", self.validate_form)
        self.var_jurusan.trace_add("write", self.validate_form)
        self.var_tgl_lahir.trace_add("write", self.validate_form)
        self.var_email.trace_add("write", self.validate_form)
        self.var_telepon.trace_add("write", self.validate_form)

        # --- Frame Biodata ---
        self.frame_biodata = tk.Frame(master=self, padx=20, pady=20)
        self.frame_biodata.columnconfigure(1, weight=1)

        # Judul
        self.label_judul = tk.Label(
            master=self.frame_biodata,
            text="FORM BIODATA MAHASISWA",
            font=("Arial", 16, "bold")
        )
        self.label_judul.grid(row=0, column=0, columnspan=2, pady=20)

        # Frame khusus untuk input dengan border
        self.frame_input = tk.Frame(
            master=self.frame_biodata,
            relief=tk.GROOVE,
            borderwidth=2,
            padx=10,
            pady=10,
        )
        self.frame_input.grid(row=1, column=0, columnspan=2, sticky="EW")

        # Input Nama (row 0)
        self.label_nama = tk.Label(
            master=self.frame_input, text="Nama Lengkap:", font=("Arial", 12)
        )
        self.label_nama.grid(row=0, column=0, sticky="W", pady=2)
        self.entry_nama = tk.Entry(
            master=self.frame_input, width=30, font=("Arial", 12),
            textvariable=self.var_nama,
        )
        self.entry_nama.grid(row=0, column=1, pady=2, sticky="W")

        # Input NIM (row 1-2)
        self.label_nim = tk.Label(
            master=self.frame_input, text="NIM:", font=("Arial", 12)
        )
        self.label_nim.grid(row=1, column=0, sticky="W", pady=2)
        self.entry_nim = tk.Entry(
            master=self.frame_input, width=30, font=("Arial", 12),
            textvariable=self.var_nim,
        )
        self.entry_nim.grid(row=1, column=1, pady=2, sticky="W")
        self.hint_nim = tk.Label(
            master=self.frame_input, text="NIM harus berisi angka",
            font=("Arial", 8), fg="gray"
        )
        self.hint_nim.grid(row=2, column=1, sticky="W")

        # Input Jurusan (row 3)
        self.label_jurusan = tk.Label(
            master=self.frame_input, text="Jurusan:", font=("Arial", 12)
        )
        self.label_jurusan.grid(row=3, column=0, sticky="W", pady=2)
        self.entry_jurusan = tk.Entry(
            master=self.frame_input, width=30, font=("Arial", 12),
            textvariable=self.var_jurusan,
        )
        self.entry_jurusan.grid(row=3, column=1, pady=2, sticky="W")

        # --- Input Tanggal Lahir (row 4-5) ---
        self.label_tgl = tk.Label(
            master=self.frame_input, text="Tanggal Lahir:", font=("Arial", 12)
        )
        self.label_tgl.grid(row=4, column=0, sticky="W", pady=2)
        self.entry_tgl = tk.Entry(
            master=self.frame_input, width=30, font=("Arial", 12),
            textvariable=self.var_tgl_lahir,
        )
        self.entry_tgl.grid(row=4, column=1, pady=2, sticky="W")
        self.hint_tgl = tk.Label(
            master=self.frame_input, text="Format: DD-MM-YYYY (Contoh: 17-08-2004)",
            font=("Arial", 8), fg="gray"
        )
        self.hint_tgl.grid(row=5, column=1, sticky="W")

        # --- Input Email (row 6-7) ---
        self.label_email = tk.Label(
            master=self.frame_input, text="Email:", font=("Arial", 12)
        )
        self.label_email.grid(row=6, column=0, sticky="W", pady=2)
        self.entry_email = tk.Entry(
            master=self.frame_input, width=30, font=("Arial", 12),
            textvariable=self.var_email,
        )
        self.entry_email.grid(row=6, column=1, pady=2, sticky="W")
        self.hint_email = tk.Label(
            master=self.frame_input, text="Contoh: nama@email.com",
            font=("Arial", 8), fg="gray"
        )
        self.hint_email.grid(row=7, column=1, sticky="W")

        # --- Input Telepon (row 8-9) ---
        self.label_telepon = tk.Label(
            master=self.frame_input, text="No. Telepon:", font=("Arial", 12)
        )
        self.label_telepon.grid(row=8, column=0, sticky="W", pady=2)
        self.entry_telepon = tk.Entry(
            master=self.frame_input, width=30, font=("Arial", 12),
            textvariable=self.var_telepon,
        )
        self.entry_telepon.grid(row=8, column=1, pady=2, sticky="W")
        self.hint_telepon = tk.Label(
            master=self.frame_input, text="Contoh: 081234567890 atau +6281234567890",
            font=("Arial", 8), fg="gray"
        )
        self.hint_telepon.grid(row=9, column=1, sticky="W")

        # Teks petunjuk bawaan, dipakai saat field kosong / valid
        self.hint_default = {
            self.hint_nim: "NIM harus berisi angka",
            self.hint_tgl: "Format: DD-MM-YYYY (Contoh: 17-08-2004)",
            self.hint_email: "Contoh: nama@email.com",
            self.hint_telepon: "Contoh: 081234567890 atau +6281234567890",
        }

        # Input alamat dengan Text widget (row 10)
        self.label_alamat = tk.Label(
            master=self.frame_input, text="Alamat:", font=("Arial", 12)
        )
        self.label_alamat.grid(row=10, column=0, sticky="NW", pady=2)

        # Frame untuk Text dan Scrollbar
        self.frame_alamat = tk.Frame(
            master=self.frame_input, relief=tk.SUNKEN, borderwidth=1
        )
        self.frame_alamat.grid(row=10, column=1, pady=2, sticky="W")

        # Scrollbar untuk alamat
        self.scrollbar_alamat = tk.Scrollbar(master=self.frame_alamat)
        self.scrollbar_alamat.pack(side=tk.RIGHT, fill=tk.Y)

        # Text widget untuk alamat
        self.text_alamat = tk.Text(
            master=self.frame_alamat, height=5, width=28, font=("Arial", 12)
        )
        self.text_alamat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Hubungkan scrollbar dengan text
        self.scrollbar_alamat.config(command=self.text_alamat.yview)
        self.text_alamat.config(yscrollcommand=self.scrollbar_alamat.set)

        # Jenis kelamin (row 11)
        self.label_jk = tk.Label(
            master=self.frame_input, text="Jenis Kelamin:", font=("Arial", 12)
        )
        self.label_jk.grid(row=11, column=0, sticky="W", pady=2)

        self.frame_jk = tk.Frame(master=self.frame_input)
        self.frame_jk.grid(row=11, column=1, sticky="W")

        self.radio_pria = tk.Radiobutton(
            master=self.frame_jk, text="Pria", variable=self.var_jk, value="Pria"
        )
        self.radio_pria.pack(side=tk.LEFT)

        self.radio_wanita = tk.Radiobutton(
            master=self.frame_jk, text="Wanita", variable=self.var_jk, value="Wanita"
        )
        self.radio_wanita.pack(side=tk.LEFT)

        # Checkbox persetujuan (row 12)
        self.check_setuju = tk.Checkbutton(
            master=self.frame_input,
            text="Saya menyetujui pengumpulan data ini.",
            variable=self.var_setuju,
            font=("Arial", 10),
            command=self.validate_form,
        )
        self.check_setuju.grid(row=12, column=0, columnspan=2, pady=10, sticky="W")

        # --- Frame tombol: Submit + Reset Form ---
        self.frame_tombol = tk.Frame(master=self.frame_biodata)
        self.frame_tombol.grid(row=6, column=0, columnspan=2, pady=20, sticky="EW")
        self.frame_tombol.columnconfigure(0, weight=3)
        self.frame_tombol.columnconfigure(1, weight=1)

        # Tombol submit
        self.btn_submit = tk.Button(
            master=self.frame_tombol,
            text="Submit Biodata",
            font=("Arial", 12, "bold"),
            command=self.submit_data,
            state=tk.DISABLED,
        )
        self.btn_submit.grid(row=0, column=0, sticky="EW", padx=(0, 5))

        # --- Tombol Reset Form ---
        self.btn_reset = tk.Button(
            master=self.frame_tombol,
            text="Reset Form",
            font=("Arial", 12),
            command=self.reset_form_konfirmasi,
        )
        self.btn_reset.grid(row=0, column=1, sticky="EW", padx=(5, 0))

        # Event bindings untuk hover dan keyboard shortcuts
        self.btn_submit.bind("<Enter>", self.on_enter)
        self.btn_submit.bind("<Leave>", self.on_leave)

        # Keyboard shortcuts: Enter pindah ke kolom berikutnya
        self._atur_enter_antar_kolom()

        # Label hasil
        self.label_hasil = tk.Label(
            master=self.frame_biodata, text="", font=("Arial", 12, "italic"), justify=tk.LEFT
        )
        self.label_hasil.grid(row=7, column=0, columnspan=2, sticky="W", padx=10)

        # CATATAN: menu TIDAK dibuat di sini.
        # Menu dibuat di _coba_login supaya muncul setiap kali login berhasil
        # (dan tidak muncul di halaman login).

    # ENTER = PINDAH KOLOM
    def _atur_enter_antar_kolom(self):
        """Menambahkan listener pada keyboard (Enter) untuk perpindahan navigasi antar field."""
        urutan = [
            self.entry_nama,
            self.entry_nim,
            self.entry_jurusan,
            self.entry_tgl,
            self.entry_email,
            self.entry_telepon,
            self.text_alamat,
            self.check_setuju,
        ]
        for sekarang, berikutnya in zip(urutan, urutan[1:]):
            sekarang.bind("<Return>", lambda e, tujuan=berikutnya: self._fokus_ke(tujuan))

        # Di kolom alamat, Shift+Enter tetap membuat baris baru
        # (handler kosong, jadi perilaku bawaan Text widget tetap jalan)
        self.text_alamat.bind("<Shift-Return>", lambda e: None)

        # Di checkbox persetujuan, Enter = submit (hanya jika form sudah lengkap)
        self.check_setuju.bind("<Return>", self.submit_shortcut)

    def _fokus_ke(self, widget):
        """Memaksa pindah kursor ke elemen berikutnya dan menghentikan event default dari sistem."""
        widget.focus_set()
        return "break"

    # NAVIGASI ANTAR TAMPILAN
    def _pindah_ke(self, frame_tujuan):
        """Menghapus tampilan frame saat ini dan merender frame layar yang baru."""
        if self.frame_aktif is not None:
            self.frame_aktif.pack_forget()

        self.frame_aktif = frame_tujuan
        self.frame_aktif.pack(fill=tk.BOTH, expand=True)

        # Auto-focus berdasarkan frame yang ditampilkan
        if frame_tujuan == self.frame_login:
            # Jika username sudah terisi (Remember Me), langsung fokus ke password
            if self.entry_username.get().strip():
                self.after(100, lambda: self.entry_password.focus_set())
            else:
                self.after(100, lambda: self.entry_username.focus_set())
        elif frame_tujuan == self.frame_biodata:
            self.after(100, lambda: self.entry_nama.focus_set())

    # LOGIKA FORM BIODATA
    def validate_form(self, *args):
        """Mengecek seluruh aturan validasi form secara langsung tiap ada perubahan teks."""
        nama_valid = self.var_nama.get().strip() != ""
        nim_valid = self.var_nim.get().strip() != ""
        jurusan_valid = self.var_jurusan.get().strip() != ""
        setuju_valid = self.var_setuju.get() == 1

        tgl_text = self.var_tgl_lahir.get()
        email_text = self.var_email.get()
        telepon_text = self.var_telepon.get()

        err_nim = pesan_error_nim(self.var_nim.get())
        err_tgl = pesan_error_tanggal(tgl_text)
        err_email = pesan_error_email(email_text)
        err_telepon = pesan_error_telepon(telepon_text)

        # Tampilkan pesan error (merah) atau petunjuk default (abu-abu)
        self._tampilkan_hint(self.hint_nim, err_nim)
        self._tampilkan_hint(self.hint_tgl, err_tgl)
        self._tampilkan_hint(self.hint_email, err_email)
        self._tampilkan_hint(self.hint_telepon, err_telepon)

        tgl_valid = tgl_text.strip() != "" and not err_tgl
        email_valid = email_text.strip() != "" and not err_email
        telepon_valid = telepon_text.strip() != "" and not err_telepon

        if (nama_valid and nim_valid and jurusan_valid and tgl_valid
                and email_valid and telepon_valid and setuju_valid):
            self.btn_submit.config(state=tk.NORMAL)
        else:
            self.btn_submit.config(state=tk.DISABLED)

    def _tampilkan_hint(self, label, pesan_error):
        """Menangani peringatan teks di bawah input box: merah untuk salah, abu-abu untuk standar."""
        if pesan_error:
            label.config(text=pesan_error, fg="red")
        else:
            label.config(text=self.hint_default[label], fg="gray")

    def on_enter(self, event):
        self.btn_submit.config(bg="lightgreen")

    def on_leave(self, event):
        self.btn_submit.config(bg=self.warna_default)

    def submit_shortcut(self, event):
        # Tombol Enter hanya memproses submit bila form sudah lengkap
        if str(self.btn_submit.cget("state")) == "normal":
            self.submit_data()

    # Optimasi Validasi dan Pengalaman Pengguna (UX)
    
    def submit_data(self):
        """Mengeksekusi pengiriman data final setelah semua input dipastikan memenuhi kriteria."""
        try:
            # Cek checkbox
            if self.var_setuju.get() == 0:
                messagebox.showwarning("Peringatan", "Anda harus menyetujui pengumpulan data!")
                return

            # Ambil data dari form
            nama = self.entry_nama.get().strip()
            nim = self.entry_nim.get().strip()
            jurusan = self.entry_jurusan.get().strip()
            tgl_lahir = self.entry_tgl.get().strip()
            email = self.entry_email.get().strip()
            telepon = normalisasi_telepon(self.entry_telepon.get())
            alamat = self.text_alamat.get("1.0", tk.END).strip()
            jenis_kelamin = self.var_jk.get()

            # Validasi field kosong
            if not nama or not nim or not jurusan or not tgl_lahir or not email or not telepon:
                messagebox.showwarning(
                    "Input Kosong",
                    "Nama, NIM, Jurusan, Tanggal Lahir, Email, dan Telepon harus diisi!"
                )
                return

            if not nim.isdigit() or len(nim) < 8:
                pesan = [
                    "NIM harus berupa angka minimal 8 digit!",
                    "Loh awas ! isi yang betul !"
                ]
                messagebox.showwarning("Format NIM Salah", random.choice(pesan))
                self.entry_nim.focus_set()
                return

            # Validasi nama (tidak boleh hanya angka)
            if nama.isdigit():
                messagebox.showwarning("Format Nama Salah", "Nama tidak boleh hanya berupa angka!")
                self.entry_nama.focus_set()
                return

            # Validasi tanggal lahir
            err_tgl = pesan_error_tanggal(tgl_lahir)
            if err_tgl:
                messagebox.showwarning("Tanggal Lahir Salah", err_tgl)
                self.entry_tgl.focus_set()
                return

            # Validasi email
            err_email = pesan_error_email(email)
            if err_email:
                messagebox.showwarning("Email Salah", err_email)
                self.entry_email.focus_set()
                return

            # Validasi telepon
            err_telepon = pesan_error_telepon(telepon)
            if err_telepon:
                messagebox.showwarning("Nomor Telepon Salah", err_telepon)
                self.entry_telepon.focus_set()
                return

            # Standarisasi tanggal ke format DD-MM-YYYY
            tgl_obj = parse_tanggal(tgl_lahir)
            tgl_tampil = tgl_obj.strftime("%d-%m-%Y")

            # Tampilkan hasil
            hasil = (
                f"Nama: {nama}\n"
                f"NIM: {nim}\n"
                f"Jurusan: {jurusan}\n"
                f"Tanggal Lahir: {tgl_tampil}\n"
                f"Email: {email}\n"
                f"Telepon: {telepon}\n"
                f"Alamat: {alamat}\n"
                f"Jenis Kelamin: {jenis_kelamin}"
            )
            messagebox.showinfo("Data Tersimpan", hasil)

            # Tampilkan hasil di label dengan info user
            hasil_lengkap = f"BIODATA TERSIMPAN:\nDiinput oleh: {self.current_user}\n\n{hasil}"
            self.label_hasil.config(text=hasil_lengkap)

            # Log successful data submission
            logging.info(f"Data submitted by user: {self.current_user} - NIM: {nim}")

        except Exception as e:
            logging.error(f"Error in submit_data by {self.current_user}: {str(e)}")
            messagebox.showerror("Error", f"Terjadi kesalahan saat memproses data:\n{str(e)}")

    # FITUR: RESET FORM
    def reset_form_konfirmasi(self):
        """Memunculkan pop-up konfirmasi sebelum membersihkan form pendaftaran."""
        if messagebox.askyesno("Reset Form", "Semua isian form akan dihapus. Lanjutkan?"):
            self._reset_form_biodata()
            logging.info(f"Form biodata di-reset oleh user: {self.current_user}")
            self.entry_nama.focus_set()

    def _reset_form_biodata(self):
        """Mengembalikan seluruh field di form registrasi ke keadaan semula (kosong/default)."""
        self.var_nama.set("")
        self.var_nim.set("")
        self.var_jurusan.set("")
        self.var_tgl_lahir.set("")
        self.var_email.set("")
        self.var_telepon.set("")
        self.text_alamat.delete("1.0", tk.END)
        self.var_jk.set("Pria")
        self.var_setuju.set(0)
        self.label_hasil.config(text="")
        # Perbarui status tombol submit & pesan petunjuk
        self.validate_form()

    
    def simpan_hasil(self):
        """Mengekspor data biodata yang telah disubmit ke dalam bentuk dokumen teks dengan aman."""
        try:
            hasil_tersimpan = self.label_hasil.cget("text")

            if not hasil_tersimpan or "BIODATA TERSIMPAN" not in hasil_tersimpan:
                messagebox.showwarning("Peringatan", "Tidak ada data untuk disimpan. Mohon submit terlebih dahulu.")
                return

            # Buat nama file dengan timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"biodata_{self.current_user}_{timestamp}.txt"

            with open(filename, "w", encoding="utf-8") as file:
                file.write(f"Data disimpan oleh: {self.current_user}\n")
                file.write(f"Waktu penyimpanan: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write("-" * 50 + "\n")
                file.write(hasil_tersimpan)

            messagebox.showinfo("Info", f"Data berhasil disimpan ke file '{filename}'.")

        except PermissionError:
            messagebox.showerror("Error", "Tidak memiliki izin untuk menyimpan file di lokasi ini.")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan saat menyimpan file:\n{str(e)}")

    # LOGIN / LOGOUT
    def _coba_login(self):
        """Mengelola mekanisme percobaan masuk aplikasi menggunakan pencocokan username/password."""
        username = self.entry_username.get().strip()
        password = self.entry_password.get()

        # Log attempt login
        logging.info(f"Login attempt for username: {username}")

        # Validasi input kosong
        if not username or not password:
            logging.warning(f"Empty credentials attempt for username: {username}")
            messagebox.showwarning("Login Gagal", "Username dan Password tidak boleh kosong.")
            self.entry_username.focus_set()
            return

        # Validasi panjang minimum
        if len(username) < 3:
            logging.warning(f"Username too short: {username}")
            messagebox.showwarning("Login Gagal", "Username minimal 3 karakter.")
            self.entry_username.focus_set()
            return

        # Cek kredensial di database
        if username in self.users_db and self.users_db[username] == password:
            self.current_user = username
            logging.info(f"Successful login for user: {username}")
            messagebox.showinfo("Login Berhasil", f"Selamat Datang, {username}!")

            # Remember Me: simpan atau hapus username terakhir
            if self.var_remember.get() == 1:
                self._simpan_username(username)
            else:
                self._hapus_username_tersimpan()

            self._reset_form_biodata()
            self._update_title_with_user()
            self._atur_background_user()   # ubah warna sesuai user
            self._buat_menu()              # tampilkan menu setelah login
            self._pindah_ke(self.frame_biodata)
            # Bersihkan field login setelah berhasil
            self.entry_username.delete(0, tk.END)
            self.entry_password.delete(0, tk.END)
            self._sembunyikan_password()
        else:
            logging.warning(f"Failed login attempt for username: {username}")
            messagebox.showerror("Login Gagal", "Username atau Password salah.")
            # Bersihkan password dan focus ke username
            self.entry_password.delete(0, tk.END)
            self.entry_username.focus_set()

    def _update_title_with_user(self):
        """Mengganti teks pada title bar jendela aplikasi sesuai dengan akun aktif."""
        if self.current_user:
            self.title(f"Aplikasi Biodata Mahasiswa - User: {self.current_user}")
        else:
            self.title("Aplikasi Biodata Mahasiswa")

    def _logout(self):
        """Mengakhiri sesi pengguna yang aktif dan memunculkan kembali layar otentikasi."""
        if messagebox.askyesno("Logout", f"Apakah {self.current_user} yakin ingin logout?"):
            logging.info(f"User logout: {self.current_user}")
            # Reset status user
            self.current_user = None
            # Kembalikan warna ke default
            self._atur_background_user()
            # Hapus menu
            self._hapus_menu()
            # Update title
            self._update_title_with_user()
            # Bersihkan field login
            self.entry_username.delete(0, tk.END)
            self.entry_password.delete(0, tk.END)
            self._sembunyikan_password()
            # Isi ulang username jika Remember Me aktif
            self._muat_username_tersimpan()
            # Reset form biodata
            self._reset_form_biodata()
            # Kembali ke halaman login
            self._pindah_ke(self.frame_login)

    # MENU
    
    def _buat_menu(self):
        """Membangun menu navigasi di bagian atas jendela aplikasi."""
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)

        file_menu = tk.Menu(master=menu_bar, tearoff=0)
        file_menu.add_command(label="Simpan Hasil", command=self.simpan_hasil)
        file_menu.add_command(label="Reset Form", command=self.reset_form_konfirmasi)
        file_menu.add_separator()
        file_menu.add_command(label="Logout", command=self._logout)
        file_menu.add_separator()
        file_menu.add_command(label="Keluar", command=self.keluar_aplikasi)
        menu_bar.add_cascade(label="File", menu=file_menu)

    def _hapus_menu(self):
        """Menghilangkan menu atas saat user kembali ke layar login."""
        empty_menu = tk.Menu(self)
        self.config(menu=empty_menu)

    
    def keluar_aplikasi(self):
        """Memastikan keinginan user sebelum menutup total aplikasi."""
        if messagebox.askokcancel("Keluar", "Apakah Anda yakin ingin keluar dari aplikasi?"):
            logging.info(f"Application closed by user: {self.current_user}")
            self.destroy()

    # BACKGROUND PER USER
    def _atur_background_user(self):
        """Mengaplikasikan perubahan warna tema secara menyeluruh berdasar hak akses user saat ini."""
        warna = self.warna_user.get(self.current_user, self.warna_default)

        self.frame_biodata.config(bg=warna)
        self.frame_input.config(bg=warna)
        self.frame_jk.config(bg=warna)
        self.frame_alamat.config(bg=warna)
        self.frame_tombol.config(bg=warna)

        for w in (self.label_judul, self.label_nama, self.label_nim,
                  self.label_jurusan, self.label_tgl, self.label_email,
                  self.label_telepon, self.label_alamat, self.label_jk,
                  self.label_hasil, self.radio_pria, self.radio_wanita,
                  self.check_setuju, self.hint_nim, self.hint_tgl, self.hint_email,
                  self.hint_telepon):
            w.config(bg=warna)


# Blok berikut hanya akan dieksekusi jika file ini dijalankan secara langsung
if __name__ == "__main__":
    # Membuat instance dari kelas aplikasi kita
    app = AplikasiBiodata()
    # Menjalankan mainloop dari instance tersebut
    app.mainloop()
    app.mainloop()
