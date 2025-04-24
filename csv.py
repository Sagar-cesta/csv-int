import streamlit as st
import pandas as pd
import boto3
import io

# Set Streamlit page configuration
st.set_page_config(page_title="📊 S3 CSV Viewer & Explorer", layout="wide")

# Header
st.title("📁 S3 CSV Viewer & Explorer")

# Load AWS credentials & S3 info from .streamlit/secrets.toml
AWS_ACCESS_KEY = st.secrets["aws_access_key_id"]
AWS_SECRET_KEY = st.secrets["aws_secret_access_key"]
BUCKET_NAME = st.secrets["bucket"]
CSV_KEY = st.secrets["csv_key"]

# Initialize S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

# Display a loading spinner while reading the file
with st.spinner("Loading preview from S3..."):
    try:
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=CSV_KEY)
        # Stream the file in memory (only partial for preview)
        preview_df = pd.read_csv(io.BytesIO(obj['Body'].read()), nrows=500)

        st.success("✅ Preview loaded successfully!")
        st.dataframe(preview_df, use_container_width=True)

        # Download button for preview
        st.download_button(
            label="⬇️ Download Preview (500 rows)",
            data=preview_df.to_csv(index=False),
            file_name="preview_sample.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

# --- Pre-signed URL for full download ---
st.markdown("---")
st.subheader("📥 Full CSV Download")

EXPIRATION_SECONDS = 3600  # 1 hour

try:
    presigned_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': CSV_KEY},
        ExpiresIn=EXPIRATION_SECONDS
    )

    st.markdown(
        f"[🔗 Click here to download full CSV file (~215 GB)]({presigned_url})\n\n"
        f"🕐 Link valid for **{EXPIRATION_SECONDS // 60} minutes**."
    )

except Exception as e:
    st.error(f"⚠️ Could not generate download link: {e}")
