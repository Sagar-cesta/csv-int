import streamlit as st
import pandas as pd
import boto3
from botocore.exceptions import ClientError
import os

st.set_page_config(page_title="S3 CSV Viewer & Downloader", layout="wide")

try:
    st.title("📂 S3 CSV Viewer & Explorer")

    # 🔐 Load credentials from secrets
    AWS_ACCESS_KEY = st.secrets["aws_access_key_id"]
    AWS_SECRET_KEY = st.secrets["aws_secret_access_key"]
    BUCKET_NAME = st.secrets["bucket"]
    CSV_KEY = st.secrets["csv_key"]

    st.markdown("✅ **Secrets Loaded:**")
    st.code(f"Bucket: {BUCKET_NAME}\nKey: {CSV_KEY}", language="text")

    # 🔗 Generate Presigned URL
    def generate_presigned_url():
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY,
                region_name="us-east-2"  # Update if using different region
            )
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': BUCKET_NAME, 'Key': CSV_KEY},
                ExpiresIn=3600  # 1 hour
            )
            return url
        except ClientError as e:
            st.error(f"❌ Failed to generate presigned URL: {e}")
            return None

    presigned_url = generate_presigned_url()
    if presigned_url:
        st.success("🎯 CSV file is available to download below:")
        st.markdown(f"[⬇️ Download full CSV (215GB)]({presigned_url})", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Could not generate a presigned URL for download.")

    # 🚀 Show only preview (first N rows)
    st.subheader("👀 Preview Top Rows")
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name="us-east-2"
    )
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=CSV_KEY)
    preview_df = pd.read_csv(obj["Body"], nrows=50)
    st.dataframe(preview_df)

except Exception as e:
    st.error(f"💥 Streamlit App Error: {e}")
    st.stop()
