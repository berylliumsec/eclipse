import argparse
import html
import json
import logging
import os
import shutil
import socket
import subprocess
from collections import defaultdict
from importlib.metadata import version
from typing import List, Set, Tuple
from zipfile import ZipFile

import requests
import torch
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from termcolor import cprint
from transformers import BertForTokenClassification, BertTokenizerFast

s3_url = "https://nebula-models.s3.amazonaws.com/ner_model_bert.zip"  # Update this with your actual S3 URL

# Define the label mappings
label_to_id = {
    "O": -100,
    "NETWORK_INFORMATION": 1,
    "BENIGN": 2,
    "SECURITY_CREDENTIALS": 3,
    "PERSONAL_DATA": 4,
}
id_to_label = {id: label for label, id in label_to_id.items()}

DEFAULT_MODEL_PATH = "./ner_model_bert"


def get_s3_file_etag(s3_url):
    if not is_internet_available():
        cprint("No internet connection available. Skipping version check.", "red")
        return None
    response = requests.head(s3_url)
    return response.headers.get("ETag")


def get_local_metadata(file_name):
    try:
        with open(file_name, "r") as f:
            data = json.load(f)
            return data.get("etag")
    except FileNotFoundError:
        return None


def is_run_as_package():
    # Check if the script is within a 'site-packages' directory
    return "site-packages" in os.path.abspath(__file__)


def get_latest_pypi_version(package_name):
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
        if response.status_code == 200:
            return response.json()["info"]["version"]
    except requests.exceptions.RequestException as e:
        cprint(f"Failed to get latest version information: {e}", "red")
    return None


def check_new_pypi_version(package_name="eclipse-ai"):
    """Check if a newer version of the package is available on PyPI."""
    if not is_internet_available():
        cprint("No internet connection available. Skipping version check.", "red")
        return

    try:
        installed_version = version(package_name)
    except Exception as e:
        cprint(f"Error retrieving installed version of {package_name}: {e}", "red")
        return

    cprint(f"Installed version: {installed_version}", "green")

    try:
        latest_version = get_latest_pypi_version(package_name)
        if latest_version is None:
            cprint(
                f"Error retrieving latest version of {package_name} from PyPI.", "red"
            )
            return

        if latest_version > installed_version:
            cprint(
                f"A newer version ({latest_version}) of {package_name} is available on PyPI. Please consider updating to access the latest features!",
                "yellow",
            )
    except Exception as e:
        cprint(f"An error occurred while checking for the latest version: {e}", "red")


def get_input_with_default(message, default_text=None):
    style = Style.from_dict({"prompt": "cyan", "info": "cyan"})
    history = InMemoryHistory()
    if default_text:
        user_input = prompt(message, default=default_text, history=history, style=style)
    else:
        user_input = prompt(message, history=history, style=style)
    return user_input


def folder_exists_and_not_empty(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return False
    # Check if the folder is empty
    if not os.listdir(folder_path):
        return False
    return True


def download_and_unzip(url, output_name):
    try:
        # Download the file from the S3 bucket using wget with progress bar
        print("Downloading...")
        subprocess.run(
            ["wget", "--progress=bar:force:noscroll", url, "-O", output_name],
            check=True,
        )

        # Define the target directory based on the intended structure
        target_dir = os.path.splitext(output_name)[0]  # Removes '.zip' from output_name

        # Extract the ZIP file
        print("\nUnzipping...")
        with ZipFile(output_name, "r") as zip_ref:
            # Here we will extract in a temp directory to inspect the structure
            temp_dir = "temp_extract_dir"
            zip_ref.extractall(temp_dir)

            # Check if there is an unwanted nested structure
            extracted_dirs = os.listdir(temp_dir)
            if len(extracted_dirs) == 1 and os.path.isdir(
                os.path.join(temp_dir, extracted_dirs[0])
            ):
                nested_dir = os.path.join(temp_dir, extracted_dirs[0])
                # Move content up if there is exactly one directory inside
                if os.path.basename(nested_dir) == "ner_model_bert":
                    shutil.move(nested_dir, target_dir)
                else:
                    shutil.move(nested_dir, os.path.join(target_dir, "ner_model_bert"))
            else:
                # No nested structure, so just move all to the target directory
                os.makedirs(target_dir, exist_ok=True)
                for item in extracted_dirs:
                    shutil.move(
                        os.path.join(temp_dir, item), os.path.join(target_dir, item)
                    )

            # Cleanup temp directory
            shutil.rmtree(temp_dir)

        # Remove the ZIP file to clean up
        os.remove(output_name)
    except subprocess.CalledProcessError as e:
        cprint(f"Error occurred during download: {e}", "red")
        logging.error(f"Error occurred during download: {e}")
    except Exception as e:
        cprint(f"Unexpected error: {e}", "red")
        logging.error(f"Unexpected error: {e}")


def save_local_metadata(file_name, etag):
    with open(file_name, "w") as f:
        json.dump({"etag": etag}, f)


def ensure_model_folder_exists():
    metadata_file = os.path.join(DEFAULT_MODEL_PATH, "metadata.json")
    local_etag = get_local_metadata(metadata_file)
    s3_etag = get_s3_file_etag(s3_url)
    if s3_etag is None:
        return  # Exit if there's no internet connection or other issues with S3

    # Check if the model directory exists and has the same etag (metadata)
    if folder_exists_and_not_empty(DEFAULT_MODEL_PATH) and local_etag == s3_etag:
        cprint(f"Model directory {DEFAULT_MODEL_PATH} is up-to-date.", "green")
        return  # No need to update anything as local version matches S3 version

    # If folder doesn't exist, is empty, or etag doesn't match, prompt for download.
    user_input = "y"
    if local_etag and local_etag != s3_etag:
        user_input = get_input_with_default(
            "New versions of the models are available, would you like to download them? (y/n) "
        )

    if user_input.lower() != "y":
        return  # Exit if user chooses not to update

    # Logic to remove the model directory if it exists
    if os.path.exists(DEFAULT_MODEL_PATH):
        cprint("Removing existing model folder...", "yellow")
        shutil.rmtree(DEFAULT_MODEL_PATH)

    cprint(
        f"{DEFAULT_MODEL_PATH} not found or is different. Downloading and unzipping...",
        "yellow",
    )
    download_and_unzip(s3_url, f"{DEFAULT_MODEL_PATH}.zip")
    # Save new metadata
    save_local_metadata(metadata_file, s3_etag)


def is_internet_available(host="8.8.8.8", port=53, timeout=3):
    """Check if there is an internet connection."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False


def recognize_entities_bert(
    prompt_text: str,
    model: BertForTokenClassification,
    tokenizer: BertTokenizerFast,
    device: torch.device,
) -> Tuple[Set[str], List[str], List[float], float]:
    """
    Recognize entities using BERT model and return unique labels detected along with all labels, their confidence scores, and average confidence score.
    """
    try:
        tokenized_inputs = tokenizer(
            prompt_text,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors="pt",
        )
        tokenized_inputs = tokenized_inputs.to(device)

        with torch.no_grad():
            outputs = model(**tokenized_inputs)

        logits = outputs.logits
        softmax = torch.nn.functional.softmax(logits, dim=-1)
        confidence_scores, predictions = torch.max(softmax, dim=2)
        average_confidence = (
            confidence_scores.mean().item()
        )  # Calculate average confidence

        predictions_labels = [
            id_to_label.get(pred.item(), "O") for pred in predictions[0]
        ]
        confidence_list = (
            confidence_scores.squeeze().tolist()
        )  # Convert to list for easier processing

        detected_labels = {label for label in predictions_labels if label != "O"}
        return detected_labels, predictions_labels, confidence_list, average_confidence
    except Exception as e:
        print(f"An error occurred in recognize_entities_bert: {e}")
        # Return empty sets and lists if an error occurs
        return set(), [], [], 0.0


def process_text(
    input_text: str, model_path: str, device: str
) -> Tuple[str, defaultdict, float, bool]:
    try:
        device = torch.device(
            "cuda" if torch.cuda.is_available() and device == "cuda" else "cpu"
        )
        tokenizer = BertTokenizerFast.from_pretrained(model_path)
        model = BertForTokenClassification.from_pretrained(model_path)

        # Ensure the model uses the correct label mappings
        model.config.id2label = id_to_label
        model.config.label2id = label_to_id

        model.to(device)
        model.eval()

        (
            unique_labels_detected,
            labels_detected,
            confidences,
            avg_confidence,
        ) = recognize_entities_bert(input_text, model, tokenizer, device)

        # Collate labels and their corresponding confidences
        label_confidences = defaultdict(list)
        for label, conf in zip(labels_detected, confidences):
            label_confidences[label].append(conf)

        # Determine the label with the highest average confidence
        highest_avg_label, highest_avg_conf = max(
            label_confidences.items(),
            key=lambda lc: sum(lc[1]) / len(lc[1]),
            default=("BENIGN", [avg_confidence]),
        )

        # Determine if non-'BENIGN' labels exist and average confidence is above threshold
        non_benign_high_conf = (
            "BENIGN" not in highest_avg_label and avg_confidence > 0.80
        )
        return input_text, highest_avg_label, highest_avg_conf, non_benign_high_conf
    except Exception as e:
        print(f"An error occurred in process_text: {e}")
        # Return empty results and false for high confidence if an error occurs
        return input_text, defaultdict(list), 0.0, False


def main():
    # Check for new PyPI package version
    check_new_pypi_version()
    # Ensure the model folder exists and is updated
    ensure_model_folder_exists()

    parser = argparse.ArgumentParser(description="Entity recognition using BERT.")
    parser.add_argument(
        "-p", "--prompt", type=str, help="Direct text prompt for recognizing entities."
    )
    parser.add_argument(
        "-f", "--file", type=str, help="Path to a text file to read prompts from."
    )
    parser.add_argument(
        "-m",
        "--model_path",
        type=str,
        default=DEFAULT_MODEL_PATH,
        help="Path to the pretrained BERT model.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="output.html",
        help="Path to the output HTML file.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode to display label and confidence for every line.",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        type=str,
        default="\n",
        help="Delimiter to separate text inputs, defaults to newline.",
    )
    args = parser.parse_args()

    if args.prompt:
        line, highest_avg_label, highest_avg_conf, high_conf = process_text(
            args.prompt, args.model_path, "cpu"
        )
        # Print results with the highest average label and its confidence
        print(
            f"{line}: {highest_avg_label} (Highest Avg. Conf.: {sum(highest_avg_conf)/len(highest_avg_conf):.2f})"
        )
    elif args.file:
        try:
            results = []
            with open(args.file, "r") as file:
                file_content = file.read()
                lines = (
                    file_content.split(args.delimiter)
                    if args.delimiter != "\n"
                    else file_content.splitlines()
                )
                for line in lines:
                    line = line.strip()
                    if line:  # Avoid processing empty lines
                        results.append(process_text(line, args.model_path, "cpu"))

            with open(args.output, "w") as html_file:
                html_file.write("<html><body>\n")
                for line, highest_avg_label, highest_avg_conf, high_conf in results:
                    debug_info = ""
                    if args.debug:
                        debug_info = f" <small>(Highest Avg. Label: {highest_avg_label}, Highest Avg. Conf.: {sum(highest_avg_conf)/len(highest_avg_conf):.2f})</small>"

                    colored_line = html.escape(line)
                    if high_conf:
                        colored_line = (
                            f"<span style='color: red;'>{colored_line}</span>"
                        )
                    html_file.write(f"{colored_line}{debug_info}<br>\n")
                html_file.write("</body></html>")
            print(f"Output written to {args.output}")
        except FileNotFoundError:
            print(f"The file {args.file} was not found.")
    else:
        print(
            "No input provided. Please use --prompt or --file to provide input text for entity recognition."
        )


if __name__ == "__main__":
    main()
