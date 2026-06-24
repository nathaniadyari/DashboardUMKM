import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO

# ======================
# INISIALISASI DATA
# ======================

if "stok" not in st.session_state:
    st.session_state.stok = {
        "Alpukat": 15,
        "Nangka": 15,
        "Kelapa": 15,
        "Agar Merah": 15
    }

if "penggunaan" not in st.session_state:
    st.session_state.penggunaan = {
        "Alpukat": 0,
        "Nangka": 0,
        "Kelapa": 0,
        "Agar Merah": 0
    }

if "riwayat" not in st.session_state:
    st.session_state.riwayat = []

# ======================
# STATUS
# ======================

def status_stok(jumlah):

    if jumlah <= 5:
        return "🔴 Restock"

    elif jumlah <= 10:
        return "🟡 Waspada"

    else:
        return "🟢 Aman"

# ======================
# HEADER
# ======================

st.title("🥑 Dashboard Monitoring Persediaan Es Teler")

st.markdown("---")

# ======================
# TABEL STOK
# ======================

data_stok = []

for bahan, jumlah in st.session_state.stok.items():

    data_stok.append([
        bahan,
        jumlah,
        status_stok(jumlah)
    ])

df_stok = pd.DataFrame(
    data_stok,
    columns=["Bahan", "Stok (Cup)", "Status"]
)

st.subheader("📦 Kondisi Stok")

st.dataframe(
    df_stok,
    use_container_width=True
)

# ======================
# POTENSI PENJUALAN
# ======================

potensi = min(st.session_state.stok.values())

st.metric(
    label="Potensi Penjualan",
    value=f"{potensi} Cup"
)

# ======================
# NOTIFIKASI
# ======================

waspada = []
restock = []

for bahan, jumlah in st.session_state.stok.items():

    if jumlah <= 5:
        restock.append(bahan)

    elif jumlah <= 10:
        waspada.append(bahan)

col1, col2 = st.columns(2)

with col1:
    st.warning(
        "Waspada : " +
        (", ".join(waspada) if waspada else "Tidak Ada")
    )

with col2:
    st.error(
        "Restock : " +
        (", ".join(restock) if restock else "Tidak Ada")
    )

# ======================
# TRANSAKSI PENJUALAN
# ======================

st.markdown("---")

st.subheader("🛒 Transaksi Penjualan")

topping = st.multiselect(
    "Pilih topping",
    list(st.session_state.stok.keys())
)

jumlah_cup = st.number_input(
    "Jumlah Cup",
    min_value=1,
    value=1
)

if st.button("JUAL"):

    if len(topping) == 0:

        st.error("Pilih topping terlebih dahulu")

    else:

        cukup = True

        for bahan in topping:

            if st.session_state.stok[bahan] < jumlah_cup:

                st.error(
                    f"Stok {bahan} tidak mencukupi"
                )

                cukup = False

        if cukup:

            for bahan in topping:

                st.session_state.stok[bahan] -= jumlah_cup

                st.session_state.penggunaan[bahan] += jumlah_cup

            waktu = datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S"
            )

            st.session_state.riwayat.append(
                [
                    waktu,
                    ", ".join(topping),
                    jumlah_cup
                ]
            )

            st.success(
                "Transaksi berhasil"
            )

            st.rerun()

# ======================
# RESTOCK
# ======================

st.markdown("---")

st.subheader("📥 Restock")

bahan_restock = st.selectbox(
    "Pilih Bahan",
    list(st.session_state.stok.keys())
)

jumlah_restock = st.number_input(
    "Jumlah Restock",
    min_value=1,
    value=1,
    key="restock"
)

if st.button("RESTOCK"):

    st.session_state.stok[
        bahan_restock
    ] += jumlah_restock

    st.success(
        f"{bahan_restock} ditambah {jumlah_restock} cup"
    )

    st.rerun()

# ======================
# RIWAYAT
# ======================

st.markdown("---")

st.subheader("📋 Riwayat Transaksi")

if len(st.session_state.riwayat) > 0:

    df_riwayat = pd.DataFrame(
        st.session_state.riwayat,
        columns=[
            "Waktu",
            "Topping",
            "Jumlah Cup"
        ]
    )

    st.dataframe(
        df_riwayat,
        use_container_width=True
    )

else:

    st.info(
        "Belum ada transaksi"
    )

# ======================
# EXPORT EXCEL
# ======================

st.markdown("---")

st.subheader("📊 Export Excel")

output = BytesIO()

with pd.ExcelWriter(
    output,
    engine="openpyxl"
) as writer:

    df_stok.to_excel(
        writer,
        sheet_name="Stok",
        index=False
    )

    if len(st.session_state.riwayat) > 0:

        df_riwayat.to_excel(
            writer,
            sheet_name="Riwayat",
            index=False
        )

st.download_button(
    label="⬇ Download Excel",
    data=output.getvalue(),
    file_name="stok_es_teler.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ======================
# GRAFIK
# ======================

st.markdown("---")

st.subheader("📈 Grafik Penggunaan Topping")

fig, ax = plt.subplots()

ax.bar(
    list(st.session_state.penggunaan.keys()),
    list(st.session_state.penggunaan.values())
)

ax.set_ylabel(
    "Jumlah Digunakan"
)

st.pyplot(fig)