import json
import pandas as pd
from tqdm import tqdm
from datasets import load_dataset

# Step 1: Read the data2.json file
with open('../../data/skywork_gemma_score.json', 'r') as f:
    data = json.load(f)

# Step 2: Convert to DataFrame
df = pd.DataFrame(data)

# Define all 19 model columns
model_columns = [
    'gemma-2-2b-it', 'gemma-2-9b-it', 'gemma-2-27b-it',
    'Meta-Llama-3-8B-Instruct', 'Meta-Llama-3-70B-Instruct', 'Meta-Llama-3.1-8B-Instruct',
    'Meta-Llama-3.1-70B-Instruct', 'Meta-Llama-3.1-405B-Instruct',
    'Phi-3-mini-128k-instruct', 'Phi-3-small-128k-instruct', 'Phi-3-medium-128k-instruct',
    'Qwen2-1.5B-Instruct', 'Qwen2-7B-Instruct', 'Qwen2-72B-Instruct',
    'Qwen2.5-3B-Instruct', 'Qwen2.5-7B-Instruct', 'Qwen2.5-14B-Instruct',
    'Qwen2.5-32B-Instruct', 'Qwen2.5-72B-Instruct'
]

# Step 3: Find the lowest score and corresponding model for each uuid
bottom_scores = []
for _, row in tqdm(df.iterrows(), total=df.shape, desc="Finding bottom scores"):
    bottom_model = min(model_columns, key=lambda col: row[col])  # Find the model with the lowest score
    bottom_score = row[bottom_model]  # Record the lowest score
    bottom_scores.append({
        'uuid': row['uuid'],
        'instruction': row['instruction'],
        'bottom_model': bottom_model,
        'bottom_score': bottom_score
    })

# Convert to DataFrame and sort by the lowest score to select the top 1k data
bottom_scores_df = pd.DataFrame(bottom_scores)
bottom_1k_df = bottom_scores_df.sort_values(by='bottom_score', ascending=True).head(1000)

# Step 4: Load the dataset
ds = load_dataset("Magpie-Align/Magpie-100K-Generator-Zoo",
                  cache_dir='../../../magpie_100k')['train']

# Store the final results
rm_bottom_output = []

# Step 5: Iterate through the bottom_1k data to extract the corresponding model responses
for _, row in tqdm(bottom_1k_df.iterrows(), total=bottom_1k_df.shape, desc="Extracting responses"):
    uuid = row['uuid']
    instruction = row['instruction']
    bottom_model = row['bottom_model']

    # Find the response content for the corresponding `uuid` and `bottom_model` in the dataset
    matched_row = next((item for item in ds if item['uuid'] == uuid), None)
    response = matched_row[bottom_model]['content']

    # Add to the results
    rm_bottom_output.append({
        'uuid': uuid,
        'instruction': instruction,
        'response': response
    })

# Step 6: Save the results to a JSON file
with open('gemma_rm_bottom.json', 'w') as f:
    json.dump(rm_bottom_output, f, indent=4)