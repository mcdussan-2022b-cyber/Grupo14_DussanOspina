
import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
import os

st.set_page_config(page_title="JSONPlaceholder Dashboard", layout="wide", page_icon="📊")

@st.cache_resource
def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432),
        dbname=os.getenv("DB_NAME", "etl_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres")
    )

@st.cache_data
def query(sql):
    conn = get_conn()
    return pd.read_sql(sql, conn)

st.title("Dashboard ETL - JSONPlaceholder")
st.caption("CORHUILA | Ingeniería de Sistemas | Minería de Datos 2026")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Usuarios",    query("SELECT COUNT(*) as n FROM usuarios").iloc[0,0])
col2.metric("Posts",       query("SELECT COUNT(*) as n FROM posts").iloc[0,0])
col3.metric("Comentarios", query("SELECT COUNT(*) as n FROM comentarios").iloc[0,0])
col4.metric("Todos",       query("SELECT COUNT(*) as n FROM todos").iloc[0,0])

st.divider()
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Posts por usuario")
    df1 = query("""SELECT u.nombre, COUNT(p.id) as posts FROM usuarios u LEFT JOIN posts p ON u.id = p.user_id GROUP BY u.nombre ORDER BY posts DESC""")
    fig1 = px.bar(df1, x="posts", y="nombre", orientation="h", color="posts", color_continuous_scale="Teal")
    fig1.update_layout(showlegend=False, yaxis_title="", xaxis_title="Posts")
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.subheader("Tasa de completitud de todos")
    df2 = query("""SELECT u.nombre, ROUND(100.0 * SUM(CASE WHEN t.completado THEN 1 ELSE 0 END) / COUNT(t.id), 1) as pct FROM usuarios u JOIN todos t ON u.id = t.user_id GROUP BY u.nombre ORDER BY pct DESC""")
    fig2 = px.bar(df2, x="pct", y="nombre", orientation="h", color="pct", color_continuous_scale="Purples", range_color=[0,100])
    fig2.update_layout(showlegend=False, yaxis_title="", xaxis_title="% completado")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Usuarios mas comentados")
df3 = query("""SELECT u.nombre, COUNT(c.id) as comentarios FROM usuarios u JOIN posts p ON u.id = p.user_id JOIN comentarios c ON p.id = c.post_id GROUP BY u.nombre ORDER BY comentarios DESC""")
fig3 = px.bar(df3, x="nombre", y="comentarios", color="comentarios", color_continuous_scale="Oranges")
fig3.update_layout(showlegend=False, xaxis_title="", yaxis_title="Comentarios")
st.plotly_chart(fig3, use_container_width=True)
