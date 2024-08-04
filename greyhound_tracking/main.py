import os
import click
from dotenv import load_dotenv
import requests

load_dotenv()


def fetch_bucket_contents(bucket_name):
    url = f"https://storage.googleapis.com/storage/v1/b/{bucket_name}/o"
    params = {
        "projection": "noAcl",
        "prettyPrint": "false"
    }

    all_contents = []
    next_page_token = None

    while True:
        if next_page_token:
            params["pageToken"] = next_page_token

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            all_contents.extend(data.get("items", []))
            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break
        else:
            print(f"Failed to fetch bucket contents. Status code: {response.status_code}")
            return None

    return all_contents

def download_blob(media_link, destination_file_name):

    response = requests.get(media_link)
    if response.status_code == 200:
        with open(destination_file_name, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded to {destination_file_name}")
        return True
    else:
        print(f"Failed to download. Status code: {response.status_code}. Attempt {attempt + 1} of {max_retries}")

        return False

@click.group()
def cli():
    pass

@click.command()
def sync():
    """Sync data from GCS bucket to local directory."""
    data_directory = os.getenv('DATA_DIRECTORY')
    if not data_directory:
        print("DATA_DIRECTORY environment variable not set.")
        return
    
    bucket_name = 'greyhound-vision-data'
    
    bucket_contents = fetch_bucket_contents(bucket_name)

    if bucket_contents:
        for item in bucket_contents:
            relative_path = item['name']
            full_path = os.path.join(data_directory, relative_path)

            # Skip directories
            if item['name'].endswith('/'):
                continue

            os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
            media_link = item.get('mediaLink')
            if media_link:
                success = download_blob(media_link, full_path)
                if not success:
                    print(f"Failed to download {item['name']} after multiple attempts.")
            else:
                print(f"No mediaLink found for {item['name']}")

@click.command()
def train():
    print("Training... (this is a stub)")

cli.add_command(sync)
cli.add_command(train)

if __name__ == '__main__':
    cli()