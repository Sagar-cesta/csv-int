import streamlit as st
import pandas as pd
import boto3
import io

st.set_page_config(page_title="📁 S3 CSV Viewer & Explorer", layout="wide")
st.title("📂 S3 CSV Viewer & Explorer")

st.info("Loading preview from S3...")

# 🔐 Load AWS credentials from secrets
AWS_ACCESS_KEY = st.secrets["aws_access_key_id"]
AWS_SECRET_KEY = st.secrets["aws_secret_access_key"]
BUCKET_NAME = st.secrets["bucket"]
CSV_KEY = st.secrets["csv_key"]

try:
    # 🔌 Connect to S3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    # 📥 Load CSV
    response = s3.get_object(Bucket=BUCKET_NAME, Key=CSV_KEY)
    csv_data = response['Body'].read().decode('utf-8')

    # 🧾 Convert to DataFrame
    df = pd.read_csv(io.StringIO(csv_data))

    st.success("✅ File loaded successfully!")
    st.dataframe(df, use_container_width=True)

    with st.expander("🔍 Filter & Search"):
        col = st.selectbox("Select column to filter:", df.columns)
        keyword = st.text_input("Enter keyword:")
        if keyword:
            filtered_df = df[df[col].astype(str).str.contains(keyword, case=False)]
            st.write(f"🔍 Showing results for '{keyword}' in `{col}`:")
            st.dataframe(filtered_df, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error loading file: {e}")

