from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import math
import os
import hashlib
from config import Config
import sqlalchemy as sa
from sqlalchemy import func
import logging

app = Flask(__name__)
app.config.from_object(Config)

# ================= KONFIGURASI LOGGING =================
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

# ================= FAVICON FIX =================
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

# Inisialisasi ekstensi
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Silakan login untuk mengakses halaman ini.'
login_manager.login_message_category = 'warning'

# ================= MODELS (SESUAI ERD & SQL BARU) =================

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nama_lengkap = db.Column(db.String(100))
    role = db.Column(db.Enum("admin", "petani"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    diagnosa_history = db.relationship(
        "Diagnosa", backref="pengguna", lazy=True, cascade="all, delete-orphan"
    )


class Penyakit(db.Model):
    __tablename__ = "penyakit"
    id = db.Column(db.Integer, primary_key=True)
    kode_penyakit = db.Column(db.String(10), unique=True, nullable=False)
    nama_penyakit = db.Column(db.String(100), nullable=False)
    prior_probability = db.Column(db.Numeric(5, 4), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bobot = db.relationship(
        "BobotProbabilitas",
        backref="penyakit_rel",
        lazy=True,
        cascade="all, delete-orphan",
    )
    rekomendasi = db.relationship(
        "Rekomendasi",
        backref="penyakit_rel",
        uselist=False,
        cascade="all, delete-orphan",
    )
    diagnosa = db.relationship("Diagnosa", backref="penyakit_rel", lazy=True)


class Gejala(db.Model):
    __tablename__ = "gejala"
    id = db.Column(db.Integer, primary_key=True)
    kode_gejala = db.Column(db.String(10), unique=True, nullable=False)
    nama_gejala = db.Column(db.Text, nullable=False)
    kategori_organ = db.Column(
        db.Enum("daun", "batang", "buah", "akar"), nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bobot = db.relationship(
        "BobotProbabilitas",
        backref="gejala_rel",
        lazy=True,
        cascade="all, delete-orphan",
    )


class BobotProbabilitas(db.Model):
    __tablename__ = "bobot_probabilitas"
    id = db.Column(db.Integer, primary_key=True)
    penyakit_id = db.Column(
        db.Integer, db.ForeignKey("penyakit.id", ondelete="CASCADE")
    )
    gejala_id = db.Column(db.Integer, db.ForeignKey("gejala.id", ondelete="CASCADE"))
    nilai_probabilitas = db.Column(db.Numeric(5, 4), nullable=False)
    fase_pertumbuhan = db.Column(db.Enum("vegetatif", "generatif"), nullable=False)


class Rekomendasi(db.Model):
    __tablename__ = "rekomendasi"
    id = db.Column(db.Integer, primary_key=True)
    penyakit_id = db.Column(
        db.Integer, db.ForeignKey("penyakit.id", ondelete="CASCADE")
    )
    prosedur_penanganan = db.Column(db.Text, nullable=False)
    sumber_literatur = db.Column(db.String(100), default="Meilin (2014)")


class Diagnosa(db.Model):
    __tablename__ = "diagnosa"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    penyakit_id = db.Column(db.Integer, db.ForeignKey("penyakit.id"))
    gejala_input = db.Column(db.Text)
    fase_input = db.Column(db.Enum("vegetatif", "generatif"))
    nilai_posterior = db.Column(db.Numeric(5, 4))
    tanggal_diagnosa = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ================= HELPER FUNCTIONS =================


def hash_password(password):
    """Generate password hash"""
    return generate_password_hash(password, method="pbkdf2:sha256")


def verify_password(password_hash, password):
    """Verify password"""
    if not password_hash or not password:
        return False
    if password_hash == password:
        return True
    try:
        return check_password_hash(password_hash, password)
    except:
        return False


def get_confidence_level(probabilitas):
    """Tentukan tingkat keyakinan berdasarkan probabilitas (persen)"""
    if probabilitas >= 80:
        return "tinggi"
    elif probabilitas >= 60:
        return "sedang"
    else:
        return "rendah"


# ================= TEMPLATE FILTERS =================


@app.template_filter("fromjson")
def fromjson_filter(data):
    if not data:
        return []
    try:
        return json.loads(data)
    except:
        return []


@app.template_filter("get_gejala_names")
def get_gejala_names_filter(gejala_input):
    if not gejala_input:
        return []
    try:
        gejala_ids = json.loads(gejala_input)
        gejala_names = []
        for g_id in gejala_ids:
            gejala = Gejala.query.get(int(g_id))
            if gejala:
                gejala_names.append(gejala.nama_gejala)
        return gejala_names
    except:
        return []


# ================= NAIVE BAYES LOGIC (SESUAI PROPOSAL BAB 4) =================

class NaiveBayesDiagnosa:
    def __init__(self):
        self.penyakit_list = Penyakit.query.all()
        self.gejala_list = Gejala.query.all()

    def hitung_probabilitas(self, gejala_ids, fase_pertumbuhan):
        """
        Menghitung probabilitas dengan integrasi Fase Pertumbuhan.
        Default likelihood jika data tidak ada di tabel bobot: 0.05
        """
        try:
            if not self.penyakit_list or not gejala_ids:
                return []

            hasil = []

            for penyakit in self.penyakit_list:
                # 1. Ambil Prior Probability P(H)
                prior = float(penyakit.prior_probability)

                # 2. Hitung Likelihood dengan asumsi independensi
                likelihood = 1.0

                for gejala_id in gejala_ids:
                    # Cari nilai bobot berdasarkan penyakit, gejala, DAN FASE
                    bp = BobotProbabilitas.query.filter_by(
                        penyakit_id=penyakit.id,
                        gejala_id=gejala_id,
                        fase_pertumbuhan=fase_pertumbuhan,
                    ).first()

                    if bp:
                        likelihood *= float(bp.nilai_probabilitas)
                    else:
                        # Nilai default jika tidak ada rule di database (Laplace Smoothing sederhana)
                        likelihood *= 0.05

                # 3. Hitung Numerator (Posterior sementara) = Prior * Likelihood
                posterior = prior * likelihood

                # 4. Ambil Rekomendasi Solusi
                rek = Rekomendasi.query.filter_by(penyakit_id=penyakit.id).first()
                solusi = (
                    rek.prosedur_penanganan
                    if rek
                    else "Belum ada rekomendasi penanganan."
                )

                hasil.append(
                    {
                        "penyakit_id": penyakit.id,
                        "nama_penyakit": penyakit.nama_penyakit,
                        "kode_penyakit": penyakit.kode_penyakit,
                        "prior": prior,
                        "likelihood": likelihood,
                        "posterior": posterior,
                        "solusi": solusi,
                    }
                )

            # 5. Normalisasi (Mendapatkan Persentase)
            total_posterior = sum(item["posterior"] for item in hasil)

            if total_posterior > 0:
                for item in hasil:
                    prob = (item["posterior"] / total_posterior) * 100
                    item["probabilitas"] = round(prob, 2)
                    item["keyakinan"] = get_confidence_level(item["probabilitas"])

                    # Tentukan warna UI
                    if item["keyakinan"] == "tinggi":
                        item["warna_keyakinan"] = "success"
                    elif item["keyakinan"] == "sedang":
                        item["warna_keyakinan"] = "warning"
                    else:
                        item["warna_keyakinan"] = "secondary"
            else:
                for item in hasil:
                    item["probabilitas"] = 0.0
                    item["keyakinan"] = "rendah"
                    item["warna_keyakinan"] = "secondary"

            # Urutkan dari tertinggi ke terendah
            hasil.sort(key=lambda x: x["probabilitas"], reverse=True)
            return hasil

        except Exception as e:
            app.logger.error(f"[NAIVE_BAYES] Error: {e}", exc_info=True)
            raise e

# ================= ROUTES UTAMA =================


@app.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and verify_password(user.password, password):
            login_user(user, remember=True)
            if user.role == "admin":
                flash("Login sebagai Admin berhasil!", "success")
                return redirect(url_for("admin_dashboard"))
            else:
                flash("Login berhasil!", "success")
                return redirect(url_for("dashboard"))
        else:
            flash("Username atau Password salah!", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        nama_lengkap = request.form.get("nama_lengkap")
        role = request.form.get("role", "petani")

        # PERBAIKAN: Hanya validasi field yang ada
        if not username or not password or not nama_lengkap:
            flash("Username, password, dan nama lengkap wajib diisi!", "danger")
            return render_template("register.html")

        if User.query.filter_by(username=username).first():
            flash("Username sudah digunakan!", "danger")
            return render_template("register.html")

        try:
            user = User(
                username=username,
                password=hash_password(password),
                nama_lengkap=nama_lengkap,
                role=role,
            )
            db.session.add(user)
            db.session.commit()
            flash("Registrasi berhasil! Silakan login.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error registrasi: {str(e)}", "danger")

    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Anda telah logout.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "admin":
        return redirect(url_for("admin_dashboard"))

    total_diagnosa = Diagnosa.query.filter_by(user_id=current_user.id).count()
    diagnosa_terbaru = (
        Diagnosa.query.filter_by(user_id=current_user.id)
        .order_by(Diagnosa.tanggal_diagnosa.desc())
        .limit(5)
        .all()
    )

    for d in diagnosa_terbaru:
        d.prob_persen = float(d.nilai_posterior or 0) * 100
        d.keyakinan = get_confidence_level(d.prob_persen)

    return render_template(
        "dashboard.html",
        total_diagnosa=total_diagnosa,
        diagnosa_terbaru=diagnosa_terbaru,
        user=current_user,
    )


@app.route("/diagnosa", methods=["GET", "POST"])
@login_required
def diagnosa():
    if current_user.role == "admin":
        flash("Admin tidak bisa melakukan diagnosis!", "warning")
        return redirect(url_for("admin_dashboard"))

    # Ambil data gejala untuk ditampilkan di form
    gejala_list = Gejala.query.order_by(Gejala.kategori_organ, Gejala.kode_gejala).all()
    gejala_by_kategori = {}
    for gejala in gejala_list:
        if gejala.kategori_organ not in gejala_by_kategori:
            gejala_by_kategori[gejala.kategori_organ] = []
        gejala_by_kategori[gejala.kategori_organ].append(gejala)

    if request.method == "POST":
        gejala_ids = request.form.getlist("gejala")
        fase_input = request.form.get("fase_pertumbuhan")

        if not gejala_ids or not fase_input:
            flash(
                "Harap pilih minimal satu gejala dan tentukan fase pertumbuhan!",
                "warning",
            )
            return redirect(url_for("diagnosa"))

        try:
            gejala_ids = [int(g_id) for g_id in gejala_ids]

            # Eksekusi Algoritma
            nb = NaiveBayesDiagnosa()
            hasil = nb.hitung_probabilitas(gejala_ids, fase_input)

            if not hasil:
                flash("Gagal menghitung, data tidak cukup.", "danger")
                return redirect(url_for("diagnosa"))

            top_result = hasil[0]

            # Konversi persen ke desimal untuk disimpan ke Database
            nilai_posterior_db = top_result["probabilitas"] / 100.0

            # Simpan riwayat
            diagnosa_record = Diagnosa(
                user_id=current_user.id,
                penyakit_id=top_result["penyakit_id"],
                gejala_input=json.dumps(gejala_ids),
                fase_input=fase_input,
                nilai_posterior=nilai_posterior_db,
            )
            db.session.add(diagnosa_record)
            db.session.commit()

            return redirect(url_for("hasil_diagnosa", diagnosa_id=diagnosa_record.id))

        except Exception as e:
            db.session.rollback()
            flash(f"Error melakukan diagnosis: {str(e)}", "danger")
            return redirect(url_for("diagnosa"))

    return render_template("diagnosa.html", gejala_by_kategori=gejala_by_kategori)


@app.route("/hasil-diagnosa/<int:diagnosa_id>")
@login_required
def hasil_diagnosa(diagnosa_id):
    try:
        diagnosa = Diagnosa.query.get_or_404(diagnosa_id)

        # Keamanan Akses
        if current_user.role != "admin" and diagnosa.user_id != current_user.id:
            flash("Akses ditolak!", "danger")
            return redirect(url_for("riwayat"))

        # Hitung Ulang On-The-Fly
        gejala_ids = json.loads(diagnosa.gejala_input) if diagnosa.gejala_input else []
        nb = NaiveBayesDiagnosa()
        hasil = nb.hitung_probabilitas(gejala_ids, diagnosa.fase_input)

        # Ambil nama gejala untuk UI
        gejala_objs = (
            Gejala.query.filter(Gejala.id.in_(gejala_ids)).all() if gejala_ids else []
        )
        gejala_names = [g.nama_gejala for g in gejala_objs]

        # Tambahkan atribut probabilitas (%) ke object diagnosa untuk UI
        if diagnosa.nilai_posterior:
            diagnosa.probabilitas = float(diagnosa.nilai_posterior) * 100
            diagnosa.keyakinan = get_confidence_level(diagnosa.probabilitas)
        else:
            diagnosa.probabilitas = 0
            diagnosa.keyakinan = "rendah"

        back_url = (
            url_for("riwayat")
            if current_user.role != "admin"
            else url_for("admin_semua_diagnosa")
        )
        user_info = (
            User.query.get(diagnosa.user_id) if current_user.role == "admin" else None
        )

        return render_template(
            "hasil_diagnosa.html",
            diagnosa=diagnosa,
            hasil=hasil,
            gejala_names=gejala_names,
            back_url=back_url,
            user_info=user_info,
        )

    except Exception as e:
        app.logger.error(f"[HASIL] Error: {e}", exc_info=True)
        flash("Terjadi kesalahan memuat hasil.", "danger")
        return redirect(url_for("dashboard"))


@app.route("/riwayat")
@login_required
def riwayat():
    if current_user.role == "admin":
        return redirect(url_for("admin_semua_diagnosa"))
    diagnosa_list = (
        Diagnosa.query.filter_by(user_id=current_user.id)
        .order_by(Diagnosa.tanggal_diagnosa.desc())
        .all()
    )

    for d in diagnosa_list:
        d.prob_persen = float(d.nilai_posterior or 0) * 100
        d.keyakinan = get_confidence_level(d.prob_persen)

    return render_template("riwayat.html", diagnosa_list=diagnosa_list)


@app.route("/tentang-sistem")
def tentang_sistem():
    return render_template("tentang_sistem.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        # PERBAIKAN: Hanya update nama_lengkap (email & lokasi sudah dihapus)
        current_user.nama_lengkap = request.form.get("nama_lengkap")
        
        # Update password jika diisi
        pw_baru = request.form.get("password_baru")
        if pw_baru:
            current_user.password = hash_password(pw_baru)
            
        db.session.commit()
        flash("Profil diperbarui!", "success")
        
    return render_template("profile.html", user=current_user)


# ================= ROUTE UNTUK STATISTIK PROFIL =================
@app.route('/profile/stats')
@login_required
def profile_stats():
    """API endpoint untuk mendapatkan statistik pengguna"""
    try:
        if current_user.role != 'petani':
            return jsonify({'error': 'Hanya untuk petani'}), 403

        total_diagnosa = Diagnosa.query.filter_by(user_id=current_user.id).count()

        # PERBAIKAN: Hitung keyakinan berdasarkan nilai_posterior
        diagnosa_list = Diagnosa.query.filter_by(user_id=current_user.id).all()
        keyakinan_counts = {'tinggi': 0, 'sedang': 0, 'rendah': 0}
        
        for d in diagnosa_list:
            if d.nilai_posterior:
                prob = float(d.nilai_posterior) * 100
                keyakinan = get_confidence_level(prob)
                keyakinan_counts[keyakinan] += 1

        penyakit_stats = db.session.query(
            Penyakit.nama_penyakit.label('nama'),
            Penyakit.kode_penyakit.label('kode'),
            func.count(Diagnosa.id).label('jumlah')
        ).join(Diagnosa, Diagnosa.penyakit_id == Penyakit.id)\
         .filter(Diagnosa.user_id == current_user.id)\
         .group_by(Penyakit.id)\
         .order_by(func.count(Diagnosa.id).desc())\
         .limit(3).all()

        penyakit_teratas = [
            {'nama': p.nama, 'kode': p.kode, 'jumlah': p.jumlah} 
            for p in penyakit_stats
        ]

        tiga_puluh_hari_lalu = datetime.utcnow() - timedelta(days=30)
        diagnosa_bulanan = Diagnosa.query.filter(
            Diagnosa.user_id == current_user.id,
            Diagnosa.tanggal_diagnosa >= tiga_puluh_hari_lalu
        ).count()

        days_since_join = (datetime.utcnow() - current_user.created_at).days
        if days_since_join > 0:
            rata_per_bulan = round(total_diagnosa / days_since_join * 30, 1)
        else:
            rata_per_bulan = 0

        return jsonify({
            'success': True,
            'total_diagnosa': total_diagnosa,
            'keyakinan': keyakinan_counts,
            'penyakit_teratas': penyakit_teratas,
            'diagnosa_bulan_terakhir': diagnosa_bulanan,
            'rata_per_bulan': rata_per_bulan,
            'hari_sejak_gabung': days_since_join
        })

    except Exception as e:
        app.logger.error(f"Error in profile_stats: {e}")
        return jsonify({'error': 'Gagal mengambil statistik', 'details': str(e)}), 500

# ================= ADMIN ROUTES =================


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    diagnosa_terbaru = (
        Diagnosa.query.order_by(Diagnosa.tanggal_diagnosa.desc()).limit(10).all()
    )

    for d in diagnosa_terbaru:
        d.prob_persen = float(d.nilai_posterior or 0) * 100
        d.keyakinan = get_confidence_level(d.prob_persen)

    return render_template(
        "admin/dashboard.html",
        total_petani=User.query.filter_by(role="petani").count(),
        total_diagnosa=Diagnosa.query.count(),
        total_penyakit=Penyakit.query.count(),
        total_gejala=Gejala.query.count(),
        diagnosa_terbaru=diagnosa_terbaru,
    )


@app.route("/admin/gejala")
@login_required
def admin_gejala():
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))
    return render_template("admin/gejala.html", gejala_list=Gejala.query.all())


@app.route("/admin/penyakit")
@login_required
def admin_penyakit():
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    penyakit_list = Penyakit.query.order_by(Penyakit.kode_penyakit).all()

    return render_template(
        "admin/penyakit.html",
        penyakit_list=penyakit_list,
        BobotProbabilitas=BobotProbabilitas,
    )


@app.route("/admin/bobot")
@login_required
def admin_bobot():
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))
    bobot_list = BobotProbabilitas.query.all()
    return render_template("admin/bobot.html", bobot_list=bobot_list)


@app.route("/admin/rekomendasi")
@login_required
def admin_rekomendasi():
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))
    rek_list = Rekomendasi.query.all()
    return render_template("admin/rekomendasi.html", rek_list=rek_list)


@app.route("/admin/diagnosa")
@login_required
def admin_semua_diagnosa():
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))
    d_list = Diagnosa.query.order_by(Diagnosa.tanggal_diagnosa.desc()).all()
    for d in d_list:
        d.prob_persen = float(d.nilai_posterior or 0) * 100
        d.keyakinan = get_confidence_level(d.prob_persen)
    return render_template("admin/diagnosa.html", diagnosa_list=d_list)


@app.route("/admin/pengguna")
@login_required
def admin_pengguna():
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))
    return render_template("admin/pengguna.html", user_list=User.query.all())

# ================= CRUD ADMIN LENGKAP =================


# --- GEJALA ---
@app.route("/admin/gejala/edit/<int:id>", methods=["POST"])
@login_required
def admin_edit_gejala(id):
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))
    gejala = Gejala.query.get_or_404(id)
    gejala.kode_gejala = request.form.get("kode")
    gejala.nama_gejala = request.form.get("nama")
    gejala.kategori_organ = request.form.get("kategori")
    db.session.commit()
    flash("Gejala diupdate", "success")
    return redirect(url_for("admin_gejala"))


@app.route("/admin/gejala/delete/<int:id>", methods=["POST"])
@login_required
def admin_delete_gejala(id):
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))
    gejala = Gejala.query.get_or_404(id)
    db.session.delete(gejala)
    db.session.commit()
    flash("Gejala dihapus", "success")
    return redirect(url_for("admin_gejala"))


# --- PENYAKIT ---
@app.route("/admin/penyakit/edit/<int:id>", methods=["POST"])
@login_required
def admin_edit_penyakit(id):
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))
    p = Penyakit.query.get_or_404(id)
    p.kode_penyakit = request.form.get("kode")
    p.nama_penyakit = request.form.get("nama")
    prior = request.form.get("prior_probability")
    p.prior_probability = float(prior) if prior else 0.3
    db.session.commit()
    flash("Penyakit diupdate", "success")
    return redirect(url_for("admin_penyakit"))


@app.route("/admin/penyakit/delete/<int:id>", methods=["POST"])
@login_required
def admin_delete_penyakit(id):
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))
    p = Penyakit.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash("Penyakit dihapus", "success")
    return redirect(url_for("admin_penyakit"))


# --- DIAGNOSA & PENGGUNA (HAPUS) ---
@app.route("/admin/diagnosa/delete/<int:id>", methods=["POST"])
@login_required
def admin_delete_diagnosa(id):
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))
    d = Diagnosa.query.get_or_404(id)
    db.session.delete(d)
    db.session.commit()
    flash("Diagnosa dihapus", "success")
    return redirect(url_for("admin_semua_diagnosa"))


# --- TAMBAH & EDIT PENGGUNA ---
@app.route("/admin/pengguna/tambah", methods=["GET", "POST"])
@login_required
def tambah_pengguna():
    if current_user.role != "admin":
        flash("Akses ditolak!", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        nama_lengkap = request.form.get("nama_lengkap")
        role = request.form.get("role", "petani")

        # Validasi field
        if not username or not password or not nama_lengkap:
            flash("Username, password, dan nama lengkap wajib diisi!", "danger")
            return redirect(url_for("tambah_pengguna"))

        # Cek apakah username sudah ada
        if User.query.filter_by(username=username).first():
            flash("Username sudah digunakan!", "danger")
            return redirect(url_for("tambah_pengguna"))

        try:
            hashed_pw = hash_password(password)
            user_baru = User(
                username=username,
                password=hashed_pw,
                nama_lengkap=nama_lengkap,
                role=role,
            )
            db.session.add(user_baru)
            db.session.commit()
            flash("Pengguna berhasil ditambahkan!", "success")
            return redirect(url_for("admin_pengguna"))
        except Exception as e:
            db.session.rollback()
            flash(f"Gagal menambah pengguna: {str(e)}", "danger")
            return redirect(url_for("tambah_pengguna"))

    # PERBAIKAN: Me-render halaman form tambah_pengguna.html, BUKAN redirect
    return render_template("admin/tambah_pengguna.html")


@app.route("/admin/pengguna/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_pengguna(id):
    if current_user.role != "admin":
        flash("Akses ditolak!", "danger")
        return redirect(url_for("dashboard"))

    user = User.query.get_or_404(id)

    if request.method == "POST":
        user.username = request.form.get("username")
        user.nama_lengkap = request.form.get("nama_lengkap")
        user.role = request.form.get("role")

        # PERBAIKAN: Hanya update password jika diisi
        password_baru = request.form.get("password")
        if password_baru:
            user.password = hash_password(password_baru)

        try:
            db.session.commit()
            flash("Data pengguna berhasil diperbarui!", "success")
        except Exception as e:
            db.session.rollback()
            flash("Gagal update! Username mungkin sudah ada.", "danger")

    return redirect(url_for("admin_pengguna"))


@app.route("/admin/pengguna/hapus/<int:id>")
@login_required
def hapus_pengguna(id):
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))
    u = User.query.get_or_404(id)
    db.session.delete(u)
    db.session.commit()
    flash("Pengguna dihapus", "success")
    return redirect(url_for("admin_pengguna"))


# ================= FIX DATA ROUTE =================
@app.route('/admin/fix-inconsistent-data')
@login_required
def fix_inconsistent_data():
    """Route untuk memperbaiki data diagnosa yang keyakinannya tidak sesuai"""
    if current_user.role != 'admin':
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        all_diagnosa = Diagnosa.query.all()
        fixed_count = 0
        inconsistent_count = 0
        
        app.logger.info(f"[FIX_DATA] Memeriksa {len(all_diagnosa)} data diagnosa")
        
        for diagnosa in all_diagnosa:
            prob = float(diagnosa.nilai_posterior or 0) * 100
            
            # Tentukan keyakinan yang seharusnya
            expected_keyakinan = get_confidence_level(prob)
            
            # PERBAIKAN: Tidak ada kolom keyakinan di database, jadi kita hitung ulang di runtime
            
        if fixed_count > 0:
            db.session.commit()
            flash(f'Berhasil memperbaiki {fixed_count} data diagnosa yang inkonsisten (dari {inconsistent_count} ditemukan)', 'success')
            app.logger.info(f"[FIX_DATA] ✅ Diperbaiki {fixed_count} data")
        elif inconsistent_count > 0:
            flash(f'Ditemukan {inconsistent_count} data inkonsisten, tetapi tidak ada yang bisa diperbaiki', 'warning')
        else:
            flash('✅ Semua data sudah konsisten', 'info')
            
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"[FIX_DATA] Error: {e}", exc_info=True)
        flash(f'Error memperbaiki data: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/fix-diagnosa-data')
@login_required
def fix_diagnosa_data():
    """Route untuk memperbaiki data diagnosa yang rusak"""
    if current_user.role != 'admin':
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('dashboard'))

    try:
        all_diagnosa = Diagnosa.query.all()
        fixed_count = 0

        # PERBAIKAN: Tidak ada kolom hasil di database, jadi route ini bisa dihapus atau dikosongkan
        flash('Tidak ada data yang perlu diperbaiki', 'info')

    except Exception as e:
        db.session.rollback()
        flash(f'Error memperbaiki data: {str(e)}', 'danger')

    return redirect(url_for('admin_dashboard'))


# ================= ERROR HANDLERS =================
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


# ================= RUN APP =================
if __name__ == "__main__":
    with app.app_context():
        try:
            with db.engine.connect() as connection:
                print("✅ Koneksi ke database BERHASIL!")
        except Exception as e:
            print("❌ Koneksi ke database GAGAL!", e)

    PORT = 5002
    print(f"\n🌐 URL Aplikasi: http://localhost:{PORT}")
    app.run(debug=True, host="0.0.0.0", port=PORT)