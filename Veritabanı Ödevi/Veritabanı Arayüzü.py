import tkinter as tk
from tkinter import ttk, messagebox 
import psycopg2
import os
import subprocess

# ===== VERİTABANI FONKSİYONLARI =====
def run_query(query, params=None):
   
    conn =  psycopg2.connect(
        host="",
        database="yemek",   # <-- DEĞİŞTİR
        user="",            # <-- DEĞİŞTİR
        password=""             # <-- DEĞİŞTİR
    )
    cur = conn.cursor()
    cur.execute(query, params)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

def run_commit(query, params=None):
    conn =  psycopg2.connect(
        host="",
        database="yemek",   
        user="",            
        password=""             
    )
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    cur.close()
    conn.close()

# ===== ANA UYGULAMA =====
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Yemek Tarif Sitesi")
        self.geometry("1400x700")

        # ---------- ÜYE ARAMA ----------
        frm_uye_ara = tk.Frame(self)
        frm_uye_ara.grid(row=0, column=0, columnspan=3, pady=8, sticky="w")
        tk.Label(frm_uye_ara, text="Üye Ara (Ad Soyad):").grid(row=0, column=0, padx=5)
        self.ent_uye_ara = tk.Entry(frm_uye_ara, width=30)
        self.ent_uye_ara.grid(row=0, column=1, padx=5)
        tk.Button(frm_uye_ara, text="Sorgula", command=self.uye_sorgula).grid(row=0, column=2, padx=5)

        self.txt_uye = tk.Text(self, width=60, height=5)
        self.txt_uye.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=5)

        # ---------- SOL VE SAĞ FRAME ----------
        frame_sol = tk.Frame(self)
        frame_sol.grid(row=2, column=0, padx=10, pady=10, sticky="nw")

        frame_sag = tk.Frame(self)
        frame_sag.grid(row=2, column=1, padx=20, pady=10, sticky="n")

        # ---------- SOL FRAME ----------
        tk.Label(frame_sol, text="Bölge").grid(row=0, column=0, sticky="w")
        self.cmb_bolge = ttk.Combobox(frame_sol, width=30, state="readonly")
        self.cmb_bolge.grid(row=0, column=1, sticky="w")
        self.cmb_bolge.bind("<<ComboboxSelected>>", self.bolge_secildi)

        tk.Label(frame_sol, text="Kategori").grid(row=1, column=0, sticky="w")
        self.cmb_kategori = ttk.Combobox(frame_sol, width=30)
        self.cmb_kategori.grid(row=1, column=1, sticky="w")
        self.cmb_kategori.bind("<<ComboboxSelected>>", self.yemekleri_yukle)

        tk.Label(frame_sol, text="Yemek").grid(row=2, column=0, sticky="w")
        self.cmb_yemek = ttk.Combobox(frame_sol, width=30)
        self.cmb_yemek.grid(row=2, column=1, sticky="w")
        self.cmb_yemek.bind("<<ComboboxSelected>>", self.tarif_adlarini_yukle)

        tk.Label(frame_sol, text="Tarif Adı").grid(row=3, column=0, sticky="w")
        self.cmb_tarif_adi = ttk.Combobox(frame_sol, width=30)
        self.cmb_tarif_adi.grid(row=3, column=1, sticky="w")
        self.cmb_tarif_adi.bind("<<ComboboxSelected>>", self.tarifi_yukle)

        tk.Label(frame_sol, text="Tarif Yapılışı").grid(row=4, column=0, sticky="nw")
        self.txt_tarif = tk.Text(frame_sol, width=60, height=12)
        self.txt_tarif.grid(row=4, column=1, pady=(5, 5), sticky="w")
        
        # ----------- RESİMLER -------------
        self.lbl_resimler = tk.Label(frame_sol, text="Resimler")
        self.lbl_resimler.grid(row=5, column=0, sticky="nw", pady=(5,0))

        link_font = ("Arial", 10, "underline")
        link_fg = "blue"

        self.lst_resimler = tk.Listbox(
            frame_sol,
            height=4,
            width=60,
            fg=link_fg,
            font=link_font,
            cursor="hand2"
        )
        
        self.lst_resimler.grid(row=5, column=1, sticky="w", pady=(5,10))  
        self.lst_resimler.bind("<Double-Button-1>", self.open_image)     


        self.lbl_ortalama = tk.Label(frame_sol, text="Ortalama Puan: —", font=("Arial", 10, "bold"))
        self.lbl_ortalama.grid(row=6, column=0, columnspan=2, pady=(8,8), sticky="w")   
        tk.Label(frame_sol, text="Yorumlar").grid(row=7, column=0, sticky="w")
        self.tree_yorum = ttk.Treeview(frame_sol, columns=("ad","yorum","puan"), show="headings", height=6)
        self.tree_yorum.heading("ad", text="Ad Soyad")
        self.tree_yorum.heading("yorum", text="Yorum")
        self.tree_yorum.heading("puan", text="Puan")
        self.tree_yorum.column("ad", width=120)
        self.tree_yorum.column("yorum", width=350)
        self.tree_yorum.column("puan", width=60, anchor="center")
        self.tree_yorum.grid(row=7, column=1, pady=5, sticky="w")   
        # ---------- SAĞ FRAME ----------
        tk.Label(frame_sag, text="Malzemeye Göre Ara").grid(row=0, column=0, sticky="w")
        self.ent_malzeme = tk.Entry(frame_sag, width=30)
        self.ent_malzeme.grid(row=0, column=1, sticky="w")
        tk.Button(frame_sag, text="Ara", command=self.malzeme_ara).grid(row=0, column=2, padx=5)    
        self.lst_sonuc = tk.Listbox(frame_sag, width=45, height=10)
        self.lst_sonuc.grid(row=1, column=0, columnspan=3, pady=10)

    ## Yorum ekleme alanı sağ frame içinde
        tk.Label(frame_sag, text="Ad Soyad").grid(row=2, column=0, sticky="w")
        self.entry_adsoyad = tk.Entry(frame_sag, width=30)
        self.entry_adsoyad.grid(row=2, column=1, sticky="w")

        tk.Label(frame_sag, text="Yorum").grid(row=3, column=0, sticky="nw")
        self.txt_yorum = tk.Text(frame_sag, width=30, height=4)
        self.txt_yorum.grid(row=3, column=1, pady=5)

        tk.Label(frame_sag, text="Puan").grid(row=4, column=0, sticky="w")
        self.spin_puan = tk.Spinbox(frame_sag, from_=1, to=5)
        self.spin_puan.grid(row=4, column=1, sticky="w")

        tk.Button(frame_sag, text="Yorum Ekle", command=self.yorum_ekle).grid(row=4, column=2, sticky="w", pady=8)

        # --- Sağ: Yeni Üye ve Bilgi Güncelleme (Yorum Ekleme Altında) ---
        self.frm_alt = tk.Frame(self, bd=2, relief=tk.RIDGE, padx=10, pady=10)
        self.frm_alt.place(x=640, y=550, width=480, height=200)

        # Sol alt: Yeni Üye
        self.frm_yeni = tk.Frame(self.frm_alt, bd=2, relief=tk.RIDGE, padx=5, pady=5)
        self.frm_yeni.place(x=0, y=0, width=230, height=190)
        tk.Label(self.frm_yeni, text="Yeni Üye Kayıt").grid(row=0, column=0, columnspan=2)

        tk.Label(self.frm_yeni, text="Ad:").grid(row=1, column=0, sticky=tk.E)
        self.entry_yeni_ad = tk.Entry(self.frm_yeni)
        self.entry_yeni_ad.grid(row=1, column=1)

        tk.Label(self.frm_yeni, text="Soyad:").grid(row=2, column=0, sticky=tk.E)
        self.entry_yeni_soyad = tk.Entry(self.frm_yeni)
        self.entry_yeni_soyad.grid(row=2, column=1)

        tk.Label(self.frm_yeni, text="Email:").grid(row=3, column=0, sticky=tk.E)
        self.entry_yeni_email = tk.Entry(self.frm_yeni)
        self.entry_yeni_email.grid(row=3, column=1)

        tk.Label(self.frm_yeni, text="Şifre:").grid(row=4, column=0, sticky=tk.E)
        self.entry_yeni_sifre = tk.Entry(self.frm_yeni, show="*")
        self.entry_yeni_sifre.grid(row=4, column=1)

        tk.Button(self.frm_yeni, text="Kaydet", command=self.uye_kayit).grid(row=5, column=0, columnspan=2, pady=5)

        # Sağ alt: Bilgi Güncelleme
        self.frm_guncelle = tk.Frame(self.frm_alt, bd=2, relief=tk.RIDGE, padx=5, pady=5)
        self.frm_guncelle.place(x=240, y=0, width=230, height=190)
        tk.Label(self.frm_guncelle, text="Bilgi Güncelleme").grid(row=0, column=0, columnspan=2)

        tk.Label(self.frm_guncelle, text="Ad:").grid(row=1, column=0, sticky=tk.E)
        self.entry_guncelle_ad = tk.Entry(self.frm_guncelle)
        self.entry_guncelle_ad.grid(row=1, column=1)

        tk.Label(self.frm_guncelle, text="Soyad:").grid(row=2, column=0, sticky=tk.E)
        self.entry_guncelle_soyad = tk.Entry(self.frm_guncelle)
        self.entry_guncelle_soyad.grid(row=2, column=1)

        tk.Label(self.frm_guncelle, text="Şifre:").grid(row=3, column=0, sticky=tk.E)
        self.entry_guncelle_sifre = tk.Entry(self.frm_guncelle, show="*")
        self.entry_guncelle_sifre.grid(row=3, column=1)

        tk.Label(self.frm_guncelle, text="Yeni Email:").grid(row=4, column=0, sticky=tk.E)
        self.entry_guncelle_email = tk.Entry(self.frm_guncelle)
        self.entry_guncelle_email.grid(row=4, column=1)

        tk.Button(self.frm_guncelle, text="Güncelle", command=self.uye_guncelle).grid(row=5, column=0, columnspan=2, pady=5)

                # --- Sağ: Admin Yönetim Paneli ---
        self.frm_admin = tk.Frame(self, bd=2, relief=tk.RIDGE, padx=10, pady=10)
        self.frm_admin.place(x=1120, y=0, width=440, height=750)

        # Tüm Üyeler
        self.frm_uyeler = tk.LabelFrame(self.frm_admin, text="Tüm Üyeler", padx=5, pady=5)
        self.frm_uyeler.pack(fill="both", expand=True, pady=5)

        self.tree_uyeler = ttk.Treeview(self.frm_uyeler, columns=("id","ad","soyad","email"), show="headings", height=6)
        self.tree_uyeler.heading("id", text="ID")
        self.tree_uyeler.heading("ad", text="Ad")
        self.tree_uyeler.heading("soyad", text="Soyad")
        self.tree_uyeler.heading("email", text="Email")
        self.tree_uyeler.column("id", width=30, anchor="center")
        self.tree_uyeler.column("ad", width=100)
        self.tree_uyeler.column("soyad", width=100)
        self.tree_uyeler.column("email", width=150)
        self.tree_uyeler.pack(fill="both", expand=True, pady=5)

        tk.Button(self.frm_uyeler, text="Yenile", command=self.uyeleri_yukle).pack(pady=5)

        # Üye Yorumları Yönetimi (Admin ve Üye)
        self.frm_yorumlar = tk.LabelFrame(self.frm_admin, text="Üye Yorumları", padx=5, pady=5)
        self.frm_yorumlar.pack(fill="both", expand=True, pady=5)

        tk.Label(self.frm_yorumlar, text="Ad Soyad:").grid(row=0, column=0, sticky=tk.E)
        self.entry_yorum_adsoyad = tk.Entry(self.frm_yorumlar)
        self.entry_yorum_adsoyad.grid(row=0, column=1)

        tk.Button(self.frm_yorumlar, text="Göster", command=self.yorumlari_goster).grid(row=0, column=2, padx=5)

        self.tree_yorumlar = ttk.Treeview(self.frm_yorumlar, columns=("tarif","yorum","puan"), show="headings", height=6)
        self.tree_yorumlar.heading("tarif", text="Tarif")
        self.tree_yorumlar.heading("yorum", text="Yorum")
        self.tree_yorumlar.heading("puan", text="Puan")
        self.tree_yorumlar.column("tarif", width=120)
        self.tree_yorumlar.column("yorum", width=180)
        self.tree_yorumlar.column("puan", width=50, anchor="center")
        self.tree_yorumlar.grid(row=1, column=0, columnspan=3, pady=5)

        tk.Button(self.frm_yorumlar, text="Seçili Yorum Sil", command=self.yorumu_sil).grid(row=2, column=0, columnspan=3, pady=5)


        # ---------- İNİT VERİLER ----------
        self.bolgeleri_yukle()
        self.kategorileri_yukle()
        self.secili_kisi_id = None

    def open_image(self, event):
        selection = self.lst_resimler.curselection()
        if not selection:
            return

        resim_adi = self.lst_resimler.get(selection[0]).strip()

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        resim_yolu = os.path.join(BASE_DIR, "resimler", resim_adi)

        print("Resim yolu:", resim_yolu)

        if not os.path.exists(resim_yolu):
            messagebox.showerror("Hata", f"{resim_yolu} bulunamadı.")
            return

        try:
            if os.name == "nt":
                os.startfile(resim_yolu)
            elif sys.platform == "darwin":
                subprocess.call(["open", resim_yolu])
            else:
                subprocess.call(["xdg-open", resim_yolu])
        except Exception as e:
            messagebox.showerror("Hata", f"Resim açılamadı: {e}")

    # ===== FONKSİYONLAR =====
   
    
    # --- Tüm üyeleri yükle ---
    def uyeleri_yukle(self):
        for i in self.tree_uyeler.get_children():
            self.tree_uyeler.delete(i)
        rows = run_query("""SELECT "kisino", ad, soyad, email FROM "kisi" ORDER BY "kisino" DESC""")
        for r in rows:
            self.tree_uyeler.insert("", "end", values=r)
    
    # --- Yorumları göster ---
    def yorumlari_goster(self):
        adsoyad = self.entry_yorum_adsoyad.get().strip()
        if " " not in adsoyad:
            messagebox.showwarning("Uyarı", "Ad ve Soyad girin!")
            return
        ad, soyad = adsoyad.split(" ", 1)
    
        row = run_query("""SELECT kisino FROM kisi WHERE ad=%s AND soyad=%s""", (ad, soyad))
        if not row:
            messagebox.showinfo("Bilgi", "Kullanıcı bulunamadı!")
            return
        kisino = row[0][0]
    
        for i in self.tree_yorumlar.get_children():
            self.tree_yorumlar.delete(i)
    
        yorumlar = run_query("""
            SELECT t.tarif_adi, y.yorum_metni, y.puan, y."Yorum_id"
            FROM "Yorum" y
            JOIN "Tarif" t ON t."Tarif_id" = y."Tarif_id"
            WHERE y.kisino=%s
            ORDER BY y.yorum_tarihi DESC
        """, (kisino,))
        for tarif, yorum, puan, yorum_id in yorumlar:
            self.tree_yorumlar.insert("", "end", values=(tarif, yorum, puan), iid=str(yorum_id))
    
    # --- Seçili yorumu sil ---
    def yorumu_sil(self):
        selected = self.tree_yorumlar.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir yorum seçin!")
            return
        yorum_id = int(selected[0])
        run_commit("""DELETE FROM "Yorum" WHERE "Yorum_id"=%s""", (yorum_id,))
        
        messagebox.showinfo("Başarılı", "Yorum silindi!")
        
        self.yorumlari_yukle()

    def uye_sorgula(self):
        ad_soyad = self.ent_uye_ara.get().strip()  # Tek kutu

        # Boş alan veya sadece ad girilmişse uyar
        if " " not in ad_soyad:
            self.txt_uye.delete("1.0", tk.END)
            self.txt_uye.insert(tk.END, "Lütfen ad ve soyad birlikte girin.")
            return

        ad, soyad = ad_soyad.split(" ", 1)

        rows = run_query("""
            SELECT "kisino", "ad", "soyad", "email"
            FROM "kisi"
            WHERE "ad" ILIKE %s AND "soyad" ILIKE %s
            ORDER BY "kisino" DESC
        """, ('%' + ad + '%', '%' + soyad + '%'))

        self.txt_uye.delete("1.0", tk.END)
        if not rows:
            self.txt_uye.insert(tk.END, "Üye bulunamadı.")
            return

        r = rows[0]
        self.secili_kisi_id = r[0]
        self.txt_uye.insert(tk.END,
            f"ID: {r[0]}\nAd: {r[1]}\nSoyad: {r[2]}\nEmail: {r[3]}"
        )
    def uye_guncelle(self):
        ad = self.entry_guncelle_ad.get().strip()
        soyad = self.entry_guncelle_soyad.get().strip()
        sifre = self.entry_guncelle_sifre.get().strip()
        yeni_email = self.entry_guncelle_email.get().strip()

        if not ad or not soyad or not sifre or not yeni_email:
            messagebox.showwarning("Uyarı", "Tüm alanları doldurun!")
            return

        # Veritabanında eşleşen kullanıcıyı bul
        rows = run_query("""
            SELECT "kisino"
            FROM "kisi"
            WHERE "ad" = %s AND "soyad" = %s AND "sifre" = %s
        """, (ad, soyad, sifre))

        if not rows:
            messagebox.showerror("Hata", "Kullanıcı bulunamadı veya bilgiler hatalı!")
            return

        kisino = rows[0][0]

        # Bilgileri güncelle
        run_commit("""
            UPDATE "kisi"
            SET email = %s
            WHERE "kisino" = %s
        """, (yeni_email, kisino))

        messagebox.showinfo("Başarılı", "Kullanıcı bilgileri güncellendi!")

        # Alanları temizle
        self.entry_guncelle_ad.delete(0, tk.END)
        self.entry_guncelle_soyad.delete(0, tk.END)
        self.entry_guncelle_sifre.delete(0, tk.END)
        self.entry_guncelle_email.delete(0, tk.END)

    def uye_kayit(self):
        ad = self.entry_yeni_ad.get().strip()
        soyad = self.entry_yeni_soyad.get().strip()
        email = self.entry_yeni_email.get().strip()
        sifre = self.entry_yeni_sifre.get().strip()

        if not ad or not soyad or not email or not sifre:
            messagebox.showwarning("Uyarı", "Tüm alanları doldurun!")
            return

        try:
            # SADECE uye tablosuna insert
            run_commit("""
                INSERT INTO "uye" (ad, soyad, email, sifre)
                VALUES (%s, %s, %s, %s);
            """, (ad, soyad, email, sifre))

            self.ent_uye_ara.delete(0, tk.END)
            self.ent_uye_ara.insert(0, ad)
            self.uye_sorgula()

            messagebox.showinfo("Başarılı", "Yeni üye kaydedildi!")

            self.entry_yeni_ad.delete(0, tk.END)
            self.entry_yeni_soyad.delete(0, tk.END)
            self.entry_yeni_email.delete(0, tk.END)
            self.entry_yeni_sifre.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Hata", f"Kayıt başarısız:\n{e}")


    def bolgeleri_yukle(self):
        rows = run_query("""
            SELECT "Bölge_id", "Bölge_adı"
            FROM "Bölge"
            ORDER BY "Bölge_id"
        """)
        self.bolge_map = {r[1]: r[0] for r in rows}
        self.cmb_bolge["values"] = list(self.bolge_map.keys())

    def kategorileri_yukle(self):
        rows = run_query("""
            SELECT "Yemek_Kategori_id", "kategori_adi"
            FROM "Yemek_Kategori"
        """)
        self.kat_map = {r[1]: r[0] for r in rows}
        self.cmb_kategori["values"] = list(self.kat_map.keys())

    def bolge_secildi(self, event=None):
        bolge_id = self.bolge_map.get(self.cmb_bolge.get(), None)
        if bolge_id:
            rows = run_query("""
                SELECT "Yemek_Kategori_id", "kategori_adi"
                FROM "Yemek_Kategori"
                WHERE "Bölge_id" = %s
            """, (bolge_id,))
        else:
            rows = run_query("""
                SELECT "Yemek_Kategori_id", "kategori_adi"
                FROM "Yemek_Kategori"
            """)
        self.kat_map = {r[1]: r[0] for r in rows}
        self.cmb_kategori["values"] = list(self.kat_map.keys())
        self.cmb_kategori.set("")
        self.cmb_yemek.set("")
        self.cmb_tarif_adi.set("")
        self.txt_tarif.delete("1.0", tk.END)

    def yemekleri_yukle(self, e):
        if not self.cmb_kategori.get():
            self.cmb_yemek["values"] = []
            return
        kat_id = self.kat_map[self.cmb_kategori.get()]
        bolge_id = self.bolge_map.get(self.cmb_bolge.get(), None)
        if bolge_id:
            rows = run_query("""
                SELECT "Yemek_id", "adi"
                FROM "Yemek"
                WHERE "Yemek_Kategori_id" = %s AND "Bölge" = %s
            """, (kat_id, bolge_id))
        else:
            rows = run_query("""
                SELECT "Yemek_id", "adi"
                FROM "Yemek"
                WHERE "Yemek_Kategori_id" = %s
            """, (kat_id,))
        self.yemek_map = {r[1]: r[0] for r in rows}
        self.cmb_yemek["values"] = list(self.yemek_map.keys())
        self.cmb_yemek.set("")
        self.cmb_tarif_adi.set("")
        self.txt_tarif.delete("1.0", tk.END)

    def tarif_adlarini_yukle(self, e):
        if not self.cmb_yemek.get():
            self.cmb_tarif_adi["values"] = []
            return
        yemek_id = self.yemek_map[self.cmb_yemek.get()]
        rows = run_query("""
            SELECT "Tarif_id", tarif_adi
            FROM "Tarif"
            WHERE "Yemek_id" = %s
            ORDER BY tarif_adi
        """, (yemek_id,))
        self.tarif_map = {r[1]: r[0] for r in rows}
        self.cmb_tarif_adi["values"] = list(self.tarif_map.keys())
        self.cmb_tarif_adi.set("")
        self.txt_tarif.delete("1.0", tk.END)

    def tarifi_yukle(self, e=None):
        if not self.cmb_tarif_adi.get():
            return

        self.tarif_id = self.tarif_map[self.cmb_tarif_adi.get()]
        yemek_id = self.yemek_map.get(self.cmb_yemek.get())

        # Tarif yapılışı ve pişirme gereci id
        row = run_query("""
            SELECT "yapilisi", "pisirme_gereci_id"
            FROM "Tarif"
            WHERE "Tarif_id" = %s
        """, (self.tarif_id,))

        if not row:
            return

        yapilis, pisirme_gereci_id = row[0]

        # Pisirme gereci adı
        pg_adi = ""
        if pisirme_gereci_id:
            pg_row = run_query("""
                SELECT "pisirme_gereci_adi"
                FROM "Pisirme_Gereci"
                WHERE "pisirme_gereci_id" = %s
            """, (pisirme_gereci_id,))
            if pg_row:
                pg_adi = pg_row[0][0]

        # Malzemeler
        malzemeler = run_query("""
            SELECT m."malzeme_adi"
            FROM "Malzeme" m
            JOIN "Tarif_Malzeme" tm ON tm."Malzeme_id" = m."Malzeme_id"
            WHERE tm."Tarif_id" = %s
            ORDER BY m."malzeme_adi"
        """, (self.tarif_id,))

        # --- Metin alanını güncelle ---
        self.txt_tarif.delete("1.0", tk.END)
        self.txt_tarif.insert(tk.END, yapilis + "\n\n--- Malzemeler ---\n")
        for m in malzemeler:
            self.txt_tarif.insert(tk.END, f"• {m[0]}\n")

        if pg_adi:
            self.txt_tarif.insert(tk.END, "\n--- Pişirme Gereçleri ---\n")
            self.txt_tarif.insert(tk.END, f"- {pg_adi}\n")

      
        self.lst_resimler.delete(0, tk.END)

        resim_row = run_query("""
            SELECT "Resim_id"
            FROM "Yemek"
            WHERE "Yemek_id" = %s
        """, (yemek_id,))

        if resim_row and resim_row[0][0]:
            resim_id = resim_row[0][0]

            resim_link_row = run_query("""
                SELECT "resim_link"
                FROM "Resim"
                WHERE "Resim_id" = %s
            """, (resim_id,))

            if resim_link_row and resim_link_row[0][0]:
                resim_link = resim_link_row[0][0]
                self.lst_resimler.insert(tk.END, resim_link)
        # -------------------


        # Ortalama puan
        ort_row = run_query("""
            SELECT AVG(puan)::numeric
            FROM "Yorum"
            WHERE "Tarif_id" = %s
        """, (self.tarif_id,))

        if ort_row and ort_row[0][0] is not None:
            ort = float(ort_row[0][0])
            ort = round(ort, 2)
        else:
            ort = "—"

        self.lbl_ortalama.config(text=f"Ortalama Puan: {ort}")

        self.yorumlari_yukle()

    def liste_resimleri_yenile(self):
        if not hasattr(self, "yemek_id") or not self.yemek_id:
            return

        rows = run_query("""
            SELECT r.resim_link
            FROM "Resim" r
            JOIN "Yemek" y ON y."Resim_id" = r."Resim_id"
            WHERE y."Yemek_id" = %s
        """, (self.yemek_id,))

        self.lst_resimler.delete(0, tk.END)
        for r in rows:
            self.lst_resimler.insert(tk.END, r[0])

   
    def yorum_ekle(self):
        if not self.tarif_id:
            messagebox.showwarning("Uyarı", "Önce bir tarif seçin!")
            return

        adsoyad = self.entry_adsoyad.get().strip()
        if not adsoyad:
            messagebox.showwarning("Uyarı", "Ad Soyad boş olamaz!")
            return

        parts = adsoyad.split()
        if len(parts) < 2:
            messagebox.showwarning("Uyarı", "Lütfen Ad ve Soyadı birlikte girin!")
            return

        ad = parts[0]
        soyad = " ".join(parts[1:])

        row = run_query("""
            SELECT kisino
            FROM kisi
            WHERE ad ILIKE %s AND soyad ILIKE %s
        """, (ad, soyad))

        if not row:
            messagebox.showwarning("Hata", "Bu ad-soyada sahip kayıtlı bir üye yok! Yorum ekleyemezsiniz.")
            return

        kisino = row[0][0]

        yorum = self.txt_yorum.get("1.0", tk.END).strip()
        if not yorum:
            messagebox.showwarning("Uyarı", "Yorum boş olamaz!")
            return

        puan = int(self.spin_puan.get())

        run_commit("""
            INSERT INTO "Yorum" (yorum_metni, puan, "Tarif_id", kisino)
            VALUES (%s, %s, %s, %s)
        """, (yorum, puan, self.tarif_id, kisino))

        messagebox.showinfo("Başarılı", "Yorum eklendi!")

        # Temizle
        self.entry_adsoyad.delete(0, tk.END)
        self.txt_yorum.delete("1.0", tk.END)

        # Yorumları güncelle
        self.yorumlari_yukle()
        # self.ortalama_puani_yukle()

    def yorumlari_yukle(self):
        for i in self.tree_yorum.get_children():
            self.tree_yorum.delete(i)
        rows = run_query("""
            SELECT k.ad, k.soyad, y.yorum_metni, y.puan, y.yorum_tarihi
            FROM "Yorum" y
            JOIN kisi k ON k.kisino = y.kisino
            WHERE y."Tarif_id" = %s
            ORDER BY y.yorum_tarihi DESC
        """, (self.tarif_id,))

        for ad, soyad, yorum, puan, tarih in rows:
            self.tree_yorum.insert("", "end", values=(f"{ad} {soyad}", yorum, puan))

        # Ortalama puanı hesapla
        ort_row = run_query("""
            SELECT AVG(puan)::numeric
            FROM "Yorum"
            WHERE "Tarif_id" = %s
        """, (self.tarif_id,))

        if ort_row and ort_row[0][0] is not None:
            ort = round(float(ort_row[0][0]), 2)
        else:
            ort = 0  # veya "—"

        # Arayüzü güncelle
        self.lbl_ortalama.config(text=f"Ortalama Puan: {ort}")

        # -----------------------------------------
        # Tarif tablosuna kaydet
        run_commit("""
            UPDATE "Tarif"
            SET ortalama_puan = %s
            WHERE "Tarif_id" = %s
        """, (ort, self.tarif_id))


    def malzeme_ara(self):
        key = self.ent_malzeme.get()
        rows = run_query("""
            SELECT DISTINCT y."adi"
            FROM "Yemek" y
            JOIN "Tarif" t ON y."Yemek_id" = t."Yemek_id"
            JOIN "Tarif_Malzeme" tm ON t."Tarif_id" = tm."Tarif_id"
            JOIN "Malzeme" m ON tm."Malzeme_id" = m."Malzeme_id"
            WHERE m."malzeme_adi" ILIKE %s
        """, ('%' + key + '%',))
        self.lst_sonuc.delete(0, tk.END)
        for r in rows:
            self.lst_sonuc.insert(tk.END, r[0])

# ===== PROGRAMI BAŞLAT =====
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
