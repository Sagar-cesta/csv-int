import streamlit as st
import pandas as pd
import boto3
import io

st.set_page_config(page_title="📊 S3 CSV Explorer", layout="wide")

st.title("🗂️ S3 CSV Viewer & Explorer")

# Load S3 credentials from Streamlit secrets
AWS_ACCESS_KEY = st.secrets["aws_access_key_id"]
AWS_SECRET_KEY = st.secrets["aws_secret_access_key"]
BUCKET_NAME = st.secrets["bucket"]
CSV_KEY = st.secrets["csv_key"]  # Example: 'your-folder/your-file.csv'

# Connect to S3
@st.cache_data
def load_data_from_s3(nrows=None):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=CSV_KEY)
    df = pd.read_csv(io.BytesIO(obj["Body"].read()), nrows=nrows)
    return df

st.info("Loading preview from S3...")
try:
    df = load_data_from_s3(nrows=100_000)  # Load top 100K rows for responsiveness
    st.success(f"✅ Loaded `{CSV_KEY}` with {len(df):,} rows.")

    # Show filters
    with st.expander("🔍 Filter Data"):
        column = st.selectbox("Choose column to filter:", df.columns)
        unique_vals = df[column].dropna().unique()
        selected = st.multiselect(f"Filter `{column}` by:", unique_vals)
        if selected:
            df = df[df[column].isin(selected)]

    st.dataframe(df, use_container_width=True)

    # Summary stats
    with st.expander("📈 Summary Stats"):
        st.write(df.describe(include="all"))

    # Option to download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Filtered CSV", csv, file_name="filtered_output.csv", mime="text/csv")

except Exception as e:
    st.error(f"❌ Error loading file: {e}")
