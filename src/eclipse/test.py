from eclipse import \
    process_text  # Replace 'your_script_name' with the actual name of the script without '.py'

# Set the path to the pretrained BERT model. This should be the same as DEFAULT_MODEL_PATH in the script
model_path = "./ner_model_bert"

# Example text to process
input_text = "Your example text here."

# Process the text
# The 'device' argument is either 'cpu' or 'cuda' depending on whether you are using CPU or GPU
(
    processed_text,
    highest_avg_label,
    highest_avg_confidence,
    is_high_confidence,
) = process_text(input_text, model_path, "cpu")

print(f"Processed Text: {processed_text}")
print(f"Highest Average Label: {highest_avg_label}")
print(f"Highest Average Confidence: {highest_avg_confidence}")
print(f"Is High Confidence: {is_high_confidence}")
