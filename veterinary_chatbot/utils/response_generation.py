from transformers import LlamaForCausalLM, LlamaTokenizer

tokenizer = LlamaTokenizer.from_pretrained("meta-llama/LLaMA-7b")  # Specify the exact model you’re using
model = LlamaForCausalLM.from_pretrained("meta-llama/LLaMA-7b")

def generate_response(query, species_embedding):
    inputs = tokenizer(query, return_tensors="pt")
    outputs = model.generate(inputs["input_ids"])
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response
