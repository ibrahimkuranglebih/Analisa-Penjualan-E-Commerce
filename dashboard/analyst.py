import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import streamlit_shadcn_ui as ui

customer = pd.read_csv('E-commerce-public-dataset/E-Commerce Public Dataset/customers_dataset.csv')
geolocation = pd.read_csv('E-commerce-public-dataset/E-Commerce Public Dataset/geolocation_dataset.csv')
order_items = pd.read_csv('E-commerce-public-dataset/E-Commerce Public Dataset/order_items_dataset.csv')
order_payments = pd.read_csv('E-commerce-public-dataset/E-Commerce Public Dataset/order_payments_dataset.csv')
order_reviews = pd.read_csv('E-commerce-public-dataset/E-Commerce Public Dataset/order_reviews_dataset.csv')
orders = pd.read_csv('E-commerce-public-dataset/E-Commerce Public Dataset/orders_dataset.csv')
products = pd.read_csv('E-commerce-public-dataset/E-Commerce Public Dataset/products_dataset.csv')
products_category = pd.read_csv('E-commerce-public-dataset/E-Commerce Public Dataset/product_category_name_translation.csv')
sellers = pd.read_csv('E-commerce-public-dataset/E-Commerce Public Dataset/sellers_dataset.csv')

# Konversi tanggal jika belum dilakukan
order_payments['payment_value'] = pd.to_numeric(order_payments['payment_value'], errors='coerce')
orders['order_approved_at'] = pd.to_datetime(orders['order_approved_at'])

# Filter berdasarkan rentang waktu
st.sidebar.header("Filter Waktu")
years = sorted(orders['order_approved_at'].dt.year.dropna().astype(int).unique())
options = ["Hingga Saat Ini"] + years  # Tambahkan opsi "Hingga Saat Ini"
selected_year = st.sidebar.selectbox("Pilih Tahun:", options)

# Filter data berdasarkan pilihan tahun
if selected_year == "Hingga Saat Ini":
    filtered_orders = orders
    filtered_order_payments = order_payments
else:
    filtered_orders = orders[orders['order_approved_at'].dt.year == selected_year]
    filtered_order_payments = order_payments[order_payments['order_id'].isin(filtered_orders['order_id'])]

# Hitung ulang metrik berdasarkan data yang difilter
total_payment_value = filtered_order_payments['payment_value'].sum()
total_orders_delivered = len(filtered_orders[filtered_orders['order_status'] == 'delivered'])

st.header('Statistik Analisis Dataset E-Commerce Public :money_with_wings:')

# Menampilkan metric card dengan data yang difilter
cols = st.columns(2)
with cols[0]:
    ui.metric_card("Total Value Order", f"R$ {round(total_payment_value):,}".replace(",", "."))
with cols[1]:
    ui.metric_card("Total Order yang sudah Dibayar", f"{total_orders_delivered:,} Order".replace(",", "."))

# Bar chart untuk lokasi seller berdasarkan valuasi
df_location = pd.merge(sellers, order_items, on='seller_id')
df_location_value = pd.merge(df_location, filtered_order_payments, on='order_id')

top_payment_value_location = (
    df_location_value.groupby('seller_state')
    .agg({'payment_value': 'sum'})
    .reset_index()
    .sort_values(by='payment_value', ascending=False)
)

st.subheader(f'Grafik Batang Untuk Lokasi Seller dengan Valuasi Order Terbesar ({selected_year})')
st.bar_chart(top_payment_value_location, x='seller_state', y='payment_value', color='#4850B5', stack=False)

# Line chart untuk perkembangan pesanan bulanan
filtered_orders['month'] = filtered_orders['order_approved_at'].dt.strftime('%B')
monthly_orders = (
    filtered_orders.groupby('month')
    .size()
    .reindex([
        'January', 'February', 'March', 'April', 'May', 'June', 'July',
        'August', 'September', 'October', 'November', 'December'
    ])
    .fillna(0)
)

st.subheader(f'Grafik Garis Perkembangan Pesanan per Bulan ({selected_year})')
st.line_chart(monthly_orders, use_container_width=True, color='#79D7BE')

# Bar chart untuk valuasi kategori produk
df_value_products = pd.merge(order_items, filtered_order_payments, on='order_id')
df_category_products = pd.merge(products, df_value_products, on='product_id')
df_category_products_eng = pd.merge(df_category_products, products_category, on='product_category_name')

top_payment_value = (
    df_category_products_eng.groupby('product_category_name_english')
    .agg({'payment_value': 'sum'})
    .reset_index()
    .sort_values(by='payment_value', ascending=False)
)

source_value_category = top_payment_value[:20]
st.subheader(f'Grafik Batang Untuk Valuasi Tiap Kategori Produk (20 Barang Teratas) ({selected_year})')
st.bar_chart(source_value_category, x='product_category_name_english', y='payment_value', color='#E82561', stack=False)

# Pie chart untuk jenis pembayaran
top_payment_method = (
    filtered_order_payments.groupby('payment_type')
    .size()
    .reset_index(name='count')
    .sort_values(by='count', ascending=False)
)

st.subheader(f'Grafik Lingkaran Jenis Pembayaran yang Paling Banyak Digunakan ({selected_year})')
sizes = top_payment_method['count']

explode = [0.1 if i == 0 else 0 for i in range(len(sizes))]
labels = top_payment_method['payment_type']

fig1, ax1 = plt.subplots()
wedges, texts, autotexts = ax1.pie(
    sizes, explode=explode, labels=None, autopct='%1.1f%%', shadow=True, startangle=90
)
ax1.axis('equal')
ax1.legend(
    wedges,
    labels,
    title="Jenis Pembayaran",
    loc="center left",
    bbox_to_anchor=(1, 0, 0.5, 1),
)

st.pyplot(fig1)